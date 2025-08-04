import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

def llm_extract_answer(context, question, model="mistralai/mixtral-8x7b-instruct", temperature=0.2):
    prompt = f"""
You are a helpful assistant. Read the context and answer the question clearly and concisely.

Context:
\"\"\"{context}\"\"\"

Question:
{question}

Guidelines:
- Write a short, factual, and concise answer.
- Do not start with "Answer:" or repeat the question.
- If information is missing, respond with: "Not found in the document.
- Please keep calm and do not hallucinate."

Answer:
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a highly capable document assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {e}"
    print("Loaded OpenRouter Key:", api_key)

