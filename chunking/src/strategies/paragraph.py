import spacy
from typing import Optional, List, Dict, Any
from text_splitters.paragraph import extract_paragraphs as text_extract_paragraphs
from html_splitters.paragraph import extract_paragraphs as html_extract_paragraphs
from strategies.chunking_utils import chunk_by_word_count


def chunk_text(
    text: str,
    chunk_min_words: int = 0,
    chunk_overlap_words: int = 0,
    code_behavior: str = None,
    nlp: Optional[spacy.language.Language] = None,
    paragraph_delimeter: Optional[str] = None,
    word_count: bool = True,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    paragraphs, paragraphs_metadata = text_extract_paragraphs(
        text=text,
        nlp=nlp,
        paragraph_delimeter=paragraph_delimeter,
        word_count=word_count,
        additional_metadata=additional_metadata,
    )

    return chunk_by_word_count(
        paragraphs,
        paragraphs_metadata,
        chunk_min_words,
        chunk_overlap_words,
        code_behavior,
        additional_metadata,
    )


def chunk_html(
    html_str: str,
    chunk_min_words: int = 0,
    chunk_overlap_words: int = 0,
    code_behavior: str = None,
    nlp: Optional[spacy.language.Language] = None,
    paragraph_delimeter: Optional[str] = None,
    word_count: bool = True,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    paragraphs, paragraphs_metadata = html_extract_paragraphs(
        html_str=html_str,
        nlp=nlp,
        paragraph_delimeter=paragraph_delimeter,
        word_count=word_count,
        additional_metadata=additional_metadata,
    )

    return chunk_by_word_count(
        paragraphs,
        paragraphs_metadata,
        chunk_min_words,
        chunk_overlap_words,
        code_behavior,
        additional_metadata,
    )
