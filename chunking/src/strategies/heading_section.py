import spacy
from typing import Optional, List, Dict, Any
from html_splitters.heading_section import (
    extract_heading_sections,
    extract_heading_section_paragraphs,
)
from strategies.chunking_utils import chunk_by_word_count


def chunk_html(
    html_str: str,
    code_behavior: str = None,
    nlp: Optional[spacy.language.Language] = None,
    word_count: bool = True,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    # default code_behavior should be ignore for this strategy
    if code_behavior is None:
        code_behavior = "ignore_code_boundaries"

    # first get paragraphs
    paragraphs, paragraphs_metadata = extract_heading_section_paragraphs(
        html_str=html_str,
        nlp=nlp,
        word_count=word_count,
        additional_metadata=additional_metadata,
    )

    # we can reuse our chunk_by_word_count function
    # but set chunk_min_words to a large number like 9_999_999
    # and chunk_overlap_words to 0
    chunks = []
    heading_section_paragraphs = []
    heading_section_metadata = []
    heading_section_index = None
    for paragraph, paragraph_metadata in zip(paragraphs, paragraphs_metadata):
        # if we reached a new heading section, save the chunks from the last section
        if (
            heading_section_index is not None
            and heading_section_index != paragraph_metadata["heading_section_index"]
        ):
            chunks.extend(
                chunk_by_word_count(
                    heading_section_paragraphs,
                    heading_section_metadata,
                    9_999_999,
                    0,
                    code_behavior,
                    additional_metadata,
                )
            )

            # reset these
            heading_section_paragraphs = []
            heading_section_metadata = []
        heading_section_paragraphs.append(paragraph)
        heading_section_metadata.append(paragraph_metadata)
        heading_section_index = paragraph_metadata["heading_section_index"]

    # and last heading section
    chunks.extend(
        chunk_by_word_count(
            heading_section_paragraphs,
            heading_section_metadata,
            9_999_999,
            0,
            code_behavior,
            additional_metadata,
        )
    )

    return chunks
