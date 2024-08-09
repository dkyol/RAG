from typing import Optional, Tuple, List, Dict, Any
import spacy
from text_splitters.sentence import extract_sentences as text_extract_sentences
from html_splitters.paragraph import extract_paragraphs


def extract_sentences(
    html_str: str,
    nlp: Optional[spacy.language.Language] = None,
    paragraph_delimeter: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    # first split into paragraphs
    # don't need to word_count because we will do that at sentence-level later
    paragraphs, paragraphs_metadata = extract_paragraphs(
        html_str=html_str,
        nlp=nlp,
        paragraph_delimeter=paragraph_delimeter,
        word_count=False,
    )

    return text_extract_sentences(
        text=paragraphs,
        nlp=nlp,
        paragraph_delimeter=paragraph_delimeter,
        paragraphs_metadata=paragraphs_metadata,
        additional_metadata=additional_metadata,
    )
