"""Optional OpenSearch threat-intelligence lookup."""

import os
from typing import Any, Dict, List


def lookup_threats(text: str) -> List[Dict[str, Any]]:
    endpoint = os.getenv("OPENSEARCH_ENDPOINT", "").strip()
    index = os.getenv("OPENSEARCH_INDEX", "trustlens-threats").strip()
    if not endpoint:
        return []

    try:
        from opensearchpy import OpenSearch

        client = OpenSearch(hosts=[endpoint], use_ssl=True, verify_certs=True)
        response = client.search(index=index, body={
            "size": 5,
            "query": {"match": {"content": text[:2000]}},
        })
        return [hit.get("_source", {}) for hit in response.get("hits", {}).get("hits", [])]
    except Exception:
        return []
