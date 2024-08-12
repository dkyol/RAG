# dummy data
metadata = {
    "text": "```# Create a mountpoint for the cgroup hierarchy as root```\n```$> cd /mnt```\n```$> mkdir cgroupV1Device```",
    "text_components": [
        "```# Create a mountpoint for the cgroup hierarchy as root```",
        "```$> cd /mnt```",
        "```$> mkdir cgroupV1Device```",
    ],
    "word_count": [9, 2, 2],
    "contains_code": [True, True, True],
    "heading_section_tag": ["h3", "h3", "h3"],
    "heading_section_index": [2, 2, 2],
    "heading_section_title": [
        "Isolating GPUs using cgroups V1",
        "Isolating GPUs using cgroups V1",
        "Isolating GPUs using cgroups V1",
    ],
    "only_code": [True, True, True],
    "paragraph_index": [2, 3, 4],
    "paragraph_sentence_index": [0, 0, 0],
    "document_title": "Improving CUDA Initialization Times Using cgroups in Certain Scenarios",
    "document_url": "https://developer.nvidia.com/blog/improving-cuda-initialization-times-using-cgroups-in-certain-scenarios/",
    "document_date": "2024-01-05T22:14:41",
    "document_date_modified": "2024-01-11T19:49:33",
    "document_full_text": "",
    "last_indexed": "2024-01-16T15:17:09",
}

index_schema = {
    "tag": [{"name": "document_url", "separator": "|"}],
    "text": [
        {"name": "text"},
        {"name": "text_components"},
        {"name": "word_count"},
        {"name": "contains_code"},
        {"name": "heading_section_tag"},
        {"name": "heading_section_index"},
        {"name": "heading_section_title"},
        {"name": "only_code"},
        {"name": "paragraph_index"},
        {"name": "paragraph_sentence_index"},
        {"name": "document_title"},
        {"name": "document_date"},
        {"name": "document_date_modified"},
        {"name": "document_full_text"},
        {"name": "last_indexed"},
    ],
}

tag_fields = set()
for field in index_schema["tag"]:
    tag_fields.add(field["name"])

text_fields = list()
for field in index_schema["text"]:
    text_fields.append(field["name"])
