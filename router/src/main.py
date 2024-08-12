from fastapi import FastAPI, Body, Query, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.vectorstores.redis import Redis
from redisvl.query.filter import Text, Tag
from redis.commands.search.query import Query
from redisvl.index import SearchIndex
from typing import List, Dict, Any
from datetime import datetime
from embeddings import TritonHFEmbeddings
from docs.common import (
    doc_description,
    tags_metadata,
    clear_openapi_responses,
)
from docs.search.semantic import (
    SemanticSearchRequest,
    semantic_search_examples,
)
from docs.search.semantic import DEFAULT_K as SEMANTIC_SEARCH_DEFAULT_K
from docs.search.keyword import (
    KeywordSearchRequest,
    keyword_search_examples,
)
from docs.search.keyword import DEFAULT_K as KEYWORD_SEARCH_DEFAULT_K
from docs.data.insert import InsertDataRequest, insert_data_examples
from docs.data.delete import DeleteDataRequest, delete_data_examples
from docs.assettypes.update import UpdateAssetTypesRequest, update_asset_types_examples
from assettypes import ASSET_TYPES
import schema
import json
import os


REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
TRITON_HOST = os.environ["TRITON_HOST"]


REDIS_STOP_WORDS = {
    "a",
    "is",
    "the",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "if",
    "in",
    "into",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "such",
    "that",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "to",
    "was",
    "will",
    "with",
}


# Instantiate FastAPI with some info needed for docs
app = FastAPI(
    title="NVIDIA DLI Router API",
    description=doc_description,
    openapi_tags=tags_metadata,
)
clear_openapi_responses(app)

# Enables CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Now create a SearchIndex that just has info about the
# asset_types being stored. Each asset_type itself will become
# its own index, but this index has metadata about the other indexes.
asset_types_index = SearchIndex.from_dict(
    {
        "index": {
            "name": "assettypes",
            "prefix": "doc:assettypes",
            "storage_type": "hash",
            "key_separator": ":",
        },
        "fields": {
            "tag": [
                {"name": "name"},
                {"name": "display_title"},
            ],
            "text": [
                {"name": "last_indexed"},
                {"name": "chunking_params"},
            ],
        },
    }
)
asset_types_index.connect(REDIS_URL)
asset_types_index.create(overwrite=False)
asset_types_index.load(
    [v for k, v in ASSET_TYPES.items()],
    key_field="name",
)


def _convert_data_structs_to_str(chunk):
    # convert non-strings and non-numeric values to JSON-compatible strings
    # because redis vectordb implementation only supports numberics and strings
    for k, v in chunk.items():
        if (
            not isinstance(v, str)
            and not isinstance(v, int)
            and not isinstance(v, float)
        ):
            chunk[k] = json.dumps(v)
    return chunk


def _redis_results_as_dicts(results) -> List[Dict[str, Any]]:
    results_as_dicts = []

    for result in results.docs:
        res = {
            k: v
            for k, v in result.__dict__.items()
            if k not in ["payload", "content", "content_vector"]
        }
        results_as_dicts.append(res)

    return results_as_dicts


def _instantiate_vectorstore(asset_type: str) -> Redis:
    embedder = TritonHFEmbeddings(triton_host=TRITON_HOST)

    metadata = dict(schema.metadata)

    text = "passage: " + metadata["text"]

    metadata = _convert_data_structs_to_str(metadata)

    try:  # try to restore from an existing index
        rds = Redis.from_existing_index(
            embedder,
            index_name=asset_type,
            redis_url=REDIS_URL,
            schema=schema.index_schema,
        )
        print(f"Restored from existing redis index {asset_type}")
    except:
        # create the index with some dummy data
        rds, keys = Redis.from_texts_return_keys(
            texts=[text],
            embedding=embedder,
            metadatas=[metadata],
            redis_url=REDIS_URL,
            index_name=asset_type,
            index_schema=schema.index_schema,  # need this to tell what is a tag
        )

        # delete dummy data
        Redis.delete(keys, redis_url=REDIS_URL)

        print(f"Created new redis index {asset_type}")

    return rds


# Create vectorstores
vectorstores = {}
for asset_type in ASSET_TYPES.keys():
    vectorstores[asset_type] = _instantiate_vectorstore(asset_type)


