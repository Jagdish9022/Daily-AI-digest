from datetime import datetime
from typing import List, Dict
import html

def generate_html_email(articles: List[Dict]) -> str:
    categories = {
        "AI Engineering": [],
        "IT Industry": [],
        "World News": [],
        "Other": []
    }
    
    for art in articles:
        cat = art.get("category", "Other")
        if cat not in categories:
            cat = "Other"
        categories[cat].append(art)
        
    date_str = datetime.now().strftime("%B %d, %Y")
    
    html_content = f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #2980b9; margin-top: 30px; font-size: 20px; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin-bottom: 20px; background: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; }}
        .title {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
        .source {{ font-size: 12px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }}
        .summary {{ font-size: 14px; margin-top: 10px; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
    </head>
    <body>
        <h1>Daily Digest - {date_str}</h1>
    """
    
    has_content = False
    for cat in ["AI Engineering", "IT Industry", "World News", "Other"]:
        if categories[cat]:
            has_content = True
            html_content += f"<h2>{html.escape(cat)}</h2><ul>"
            for art in categories[cat]:
                title = html.escape(art.get("title", "Untitled"))
                url = art.get("url", "#")
                source = html.escape(art.get("source", "Unknown Source"))
                summary = html.escape(art.get("summary", "No summary available."))
                
                html_content += f"""
                <li>
                    <div class="title"><a href="{url}">{title}</a></div>
                    <div class="source">{source}</div>
                    <div class="summary">{summary}</div>
                </li>
                """
            html_content += "</ul>"
                
    if not has_content:
        html_content += "<p>No new articles today.</p>"
        
    html_content += """
    </body>
    </html>
    """
    return html_content
