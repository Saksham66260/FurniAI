"""
End-to-End Integration Tests (Day 7 Requirement)
Covers:
FastAPI -> PostgreSQL -> Redis -> Observability -> RAG -> Hybrid Search
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_database_health():
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"database": True}


def test_observability_headers():
    response = client.get("/")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time-Ms" in response.headers
    assert float(response.headers["X-Process-Time-Ms"]) >= 0


def test_hybrid_search_returns_ranked_results_with_breakdown():
    response = client.get("/products/hybrid-search?q=wooden%20study%20desk&limit=5")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) > 0

    first = results[0]
    assert "product_id" in first
    assert "name" in first
    assert "price" in first
    assert "score" in first
    assert "score_breakdown" in first

    breakdown = first["score_breakdown"]
    assert "semantic" in breakdown
    assert "keyword" in breakdown
    assert "rating" in breakdown
    assert "price" in breakdown


def test_product_detail_and_redis_cache():
    # Fetch product 2
    response1 = client.get("/products/2")
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["product_id"] == 2
    assert "name" in data1
    assert "price" in data1

    # Second fetch should hit Redis cache without error
    response2 = client.get("/products/2")
    assert response2.status_code == 200
    assert response2.json() == data1


def test_product_rag_knowledge_endpoint():
    # Query knowledge for Product 2 (Walnut Study Desk)
    response = client.get("/products/2/knowledge?q=how%20to%20clean%20and%20maintain%20wood")
    assert response.status_code == 200
    chunks = response.json()
    assert isinstance(chunks, list)
    assert len(chunks) > 0

    top_chunk = chunks[0]
    assert top_chunk["product_id"] == 2
    assert "document_type" in top_chunk
    assert "content" in top_chunk
    assert "similarity" in top_chunk
    assert top_chunk["similarity"] > 0.0


def test_cart_retrieval():
    response = client.get("/cart/1")
    assert response.status_code == 200
    cart = response.json()
    assert cart["user_id"] == 1
    assert "items" in cart


def test_agent_chat_endpoint():
    # Basic query to AI assistant
    payload = {
        "message": "What is the price of product 2?",
        "user_id": 1,
    }
    response = client.post("/agent/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "thread_id" in data
    assert "reply" in data
    assert data["status"] in ["COMPLETED", "APPROVAL_REQUIRED"]
