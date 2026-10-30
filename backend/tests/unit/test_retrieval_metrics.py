from evals.retrieval import metrics


def test_ranked_recall_and_mrr_exclude_unanswerable_cases():
    result = metrics(["wrong", "good", "good", "also-good"], ["good", "also-good"])
    assert result["recall@3"] == 0.5 and result["recall@5"] == 1
    assert result["mrr"] == 0.5
    assert metrics(["wrong"], []) == {"unanswerable": True, "retrieved_documents": 1}
