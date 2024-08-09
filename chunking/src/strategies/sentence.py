import spacy
from typing import Optional, List, Dict, Any
from text_splitters.sentence import extract_sentences as text_extract_sentences
from html_splitters.sentence import extract_sentences as html_extract_sentences
from strategies.chunking_utils import chunk_by_word_count


def chunk_text(
    text: str,
    chunk_min_words: int = 0,
    chunk_overlap_words: int = 0,
    code_behavior: str = None,
    nlp: Optional[spacy.language.Language] = None,
    paragraph_delimeter: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    sentences, sentences_metadata = text_extract_sentences(
        text=text,
        nlp=nlp,
        paragraph_delimeter=paragraph_delimeter,
        additional_metadata=additional_metadata,
    )

    return chunk_by_word_count(
        sentences,
        sentences_metadata,
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
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    sentences, sentences_metadata = html_extract_sentences(
        html_str=html_str,
        nlp=nlp,
        paragraph_delimeter=paragraph_delimeter,
        additional_metadata=additional_metadata,
    )

    return chunk_by_word_count(
        sentences,
        sentences_metadata,
        chunk_min_words,
        chunk_overlap_words,
        code_behavior,
        additional_metadata,
    )
