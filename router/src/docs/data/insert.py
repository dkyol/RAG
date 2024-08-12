from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class InsertDataRequest(BaseModel):
    chunks: List[Dict[str, Any]]
    asset_type: str


insert_data_examples = {
    "example1": {
        "summary": "Insert chunks into the database.",
        "description": "We insert two chunks into the database for asset_type techblogs.",
        "value": {
            "asset_type": "techblogs",
            "chunks": [
                {
                    "text": "Many CUDA applications running on multi-GPU platforms usually use a single GPU for their compute needs. In such scenarios, a performance penalty is paid by applications because CUDA has to enumerate/initialize all the GPUs on the system. If a CUDA application does not require other GPUs to be visible and accessible, you can launch such applications by isolating the unwanted GPUs from the CUDA process and eliminating unnecessary initialization steps. This post discusses the various methods to accomplish this and their performance benefits.",
                    "text_components": [
                        "Many CUDA applications running on multi-GPU platforms usually use a single GPU for their compute needs. In such scenarios, a performance penalty is paid by applications because CUDA has to enumerate/initialize all the GPUs on the system. If a CUDA application does not require other GPUs to be visible and accessible, you can launch such applications by isolating the unwanted GPUs from the CUDA process and eliminating unnecessary initialization steps.",
                        "This post discusses the various methods to accomplish this and their performance benefits.",
                    ],
                    "word_count": [72, 13],
                    "contains_code": [False, False],
                    "heading_section_tag": ["h1", "h1"],
                    "heading_section_index": [0, 0],
                    "heading_section_title": [
                        "Improving CUDA Initialization Times Using cgroups in Certain Scenarios",
                        "Improving CUDA Initialization Times Using cgroups in Certain Scenarios",
                    ],
                    "only_code": [False, False],
                    "paragraph_index": [0, 1],
                    "paragraph_sentence_index": [0, 0],
                    "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios",
                    "document_url": "https://developer.nvidia.com/blog/improving-cuda-initialization-times-using-cgroups-in-certain-scenarios/",
                    "document_date": "2024-01-05T22:14:41",
                    "document_date_modified": "2024-01-11T19:49:33",
                },
                {
                    "text": "GPU isolation can be achieved on Linux systems by using Linux tools like ```cgroups```. In this section, we first discuss a lower-level approach and then a higher-level possible approach. Another method exposed by CUDA to isolate devices is the use of ```CUDA_VISIBLE_DEVICES```. Although functionally similar, this approach has limited initialization performance gains compared to the ```cgroups``` approach.",
                    "text_components": [
                        "GPU isolation can be achieved on Linux systems by using Linux tools like ```cgroups```. In this section, we first discuss a lower-level approach and then a higher-level possible approach.",
                        "Another method exposed by CUDA to isolate devices is the use of ```CUDA_VISIBLE_DEVICES```. Although functionally similar, this approach has limited initialization performance gains compared to the ```cgroups``` approach.",
                    ],
                    "word_count": [37, 40],
                    "contains_code": [True, True],
                    "heading_section_tag": ["h2", "h2"],
                    "heading_section_index": [1, 1],
                    "heading_section_title": ["GPU isolation", "GPU isolation"],
                    "only_code": [False, False],
                    "paragraph_index": [0, 1],
                    "paragraph_sentence_index": [0, 0],
                    "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios",
                    "document_url": "https://developer.nvidia.com/blog/improving-cuda-initialization-times-using-cgroups-in-certain-scenarios/",
                    "document_date": "2024-01-05T22:14:41",
                    "document_date_modified": "2024-01-11T19:49:33",
                },
            ],
        },
    },
}
