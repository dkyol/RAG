import re
from typing import Tuple, List, Optional


def count_words(spacy_doc_or_sent) -> int:
    return sum(1 for token in spacy_doc_or_sent if not token.is_punct)


def count_words_code(code_string: str) -> int:
    # Use regular expression to split code on common delimiters
    words = re.findall(r"\b\w+\b", code_string)

    # Count the number of words
    num_words = len(words)

    return num_words


def detect_code(paragraph: str) -> Tuple[bool, bool]:
    # if there are at least two triple backticks, there is some code in the paragraph
    contains_code = paragraph.count("```") >= 2

    # if there are only two triple backticks and they are at the start and end,
    # this paragraph is ONLY code
    only_code = (
        paragraph.count("```") == 2
        and paragraph[:3] == "```"
        and paragraph[-3:] == "```"
    )
    return contains_code, only_code


def replace_backticks_pattern(
    text: str, placeholder: Optional[str] = None
) -> Tuple[str, str, List[str]]:
    if placeholder is None:
        placeholder = "BACKTICKS_PLACEHOLDER"

    # Define a regular expression pattern to match triple backticks
    backticks_pattern = re.compile(r"```.*?```", re.DOTALL)

    # Find all occurrences of triple backticks in the input string
    backticks_matches = backticks_pattern.findall(text)

    # Replace triple backticks with a placeholder to preserve them during splitting
    text = backticks_pattern.sub(placeholder, text)

    return text, placeholder, backticks_matches
