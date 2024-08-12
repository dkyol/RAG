from typing import List, Dict, Any, Optional
from pydantic import BaseModel

DEFAULT_K = 10


class SemanticSearchRequest(BaseModel):
    query: str
    asset_types: Optional[List[str]] = None
    k: Optional[int] = DEFAULT_K


semantic_search_examples = {
    "example1": {
        "summary": "Simplest semantic search.",
        "description": "We must provide a query to search for. If asset_types is missing, results for all asset_types are returned."
        "If k is missing, it uses default value.",
        "value": {
            "query": "recommender systems",
        },
    },
    "example2": {
        "summary": "Semantic search. Set k and asset_types to non-default values.",
        "description": "We can limit to k results by including parameter k. We can also "
        "choose which asset_types to search by passing in the list asset_types.",
        "value": {
            "query": "recommender systems",
            "k": 3,
            "asset_types": ["techblogs"],
        },
    },
}
