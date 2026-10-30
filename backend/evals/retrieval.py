"""Ranking metrics are independent from answer quality and evidence sufficiency."""


def metrics(ranked_documents, relevant):
    relevant = set(relevant)
    if not relevant:
        return {"unanswerable": True, "retrieved_documents": len(set(ranked_documents))}
    result = {
        f"recall@{k}": len(set(ranked_documents[:k]) & relevant) / len(relevant)
        for k in (3, 5, 8)
    }
    result["mrr"] = next(
        (1 / i for i, key in enumerate(ranked_documents, 1) if key in relevant), 0
    )
    return result
