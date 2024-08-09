import spacy
from typing import Optional, List, Dict, Any
from html_splitters.heading_section import extract_heading_section_paragraphs
from strategies.chunking_utils import chunk_by_word_count


def chunk_html(
    html_str: str,
    chunk_min_words: int = 0,
    chunk_overlap_words: int = 0,
    code_behavior: str = None,
    nlp: Optional[spacy.language.Language] = None,
    word_count: bool = True,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    paragraphs, paragraphs_metadata = extract_heading_section_paragraphs(
        html_str=html_str,
        nlp=nlp,
        word_count=word_count,
        additional_metadata=additional_metadata,
    )

    # we just want to chunk by paragraph but preserve the heading information
    chunks = chunk_by_word_count(
        paragraphs,
        paragraphs_metadata,
        chunk_min_words,
        chunk_overlap_words,
        code_behavior,
        additional_metadata,
    )

    return chunks
