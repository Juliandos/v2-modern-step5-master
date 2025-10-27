import os
from operator import itemgetter
from typing import TypedDict

from dotenv import load_dotenv
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import get_buffer_string

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

# Create the old_chain with MultiQuery integration
old_chain = (
    RunnableParallel(
        context=(itemgetter("question") | multiquery),
        question=itemgetter("question")
    ) |
    RunnableParallel(
        answer=(ANSWER_PROMPT | llm),
        docs=itemgetter("context")
    )
).with_types(input_type=RagInput)

# Chat history configuration
postgres_memory_url = "postgresql+psycopg://postgres:postgres@localhost:5432/pdf_rag_history"

get_session_history = lambda session_id: SQLChatMessageHistory(
    connection_string=postgres_memory_url,
    session_id=session_id
)

# Template for standalone question generation from chat history
template_with_history = """
Given the following conversation and a follow
up question, rephrase the follow up question
to be a standalone question, in its original
language

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""

standalone_question_prompt = PromptTemplate.from_template(template_with_history)

# Mini-chain to generate standalone questions from chat context
standalone_question_mini_chain = RunnableParallel(
    question=RunnableParallel(
        question=RunnablePassthrough(),
        chat_history=lambda x: get_buffer_string(x["chat_history"])
    )
    | standalone_question_prompt
    | llm
    | StrOutputParser()
)

# Final chain with message history support
final_chain = RunnableWithMessageHistory(
    runnable=standalone_question_mini_chain | old_chain,
    input_messages_key="question",
    history_messages_key="chat_history",
    output_messages_key="answer",
    get_session_history=get_session_history,
)