import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def llm_extract_answer(
    context: str,
    question: str,
    temperature: float = 0.5,
) -> str:
    prompt = f"""Based on the following document context, answer the user's question.

Document Context:
\"\"\"{context}\"\"\"

User Question:
{question}

Instructions for your answer:
- **Be Concise and Direct:** Provide a clear, direct answer to the question, avoiding unnecessary preamble or conversational filler.
- **Extract and Synthesize:** Focus on extracting relevant information directly from the provided context. If multiple pieces of information are relevant, synthesize them into a coherent response.
- **Maintain Neutral Tone:** Present information factually and objectively.
- **Handle Missing Information Gracefully:** If the answer is not explicitly available in the provided context, state clearly and politely that the information could not be found in the document. Do not invent or hallucinate information.
- **Format for Readability:** Use clear paragraphs. If listing items, use bullet points or numbered lists for clarity.
- **Completeness:** Ensure the answer fully addresses all parts of the question based on the available context.

Answer:"""

    try:
        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b-instruct", # This model is generally good for instruction following
            messages=[
                {"role": "system", "content": "You are a highly intelligent and accurate document analysis assistant. Your primary goal is to provide precise answers based *only* on the given document context. You prioritize factual accuracy and clarity."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            # max_tokens=250 # Uncomment and adjust if you want to limit answer length
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {e}"