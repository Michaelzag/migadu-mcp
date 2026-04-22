"""Tests for the static response summarizer."""

from __future__ import annotations

from migadu_mcp.utils.summarize import estimate_tokens, summarize


def test_small_response_passes_through() -> None:
    data = {"mailboxes": [{"address": "a@x.com"}]}
    assert summarize(data, max_tokens=1000) == data


def test_large_list_response_is_truncated() -> None:
    mailboxes = [{"address": f"user{i}@x.com", "name": f"User {i}"} for i in range(200)]
    data = {"mailboxes": mailboxes}
    result = summarize(data, max_tokens=100, sample_size=3)
    assert "mailboxes_summary" in result
    assert result["mailboxes_summary"]["total_count"] == 200
    assert result["mailboxes_summary"]["truncated"] is True
    assert len(result["sample"]) == 3


def test_generic_dict_over_budget_gets_generic_summary() -> None:
    data = {"random_key": "x" * 100000}  # not a known list key
    result = summarize(data, max_tokens=100)
    assert "response_summary" in result
    assert result["response_summary"]["truncated"] is True
    assert "random_key" in result["response_summary"]["keys"]


def test_sample_size_configurable() -> None:
    mailboxes = [{"address": f"u{i}@x.com"} for i in range(50)]
    result = summarize({"mailboxes": mailboxes}, max_tokens=10, sample_size=5)
    assert len(result["sample"]) == 5


def test_estimate_tokens_rough_heuristic() -> None:
    # 1 token ≈ 4 chars
    assert estimate_tokens("a") == 0
    assert estimate_tokens("abcd") >= 1
    assert estimate_tokens({"k": "v" * 400}) > 50
