from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = DirectoryLoader(
    "uniswap-docs/content", 
    glob="**/*.mdx", # matches .md and .mdx 
    loader_cls=TextLoader, 
    loader_kwargs={"encoding": "utf-8"},
)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(docs)

print(f"{len(docs)} documents -> {len(chunks)} chunks")
print(chunks[0].page_content[:300])
print(chunks[0].metadata)


import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

load_dotenv()

embeddings = OllamaEmbeddings(model="nomic-embed-text")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma-db",
)

print(f"stored {vectorstore._collection.count()} chunks in chroma_db")