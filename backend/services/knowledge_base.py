from pathlib import Path
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTOR_INDEX_DIR = PROJECT_ROOT / "vector_index"
EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"
RETRIEVED_CHUNK_COUNT = 4

load_dotenv()

embedding_model = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL_NAME
)

knowledge_index = FAISS.load_local(
    str(VECTOR_INDEX_DIR),
    embedding_model,
    allow_dangerous_deserialization=True
)

knowledge_retriever = knowledge_index.as_retriever(
    search_kwargs={"k": RETRIEVED_CHUNK_COUNT}
)


@tool
def search_travel_knowledge_base(query: str) -> str:
    """
    Search the Singapore travel knowledge base.

    Use this tool for relatively stable destination information
    such as attractions, neighbourhoods, transportation,
    food, activities, cultural information, and sample itineraries.

    Do NOT use this tool for current weather or current exchange rates.
    """

    matched_chunks = knowledge_retriever.invoke(query)

    if not matched_chunks:
        return (
            "No relevant information was found in the Singapore knowledge base."
        )

    formatted_results = []

    for chunk in matched_chunks:
        title = chunk.metadata.get(
            "source_title",
            "Unknown source"
        )

        url = chunk.metadata.get(
            "source_url",
            ""
        )

        formatted_results.append(
            f"""
            SOURCE TITLE: {title}
            SOURCE URL: {url}

            CONTENT:
            {chunk.page_content}
            """
        )

    return "\n\n".join(formatted_results)
