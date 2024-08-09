import re
import spacy
from typing import Optional, List, Dict, Tuple, Any
from bs4 import BeautifulSoup
from html_splitters.html_utils import (
    html_str_to_soup,
    clean_html,
    soup_to_str_list,
    clean_concat_str_list,
)
from text_splitters.paragraph import extract_paragraphs
from text_splitters.sentence import extract_sentences
from text_splitters.text_utils import count_words


# regex for headings
_heading_pattern = re.compile("^h[1-6]$")


def _get_first_heading_child(elem):
    # find_all() is recursive=True by default
    for ch in elem.find_all():
        if _heading_pattern.match(ch.name):
            return ch
    return None


def _update_lists(heading, strs, section_text_list, heading_list):
    # if we only have leftover strs and have not found a new heading element
    if heading is None and len(strs) > 0:
        section_text_list.append(clean_concat_str_list(strs))
        strs = []
    # create an empty heading if there was text before
    # first heading
    elif len(heading_list) == 0 and len(strs) > 0:
        heading_list.append(None)
        section_text_list.append(clean_concat_str_list(strs))
        heading_list.append(heading)
        strs = []
    # if we reached the first heading and no strs before, then
    # just add the heading
    elif len(heading_list) == 0 and len(strs) == 0:
        heading_list.append(heading)
    else:
        section_text_list.append(clean_concat_str_list(strs))
        heading_list.append(heading)
        strs = []
    return strs, section_text_list, heading_list


def _recursive_get_sections(
    soup, strs, section_text_list, heading_list, search_heading_child=None
):
    for elem in soup.find_all(recursive=False):
        if elem == search_heading_child:
            strs, section_text_list, heading_list = _update_lists(
                search_heading_child, strs, section_text_list, heading_list
            )
            search_heading_child = None
            continue
        if _heading_pattern.match(elem.name):
            strs, section_text_list, heading_list = _update_lists(
                elem, strs, section_text_list, heading_list
            )
            search_heading_child = None
            continue

        first_heading_child = _get_first_heading_child(elem)
        if first_heading_child is None:  # could not find a heading child within elem
            str_list = soup_to_str_list(elem)
            strs.extend(str_list)
        else:
            strs = _recursive_get_sections(
                elem,
                strs,
                section_text_list,
                heading_list,
                search_heading_child=first_heading_child,
            )
    return strs


def _soup_to_heading_sections(
    html_soup: BeautifulSoup,
    nlp: Optional[spacy.language.Language] = None,
    word_count: bool = True,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    # load nlp obj if none provided and we need a word_count
    if word_count and nlp is None:
        nlp = spacy.load("en_core_web_sm")

    # remove unwanted elements that will never contain text and may confuse the scraper
    html_soup = clean_html(html_soup)

    # Now we can start parsing the HTML tree
    section_text_list = []
    heading_list = []
    all_metadata = []

    strs = []
    strs = _recursive_get_sections(html_soup, strs, section_text_list, heading_list)
    # print(f"A {len(section_text_list)} {len(strs)}")

    # if there are leftover strs
    if len(strs) > 0:
        strs, section_text_list, heading_list = _update_lists(
            None, strs, section_text_list, heading_list
        )

    # print(f"B {len(section_text_list)} {len(strs)}")
    assert len(strs) == 0

    # if there is no headings found, create an empty one
    if len(heading_list) == 0:
        heading_list.append(None)

    for heading_section_index, heading in enumerate(heading_list):
        if heading is not None:
            title = str(heading.text).replace("\xa0", " ").strip()
            tag = heading.name

        # Assume that if the text has no heading, that means it came from html
        # elements before the first heading provided.
        # For example, with NVIDIA blogs where the title is not included with
        # the content HTML.
        else:
            # if we have a document title use that
            if (
                additional_metadata is not None
                and "document_title" in additional_metadata
            ):
                title = additional_metadata["document_title"]
                tag = "h1"

            # otherwise we don't have a "document_title" to use
            else:
                title = None
                tag = None

        metadata = {
            "heading_section_index": heading_section_index,
            "heading_section_tag": tag,
            "heading_section_title": title,
        }
        if additional_metadata is not None:
            metadata.update(additional_metadata)

        if word_count:
            if heading_section_index > len(section_text_list) - 1:
                # only keep this section if there is a title
                if title is not None and title != "":
                    metadata["word_count"] = 0
                    section_text_list.append("")
                # otherwise, we don't need to add this to metadata
                # since it has empty text and empty title
                else:
                    continue
            else:
                doc = nlp(section_text_list[heading_section_index])
                metadata["word_count"] = count_words(doc)

        all_metadata.append(metadata)

    # assert len(section_text_list) == len(all_metadata)
    # if len(section_text_list) != len(all_metadata):
        # raise Exception(f"{len(section_text_list)} {len(all_metadata)} {len(heading_list)} {section_text_list}")

    return section_text_list, all_metadata


def extract_heading_sections(
    html_str: str,
    nlp: Optional[spacy.language.Language] = None,
    word_count: bool = True,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    html_soup = html_str_to_soup(html_str)
    return _soup_to_heading_sections(
        html_soup,
        nlp,
        word_count,
        additional_metadata,
    )


def extract_heading_section_paragraphs(
    html_str: str,
    nlp: Optional[spacy.language.Language] = None,
    word_count: bool = True,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    heading_sections, all_metadata = extract_heading_sections(
        html_str=html_str,
        nlp=nlp,
        word_count=word_count,
        additional_metadata=additional_metadata,
    )

    paragraphs_list = []
    metadata_list = []

    for heading_section, metadata in zip(heading_sections, all_metadata):
        # remove word_count from heading_section
        # that's because this is word_count of the heading section
        if word_count is True and "word_count" in metadata:
            metadata.pop("word_count")

        paragraphs, paragraphs_metadata = extract_paragraphs(
            text=heading_section,
            nlp=nlp,
            word_count=word_count,
            additional_metadata=metadata,
        )

        paragraphs_list.extend(paragraphs)
        metadata_list.extend(paragraphs_metadata)

    return paragraphs_list, metadata_list


def extract_heading_section_sentences(
    html_str: str,
    nlp: Optional[spacy.language.Language] = None,
    word_count: bool = True,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    paragraphs, paragraphs_metadata = extract_heading_section_paragraphs(
        html_str, nlp, word_count, additional_metadata
    )
    return extract_sentences(
        text=paragraphs,
        nlp=nlp,
        paragraphs_metadata=paragraphs_metadata,
        additional_metadata=additional_metadata,
    )
