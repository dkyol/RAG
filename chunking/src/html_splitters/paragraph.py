import spacy
from typing import Optional, List, Dict, Tuple, Any
from text_splitters.paragraph import extract_paragraphs as text_extract_paragraphs
from html_splitters.html_utils import (
    html_str_to_soup,
    clean_html,
    soup_to_str_list,
    clean_concat_str_list,
)


def extract_paragraphs(
    html_str: str,
    nlp: Optional[spacy.language.Language] = None,
    paragraph_delimeter: Optional[str] = None,
    word_count: bool = True,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Extract a list of paragraphs as strings, given an HTML string.
    Uses newline characters as paragraph_delimter by default.
    Also returns a dictionary of metadata about each paragraph.

    Args:
        text (str): block of text
        nlp (Optional[spacy.language.Language], optional): spacy nlp model. Defaults to None.
        paragraph_delimeter (Optional[str], optional): Delimeter to separate paragraphs. If None, defaults to "\n".
        word_count (bool, optional): Whether to count words and return in metadata. Defaults to True.
        additional_metadata (Optional[Dict[str, Any]], optional): Dict of any additional metadata that is associated with all paragraphs.

    Returns:
        Tuple[List[str], List[Dict[str, Any]]]: Tuple of two lists: paragraphs and metadata
    """
    html_soup = html_str_to_soup(html_str)
    html_soup = clean_html(html_soup)
    strs = soup_to_str_list(html_soup)
    text = clean_concat_str_list(strs)

    return text_extract_paragraphs(
        text=text,
        nlp=nlp,
        paragraph_delimeter=paragraph_delimeter,
        word_count=word_count,
        additional_metadata=additional_metadata,
    )
