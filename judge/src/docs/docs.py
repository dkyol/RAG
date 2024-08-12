from typing import Union, List, Optional
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi

description = """The **NVIDIA DLI Judge API** is developed by the Developer Programs Solutions Engineering team.
It serves as a user interface for collecting feedback on retrieval performance. The API is built with FastAPI.

## Usage
## ❗To use these docs, click "Try it out", pick your example from the dropdown, and then click "Execute".
"""

tags_metadata = [
    {
        "name": "feedback",
        "description": "Provide feedback to be used for retrieval evaluation.",
    },
    {
        "name": "health",
        "description": "Health check. Returns code 200 response if application is running.",
    },
    {
        "name": "users",
        "description": "Reading existing users and creating new users.",
    },
    {
        "name": "cookies",
        "description": "Reading existing Adobe session cookies and creating new cookies associated with a user.",
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
            for _, method_item in app.openapi_schema.get('paths').items():
                for _, param in method_item.items():
                    responses = param.get('responses')
                    responses.clear()
        return app.openapi_schema
    
    app.openapi = custom_openapi