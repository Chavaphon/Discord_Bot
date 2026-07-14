import os
from dotenv import load_dotenv
from pathlib import Path
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma 
from langchain_ollama import OllamaEmbeddings

from typing import Annotated, TypedDict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

from prompt_template import prompt_template

load_dotenv()

class State(TypedDict):
    folder: str
    question: str
    query: str
    retriever: any
    context: str
    source: List[str]
    answer: str

llm = ChatOllama(model=os.getenv("MODEL"))

query_prompt = ChatPromptTemplate.from_template(
    """
        You are an AI assistant specialized in optimizing search queries for a vector database.
        Your task is to analyze the user"s raw question and rewrite it into a concise, keyword-rich query 
        that will retrieve the most relevant documents.

        - Remove conversational filler, greetings, and polite phrasing.
        - Focus on core concepts, terminology, and keywords.
        - Output ONLY the optimized search query. Do not include any explanations, introduction, or markdown.

        User Question: {question}
        Optimized Search Query:
    """
)

answer_prompt = ChatPromptTemplate.from_template(prompt_template.prompt + 
    """
        You are also a helpful guide who answers question only using information from the context.
        Always cite the files you used to answer the question.

        Question: {question}
        Context: {context}
        Source: {source}
    """
)

def setup_retriever(state: State) -> dict:
    documents = []
    folder_path = Path(state["folder"])
    
    for file_path in folder_path.glob("*.pdf"):
        reader = PdfReader(file_path)
        text_content = ""
        
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text_content += extracted_text + "\n"
        
        documents.append(Document(
            page_content=text_content, 
            metadata={"source": str(file_path)}
        ))
            
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    vector_store = Chroma.from_documents(chunks, embeddings)
    
    return {"retriever": vector_store.as_retriever(search_kwargs={"k": 3})}

def generate_query(state: State) -> dict:
    message = query_prompt.invoke({"question": state["question"]})
    response = llm.invoke(message)

    query = response.content.strip().strip('"').strip("'")
    return {"query": query}

def query(state: State) -> dict:
    retriever = state["retriever"]
    
    docs = retriever.invoke(state["query"])
    
    formatted_chunks = []
    source = set()
    
    for doc in docs:
        source_path = doc.metadata.get("source", "Unknown Source")
        filename = os.path.basename(source_path)
        source.add(filename)
        
        chunk_text = f"[Source: {filename}]\n{doc.page_content}"
        formatted_chunks.append(chunk_text)
    
    context = "\n\n---\n\n".join(formatted_chunks)
    
    return {"context": context, "source": list(source)}

def answer(state: State) -> dict:
    message = answer_prompt.invoke({
        "question": state["question"], 
        "context": state["context"], 
        "source": state["source"]
    })
    response = llm.invoke(message)
    return {"answer": response.content}

builder = StateGraph(State)

builder.add_node("setup_retriever", setup_retriever)
builder.add_node("generate_query", generate_query)
builder.add_node("query", query)
builder.add_node("answer", answer)

builder.add_edge(START, "setup_retriever")
builder.add_edge("setup_retriever", "generate_query")
builder.add_edge("generate_query", "query")
builder.add_edge("query", "answer")
builder.add_edge("answer", END)

graph = builder.compile()

def RAG(user_input: str) -> str:
    folder = os.getenv("PDF_FOLDER")
    response = graph.invoke({"question": user_input, "folder": folder})

    return response["answer"]

if __name__ == "__main__":
    print(RAG("what do we learn in AI Automation?"))