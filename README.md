# Daily AI & Tech News Digest Pipeline

This repository contains a Python-based pipeline that fetches the top daily news from various AI and tech RSS feeds, summarizes them using the Gemini API, categorizes them, and emails a clean HTML digest.

It runs completely for free using GitHub Actions and the Gemini API free tier.

## Architecture
1. **Fetch**: Pulls top daily posts from arXiv (cs.AI, cs.LG), Hacker News (via Algolia API), TechCrunch, Ars Technica, r/MachineLearning, and a World News feed.
2. **Deduplicate**: Uses a local `sent_articles.json` file to keep track of previously sent articles.
3. **Summarize & Categorize**: Calls Gemini 2.5 Flash (`google-generativeai`) to generate 2-3 sentence summaries and bucket them into logical categories.
4. **Format & Send**: Generates a mobile-friendly HTML digest and sends it via Gmail SMTP.
5. **Persist State**: The GitHub Action commits `sent_articles.json` back to the repository so it won't send you the same article twice.

## Setup Instructions

### 1. Prerequisites
- A Gmail account with 2-Step Verification enabled.
- An App Password for your Gmail account.
- A Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. GitHub Secrets Configuration
To run this pipeline automatically via GitHub Actions, you need to configure the following **Secrets** in your repository settings:
Go to `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`.

Add the following secrets:
* `GEMINI_API_KEY`: Your Gemini API key.
* `EMAIL_ADDRESS`: The Gmail address sending the email (e.g. `your.email@gmail.com`).
* `EMAIL_APP_PASSWORD`: The 16-character Gmail App Password (no spaces). Do **not** use your regular email password.
* `RECIPIENT_EMAIL`: The email address where you want to receive the digest.

### 3. Workflow Permissions
Since the action commits the `sent_articles.json` file back to the repository to track state, ensure GitHub Actions has write access:
1. Go to `Settings` -> `Actions` -> `General`.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Save the changes.

### 4. Running the Action
- The action will automatically run every day at 7:00 AM IST.
- You can manually trigger it immediately by going to the `Actions` tab -> selecting `Daily AI Digest` -> `Run workflow`.
