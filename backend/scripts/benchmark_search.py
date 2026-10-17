"""
Search Performance Benchmarking Script (Day 7 Requirement)
Measures actual p50, p95, and p99 query latency for:
1. PostgreSQL Lexical Search (GIN index with tsvector / plainto_tsquery)
2. PostgreSQL Semantic Search (HNSW index with pgvector cosine_ops)
3. Hybrid Search (Semantic + Lexical + Deterministic Python Ranking)
"""

import time
import numpy as np
from sqlalchemy import text
from app.db.database import SessionLocal
from app.services.product_service import ProductService

QUERIES = [
    "minimalist wooden desk",
    "ergonomic leather office chair",
    "round oak dining table",
    "contemporary velvet sofa",
    "king platform bed",
    "industrial coffee table",
    "modern fabric armchair",
    "solid walnut bookcase",
    "outdoor patio bench",
    "compact study desk for bedroom",
]

ITERATIONS_PER_QUERY = 5


def run_benchmark():
    db = SessionLocal()
    print("=" * 65)
    print("FURNIAI SEARCH PERFORMANCE BENCHMARK (5,000 PRODUCTS)")
    print("=" * 65)

    lexical_latencies = []
    semantic_latencies = []
    hybrid_latencies = []

    # 1. Lexical Search Benchmark (GIN index)
    print("\n[1/3] Benchmarking Lexical Search (PostgreSQL GIN Index)...")
    for q in QUERIES:
        for _ in range(ITERATIONS_PER_QUERY):
            t0 = time.perf_counter()
            _ = ProductService.search_products(db=db, query=q, limit=20)
            t1 = time.perf_counter()
            lexical_latencies.append((t1 - t0) * 1000)

    # 2. Semantic Search Benchmark (HNSW index)
    print("[2/3] Benchmarking Semantic Search (pgvector HNSW Index)...")
    for q in QUERIES:
        for _ in range(ITERATIONS_PER_QUERY):
            t0 = time.perf_counter()
            _ = ProductService.semantic_search(db=db, query=q, limit=20)
            t1 = time.perf_counter()
            semantic_latencies.append((t1 - t0) * 1000)

    # 3. Hybrid Search Benchmark (Combined + Deterministic Ranking)
    print("[3/3] Benchmarking Hybrid Search + Deterministic Ranking...")
    for q in QUERIES:
        for _ in range(ITERATIONS_PER_QUERY):
            t0 = time.perf_counter()
            _ = ProductService.hybrid_search(db=db, query=q, limit=20)
            t1 = time.perf_counter()
            hybrid_latencies.append((t1 - t0) * 1000)

    db.close()

    def print_stats(name, data):
        p50 = np.percentile(data, 50)
        p95 = np.percentile(data, 95)
        p99 = np.percentile(data, 99)
        avg = np.mean(data)
        min_v = np.min(data)
        max_v = np.max(data)
        print(f"\n--- {name} (N={len(data)}) ---")
        print(f"  Mean:   {avg:6.2f} ms")
        print(f"  Min:    {min_v:6.2f} ms | Max: {max_v:6.2f} ms")
        print(f"  p50:    {p50:6.2f} ms")
        print(f"  p95:    {p95:6.2f} ms")
        print(f"  p99:    {p99:6.2f} ms")
        return p50, p95, p99

    lex_p50, lex_p95, lex_p99 = print_stats("Lexical Search (GIN)", lexical_latencies)
    sem_p50, sem_p95, sem_p99 = print_stats("Semantic Search (HNSW)", semantic_latencies)
    hyb_p50, hyb_p95, hyb_p99 = print_stats("Hybrid Search (Ranked)", hybrid_latencies)

    print("\n" + "=" * 65)
    print("BENCHMARK SUMMARY TABLE")
    print("=" * 65)
    print(f"{'Retrieval Pipeline':<26} | {'p50 (ms)':<10} | {'p95 (ms)':<10} | {'p99 (ms)':<10}")
    print("-" * 65)
    print(f"{'Lexical (GIN)':<26} | {lex_p50:<10.2f} | {lex_p95:<10.2f} | {lex_p99:<10.2f}")
    print(f"{'Semantic (HNSW)':<26} | {sem_p50:<10.2f} | {sem_p95:<10.2f} | {sem_p99:<10.2f}")
    print(f"{'Hybrid + Ranking':<26} | {hyb_p50:<10.2f} | {hyb_p95:<10.2f} | {hyb_p99:<10.2f}")
    print("=" * 65)


if __name__ == "__main__":
    run_benchmark()
