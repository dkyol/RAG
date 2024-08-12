from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables.base import Runnable
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import Document
from typing import List
from sentencepiece import SentencePieceProcessor
import json

# Count tokens
sp = SentencePieceProcessor(model_file="tokenizer.model")

# Used for langchain
document_prompt = PromptTemplate(
    input_variables=["idx", "title", "page_content"],
    template="[{idx}]: {title}\n{page_content}",
)

document_variable_name = "context"

summarization_prompt = PromptTemplate.from_template(
    """After conducting research on the topic of "{query}", you found the following resources. Each resource is numbered [1], [2], [3], etc. While these resources should be relevant to the topic, some may not be relevant. Use relevant resources as context to write a high-level overview of the topic. Limit yourself to one tight paragraph. Add in-line citations to indicate when a sentence was pulled from a specific resource. Your overview should include the names of SDKs, libraries, models, or frameworks if they are relevant.\n\n{context}"""
)
qa_prompt = PromptTemplate.from_template(
    """To help answer the question "{query}", you found the following resources. Each resource is numbered [1], [2], [3], etc. While these resources should be relevant to the topic, some may not be relevant. Use relevant resources as context to answer the original question. Add in-line citations to indicate when a sentence was pulled from a specific resource.\n\n{context}"""
)
codeqa_prompt = PromptTemplate.from_template(
    """To help answer the coding question "{query}", you found the following resources. The resouces may themselves contain code, in which case the code has been surrounded with triple backticks (```). While these resources should be relevant to the topic, some may not be relevant. Use relevant resources as context to answer the original question. Any code you include should be surrounded with triple backticks (```).\n\n{context}"""
)


def _get_stuff_documents_chain(llm: BaseChatModel, prompt) -> Runnable:
    chain = create_stuff_documents_chain(
        llm = llm,
        prompt=prompt,
        document_prompt=document_prompt
    )
    return chain


def get_summarization_chain(llm: BaseChatModel) -> Runnable:
    return _get_stuff_documents_chain(llm, summarization_prompt)


def get_qa_chain(llm: BaseChatModel) -> Runnable:
    return _get_stuff_documents_chain(llm, qa_prompt)


def get_codeqa_chain(llm: BaseChatModel) -> Runnable:
    return _get_stuff_documents_chain(llm, codeqa_prompt)


# add newlines between headings and paragraphs
def _format_text_without_code(result: dict) -> str:
    heading_section_index = json.loads(result["heading_section_index"])
    heading_section_title = json.loads(result["heading_section_title"])
    paragraph_index = json.loads(result["paragraph_index"])
    only_code = json.loads(result["only_code"])
    text_components = json.loads(result["text_components"])

    text = ""
    last_hsi = None

    for i in range(len(text_components)):
        if last_hsi is None or last_hsi != heading_section_index[i]:
            text += heading_section_title[i] + "\n"

        if not only_code[i]:
            text += text_components[i] + " "
            # look ahead
            if i < len(text_components) - 1:
                if paragraph_index[i] != paragraph_index[i + 1]:
                    text += "\n"

        last_hsi = heading_section_index[i]

    return text.strip()


# add newlines between headings and paragraphs
def _format_text_with_code(result: dict) -> str:
    heading_section_index = json.loads(result["heading_section_index"])
    heading_section_title = json.loads(result["heading_section_title"])
    paragraph_index = json.loads(result["paragraph_index"])
    only_code = json.loads(result["only_code"])
    text_components = json.loads(result["text_components"])

    text = ""
    last_hsi = None

    for i in range(len(text_components)):
        if last_hsi is None or last_hsi != heading_section_index[i]:
            text += heading_section_title[i] + "\n"
        text += text_components[i]
        if only_code[i]:
            text += "\n"
        else:
            text += " "
        # look ahead
        if i < len(text_components) - 1:
            if paragraph_index[i] != paragraph_index[i + 1]:
                text += "\n"

        last_hsi = heading_section_index[i]

    return text.strip()


def count_tokens(input_text):
    tokens = sp.EncodeAsIds(input_text)
    return len(tokens)


def results_as_docs(results: List[dict], classification: str, max_tokens: int=-1) -> List[Document]:
    docs = []
    idx = 1
    running_token_count = 0
    for result in results:  # loop thru asset types
        for res in result:
            if classification == "qa":
                page_content = _format_text_without_code(res)
            elif classification == "codeqa":
                page_content = _format_text_with_code(res)
            else:  # summarization, just use summary text as is
                page_content = res["text"]

            if max_tokens > 0:
                 running_token_count += count_tokens(page_content)
                 if running_token_count > max_tokens:
                    # Stop processing more docs
                    print(f"Running token count reached max_tokens {max_tokens}")
                    return docs

            doc = Document(
                page_content=page_content,
                metadata={
                    "title": res["document_title"],
                    "url": res["document_url"],
                    "idx": idx,
                },
            )
            idx += 1
            docs.append(doc)
    return docs


def get_classifier_chain(llm: BaseChatModel) -> Runnable:
    system_message = "You are a helpful AI bot being used in a technical domain. Format your output as a JSON object."
    human_msg_pt = HumanMessagePromptTemplate.from_template(
        "First, is the following text a user question that needs answering or just a topic to learn more about? Second, if the text is a user question that needs answering, is the question asking for code to be written?\nText: {text}"
    )

    # three classification categories
    code_question = AIMessage(
        content='{\n  "is_user_question": true,\n  "asks_for_code": true\n}'
    )
    regular_question = AIMessage(
        content='{\n  "is_user_question": true,\n  "asks_for_code": false\n}'
    )
    not_question = AIMessage(content='{\n  "is_user_question": false\n}')

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessage(content=system_message),
            human_msg_pt.format(text="how do I install cuda drivers"),
            code_question,
            human_msg_pt.format(
                text="what is the right NVIDIA SDK to use for computer vision"
            ),
            regular_question,
            human_msg_pt.format(text="recommender systems for online shopping"),
            not_question,
            human_msg_pt.format(text="How to import rapids cudf in python?"),
            code_question,
            human_msg_pt.format(text="biomedical devices"),
            not_question,
            human_msg_pt.format(text="write some code that prints hello world"),
            code_question,
            human_msg_pt.format(
                text="The leading cause of death in the 16th century was infection."
            ),
            not_question,
            human_msg_pt.format(text="NVIDIA Merlin SDK for recommendation systems"),
            not_question,
            human_msg_pt.format(text="who founded the company NVIDIA?"),
            regular_question,
            human_msg_pt,
        ]
    )
    chain = prompt | llm
    return chain
