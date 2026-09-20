from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_community.vectorstores import FAISS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTOR_INDEX_DIR = PROJECT_ROOT / "vector_index"
EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"
CHAT_MODEL_NAME = "gemini-3.5-flash"
RETRIEVED_CHUNK_COUNT = 4

ANSWER_PROMPT_TEMPLATE = """
You are a context-aware Singapore travel planning assistant.

Your job is to answer the user's question using the retrieved
knowledge-base information.

IMPORTANT RULES:

1. Use the knowledge-base context as the primary source for
   destination information.

2. Do not invent attractions, transportation information,
   activities, prices, opening hours, or other facts that are
   not supported by the context.

3. If the retrieved knowledge does not contain enough information
   to answer the question, explicitly say:
   "I don't have enough information in my current knowledge base
   to answer that accurately."

4. Clearly distinguish between:
   - Facts from the knowledge base
   - Recommendations or suggestions made by you

5. Do not present your own recommendation as a fact.

6. Give a concise but useful answer.

7. When appropriate, organize the answer using headings or
   bullet points.

RETRIEVED KNOWLEDGE:
--------------------
{context}
--------------------

USER QUESTION:
{question}

Now answer the user.
"""


def answer_sample_question(question):
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

    chat_model = ChatGoogleGenerativeAI(
        model=CHAT_MODEL_NAME,
        temperature=0
    )

    matched_chunks = knowledge_retriever.invoke(question)

    context = "\n\n".join(
        chunk.page_content
        for chunk in matched_chunks
    )

    prompt = ANSWER_PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )

    response = chat_model.invoke(prompt)

    print("\nAnswer:")
    print(response.content)

    print("\nSources:")

    seen_sources = set()

    for chunk in matched_chunks:
        title = chunk.metadata.get("source_title")
        url = chunk.metadata.get("source_url")

        if title and url and (title, url) not in seen_sources:
            print(f"- {title}")
            print(f"  {url}")
            seen_sources.add((title, url))


if __name__ == "__main__":
    answer_sample_question("What are some good things to do in Singapore?")
