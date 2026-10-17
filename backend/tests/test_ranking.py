"""
Unit tests for deterministic search ranking algorithm (Day 7 Requirement)
Formula:
Score = 0.50 * S_semantic + 0.20 * S_keyword + 0.15 * S_rating + 0.15 * S_price
"""

import pytest


def calculate_deterministic_score(
    semantic: float,
    keyword: float,
    rating_out_of_5: float,
    price: float,
    min_price: float,
    max_price: float,
) -> tuple[float, dict]:
    rating_norm = max(0.0, min(1.0, rating_out_of_5 / 5.0))
    if max_price == min_price:
        price_norm = 1.0
    else:
        price_norm = max(0.0, min(1.0, (max_price - price) / (max_price - min_price)))

    sem_norm = max(0.0, min(1.0, semantic))
    kw_norm = max(0.0, min(1.0, keyword))

    score = (
        0.50 * sem_norm
        + 0.20 * kw_norm
        + 0.15 * rating_norm
        + 0.15 * price_norm
    )

    breakdown = {
        "semantic": sem_norm,
        "keyword": kw_norm,
        "rating": rating_norm,
        "price": price_norm,
    }
    return score, breakdown


def test_weights_sum_to_one():
    w_sem, w_kw, w_rate, w_price = 0.50, 0.20, 0.15, 0.15
    assert (w_sem + w_kw + w_rate + w_price) == pytest.approx(1.0)


def test_perfect_signals_yield_maximum_score():
    score, breakdown = calculate_deterministic_score(
        semantic=1.0,
        keyword=1.0,
        rating_out_of_5=5.0,
        price=100.0,
        min_price=100.0,
        max_price=500.0,
    )
    assert score == pytest.approx(1.0)
    assert breakdown["semantic"] == 1.0
    assert breakdown["keyword"] == 1.0
    assert breakdown["rating"] == 1.0
    assert breakdown["price"] == 1.0


def test_zero_signals_yield_minimum_score():
    score, breakdown = calculate_deterministic_score(
        semantic=0.0,
        keyword=0.0,
        rating_out_of_5=0.0,
        price=500.0,
        min_price=100.0,
        max_price=500.0,
    )
    assert score == pytest.approx(0.0)
    assert breakdown["semantic"] == 0.0
    assert breakdown["keyword"] == 0.0
    assert breakdown["rating"] == 0.0
    assert breakdown["price"] == 0.0


def test_price_tie_yields_full_price_score():
    score, breakdown = calculate_deterministic_score(
        semantic=0.5,
        keyword=0.5,
        rating_out_of_5=4.0,
        price=250.0,
        min_price=250.0,
        max_price=250.0,
    )
    # When max_price == min_price, price normalization is 1.0
    assert breakdown["price"] == 1.0
    expected = 0.50 * 0.5 + 0.20 * 0.5 + 0.15 * 0.8 + 0.15 * 1.0
    assert score == pytest.approx(expected)


def test_ranking_prefers_higher_semantic_similarity():
    # Product A has high semantic similarity (0.9), average price
    score_a, _ = calculate_deterministic_score(
        semantic=0.9,
        keyword=0.3,
        rating_out_of_5=4.0,
        price=300.0,
        min_price=100.0,
        max_price=500.0,
    )
    # Product B has low semantic similarity (0.2), same other signals
    score_b, _ = calculate_deterministic_score(
        semantic=0.2,
        keyword=0.3,
        rating_out_of_5=4.0,
        price=300.0,
        min_price=100.0,
        max_price=500.0,
    )
    assert score_a > score_b
    assert (score_a - score_b) == pytest.approx(0.50 * (0.9 - 0.2))
