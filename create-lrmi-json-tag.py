#!/usr/bin/env python3

import yaml
import json
from helper import init_list, get_config, get_creator_string, get_license_url


def add_default_value(item, field_name, default_value):
    if field_name not in item:
        item[field_name] = default_value


def get_file_extension(type):
    if type.lower() == "asciidoc":
        return "asc"
    return type.lower()

def get_pandoc_format(type):
    if type.lower() == "pdf":
        return "latex"
    return type

config = get_config()

with open("metadata.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

    data['@context'] = 'http://schema.org/'
    data['publisher'] = init_list(data, 'publisher')
    data['creator'] = init_list(data, 'creator')
    for c in data['publisher']:
        add_default_value(c, '@type', 'Person')
    for c in data['creator']:
        add_default_value(c, '@type', 'Person')

    with open("metadata.json", 'w', encoding='utf8') as outputfile:
        jsonstring = json.dumps(data, indent=4, ensure_ascii=0)
        tagstring = '<link rel="license" href="' + get_license_url(data) + '"/>'
        tagstring = tagstring + '<script type="application/ld+json">' + jsonstring + '</script>'
        outputfile.write(tagstring)
    
    with open('title.txt', 'w', encoding='utf8') as titlefile:
        authors = list(map(lambda a: get_creator_string(a), init_list(data, "creator")))
        lngs = init_list(data, 'inLanguage')
        main_lng = "en"
        if "en" in lngs:
            main_lng = "en"
        elif "de" in lngs:
            main_lng = "de"
        elif len(lngs) > 0:
            main_lng = lngs[0]
        generated_metadata = {
            "title": data['name'],
            "author": authors,
            "rights": get_license_url(data),
            "language": lngs,
            "lang": main_lng
        }
        output_format = list(map(lambda x: x["format"],init_list(config, "output")))
        generated_metadata["has_online_version"] = "html" in output_format
        downloads = list(filter(lambda x: x != "html", output_format))
        generated_metadata["downloads"] = list(map(lambda x: {"pandoc_format": get_pandoc_format(x), "file_extension": get_file_extension(x), "label": x.upper()}, downloads))
        yaml.dump(generated_metadata, titlefile, explicit_start=True, explicit_end=True)
