from langchain_groq import ChatGroq

from app.config import settings


llm = ChatGroq(
    api_key=settings.groq_api_key,
    model="openai/gpt-oss-120b",
    temperature=0,
)