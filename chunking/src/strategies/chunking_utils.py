from typing import Optional, List, Dict, Any


def chunk_by_word_count(
    texts: List[str],
    texts_metadata: List[Dict[str, Any]],
    chunk_min_words: int,
    chunk_overlap_words: int,
    code_behavior: str,
    additional_metadata: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not code_behavior or code_behavior.lower() == "respect_code_boundaries":
        return _chunk_by_word_count_code_boundaries(
            texts,
            texts_metadata,
            chunk_min_words,
            chunk_overlap_words,
            True,
            additional_metadata,
        )
    if code_behavior.lower() == "ignore_code_boundaries":
        return _chunk_by_word_count_code_boundaries(
            texts,
            texts_metadata,
            chunk_min_words,
            chunk_overlap_words,
            False,
            additional_metadata,
        )
    if code_behavior.lower() == "remove_code_sections":
        return _chunk_by_word_count_remove_code_sections(
            texts,
            texts_metadata,
            chunk_min_words,
            chunk_overlap_words,
            additional_metadata,
        )
    raise ValueError(f"code_behavior {code_behavior} is not supported")


def _new_chunk(
    indiv_level_metadata_keys: Dict[str, Any],
    additional_metadata: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    chunk = {
        "text": "",
        "text_components": [],
    }
    chunk.update({k: [] for k in indiv_level_metadata_keys})
    if additional_metadata is not None:
        chunk.update(additional_metadata)

    return chunk


def _chunk_by_word_count_remove_code_sections(
    texts: List[str],
    texts_metadata: List[Dict[str, Any]],
    chunk_min_words: int,
    chunk_overlap_words: int,
    additional_metadata: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    assert len(texts) == len(texts_metadata)

    # chunks that will be returned
    chunks: List[Dict[str, Any]] = []

    # additional_metadata applies to the whole document, so it should not be on an individual level
    # this is a set of metadata keys that are only individual level
    indiv_level_metadata_keys = {
        k
        for k in texts_metadata[0].keys()
        if additional_metadata is None or k not in additional_metadata
    }

    # if no minimum, then it's pretty simple
    # each chunk corresponds to directly to input texts
    if chunk_min_words <= 0:
        for txt, txt_metadata in zip(texts, texts_metadata):
            only_code = txt_metadata.get("only_code")
            if only_code is None:
                only_code = False

            heading_section_title = txt_metadata.get("heading_section_title")
            chunk = {
                "text": ""
                if only_code
                else (
                    txt
                    if not heading_section_title
                    else heading_section_title + "\n" + txt
                ),
                "text_components": [txt],  # wrap in a single-element list
            }
            chunk.update(
                {
                    k: [txt_metadata[k]]  # wrap in a single-element list
                    for k in indiv_level_metadata_keys
                }
            )
            if additional_metadata is not None:
                chunk.update(additional_metadata)
            chunks.append(chunk)
        return chunks

    # otherwise, we have a chunk_min_words > 0
    combined_word_count = 0
    chunk = _new_chunk(indiv_level_metadata_keys, additional_metadata)

    for i, (txt, txt_metadata) in enumerate(zip(texts, texts_metadata)):
        only_code = txt_metadata.get("only_code")
        if only_code is None:
            only_code = False

        chunk["text_components"].append(txt)

        for k in indiv_level_metadata_keys:
            chunk[k].append(txt_metadata[k])

        if not only_code:
            word_count = txt_metadata["word_count"]
            combined_word_count += word_count

        # if we've hit chunk_min_words requirement or we reach the last text
        if combined_word_count >= chunk_min_words or i + 1 == len(texts):
            # append our new chunk
            chunks.append(chunk)
            # create a new empty chunk
            combined_word_count = 0
            chunk = _new_chunk(indiv_level_metadata_keys, additional_metadata)

            # if we want overlap and not on the last text
            if i < len(texts) - 1 and chunk_overlap_words > 0:
                # go backwards and add
                for j in range(i, -1, -1):
                    back_only_code = texts_metadata[j].get("only_code")
                    if back_only_code is None:
                        back_only_code = False

                    chunk["text_components"] = [texts[j]] + chunk["text_components"]
                    for k in indiv_level_metadata_keys:
                        chunk[k] = [texts_metadata[j][k]] + chunk[k]

                    if not back_only_code:
                        word_count = texts_metadata[j]["word_count"]
                        combined_word_count += word_count

                    if combined_word_count >= chunk_overlap_words:
                        break

                combined_word_count = 0

    # concatenate text components
    for chunk in chunks:
        text_components_list = chunk.get("text_components")
        only_code_list = chunk.get("only_code")
        heading_section_title_list = chunk.get("heading_section_title")

        num_text_components = len(text_components_list)

        if not only_code_list:
            only_code_list = [False] * num_text_components
        if not heading_section_title_list:
            heading_section_title_list = [None] * num_text_components

        chunk["text"] = ""

        last_heading_section_title = None
        for text_component, only_code, heading_section_title in zip(
            text_components_list, only_code_list, heading_section_title_list
        ):
            if heading_section_title and (
                last_heading_section_title is None
                or heading_section_title != last_heading_section_title
            ):
                chunk["text"] += "\n" + heading_section_title + "\n"
                last_heading_section_title = heading_section_title
            if not only_code:
                chunk["text"] += text_component + " "
        if len(chunk["text"]) > 0:
            chunk["text"] = chunk["text"].strip()

    return chunks


# TODO: check if last chunk is only_code but does not start with ```. same with first chunk
def _chunk_by_word_count_code_boundaries(
    texts: List[str],
    texts_metadata: List[Dict[str, Any]],
    chunk_min_words: int,
    chunk_overlap_words: int,
    respect_code_boundaries: bool,
    additional_metadata: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    assert len(texts) == len(texts_metadata)

    # chunks that will be returned
    chunks: List[Dict[str, Any]] = []

    # additional_metadata applies to the whole document, so it should not be on an individual level
    # this is a set of metadata keys that are only individual level
    indiv_level_metadata_keys = {
        k
        for k in texts_metadata[0].keys()
        if additional_metadata is None or k not in additional_metadata
    }

    # if no minimum, then it's pretty simple
    # each chunk corresponds to directly to input texts
    if chunk_min_words <= 0:
        for txt, txt_metadata in zip(texts, texts_metadata):
            heading_section_title = txt_metadata.get("heading_section_title")
            chunk = {
                "text": (
                    txt
                    if not heading_section_title
                    else heading_section_title + "\n" + txt
                ),
                "text_components": [txt],  # wrap in a single-element list
            }
            chunk.update(
                {
                    k: [txt_metadata[k]]  # wrap in a single-element list
                    for k in indiv_level_metadata_keys
                }
            )
            if additional_metadata is not None:
                chunk.update(additional_metadata)
            chunks.append(chunk)
        return chunks

    # otherwise, we have a chunk_min_words > 0
    combined_word_count = 0
    chunk = _new_chunk(indiv_level_metadata_keys, additional_metadata)

    prev_text_only_code = False
    for i, (txt, txt_metadata) in enumerate(zip(texts, texts_metadata)):
        only_code = txt_metadata.get("only_code")
        if only_code is None:
            only_code = False

        # if not the first text and only_code change
        if (
            respect_code_boundaries
            and len(chunk["text_components"]) > 0
            and only_code is not prev_text_only_code
        ):
            # then create a new chunk
            chunks.append(chunk)
            # reset
            combined_word_count = 0
            chunk = _new_chunk(indiv_level_metadata_keys, additional_metadata)

        chunk["text_components"].append(txt)

        for k in indiv_level_metadata_keys:
            chunk[k].append(txt_metadata[k])

        word_count = txt_metadata["word_count"]
        combined_word_count += word_count

        # if we've hit chunk_min_words requirement or we reach the last text
        if combined_word_count >= chunk_min_words or i + 1 == len(texts):
            # append our new chunk
            chunks.append(chunk)
            # create a new empty chunk
            combined_word_count = 0
            chunk = _new_chunk(indiv_level_metadata_keys, additional_metadata)

            # if we want overlap and not on the last text
            if i < len(texts) - 1 and chunk_overlap_words > 0:
                next_only_code = texts_metadata[i + 1].get("only_code")
                if next_only_code is None:
                    next_only_code = False
                if only_code is next_only_code:
                    # go backwards and add
                    for j in range(i, -1, -1):
                        back_only_code = texts_metadata[j].get("only_code")
                        if back_only_code is None:
                            back_only_code = False
                        if respect_code_boundaries and back_only_code is not only_code:
                            break
                        chunk["text_components"] = [texts[j]] + chunk["text_components"]
                        for k in indiv_level_metadata_keys:
                            chunk[k] = [texts_metadata[j][k]] + chunk[k]
                        word_count = texts_metadata[j]["word_count"]
                        combined_word_count += word_count

                        if combined_word_count >= chunk_overlap_words:
                            break

                    combined_word_count = 0

        prev_text_only_code = only_code

    # concatenate text components
    for chunk in chunks:
        text_components_list = chunk.get("text_components")
        only_code_list = chunk.get("only_code")
        heading_section_title_list = chunk.get("heading_section_title")

        num_text_components = len(text_components_list)

        if not only_code_list:
            only_code_list = [False] * num_text_components
        if not heading_section_title_list:
            heading_section_title_list = [None] * num_text_components

        chunk["text"] = ""

        last_heading_section_title = None
        for text_component, only_code, heading_section_title in zip(
            text_components_list, only_code_list, heading_section_title_list
        ):
            if heading_section_title and (
                last_heading_section_title is None
                or heading_section_title != last_heading_section_title
            ):
                chunk["text"] += "\n" + heading_section_title + "\n"
                last_heading_section_title = heading_section_title
            if not only_code:
                chunk["text"] += text_component + " "
            else:
                chunk["text"] += text_component + "\n"
        if len(chunk["text"]) > 0:
            chunk["text"] = chunk["text"].strip()

    return chunks
