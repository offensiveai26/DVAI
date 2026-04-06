"""
Challenge: Retrieval Hijacking
Craft queries that retrieve documents from a restricted collection.
"""

from app.flags import get_flag

FLAG = get_flag("rag-retrieval-hijack")

PUBLIC_DOCS = [
    {"id": "pub1", "content": "DVAI supports 8 categories of AI security challenges.", "tags": ["public"]},
    {"id": "pub2", "content": "Prompt injection is the most common LLM vulnerability.", "tags": ["public"]},
    {"id": "pub3", "content": "RAG systems combine retrieval with generation.", "tags": ["public"]},
]

RESTRICTED_DOCS = [
    {"id": "sec1", "content": f"RESTRICTED: Admin credentials and flag: {FLAG}", "tags": ["restricted"]},
    {"id": "sec2", "content": "RESTRICTED: Internal API keys for production services.", "tags": ["restricted"]},
]

ALL_DOCS = PUBLIC_DOCS + RESTRICTED_DOCS


def retrieve(query: str, difficulty: int) -> list[dict]:
    """Retrieve documents - difficulty controls access filtering."""
    query_words = set(query.lower().split())
    scored = []
    for doc in ALL_DOCS:
        doc_words = set(doc["content"].lower().split())
        score = len(query_words & doc_words)
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)

    if difficulty == 1:
        # No filtering - returns everything
        return [d for _, d in scored if _ > 0][:3]
    elif difficulty == 2:
        # Filter by tag AFTER retrieval (can be bypassed by keyword matching)
        results = [d for _, d in scored if _ > 0][:3]
        return [d for d in results if "restricted" not in d.get("tags", [])]
    else:
        # Filter BEFORE retrieval
        public_only = [d for d in ALL_DOCS if "restricted" not in d.get("tags", [])]
        scored = []
        for doc in public_only:
            doc_words = set(doc["content"].lower().split())
            score = len(query_words & doc_words)
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored if _ > 0][:3]


async def handle(user_input: str, difficulty: int = 1) -> dict:
    cmd = user_input.strip()

    if cmd.lower() == "help":
        return {
            "response": (
                "Retrieval Service v1.0\n"
                "──────────────────────\n"
                "Type a query to search the document store.\n"
                "Some documents are restricted - can you access them?\n\n"
                "Commands:\n"
                "  <query>  - Search documents\n"
                "  help     - Show this message"
            ),
            "flag_found": False,
        }

    results = retrieve(cmd, difficulty)
    flag_found = any(FLAG in d["content"] for d in results)

    return {
        "response": "Search results:",
        "results": [{"id": d["id"], "content": d["content"], "tags": d["tags"]} for d in results],
        "flag_found": flag_found,
        "flag": FLAG if flag_found else None,
    }
