from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class UpdateAssetTypesRequest(BaseModel):
    data: Dict[str, Any]


update_asset_types_examples = {
    "example1": {
        "summary": "Update the techblogs asset type.",
        "description": "We pass in a dictionary which contains arbitrary metadata we want to associate "
        "with this asset type. Note that the field 'last_indexed' will automatically be updated when you "
        "hit this endpoint.",
        "value": {
            "data": {
                'asset_type': 'techblogs', 
                'display_title': 'TechBlog Posts', 
            }
        },
    },
}
