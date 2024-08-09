import spacy
from typing import Union, Optional, List, Dict, Tuple, Any
from text_splitters.paragraph import extract_paragraphs
from text_splitters.text_utils import count_words, count_words_code, detect_code


def extract_sentences(
    text: Union[str, List[str]],
    nlp: Optional[spacy.language.Language] = None,
    paragraph_delimeter: Optional[str] = None,
    paragraphs_metadata: Optional[List[Dict[str, Any]]] = None,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Extract a list of sentences as strings, given either
    a block of text or a list of strings assumed to be paragraphs.
    Uses newline characters as paragraph_delimter by default.
    Also returns a dictionary of metadata about each paragraph.

    Args:
        text (Union[str, List[str]]): either a block of text or a list of strings already separated into paragraphs.
        nlp (Optional[spacy.language.Language], optional): spacy nlp model. Defaults to None.
        paragraph_delimeter (Optional[str], optional): Delimeter to separate paragraphs. If None, defaults to "\n".
        paragraphs_metadata (Optional[List[Dict[str, Any]]], optional): list of dicts with metadata concerning each paragraph.
            Only used when text is a list of strings already separated into paragraphs.
        additional_metadata (Optional[Dict[str, Any]], optional): Dict of any additional metadata that is associated with all sentences.

    Returns:
        Tuple[List[str], List[Dict[str, Any]]]: Tuple of two lists: sentences and metadata
    """
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")

    # first check if we need to split text into paragraphs on paragraph_delimeter
    # if input `text` is a single str, we assume it needs to be split
    if isinstance(text, str):
        # first split into paragraphs
        # don't need to word_count because we will do that at sentence-level later
        # this will overwrite whatever was passed into the function argument paragraphs_metadata
        paragraphs, paragraphs_metadata = extract_paragraphs(
            text=text,
            nlp=nlp,
            paragraph_delimeter=paragraph_delimeter,
            word_count=False,
        )
    # otherwise we assume each string in the list is a paragraph
    else:  # text is List[str]
        paragraphs = text
        if paragraphs_metadata is None:
            paragraphs_metadata = []
            for paragraph in paragraphs:
                contains_code, only_code = detect_code(paragraph)
                paragraphs_metadata.append(
                    {
                        "contains_code": contains_code,
                        "only_code": only_code,
                    }
                )
        assert len(paragraphs) == len(paragraphs_metadata)

    indiv_level_metadata_keys = {
        k
        for k in paragraphs_metadata[0].keys()
        if additional_metadata is None or k not in additional_metadata
    }

    all_sentences = []
    all_metadata = []
    for paragraph_index, paragraph in enumerate(paragraphs):
        sentences = []
        sentences_metadata = []

        contains_code = paragraphs_metadata[paragraph_index]["contains_code"]
        only_code = paragraphs_metadata[paragraph_index]["only_code"]
        if only_code:
            # split on newlines
            # TODO: should code "sentence" delimiter be parameter?
            paragraph_sentences = paragraph.split("\n")
            for sentence in paragraph_sentences:
                if sentence.strip() != "":
                    sentence_metadata = {
                        k: paragraphs_metadata[paragraph_index][k]
                        for k in indiv_level_metadata_keys
                    }
                    sentence_metadata.update({
                        "paragraph_index": paragraph_index,
                        "paragraph_sentence_index": len(sentences),
                        "contains_code": contains_code,
                        "only_code": only_code,
                        "word_count": count_words_code(sentence),
                    })
                    sentences_metadata.append(sentence_metadata)
                    sentences.append(sentence)

        else:  # this is text (and maybe some code). We expect that to be inline code, though.
            # Use Spacy to split the text into sentences
            doc = nlp(paragraph)

            for sentence in doc.sents:
                sentence_text = sentence.text.strip()
                if sentence_text != "":
                    sentence_metadata = {
                        k: paragraphs_metadata[paragraph_index][k]
                        for k in indiv_level_metadata_keys
                    }
                    sentence_metadata.update(
                        {
                            "paragraph_index": paragraph_index,
                            "paragraph_sentence_index": len(sentences),
                            "contains_code": contains_code,
                            "only_code": only_code,
                            "word_count": count_words(sentence),
                        }
                    )
                    sentences_metadata.append(sentence_metadata)
                    sentences.append(sentence_text)

        all_sentences.extend(sentences)
        all_metadata.extend(sentences_metadata)

    if additional_metadata is not None:
        for m in all_metadata:
            m.update(additional_metadata)

    return all_sentences, all_metadata