def _get_vectorstore(asset_type: str) -> Redis:
    if asset_type not in ASSET_TYPES:
        raise ValueError(f"asset_type {asset_type} is not valid")
    rds = vectorstores[asset_type]
    return rds


@app.get("/health", tags=["health"])
async def health_endpoint() -> JSONResponse:
    return JSONResponse(status_code=200, content={"success": True})


def _ends_with_eos_punctuation(text: str):
    return text.endswith(".") or text.endswith("!") or text.endswith("?")


@app.post("/search/semantic", tags=["search"])
async def semantic_search_endpoint(
    params: SemanticSearchRequest = Body(openapi_examples=semantic_search_examples),
) -> List[Dict[str, Any]]:
    """Semantic search

    Args:
        params (SemanticSearchRequest, optional): _description_. Defaults to Body(openapi_examples=semantic_search_examples).

    Raises:
        ValueError: if invalid "asset_types" passed in body

    Returns:
        List[Dict[str, Any]]: list of dicts. Each dict corresponds to an asset_type.
    """

    # add necessary prefix for e5-large-unsupervised embedder
    query = "query: " + params.query.strip()

    # number of top k results to return
    k = params.k
    if not k:
        k = SEMANTIC_SEARCH_DEFAULT_K
    else:
        k = int(k)

    # which asset_types we are searching for
    asset_types = params.asset_types
    if not asset_types:
        asset_types = list(sorted(ASSET_TYPES.keys()))

    print(f"Semantic search for query '{params.query}' in asset_types {asset_types}")

    output = []

    #TODO: change rds.similarity_search_with_relevance_scores
    # so that we don't re-embed query over and over...
    # this adds latency. 
    # we should first embed the query independently, and then...
    # this means subclassing langchain Redis vectorstore
    # so that we have similarity_search_by_vector but with returning scores 
    for asset_type in asset_types:
        rds: Redis = _get_vectorstore(asset_type)

        display_title = ASSET_TYPES[asset_type]["display_title"]

        docs_and_scores = rds.similarity_search_with_relevance_scores(query, k=k)

        asset_type_results = []

        for doc, similarity_score in docs_and_scores:
            # print(
            #     f"Content: {doc.page_content} --- Similiarity: {similarity_score} --- Metadata: {doc.metadata}"
            # )
            # merge metadata dictionary with new dictionary containing similarity_score
            asset_type_results.append({**doc.metadata, **{"score": similarity_score}})

        output.append(
            {
                "asset_type": asset_type,
                "display_title": display_title,
                "results": asset_type_results,
            }
        )

    return output


def _keyword_search(index: SearchIndex, query_string: str, k: int):
    """Searches the index for the query_string using BM25 as scorer. Includes scores

    Args:
        index (SearchIndex): _description_
        query_string (str): _description_
        k (int): Max number of results to return

    Returns:
        _type_: _description_
    """
    results = index.search(
        Query(query_string).with_scores().scorer("BM25").paging(offset=0, num=k)
    )
    return _redis_results_as_dicts(results)


def _keyword_search_union(
    index: SearchIndex, field: str, value: str, k: int
) -> List[Dict[str, Any]]:
    """Used when you want to search TEXT fields that contain a union of multiple
    keywords. Order of keywords does not matter.

    Args:
        index (SearchIndex): _description_
        field (str): _description_
        value (str): String with each keyword separated by a space from the next.
        k (int): Max number of results to return

    Returns:
        _type_: _description_
    """
    return _keyword_search(index, f"@{field}:({value})", k)


def _keyword_search_exact(index: SearchIndex, field: str, value: str, k: int):
    """Used when you want to search for an exact match on a TAG field, or for
    an exact match on a subphrase of a TEXT field.

    Args:
        index (SearchIndex): _description_
        field (str): _description_
        value (str): _description_
        k (int): Max number of results to return

    Returns:
        _type_: _description_
    """
    # if it's a tag field, we use tag syntax: "@field:{value}""
    if field in schema.tag_fields:
        filter_expression = Tag(field) == value
    # otherwise using text syntax: "@field:\"value\""
    else:
        filter_expression = Text(field) == value

    filter_expression = str(filter_expression)
    return _keyword_search(index, filter_expression, k)


