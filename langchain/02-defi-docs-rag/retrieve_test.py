from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma(persist_directory="./chroma-db", embedding_function=embeddings)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

query = "how does uniswap v4 handke hooks?"
results = retriever.invoke(query)

for i, doc in enumerate(results):
    print(f"--- result {i+1} (source: {doc.metadata['source']}) ---")
    print(doc.page_content[:300])
    print()