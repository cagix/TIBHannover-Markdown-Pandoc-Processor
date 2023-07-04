#!/usr/bin/env python3

import yaml
import json
import requests
import os.path
from datetime import datetime
from babel.dates import format_date
from helper import init_list, get_config, get_name_string, get_license_url


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

def init_list(record, field_name):
    if field_name not in record:
        return []
    value = record[field_name]
    return value if isinstance(value, list) else [value]

def convert_to_standard_vocab_entry(record, field_name):
    if field_name in record:
        record[field_name] = list(map(lambda x: {"id": x} if isinstance(x, str) else x, init_list(record, field_name)))

def add_missing_labels(record, field_name):
    if field_name in record:
        labels_filename = os.path.realpath(os.path.dirname(__file__)) + "/labels/" + field_name + ".json"
        if os.path.isfile(labels_filename):
            with open(labels_filename, 'r') as stream:
                all_labels = json.load(stream)
            for entry in record[field_name]:
                existing_labels = entry["prefLabel"] if "prefLabel" in entry else {}
                default_labels = all_labels[entry["id"]] if entry["id"] in all_labels else {}
                merged_labels = {**default_labels, **existing_labels}
                if len(merged_labels) > 0:
                    entry["prefLabel"] = merged_labels

def format_date_to_locale(record, main_lng, date_field, date_format_str):
    """Formats a date to the locale.

    Args:
        record (dict): The current record
        main_lng (string): The main language of the record
        date_field (string): The field of the date to be formatted inside the record
        date_format_str (string): The current format of the date

    Returns:
        string: Date formatted to locale
    """    
    if date_field in record:
        date = datetime.strptime(record[date_field][:10], date_format_str)
        return format_date(date, locale=main_lng)
        

config = get_config()

data = {}
with open("metadata.yml", 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

data['@context'] = 'http://schema.org/'
data['publisher'] = init_list(data, 'publisher')
data['creator'] = init_list(data, 'creator')

for c in data['publisher']:
    add_default_value(c, '@type', 'Person')
for c in data['creator']:
    add_default_value(c, '@type', 'Person')

with open("metadata.json", 'w', encoding='utf8') as outputfile:
    jsonstring = json.dumps(data, indent=4, ensure_ascii=0)
    license_url = get_license_url(data)
    tagstring = ''
    if license_url:
        tagstring += '<link rel="license" href="' + license_url + '"/>'
    tagstring += '<script type="application/ld+json">' + jsonstring + '</script>'
    outputfile.write(tagstring)

with open("metadata.yml", 'w', encoding='utf8') as metadata_file:
    convert_to_standard_vocab_entry(data, "about")
    convert_to_standard_vocab_entry(data, "educationalLevel")
    convert_to_standard_vocab_entry(data, "learningResourceType")
    convert_to_standard_vocab_entry(data, "inLanguage")
    add_missing_labels(data, "about")
    add_missing_labels(data, "educationalLevel")
    add_missing_labels(data, "learningResourceType")
    add_missing_labels(data, "inLanguage")
    yaml.dump(data, metadata_file, allow_unicode=True, explicit_start=True)

with open('title.txt', 'w', encoding='utf8') as titlefile:
    authors = list(map(lambda a: get_name_string(a), init_list(data, "creator")))
    lngs = init_list(data, 'inLanguage')
    
    # If prefLabels are already assigned to languages, get only the language ids
    if len(lngs) > 0 and type(lngs[0]) == dict:
        lngs = [lang["id"] for lang in lngs]

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
        "lang": main_lng,
        "langLabels": []
    }
    if "image" in data or "thumbnailUrl" in data:
        generated_metadata["thumbnailUrl"] = data["thumbnailUrl"] if "thumbnailUrl" in data else data["image"]
    
    def get_label(entry, lng):
        if "prefLabel" in entry:
            if lng in entry["prefLabel"]:
                return entry["prefLabel"][lng]
            elif "en" in entry["prefLabel"]:
                return entry["prefLabel"]["en"]
        return entry["id"]

    def get_labels_for_main_lng(field):
        return list(filter(None, map(lambda x: get_label(x, main_lng), data[field]))) if field in data else []

    generated_metadata["about"] = get_labels_for_main_lng("about")
    generated_metadata["educationalLevel"] = get_labels_for_main_lng("educationalLevel")
    generated_metadata["learningResourceType"] = get_labels_for_main_lng("learningResourceType")
    output_format = list(map(lambda x: x["format"],init_list(config, "output")))
    generated_metadata["has_online_version"] = "html" in output_format
    downloads = list(filter(lambda x: x != "html", output_format))
    generated_metadata["downloads"] = list(map(lambda x: {"pandoc_format": get_pandoc_format(x), "file_extension": get_file_extension(x), "label": x.upper()}, downloads))
    generated_metadata["langLabels"] = get_labels_for_main_lng("inLanguage")
    generated_metadata["publisher"] = list(map(lambda a: get_name_string(a), init_list(data, "publisher")))
    generated_metadata["datePublishedFormatted"] = format_date_to_locale(data, main_lng, "datePublished", "%Y-%m-%d")

    yaml.dump(generated_metadata, titlefile, allow_unicode=True, explicit_start=True, explicit_end=True)