def _keyword_search_fuzzy(index: SearchIndex, field: str, value: str, k: int):
    """For Levenshtein fuzzy match for a TEXT field.

    Args:
        index (SearchIndex): _description_
        field (str): _description_
        value (str): _description_
        k (int): Max number of results to return

    Returns:
        _type_: _description_
    """
    # TODO: can make it configurable how much Levenshtein distance to allow
    # For example, one % is used for stricter matches, and three %%% for looser matches
    keywords = [f"%%{x}%%" for x in value.split() if x not in REDIS_STOP_WORDS]
    fuzzy_match = Text(field) % "".join(keywords)
    filter_expression = str(fuzzy_match)
    return _keyword_search(index, filter_expression, k)


def _keyword_search_wildcard(index: SearchIndex, field: str, value: str, k: int):
    """Allows using * as wildcard symbol

    Args:
        index (SearchIndex): _description_
        field (str): _description_
        value (str): Should contain "*"
        k (int): Max number of results to return

    Returns:
        _type_: _description_
    """
    assert "*" in value

    wildcard_match = Text(field) % value
    filter_expression = str(wildcard_match)
    return _keyword_search(index, filter_expression, k)


@app.post("/search/keyword", tags=["search"])
async def keyword_search_endpoint(
    params: KeywordSearchRequest = Body(openapi_examples=keyword_search_examples),
) -> List[Dict[str, Any]]:
    ### START JSON BODY PARAMATERS ###

    # name of field we are looking for
    # this could be "text" (which it is by default if field is not supplied)
    field = params.field
    if not field:
        field = "content"

    # value to match on
    value = params.value

    # number of top k results to return
    k = params.k
    if not k:
        k = KEYWORD_SEARCH_DEFAULT_K
    else:
        k = int(k)

    # which asset_types we are searching for
    asset_types = params.asset_types
    if not asset_types:
        asset_types = list(sorted(ASSET_TYPES.keys()))

    # check what type of search we're doing
    # possible values are "union", "exact", "fuzzy", "wildcard"
    search_type = params.search_type
    if not search_type:
        search_type = "union"
    search_type = search_type.lower().strip()

    if search_type not in ["union", "exact", "fuzzy", "wildcard"]:
        raise ValueError(f"search_type parameter has invalid value: {search_type}")

    ### END JSON BODY PARAMATERS ###

    print(
        f"Keyword search for value '{value}' in field '{field}' with search_type '{search_type}' in asset_types {asset_types}"
    )

    output = []

    for asset_type in asset_types:
        display_title = ASSET_TYPES[asset_type]["display_title"]

        # index = SearchIndex.from_existing(name=asset_type, redis_url=REDIS_URL)
        schema_dict = {
            "index": {
                "name": asset_type,
                "prefix": f"doc:{asset_type}",
                "storage_type": "hash",
                "key_separator": ":",
            },
            "fields": schema.index_schema,
        }
        index = SearchIndex.from_dict(
            schema_dict=schema_dict, 
            redis_url=REDIS_URL
        )

        if search_type == "union":
            asset_type_results = _keyword_search_union(index, field, value, k)
        elif search_type == "exact":
            asset_type_results = _keyword_search_exact(index, field, value, k)
        elif search_type == "fuzzy":
            asset_type_results = _keyword_search_fuzzy(index, field, value, k)
        elif search_type == "wildcard":
            asset_type_results = _keyword_search_wildcard(index, field, value, k)

        # print(asset_type_results)

        output.append(
            {
                "asset_type": asset_type,
                "display_title": display_title,
                "results": asset_type_results,
            }
        )

    return output


