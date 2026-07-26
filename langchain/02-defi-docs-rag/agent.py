import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

load_dotenv()

embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma(persist_directory="./chroma-db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

llm = ChatOpenAI(
    model=os.environ.get("LLM_MODEL"),
    base_url=os.environ.get("LLM_BASE_URL"),
    api_key=os.environ.get("LLM_API_KEY"),
)

SYSTEM_PROMPT = """You are a Uniswap documentation assistant. Answer the user's question using ONLY the context below, taken from Uniswap's official docs. If the context doesn't contain the answer, say you don't know — don't make things up.

Context:
{context}
"""

def ask(question: str) -> tuple[str, list[str]]:
    docs = retriever.invoke(question)
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])
    messages = [
        ("system", SYSTEM_PROMPT.format(context=context)),
        ("human", question),
    ]
    response = llm.invoke(messages)
    sources = sorted(set([doc.metadata["source"] for doc in docs]))
    return response.content, sources