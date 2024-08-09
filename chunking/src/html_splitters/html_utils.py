import re
from typing import Optional, List, Dict, Tuple, Any
from bs4 import BeautifulSoup
from text_splitters.text_utils import replace_backticks_pattern


def html_str_to_soup(html_str: str) -> BeautifulSoup:
    """Convert an HTML string into a BeautifulSoup object using lxml parser.

    Args:
        html_str (str): HTML as string

    Returns:
        BeautifulSoup: parsed BeautifulSoup object
    """
    return BeautifulSoup(html_str, features="lxml")


def _remove_unwanted_elements(html_soup: BeautifulSoup) -> BeautifulSoup:
    # Remove all of these elements
    for elem in [
        "video",
        "script",
        "style",
        "meta",
        "iframe",
        "link",
        "base",
        "area",
    ]:
        for x in html_soup.find_all(elem):
            x.extract()
    return html_soup


def _replace_images(html_soup: BeautifulSoup) -> BeautifulSoup:
    # Replace each img element with a div containing its alt text or remove if no alt text
    img_elements = html_soup.find_all("img")
    for img in img_elements:
        alt_text = img.get(
            "alt", ""
        )  # Get the alt text, or an empty string if not present
        alt_text = alt_text.strip()
        if alt_text == "":
            img.extract()
        else:
            new_div = html_soup.new_tag("div")
            new_div.string = alt_text
            img.replace_with(new_div)
    return html_soup


def _add_code_delimiters(html_soup: BeautifulSoup) -> BeautifulSoup:
    for elem in [
        "code",
        "pre",
    ]:
        # Replace each code element with a triple-backtick
        code_elements = html_soup.find_all(elem)
        for code in code_elements:
            # if just a single string
            if code.string is not None and code.string != "":
                code.string = "```" + code.string + "```"
            # if multiple strings
            elif code.string is None:
                gen = code.strings

                first_str = None
                while True:
                    try:
                        s = next(gen)
                        if first_str is None:
                            first_str = s
                    except StopIteration:
                        # StopIteration is raised when there are no more elements
                        # So s will be the last string
                        try:
                            s.replace_with(s + "```")
                        except UnboundLocalError:
                            pass
                        except ValueError:
                            pass
                        break
                if first_str is not None:
                    try:
                        first_str.replace_with("```" + first_str)
                    except UnboundLocalError:
                        pass
                    except ValueError:
                        pass
    return html_soup


def _replace_line_breaks(html_soup: BeautifulSoup) -> BeautifulSoup:
    # Replace all line breaks with newline characters
    for br in html_soup.find_all("br"):
        br.replace_with("\n")
    return html_soup

# all block level elements
_block_level_elems = (
    "div",
    "p",
    "ul",
    "ol",
    "li",
    "table",
    "tr",
    "td",
    "th",
    "form",
    "nav",
    "blockquote",
    "section",
    "article",
    "aside",
)

def clean_html(html_soup: BeautifulSoup) -> BeautifulSoup:
    html_soup = _remove_unwanted_elements(html_soup)
    html_soup = _replace_images(html_soup)
    html_soup = _add_code_delimiters(html_soup)
    html_soup = _replace_line_breaks(html_soup)

    # next we add newlines to block level elements
    for elem in html_soup.find_all():
        if elem.name in _block_level_elems:
            if elem.string is not None and elem.string != "":
                elem.string += "\n"
            elif elem.string is None:
                gen = elem.strings
                while True:
                    try:
                        s = next(gen)
                    except StopIteration:
                        # StopIteration is raised when there are no more elements
                        try:
                            s.replace_with(s + "\n")
                        except UnboundLocalError:
                            pass
                        except ValueError:
                            pass
                        break
    return html_soup


def soup_to_str_list(html_soup: BeautifulSoup) -> List[str]:
    """Extract list of strings from BeautifulSoup object.

    Args:
        html_soup (BeautifulSoup): parsed BeautifulSoup object

    Returns:
        List[str]: list of strings within BeautifulSoup
    """
    strs = html_soup.strings
    # strs = [x.replace("\xa0", " ").strip(" ") for x in strs]
    strs = [x.replace("\xa0", " ") for x in strs]
    strs = [x for x in strs if x != ""]
    return strs


def clean_concat_str_list(strs: List[str]) -> str:
    """Clean and concat list of strings into one block of text.
    Includes newline characters between HTML elements.

    Args:
        strs (List[str]): list of text strings pulled from the HTML soup

    Returns:
        str: Cleaned and concatenated text from HTML, separated by newlines.
    """
    out_text = ""
    punc = (",", ".", "?", "!", ":", "-")
    last_str_code = False
    for x in strs:
        xstrip = x.strip()
        # if this string is code
        if len(xstrip) > 6 and xstrip[:3] == "```" and xstrip[-3:] == "```":
            # if last string was code, no need for a space separation
            # we will want to merge these two code blocks together
            if last_str_code:
                out_text += x 
            # otherwise we do need a space
            else:
                out_text += " " + x
            last_str_code = True
        elif x[:1] in punc or out_text[-1:] == "\n":
            out_text += x
            last_str_code = False
        else:
            out_text += " " + x
            last_str_code = False
    out_text = out_text.strip()

    # Replace triple backticks with a placeholder to preserve them during splitting
    out_text, placeholder, backticks_matches = replace_backticks_pattern(out_text)

    # Now that we've removed any code elements in backticks we can run the following replacements:
    # Get rid of carriage return Windows-style and replace with simpler newline
    out_text = out_text.replace("\r\n", "\n")
    # Replace multiple newlines with a single newline
    out_text = re.sub(r"\n+", "\n", out_text)
    # Replace two or more consecutive spaces with a single space
    out_text = re.sub(r" {2,}", " ", out_text)
    while "\n \n" in out_text:
        # replace newline, space, newline with single newline
        out_text = out_text.replace("\n \n", "\n")

    # Reinsert the backticks_matches
    for match in backticks_matches:
        out_text = out_text.replace(placeholder, match, 1)

    # Merge consecutive code blocks by removing six consecutive backticks
    out_text = out_text.replace("``````", "")
    out_text = out_text.replace("``` ```", " ")
    out_text = out_text.replace("```\n```", "\n")

    return out_text
