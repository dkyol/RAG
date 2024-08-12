from typing import List, Dict, Any, Optional
from pydantic import BaseModel

DEFAULT_K = 10


class KeywordSearchRequest(BaseModel):
    value: str
    field: Optional[str] = None
    asset_types: Optional[List[str]] = None
    search_type: Optional[str] = None
    k: Optional[int] = DEFAULT_K


keyword_search_examples = {
    "example1": {
        "summary": "Simple default keyword search.",
        "description": "Look for keywords in the 'text' field of the database items. "
        "By default, this endpoint uses 'search_type': 'union' mode, which searches for items that "
        "contain the union of the keywords found in 'value' regardless of the order of "
        "the words in 'value'",
        "value": {
            "value": "recommender systems",
        },
    },
    "example2": {
        "summary": "Simple default keyword search, specifying which asset type.",
        "description": "Simple default keyword search, specifying which asset type.",
        "value": {
            "value": "recommender systems",
            "asset_types": ["techblogs"],
        },
    },
    "example3": {
        "summary": "Exact match keyword search.",
        "description": "We can look for an exact phrase found in the text. In this case, "
        "the order of the words is preserved.",
        "value": {
            "value": "recommender systems",
            "asset_types": ["techblogs"],
            "search_type": "exact",
        },
    },
    "example4": {
        "summary": "Exact match search for a categorical field.",
        "description": "We can look for an exact match for a categorical field (a.k.a. TAG field in redis) "
        "such as 'document_url'.",
        "value": {
            "value": "https://developer.nvidia.com/blog/improving-cuda-initialization-times-using-cgroups-in-certain-scenarios/",
            "field": "document_url",
            "asset_types": ["techblogs"],
            "search_type": "exact",
            "k": 1000,
        },
    },
    "example5": {
        "summary": "Fuzzy match keyword search.",
        "description": "We can look for a close match on a particular field using fuzzy matching with Levenshtein distance. "
        "In this case, order does not matter.",
        "value": {
            "value": "Improving CUDA Initialisation Times Using cgroups in Certain Scenarios",
            "field": "document_title",
            "asset_types": ["techblogs"],
            "search_type": "fuzzy",
        },
    },
    "example6": {
        "summary": "Wildcard match keyword search.",
        "description": "Allows you to use wildcard asterisk symbol * within 'value'.",
        "value": {
            "value": "Improving CUDA Initialization Times*",
            "field": "document_title",
            "asset_types": ["techblogs"],
            "search_type": "wildcard",
        },
    },
}
