from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class DeleteDataRequest(BaseModel):
    ids: List[str]
    asset_type: str


delete_data_examples = {
    "example1": {
        "summary": "Delete data from the db based on id.",
        "description": "Delete data from the db. You will need to modify ids below to correspond to actual ids in the database.",
        "value": {
            "asset_type": "techblogs",
            "ids": ['doc:techblogs:88f63c9699c54c4da36b2dda387baeed', 'doc:techblogs:6a1a273cc5494b5ebf17203d7c8e98c6'],
        },
    },
}
