from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import tempfile
import os
from dotenv import load_dotenv

print("🚀 FastAPI app is starting...")

load_dotenv()

API_KEY = os.getenv("HACKRX_API_KEY", "123456")  # fallback for dev use
app = FastAPI(title="HackRx DocuQuery API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/hackrx/run")
async def hackrx_run(request: Request):
    try:
        # --- Auth Check ---
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        token = auth.split(" ")[1]
        if token != API_KEY:
            raise HTTPException(status_code=403, detail="Unauthorized")

        # --- Parse Body ---
        body = await request.json()
        document_url = body.get("documents")
        questions = body.get("questions", [])
        if not document_url or not questions:
            raise HTTPException(status_code=400, detail="Missing 'documents' or 'questions'")

        # --- Download File ---
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(document_url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download document")

        # --- Save Temp File ---
        with tempfile.NamedTemporaryFile(delete=False, suffix=document_url.split('.')[-1]) as tmp:
            tmp.write(response.content)
            tmp.flush()
            tmp_file_path = tmp.name

        class DummyUploadFile:
            def __init__(self, file_path, filename):
                self.filename = filename
                self.file = open(file_path, "rb")

        filename = document_url.split("/")[-1]
        file = DummyUploadFile(tmp_file_path, filename)

        # --- Lazy Import Heavy Modules ---
        from modules.extractor import extract_text_from_file
        from modules.embedder import get_faiss_index, get_top_chunks
        from modules.llm import llm_extract_answer

        # --- Process ---
        text = extract_text_from_file(file)
        index_data = get_faiss_index(text)

        answers = []
        for question in questions:
            matched_chunks = get_top_chunks(index_data, question, text)
            context = "\n\n".join(matched_chunks)
            answer = llm_extract_answer(context, question)
            answers.append(answer)

        return JSONResponse({"answers": answers})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
