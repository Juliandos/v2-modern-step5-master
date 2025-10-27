import os
from operator import itemgetter
from typing import TypedDict, List, Dict, Any
import json

from dotenv import load_dotenv
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, get_buffer_string
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

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
You are a helpful assistant. Use the following context and previous conversation to answer the user's question.

Chat History:
{chat_history}

Context:
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

# ========== IMPLEMENTACIÓN DIRECTA DEL HISTORIAL CON SQLAlchemy ==========

# Crear engine para la base de datos de historial
postgres_memory_url = os.getenv("DATABASE_URL_UNO")
history_engine = create_engine(
    postgres_memory_url,
    poolclass=StaticPool,
    pool_pre_ping=True
)

def get_chat_history(session_id: str) -> List:
    """Obtener historial de chat directamente desde la DB"""
    try:
        with history_engine.connect() as conn:
            result = conn.execute(
                text("SELECT message FROM message_store WHERE session_id = :session_id ORDER BY id ASC"),
                {"session_id": session_id}
            )
            
            messages = []
            for row in result:
                msg_data = row[0]  # El mensaje está en JSONB
                
                # Convertir el JSONB a objetos de mensaje de LangChain
                if msg_data.get('type') == 'human':
                    messages.append(HumanMessage(content=msg_data.get('data', {}).get('content', '')))
                elif msg_data.get('type') == 'ai':
                    messages.append(AIMessage(content=msg_data.get('data', {}).get('content', '')))
            
            print(f"📜 Loaded {len(messages)} messages from history for session {session_id}")
            
            if messages:
                for i, msg in enumerate(messages):
                    content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                    print(f"  Message {i+1}: {type(msg).__name__} - {content_preview}")
            
            return messages
            
    except Exception as e:
        print(f"⚠️ Error loading chat history: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_to_chat_history(session_id: str, human_message: str, ai_message: str):
    """Guardar mensajes en el historial directamente en la DB"""
    try:
        with history_engine.connect() as conn:
            # Guardar mensaje humano
            human_msg = {
                "type": "human",
                "data": {
                    "content": human_message,
                    "type": "human"
                }
            }
            
            # Usar CAST en lugar de :: para compatibilidad
            conn.execute(
                text("INSERT INTO message_store (session_id, message) VALUES (:session_id, CAST(:message AS jsonb))"),
                {"session_id": session_id, "message": json.dumps(human_msg)}
            )
            
            # Guardar mensaje AI
            ai_msg = {
                "type": "ai",
                "data": {
                    "content": ai_message,
                    "type": "ai"
                }
            }
            
            conn.execute(
                text("INSERT INTO message_store (session_id, message) VALUES (:session_id, CAST(:message AS jsonb))"),
                {"session_id": session_id, "message": json.dumps(ai_msg)}
            )
            
            conn.commit()
            
            print(f"💾 Saved conversation to history for session {session_id}")
            
            # Verificar que se guardó
            result = conn.execute(
                text("SELECT COUNT(*) FROM message_store WHERE session_id = :session_id"),
                {"session_id": session_id}
            )
            count = result.scalar()
            print(f"✅ Verification: Now have {count} messages in history")
            
    except Exception as e:
        print(f"⚠️ Error saving chat history: {e}")
        import traceback
        traceback.print_exc()

# Template for standalone question generation from chat history
template_with_history = """Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is.

Chat History:
{chat_history}

Follow Up Input: {question}

Standalone question:"""

standalone_question_prompt = PromptTemplate.from_template(template_with_history)

def generate_standalone_question(question: str, chat_history: List) -> str:
    """Generar pregunta standalone basada en el historial"""
    if not chat_history or len(chat_history) == 0:
        print("🔍 No history, using original question")
        return question
    
    # Limitar el historial a los últimos 6 mensajes (3 intercambios) para mejor contexto
    recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
    history_text = get_buffer_string(recent_history)
    
    print(f"🔍 Generating standalone question with {len(recent_history)} recent messages")
    
    standalone_chain = (
        standalone_question_prompt 
        | llm 
        | StrOutputParser()
    )
    
    standalone = standalone_chain.invoke({
        "chat_history": history_text,
        "question": question
    })
    print(f"🔍 Standalone question: {standalone}")
    return standalone

# Chain base SIN historial (para cuando no hay session_id)
simple_chain = (
    RunnableParallel(
        context=(itemgetter("question") | multiquery),
        question=itemgetter("question"),
        chat_history=itemgetter("chat_history")
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
        print(f"\n{'='*60}")
        print(f"🎯 Processing question with history")
        print(f"📝 Session ID: {session_id}")
        print(f"❓ Question: {question}")
        
        # Obtener historial
        chat_history = get_chat_history(session_id)
        
        # Generar pregunta standalone si hay historial
        if chat_history and len(chat_history) > 0:
            final_question = generate_standalone_question(question, chat_history)
        else:
            final_question = question
        
        print(f"✨ Final question: {final_question}")
        
        history_text = get_buffer_string(chat_history) if chat_history else ""
        result = await simple_chain.ainvoke({
            "question": final_question,
            "chat_history": history_text
        })
        
        # Guardar en historial
        answer_text = result.get("answer", "")
        save_to_chat_history(session_id, question, answer_text)
        
        print(f"{'='*60}\n")
        return result
        
    except Exception as e:
        # Fallback a chain simple sin historial
        print(f"❌ Error in chain_with_history: {e}")
        import traceback
        traceback.print_exc()
        return await simple_chain.ainvoke({"question": question})

# Stream con historial
async def stream_with_history(question: str, session_id: str):
    """Stream con historial implementado manualmente"""
    try:
        print(f"\n{'='*60}")
        print(f"🎯 Streaming with history")
        print(f"📝 Session ID: {session_id}")
        print(f"❓ Question: {question}")
        
        # Obtener historial
        chat_history = get_chat_history(session_id)
        
        # Detectar si la pregunta es sobre la conversación misma
        question_lower = question.lower().strip()
        meta_question_keywords = [
            "qué te pregunté", "que te pregunte", "qué pregunté", "que pregunte",
            "pregunta anterior", "preguntaste antes", "pregunté antes", "pregunte antes",
            "what did i ask", "previous question", "última pregunta", "ultima pregunta",
            "te pregunte algo", "te pregunté algo", "no tienes memoria", "tienes memoria"
        ]
        
        is_meta_question = any(keyword in question_lower for keyword in meta_question_keywords)
        
        print(f"🔎 Checking if meta-question: '{question_lower}' -> {is_meta_question}")
        
        if is_meta_question and chat_history and len(chat_history) >= 2:
            print("🔍 Meta-question detected! Answering from conversation history directly")
            
            # Obtener las últimas preguntas del usuario (mensajes humanos)
            user_questions = [msg.content for msg in chat_history if isinstance(msg, HumanMessage)]
            
            if len(user_questions) >= 2:
                # La penúltima pregunta (la actual es la última)
                previous_question = user_questions[-2]
                answer = f"Tu pregunta anterior fue: \"{previous_question}\""
            else:
                answer = "Esta es tu primera pregunta en la conversación."
            
            print(f"✨ Direct answer from history: {answer}")
            
            # Simular el formato de chunk para mantener consistencia con el frontend
            yield {"answer": answer}
            
            # Guardar en historial
            save_to_chat_history(session_id, question, answer)
            print(f"💾 Saved meta-conversation")
            print(f"{'='*60}\n")
            return
        
        # Para preguntas normales, continuar con el flujo normal
        # Generar pregunta standalone si hay historial
        if chat_history and len(chat_history) > 0:
            final_question = generate_standalone_question(question, chat_history)
        else:
            final_question = question
        
        print(f"✨ Final question for streaming: {final_question}")
        
        # Recolectar la respuesta completa para guardarla después
        full_answer = ""
        
        history_text = get_buffer_string(chat_history) if chat_history else ""
        async for chunk in simple_chain.astream({
            "question": final_question,
            "chat_history": history_text
        }):
            # Capturar el texto de la respuesta
            if isinstance(chunk, dict) and 'answer' in chunk:
                answer_part = chunk['answer']
                if hasattr(answer_part, 'content'):
                    full_answer += answer_part.content
                elif isinstance(answer_part, str):
                    full_answer += answer_part
            
            yield chunk
        
        # Guardar en historial después del stream
        if full_answer:
            save_to_chat_history(session_id, question, full_answer)
            print(f"💾 Saved streamed conversation")
        
        print(f"{'='*60}\n")
        
    except Exception as e:
        # Fallback a stream simple sin historial
        print(f"❌ Error in stream_with_history: {e}")
        import traceback
        traceback.print_exc()
        async for chunk in simple_chain.astream({"question": question}):
            yield chunk

# Función principal para elegir la cadena correcta
async def get_chain_response(question: str, config: dict = None):
    """Elige entre chain con historial o sin historial"""
    if config and config.get('configurable', {}).get('session_id'):
        session_id = config['configurable']['session_id']
        print(f"🔄 Using chain WITH history (session: {session_id})")
        return await chain_with_history(question, session_id)
    else:
        print(f"🔄 Using chain WITHOUT history")
        return await simple_chain.ainvoke({"question": question})

# Función para streaming
async def get_chain_stream(question: str, config: dict = None):
    """Elige entre stream con historial o sin historial"""
    if config and config.get('configurable', {}).get('session_id'):
        session_id = config['configurable']['session_id']
        print(f"🔄 Using stream WITH history (session: {session_id})")
        async for chunk in stream_with_history(question, session_id):
            yield chunk
    else:
        print(f"🔄 Using stream WITHOUT history")
        async for chunk in simple_chain.astream({"question": question}):
            yield chunk