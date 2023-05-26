#!/usr/bin/env python3

import os
import sys
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from helper import get_config, init_list


label = {
    "de": {
        "TOC_TITLE": "Inhaltsverzeichnis"
    },
    "en": {
        "TOC_TITLE": "Contents"
    }
}
markdown_filename = sys.argv[1]
language = "en"
with open("title.txt", "r") as title_file:
    try:
        title_metadata = yaml.safe_load(title_file)
        page_title = title_metadata["title"]
        language = title_metadata["lang"]
        has_online_version = title_metadata["has_online_version"] if "has_online_version" in title_metadata else True
        downloads = init_list(title_metadata, "downloads")
        if language not in label:
            language = "en"
    except yaml.YAMLError as exc:
        print(exc)
config = get_config()
with open("metadata.yml", "r") as metadata_file:
    try:
        data = yaml.safe_load(metadata_file)
        url = data["url"] if "url" in data else None
    except yaml.YAMLError as exc:
        print(exc)


env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape()
)
template = env.get_template("pandoc-generate.sh.j2")
template.stream({
    "markdown_filename": markdown_filename,
    "page_title": page_title,
    "toc_title": label[language]["TOC_TITLE"],
    "has_online_version": has_online_version,
    "downloads": downloads,
    "url": url,
    **config
}).dump(".pandoc-generate.sh")
