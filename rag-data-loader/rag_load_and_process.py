import os

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, UnstructuredPDFLoader
from langchain_community.vectorstores.pgvector import PGVector
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

load_dotenv()

loader = DirectoryLoader(
    os.path.abspath("../pdf-documents"),
    glob="**/*.pdf",
    use_multithreading=True,
    show_progress=True,
    max_concurrency=50,
    loader_cls=UnstructuredPDFLoader,
)
docs = loader.load()

# Using the modern text-embedding-3-small model (5x cheaper than ada-002)
embeddings = OpenAIEmbeddings(model='text-embedding-3-small')

text_splitter = SemanticChunker(
    embeddings=embeddings
)

# The docs structure has been simplified in newer versions
# No need for the flattening step that was required in the original
chunks = text_splitter.split_documents(docs)

print(f"Created {len(chunks)} chunks from {len(docs)} documents")

# Create the vector database with the processed chunks
PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="modern_rag_collection",
    connection_string=os.getenv("DATABASE_URL"),
    pre_delete_collection=True,
)

print("Vector database created successfully!")