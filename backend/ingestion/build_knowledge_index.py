from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_SOURCE_DIR = PROJECT_ROOT / "knowledge_base" / "singapore"
VECTOR_INDEX_DIR = PROJECT_ROOT / "vector_index"
EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
RETRIEVED_CHUNK_COUNT = 4

SOURCE_CATALOG = {
    "wikivoyage": {
        "title": "Wikivoyage \u2014 Singapore Travel Guide",
        "url": "https://en.wikivoyage.org/wiki/Singapore",
    },
    "essential_travel_information": {
        "title": "Visit Singapore \u2014 Essential Travel Information",
        "url": (
            "https://www.visitsingapore.com/travel-tips/"
            "essential-travel-information/"
        ),
    },
    "things_to_do": {
        "title": "Visit Singapore \u2014 Things To Do",
        "url": (
            "https://www.visitsingapore.com/things-to-do/"
            "top-things-to-do/"
        ),
    },
}

load_dotenv()


def tag_chunk_source(chunk):
    source_path = chunk.metadata.get("source", "").lower()

    for keyword, source_info in SOURCE_CATALOG.items():
        if keyword in source_path:
            chunk.metadata["source_title"] = source_info["title"]
            chunk.metadata["source_url"] = source_info["url"]
            break

    return chunk


def build_knowledge_index():
    markdown_loader = DirectoryLoader(
        KNOWLEDGE_SOURCE_DIR,
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    raw_documents = markdown_loader.load()
    print(f"Loaded {len(raw_documents)} documents")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    knowledge_chunks = text_splitter.split_documents(raw_documents)
    knowledge_chunks = [tag_chunk_source(chunk) for chunk in knowledge_chunks]
    print(f"Created {len(knowledge_chunks)} chunks")

    embedding_model = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME
    )

    knowledge_index = FAISS.from_documents(
        knowledge_chunks,
        embedding_model
    )

    knowledge_index.save_local(str(VECTOR_INDEX_DIR))
    print(f"FAISS knowledge index saved to: {VECTOR_INDEX_DIR}")

    return knowledge_index


def preview_sample_query(knowledge_index, question):
    knowledge_retriever = knowledge_index.as_retriever(
        search_kwargs={"k": RETRIEVED_CHUNK_COUNT}
    )

    results = knowledge_retriever.invoke(question)

    print(f"\nRetrieved information for: {question}\n")

    for position, chunk in enumerate(results, start=1):
        print(f"--- Result {position} ---")
        print(chunk.page_content[:500])
        print()


if __name__ == "__main__":
    index = build_knowledge_index()
    preview_sample_query(index, "What are some interesting things to do in Singapore?")
