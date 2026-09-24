import os
import json
import logging
import google.generativeai as genai
from typing import List, Dict
from pydantic import BaseModel, Field
from groq import Groq

logger = logging.getLogger(__name__)

class ArticleResult(BaseModel):
    id: int
    summary: str = Field(description="2-3 sentence summary of the article")
    category: str = Field(description='Must be exactly one of: "AI Engineering", "IT Industry", or "World News"')

class BatchResult(BaseModel):
    results: list[ArticleResult]

def summarize_with_groq(batch: List[Dict], input_data: List[Dict]) -> bool:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("GROQ_API_KEY not found for fallback.")
        return False
        
    try:
        client = Groq(api_key=groq_api_key)
        prompt = (
            "You are an expert tech and news editor. For each article provided in the JSON array below, "
            "provide a 2-3 sentence summary and classify it into one of these exact categories: "
            "'AI Engineering', 'IT Industry', or 'World News'.\n\n"
            f"Articles: {json.dumps(input_data)}\n\n"
            "You MUST output your response in valid JSON format matching this schema:\n"
            "{\"results\": [{\"id\": <int>, \"summary\": \"<string>\", \"category\": \"<string>\"}]}"
        )
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        res_json = json.loads(completion.choices[0].message.content)
        results_list = res_json.get("results", [])
        
        for result in results_list:
            idx = result["id"]
            if 0 <= idx < len(batch):
                batch[idx]["summary"] = result["summary"]
                batch[idx]["category"] = result["category"]
        return True
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return False

def summarize_and_categorize(articles: List[Dict]) -> List[Dict]:
    api_key = os.getenv("GEMINI_API_KEY")
    model = None
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3-flash-preview")
    else:
        logger.warning("GEMINI_API_KEY not found. Will try Groq directly.")

    processed = []
    batch_size = 15
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        
        input_data = []
        for idx, art in enumerate(batch):
            input_data.append({
                "id": idx,
                "title": art.get("title", ""),
                "source": art.get("source", ""),
                "content": art.get("content", "")
            })
            
        success = False
        
        if model:
            prompt = (
                "You are an expert tech and news editor. For each article provided in the JSON array below, "
                "provide a 2-3 sentence summary and classify it into one of these exact categories: "
                "'AI Engineering', 'IT Industry', or 'World News'.\n\n"
                f"Articles: {json.dumps(input_data)}"
            )
            
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=BatchResult,
                        temperature=0.2
                    )
                )
                
                try:
                    res_json = json.loads(response.text)
                    results_list = res_json.get("results", [])
                    
                    for result in results_list:
                        idx = result["id"]
                        if 0 <= idx < len(batch):
                            batch[idx]["summary"] = result["summary"]
                            batch[idx]["category"] = result["category"]
                    success = True
                except Exception as parse_e:
                    logger.error(f"Error parsing JSON from Gemini: {parse_e}")
                    
            except Exception as e:
                logger.error(f"Error calling Gemini API: {e}. Falling back to Groq.")
                
        if not success:
            logger.info("Attempting Groq fallback...")
            summarize_with_groq(batch, input_data)
            
        processed.extend(batch)
        
    return processed
