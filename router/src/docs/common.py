from fastapi.openapi.utils import get_openapi


doc_description = """The **NVIDIA DLI Router API** is developed by the Developer Programs Solutions Engineering team.
It serves as an entrypoint for API requests and coordinates between an embedding model being served with Triton and 
Redis as a vector/document+metadata database, for the purposes of retrieval. Redis allows us to store information alongisde each vector, 
including the original text and other metadata. The API is built with FastAPI.

## Usage
### ❗To use these docs, click "Try it out", pick your example from the dropdown, and then click "Execute".
"""


tags_metadata = [
    {
        "name": "search",
        "description": "Primary search API endpoints. Semantic and keyword.",
    },
    {
        "name": "data",
        "description": "API Endpoints for inserting and deleting data from db.",
    },
    {
        "name": "asset-types",
        "description": "API Endpoints for getting metadata about available asset types and updating that metadata with new information.",
    },
    {
        "name": "health",
        "description": "Health check. Returns code 200 response if application is running.",
    },
]


def clear_openapi_responses(app):
    def custom_openapi():
        if not app.openapi_schema:
            app.openapi_schema = get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                terms_of_service=app.terms_of_service,
                contact=app.contact,
                license_info=app.license_info,
                routes=app.routes,
                tags=app.openapi_tags,
                servers=app.servers,
            )
            for _, method_item in app.openapi_schema.get("paths").items():
                for _, param in method_item.items():
                    responses = param.get("responses")
                    responses.clear()
        return app.openapi_schema

    app.openapi = custom_openapi




# for examples in [chunking_examples]:
#     for k, v in examples.items():
#         v[
#             "description"
#         ] = f'{v["description"]}\n\n**❗To run this example, click "Try it out", and then click "Execute".**'
