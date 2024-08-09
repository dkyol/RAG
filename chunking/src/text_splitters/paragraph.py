import spacy
from typing import Optional, List, Dict, Tuple, Any
from text_splitters.text_utils import (
    count_words,
    count_words_code,
    replace_backticks_pattern,
    detect_code,
)


def extract_paragraphs(
    text: str,
    nlp: Optional[spacy.language.Language] = None,
    paragraph_delimeter: Optional[str] = None,
    word_count: bool = True,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Extract a list of paragraphs as strings, given a block of text.
    Uses newline characters as paragraph_delimter by default.
    Also returns a dictionary of metadata about each paragraph.
    Note that it will not split text on the paragraph_delimiter if
    it occurs within triple backticks, which is treated as code.
    TODO: make this backticks delimiter customizable

    Args:
        text (str): block of text
        nlp (Optional[spacy.language.Language], optional): spacy nlp model. Defaults to None.
        paragraph_delimeter (Optional[str], optional): Delimeter to separate paragraphs. If None, defaults to "\n".
        word_count (bool, optional): Whether to count words and return in metadata. Defaults to True.
        additional_metadata (Optional[Dict[str, Any]], optional): Dict of any additional metadata that is associated with all paragraphs.

    Returns:
        Tuple[List[str], List[Dict[str, Any]]]: Tuple of two lists: paragraphs and metadata
    """
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")

    if paragraph_delimeter is None:
        paragraph_delimeter = "\n"

    # Replace triple backticks with a placeholder to preserve them during splitting
    text, placeholder, backticks_matches = replace_backticks_pattern(text)

    # split on paragraph_delimiter and throw away empty strings
    paragraphs = [
        x for s in text.split(paragraph_delimeter) if (x := s.strip()) and x != ""
    ]

    # replace placeholder with matches
    match_idx = 0
    for i in range(len(paragraphs)):
        while True:
            if placeholder in paragraphs[i]:
                paragraphs[i] = paragraphs[i].replace(
                    placeholder, backticks_matches[match_idx], 1
                )
                match_idx += 1
            else:
                break
    assert len(backticks_matches) == match_idx

    all_metadata = []
    for paragraph_index, paragraph in enumerate(paragraphs):
        contains_code, only_code = detect_code(paragraph)

        # metadata about this paragraph
        metadata = {
            "paragraph_index": paragraph_index,
            "contains_code": contains_code,
            "only_code": only_code,
        }
        if word_count:
            if only_code:
                metadata.update({"word_count": count_words_code(paragraph)})
            else:
                doc = nlp(paragraph)
                metadata.update({"word_count": count_words(doc)})
        all_metadata.append(metadata)

    if additional_metadata is not None:
        for metadata in all_metadata:
            metadata.update(additional_metadata)

    return paragraphs, all_metadata
