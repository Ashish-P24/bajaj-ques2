import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def llm_extract_answer(context, question, model="mistralai/mixtral-8x7b-instruct", temperature=0.5):
    prompt = f"""
You are a helpful assistant. Read the context and answer the question clearly and thoroughly.

Context:
\"\"\"{context}\"\"\"

Question:
{question}

Guidelines:
- Write a well-structured, detailed answer in clear form.
- Do not start with "Answer:" or repeat the question.
- If information is missing, respond with: "Not found in the document."

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
