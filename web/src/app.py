from flask import Flask, request, render_template
from flask_sse import sse
from utils import empty
from users import UserDb
import chains
import os
import re
import requests
import json
from dp_solutions_architecture_utils.logger import LoggerUtil

from llms import llms

# llm = llms.nim_mixtral_llm


logger = LoggerUtil(__name__)

ROUTER_HOST = os.environ.get("ROUTER_HOST", "localhost")
ROUTER_PORT = os.environ.get("ROUTER_PORT", "5006")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
K_TEXT_RECS = 5
MAX_TOKENS_CONTEXT = 2400  # max input seq length of 3072, leave room for prompt 


app = Flask(__name__)
app.config["REDIS_URL"] = f"redis://{REDIS_HOST}"
app.register_blueprint(sse, url_prefix="/stream")


base_dir = os.path.abspath(os.path.join(app.root_path, os.path.pardir))
data_dir = os.path.join(base_dir, "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

userdb = UserDb(data_dir)


@app.route("/health")
def health():
    return {"success": True}, 200


@app.route("/")
def home():

    # Parameters for Text-based Search
    query = request.args.get(
        "query"
    )  # TODO: this param is limited in size to the URL max size; may need to have shortlinks for query page
    if empty(query):
        query = ""
    k = request.args.get("k")
    if empty(k):
        k = str(K_TEXT_RECS)

    # only a limited subset
    all_asset_types = [
        {
            "display_default": True,
            "display_sort_order": 1,
            "display_title": "TechBlog Posts",
            "group": "Written Content",
            "group_sort_order": 2,
            "name": "techblogs",
        },
    ]

    if "asset_types" in request.args:
        asset_types = request.args.getlist("asset_types")
    elif "asset_types[]" in request.args:
        asset_types = request.args.getlist("asset_types[]")
    else:
        asset_types = None

    # No asset_types passed in as parameters
    if asset_types is None or len(asset_types) == 0:
        for atype in all_asset_types:
            atype["display"] = atype["display_default"]

    # Otherwise we do have asset_types passed in as parameters
    else:
        for atype in all_asset_types:
            atype["display"] = atype["name"] in asset_types

    model_name = request.args.get("model_name")
    if empty(model_name):
        model_name = "nim_mixtral_8x7b"

    return render_template(
        "index.html",
        query=query,
        k=k,
        all_asset_types=all_asset_types,
        model_name=model_name,
    )


def _extract_json(text: str):
    stack = []
    start_index = None

    for i, char in enumerate(text):
        if char == '{':
            if not stack:
                start_index = i
            stack.append(char)
        elif char == '}':
            if stack:
                stack.pop()
                if not stack:
                    end_index = i + 1
                    json_str = text[start_index:end_index]
                    try:
                        json_obj = json.loads(json_str)
                        return json_obj
                    except json.JSONDecodeError:
                        logger.error("Error: JSON decoding failed.")
                        return None
            else:
                logger.error("Error: Unmatched '}' character.")
                return None

    logger.error("No JSON object found in the text.")
    return None


def _classify_intent(text: str, llm) -> str:
    chain = chains.get_classifier_chain(llm=llm)
    
    generation = chain.invoke({"text": text}).content
    logger.info(f"Classification: {generation}")
    try:
        response = _extract_json(generation)
    except Exception as e:
        logger.error(e)
        # this is default fallback
        return "summarization"
    if response is None:
        # this is default fallback
        return "summarization"

    classification = "summarization"
    if response["is_user_question"]:
        if response["asks_for_code"]:
            classification = "codeqa"
        else:
            classification = "qa"
    return classification


def _reformat_router_response(response_json: dict) -> dict:
    results = []
    response_asset_types = []
    response_display_titles = []

    for item in response_json:
        results.append(item["results"])
        response_asset_types.append(item["asset_type"])
        response_display_titles.append(item["display_title"])

    response_json = {
        "results": results,
        "response_asset_types": response_asset_types,
        "response_display_titles": response_display_titles,
    }
    return response_json


@app.route("/generate", methods=["POST"])
def generate():
    query = request.json.get("query")
    assert query is not None and query != ""

    session_id = request.json.get("session_id")
    # assert session_id is not None and session_id != ""
    if session_id == "":
        session_id = None

    model_name = request.json.get("model_name")
    print(f'MODEL_NAME model_name == {model_name}')
    assert model_name is not None and model_name != ""

    if "k" in request.json:
        k = request.json.get("k")
    else:
        k = K_TEXT_RECS

    if "asset_types" in request.json:
        asset_types = request.json.get("asset_types")
    else:
        asset_types = ["techblogs"]
    if asset_types is None or len(asset_types) == 0:
        asset_types = ["techblogs"]

    # asset_types should be a list, not a string
    assert isinstance(asset_types, list)

    llm_type, model_name = model_name.split('_', maxsplit=1)

    # TODO: use model_name to pull other llms from openai, nv
    if llm_type == "nim":
        llm = llms.nim_mixtral_llm 
    elif llm_type == "nvai":
        llm = llms.nvai_mixtral_llm
    elif llm_type == "openai":
        llm = llms.openai_gpt3_llm
    else: 
        raise Exception(f"llm_type {llm_type}, model_name {model_name} not supported")

    # First we classify intent
    classification = _classify_intent(text=query, llm=llm)
    sse.publish(
        {"message": "Intent classification: " + classification + "\n"},
        type="publish",
        channel=f"generate.{session_id}",
    )

    # if not answering a user question, we are in asset discovery/summarization mode
    # so we want to hit the index with summaries
    if classification == "summarization":
        for i in range(len(asset_types)):
            asset_types[i] = "summarize_" + asset_types[i]

    # pass the query to the Prospero query router for handling
    response = requests.post(
        url=f"http://{ROUTER_HOST}:{ROUTER_PORT}/search/semantic",
        json={
            "query": query,
            "k": k,
            "asset_types": asset_types,
        },
    )
    if response.status_code == 200:
        response_json = response.json()
    else:
        raise Exception(
            f"Received status code {response.status_code} from query router"
        )

    # Reformat response_json into legacy format
    response_json = _reformat_router_response(response_json)

    if session_id is not None:
        # publish the JSON results as a "greeting" type message. So that the sources
        # load before the generation starts being generated
        json_docs_str = json.dumps(response_json)
        sse.publish(
            {"message": json_docs_str},
            type="greeting",
            channel=f"generate.{session_id}",
        )

    results = response_json.get("results")

    if classification == "qa":
        chain = chains.get_qa_chain(llm=llm)
    elif classification == "codeqa":
        chain = chains.get_codeqa_chain(llm=llm)
    else:
        chain = chains.get_summarization_chain(llm=llm)

    docs = chains.results_as_docs(results, classification, max_tokens=MAX_TOKENS_CONTEXT)

    chunks = []
    for chunk in chain.stream({"query": query, "context": docs}):
        if session_id is not None:
            sse.publish(
                {"message": chunk},
                type="publish",
                channel=f"generate.{session_id}",
            )
        chunks.append(chunk)

    generation = ''.join(chunks)
    generation = generation.strip()

    # Regular QA and Summaries will contain sources in brackets
    # Need to change this into HTML links
    if classification != "codeqa":
        # define a regex that looks for numbers within square brackets
        num_bracket_regex = r"\[(\d+)\]"

        # if no numbers in brackets, try changing numbers in parentheses to brackets
        if len(re.findall(num_bracket_regex, generation)) == 0:
            generation = re.sub(r"\((\d+)\)", r"[\1]", generation)

        # replace combination parentheses and brackets that doesn't look clean
        generation = re.sub(r"\(\[([\d]+)\]\)", r"[\1]", generation)

        if len(re.findall(num_bracket_regex, generation)) > 0:
            generation = re.sub(
                num_bracket_regex,
                r'<a class="citation_\1_" href="#citation_\1_" onclick="scrollToCitation(event, \1);">[\1]</a>',
                generation,
            )
            for doc in docs:
                citation_idx = doc.metadata["idx"]
                url = doc.metadata["url"]
                generation = generation.replace(
                    f'href="#citation_{citation_idx}_"', f'href="{url}"'
                )

    return {"generation": generation, "search": response_json}


@app.route("/user", methods=["GET", "POST"])
def user():
    if request.method == "GET":
        s_ecid = request.args.get("s_ecid")
        username = userdb.get_username(s_ecid)
    else:  # POST
        s_ecid = request.json.get("s_ecid")
        username = request.json.get("username")
        userdb.associate_username(s_ecid, username)
    return {"s_ecid": s_ecid, "username": username}


@app.route("/logquery", methods=["POST"])
def log_query():
    userdb.log_query(
        request.json.get("s_ecid"),
        request.json.get("queryType"),
        request.json.get("query"),
    )
    return ("", 204)  # No Content
