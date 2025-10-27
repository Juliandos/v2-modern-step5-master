import os
from operator import itemgetter
from typing import TypedDict, List, Dict, Any

from dotenv import load_dotenv
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import get_buffer_string, HumanMessage, AIMessage

load_dotenv()

# Initialize embeddings with the modern model
embeddings = OpenAIEmbeddings(model='text-embedding-3-small')

# Connect to the vector store  
vector_store = PGVector(
    collection_name="collection164",
    connection_string=os.getenv("DATABASE_URL"),
    embedding_function=embeddings
)

# Define the prompt template
template = """
Answer given the following context:
{context}

Question: {question}
"""

ANSWER_PROMPT = ChatPromptTemplate.from_template(template)

# Initialize the LLM with modern model  
llm = ChatOpenAI(temperature=0, model='gpt-4o-mini', streaming=True)

# Define input type for the chain
class RagInput(TypedDict):
    question: str

# Create MultiQuery retriever for improved document retrieval
multiquery = MultiQueryRetriever.from_llm(
    retriever=vector_store.as_retriever(),
    llm=llm,
)

# ========== IMPLEMENTACIÓN MANUAL DEL HISTORIAL ==========

# Chat history configuration
postgres_memory_url = os.getenv("DATABASE_URL_UNO")

def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    """Obtener historial de chat manualmente"""
    try:
        history = SQLChatMessageHistory(
            connection_string=postgres_memory_url,
            session_id=session_id
        )
        return history.messages
    except Exception:
        return []

def save_to_chat_history(session_id: str, human_message: str, ai_message: str):
    """Guardar mensajes en el historial manualmente"""
    try:
        history = SQLChatMessageHistory(
            connection_string=postgres_memory_url,
            session_id=session_id
        )
        history.add_user_message(human_message)
        history.add_ai_message(ai_message)
    except Exception as e:
        print(f"Error saving chat history: {e}")

# Template for standalone question generation from chat history
template_with_history = """
Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""

standalone_question_prompt = PromptTemplate.from_template(template_with_history)

def generate_standalone_question(question: str, chat_history: List) -> str:
    """Generar pregunta standalone basada en el historial"""
    if not chat_history:
        return question
    
    history_text = get_buffer_string(chat_history)
    
    # Usar invoke en lugar de ainvoke para evitar problemas async
    standalone_chain = (
        standalone_question_prompt 
        | llm 
        | StrOutputParser()
    )
    
    return standalone_chain.invoke({
        "chat_history": history_text,
        "question": question
    })

# Chain base SIN historial (para cuando no hay session_id)
simple_chain = (
    RunnableParallel(
        context=(itemgetter("question") | multiquery),
        question=itemgetter("question")
    ) |
    RunnableParallel(
        answer=(ANSWER_PROMPT | llm | StrOutputParser()),
        docs=itemgetter("context")
    )
).with_types(input_type=RagInput)

# Chain CON historial (implementación manual)
async def chain_with_history(question: str, session_id: str):
    """Chain con historial implementado manualmente"""
    try:
        # Obtener historial
        chat_history = get_chat_history(session_id)
        
        # Generar pregunta standalone si hay historial
        if chat_history:
            final_question = generate_standalone_question(question, chat_history)
        else:
            final_question = question
        
        # Ejecutar la chain simple con la pregunta procesada
        result = await simple_chain.ainvoke({"question": final_question})
        
        # Guardar en historial
        save_to_chat_history(session_id, question, result["answer"])
        
        return result
        
    except Exception as e:
        # Fallback a chain simple sin historial
        print(f"Error in chain_with_history: {e}")
        return await simple_chain.ainvoke({"question": question})

# Stream con historial
async def stream_with_history(question: str, session_id: str):
    """Stream con historial implementado manualmente"""
    try:
        # Obtener historial
        chat_history = get_chat_history(session_id)
        
        # Generar pregunta standalone si hay historial
        if chat_history:
            final_question = generate_standalone_question(question, chat_history)
        else:
            final_question = question
        
        # Ejecutar stream con la pregunta procesada
        async for chunk in simple_chain.astream({"question": final_question}):
            yield chunk
        
        # Guardar en historial (necesitamos capturar la respuesta completa)
        # Para streaming, esto es más complejo, así que lo omitimos por ahora
        
    except Exception as e:
        # Fallback a stream simple sin historial
        print(f"Error in stream_with_history: {e}")
        async for chunk in simple_chain.astream({"question": question}):
            yield chunk

# Función principal para elegir la cadena correcta
async def get_chain_response(question: str, config: dict = None):
    """Elige entre chain con historial o sin historial"""
    if config and config.get('configurable', {}).get('session_id'):
        session_id = config['configurable']['session_id']
        return await chain_with_history(question, session_id)
    else:
        return await simple_chain.ainvoke({"question": question})

# Función para streaming
async def get_chain_stream(question: str, config: dict = None):
    """Elige entre stream con historial o sin historial"""
    if config and config.get('configurable', {}).get('session_id'):
        session_id = config['configurable']['session_id']
        async for chunk in stream_with_history(question, session_id):
            yield chunk
    else:
        async for chunk in simple_chain.astream({"question": question}):
            yield chunk