@app.post("/data/insert", tags=["data"])
async def insert_data_endpoint(
    params: InsertDataRequest = Body(openapi_examples=insert_data_examples),
) -> List[str]:
    """Insert new chunks as vectors in the redis db, along with the metadata

    Args:
        params (InsertDataRequest, optional): _description_. Defaults to Body(openapi_examples=insert_data_examples).

    Returns:
        List[str]: Chunks formatted for the embedder.
    """
    chunks: List[Dict[str, Any]] = params.chunks

    asset_type: str = params.asset_type

    rds: Redis = _get_vectorstore(asset_type)

    text_inputs = []
    chunk_inputs = []
    for chunk in chunks:
        if not chunk.get("text"):
            print("Warning: chunk is missing text")
            continue

        # must have prefix for e5 embedder
        new_text = "passage: "

        # document_title
        if chunk.get("document_title") is not None:
            document_title = chunk["document_title"].strip()
            if not chunk["text"].startswith(document_title):
                if not _ends_with_eos_punctuation(document_title):
                    new_text += document_title + ". "
                else:
                    new_text += document_title + " "
        
        new_text += chunk["text"].strip()

        text_inputs.append(new_text)

        chunk["last_indexed"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

        chunk_inputs.append(_convert_data_structs_to_str(chunk))

        # print(f"Added text chunk: {new_text}")

    if len(text_inputs) > 0:
        # embed all chunks at once
        # if we do not create embeddings here first, then
        # they are created in rds.add_texts, but sequentially looping through
        # each chunk and making a separate triton request which is slow
        embedder = TritonHFEmbeddings(triton_host=TRITON_HOST)
        embeddings = []
        # 16 is max batch size triton accepts based on our config
        for i in range(0, len(text_inputs), 16):
            embeddings.extend(embedder.embed_documents(text_inputs[i : i + 16]))

        # first param is texts to embed into a vector
        # second param is metadata to be saved alongside the vector
        # third param is embeddings
        rds.add_texts(texts=text_inputs, metadatas=chunk_inputs, embeddings=embeddings)

    return text_inputs


@app.post("/data/delete", tags=["data"])
async def delete_data_endpoint(
    params: DeleteDataRequest = Body(openapi_examples=delete_data_examples),
) -> Dict[str, int]:
    ids: List[str] = params.ids
    asset_type: str = params.asset_type

    # index = SearchIndex.from_existing(name=asset_type, redis_url=REDIS_URL)
    schema_dict = {
        "index": {
            "name": asset_type,
            "prefix": f"doc:{asset_type}",
            "storage_type": "hash",
            "key_separator": ":",
        },
        "fields": schema.index_schema,
    }
    index = SearchIndex.from_dict(
        schema_dict=schema_dict, 
        redis_url=REDIS_URL
    )

    print(f"Deleting items with ids: {ids}")

    items_deleted: int = index.client.delete(*ids)

    print(f"Number of items deleted: {items_deleted}")

    return {"items_deleted": items_deleted}


@app.post("/data/dump", tags=["data"])
async def dump_data_endpoint() -> JSONResponse:
    r = asset_types_index.client
    success = r.bgsave()
    if success:
        return JSONResponse(status_code=200, content={"success": True})
    return JSONResponse(status_code=500, content={"success": False})


@app.get("/asset-types", tags=["asset-types"])
async def asset_types_endpoint() -> List[Dict[str, Any]]:
    results = asset_types_index.search("*")

    dicts = _redis_results_as_dicts(results)
    for d in dicts:
        # bool field
        if "display_default" in d:
            d["display_default"] = bool(d["display_default"])

        # int fields
        if "display_sort_order" not in d:
            d["display_sort_order"] = 1000000
        for int_field_name in [
            "display_sort_order",
            "group_sort_order",
        ]:
            d[int_field_name] = int(d[int_field_name])

    # sort by two int keys using a tuple, with ascending order
    dicts = sorted(
        dicts,
        key=lambda x: (x["group_sort_order"], x["display_sort_order"]),
        reverse=False,
    )

    return dicts


@app.post("/asset-types/update", tags=["asset-types"])
async def update_asset_types_endpoint(
    params: UpdateAssetTypesRequest = Body(
        openapi_examples=update_asset_types_examples
    ),
) -> Dict[str, Any]:
    updated_data = params.data

    if "id" in updated_data:
        updated_data.pop("id")

    # add last_indexed date
    updated_data["last_indexed"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    # bool field
    if "display_default" in updated_data:
        updated_data["display_default"] = int(updated_data["display_default"])

    asset_types_index.load([updated_data], key_field="name")
    return updated_data


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")
