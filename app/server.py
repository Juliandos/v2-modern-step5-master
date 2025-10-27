from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import AsyncGenerator
import asyncio
import json
import os
import shutil
import subprocess

from app.rag_chain import final_chain

app = FastAPI(
    title="Modern RAG API",
    description="A modern RAG application for querying PDF documents (2025 update)",
    version="5.0.0"
)

# Add CORS middleware to enable frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"  # React development server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for PDF downloads
app.mount("/static", StaticFiles(directory="./pdf-documents"), name="static")

# Create PDF documents directory if it doesn't exist
pdf_directory = "./pdf-documents"
os.makedirs(pdf_directory, exist_ok=True)


class QueryRequest(BaseModel):
    question: str
    config: dict = {}


class QueryResponse(BaseModel):
    answer: str
    docs: list = []


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system with a question about the uploaded documents.
    """
    try:
        # Use the enhanced RAG chain with session support
        invoke_input = {"question": request.question}
        if request.config:
            result = await final_chain.ainvoke(invoke_input, config=request.config)
        else:
            result = await final_chain.ainvoke(invoke_input)
        return QueryResponse(
            answer=str(result.get("answer", "")),
            docs=[doc.page_content for doc in result.get("docs", [])]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/stream")
async def stream_query(request: QueryRequest):
    """
    Stream the RAG response for real-time interaction.
    """
    async def generate_response():
        try:
            invoke_input = {"question": request.question}
            config = request.config if hasattr(request, 'config') and request.config else None
            
            if config:
                async for chunk in final_chain.astream(invoke_input, config=config):
                    yield f"data: {json.dumps({'chunk': str(chunk)})}\n\n"
            else:
                async for chunk in final_chain.astream(invoke_input):
                    yield f"data: {json.dumps({'chunk': str(chunk)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    """
    Upload one or more PDF files to the server.
    """
    uploaded_files = []
    for file in files:
        try:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}. Only PDF files are allowed.")
            
            # Save file to PDF directory
            file_path = os.path.join(pdf_directory, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_files.append(file.filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not save file {file.filename}: {e}")
    
    return {"message": "Files uploaded successfully", "filenames": uploaded_files}


@app.post("/load-and-process-pdfs")
async def load_and_process_pdfs():
    """
    Load and process all PDF files from the pdf-documents directory.
    """
    try:
        # Run the RAG data loader script to process PDFs
        subprocess.run(["python", "./rag-data-loader/rag_load_and_process.py"], check=True, cwd=".")
        return {"message": "PDFs loaded and processed successfully"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute processing script: {e}")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Processing script not found. Please ensure rag-data-loader/rag_load_and_process.py exists.")


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy", "version": "5.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)