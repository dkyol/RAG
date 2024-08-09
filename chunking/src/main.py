from fastapi import FastAPI, Body, Query, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from strategies import (
    sentence,
    paragraph,
    heading_section,
    heading_section_sentence,
    heading_section_paragraph,
)

import docs

import spacy

nlp = spacy.load("en_core_web_sm")


# Instantiate FastAPI with some info needed for docs
app = FastAPI(
    title="NVIDIA DLI Chunking API",
    description=docs.description,
    openapi_tags=docs.tags_metadata,
)
docs.clear_openapi_responses(app)

# Enables CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
async def health_endpoint() -> JSONResponse:
    return JSONResponse(status_code=200, content={"success": True})


@app.post("/api/chunking", tags=["chunking"])
async def chunking_endpoint(
    params: docs.ChunkingRequest = Body(openapi_examples=docs.chunking_examples),
):
    strategy = params.strategy.lower()
    input_type = params.input_type.lower()

    if strategy == "sentence":
        if input_type == "text":
            chunks = sentence.chunk_text(
                text=params.input_str,
                chunk_min_words=params.chunk_min_words,
                chunk_overlap_words=params.chunk_overlap_words,
                code_behavior=params.code_behavior,
                nlp=nlp,
                paragraph_delimeter=params.paragraph_delimeter,
                additional_metadata=params.additional_metadata,
            )
        elif input_type == "html":
            chunks = sentence.chunk_html(
                html_str=params.input_str,
                chunk_min_words=params.chunk_min_words,
                chunk_overlap_words=params.chunk_overlap_words,
                code_behavior=params.code_behavior,
                nlp=nlp,
                additional_metadata=params.additional_metadata,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"input_type '{params.input_type}' not supported with chunking strategy '{params.strategy}'. Please use one of 'text' or 'html'.",
            )
    elif strategy == "paragraph":
        if input_type == "text":
            chunks = paragraph.chunk_text(
                text=params.input_str,
                chunk_min_words=params.chunk_min_words,
                chunk_overlap_words=params.chunk_overlap_words,
                code_behavior=params.code_behavior,
                nlp=nlp,
                paragraph_delimeter=params.paragraph_delimeter,
                additional_metadata=params.additional_metadata,
            )
        elif input_type == "html":
            chunks = paragraph.chunk_html(
                html_str=params.input_str,
                chunk_min_words=params.chunk_min_words,
                chunk_overlap_words=params.chunk_overlap_words,
                code_behavior=params.code_behavior,
                nlp=nlp,
                additional_metadata=params.additional_metadata,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"input_type '{params.input_type}' not supported with chunking strategy '{params.strategy}'. Please use one of 'text' or 'html'.",
            )
    elif strategy == "heading_section":
        if input_type == "html":
            chunks = heading_section.chunk_html(
                html_str=params.input_str,
                code_behavior=params.code_behavior,
                nlp=nlp,
                additional_metadata=params.additional_metadata,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"input_type '{params.input_type}' not supported with chunking strategy '{params.strategy}'. Please use 'html'.",
            )
    elif strategy == "heading_section_sentence":
        if input_type == "html":
            chunks = heading_section_sentence.chunk_html(
                html_str=params.input_str,
                chunk_min_words=params.chunk_min_words,
                chunk_overlap_words=params.chunk_overlap_words,
                code_behavior=params.code_behavior,
                nlp=nlp,
                additional_metadata=params.additional_metadata,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"input_type '{params.input_type}' not supported with chunking strategy '{params.strategy}'. Please use 'html'.",
            )
    elif strategy == "heading_section_paragraph":
        if input_type == "html":
            chunks = heading_section_paragraph.chunk_html(
                html_str=params.input_str,
                chunk_min_words=params.chunk_min_words,
                chunk_overlap_words=params.chunk_overlap_words,
                code_behavior=params.code_behavior,
                nlp=nlp,
                additional_metadata=params.additional_metadata,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"input_type '{params.input_type}' not supported with chunking strategy '{params.strategy}'. Please use 'html'.",
            )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Chunking strategy '{params.strategy}' is currently unsupported. Please use one of 'sentence', 'paragraph', 'heading_section', 'heading_section_sentence', or 'heading_section_paragraph'.",
        )
    return chunks


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")
