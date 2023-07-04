#!/usr/bin/env python3
import yaml
import json
import requests
import re
import sys
from jinja2 import Template
from urllib.parse import urlparse
from helper import init_list, get_config, get_name_string, get_license_url
import pandoc
from pandoc.types import Header


filename = sys.argv[1]
config = get_config()
generate_reuse_note = config["generate_reuse_note"] if "generate_reuse_note" in config else True

text_templates = {
    "mtullu": {
        "de": "<div about=\"{{ link }}\"><a rel=\"dc:source\" href=\"{{ image_page }}\"><span property=\"dc:title\">{{ image_title }}</span></a> von <a rel=\"cc:attributionURL dc:creator\" href=\"{{ image_author_link }}\" property=\"cc:attributionName\">{{ image_author }}</a> unter <a rel=\"license\" href=\"{{ license_url }}\">{{ license_short_name }}</a></div>",
        "en": "<div about=\"{{ link }}\"><a rel=\"dc:source\" href=\"{{ image_page }}\"><span property=\"dc:title\">{{ image_title }}</span></a> by <a rel=\"cc:attributionURL dc:creator\" href=\"{{ image_author_link }}\" property=\"cc:attributionName\">{{ image_author }}</a> under <a rel=\"license\" href=\"{{ license_url }}\">{{ license_short_name }}</a></div>"
    },
    "reusage_note": {
        "de": """{% if document_license_url or  document_url %}

---
{% for n in range(reuse_note_heading_level) %}#{% endfor %} Hinweis zur Nachnutzung

{% if document_license_url %}Dieses Werk und dessen Inhalte sind - sofern nicht anders angegeben - lizenziert unter {{ document_license_short_name }}.
Nennung dieses Werkes bitte wie folgt: "[{{ document_title }}]({{ document_url }})" von {{ document_author }}, Lizenz: [{{ document_license_short_name }}]({{ document_license_url }}).{% endif %}
{% if document_url %}Die Quellen dieses Werks sind verfügbar auf [{{ domain }}]({{ document_url }}).{% endif %}
{% endif %}""",
        "en": """{% if document_license_url or  document_url %}

---
{% for n in range(reuse_note_heading_level) %}#{% endfor %} Note on reuse

{% if document_license_url %}This work and its contents are licensed under {{ document_license_short_name }} unless otherwise noted.
Please cite this work as follows: "[{{ document_title }}]({{ document_url }})" by {{ document_author }}, license: [{{ document_license_short_name }}]({{ document_license_url }}).{% endif %}
{% if document_url %}The sources of this work are available on [{{ domain }}]({{ document_url }}).{% endif %}
{% endif %}"""
    },
    "reusage_note_landingpage": {
        "de": "{% if document_license_url or  document_url %}{% if document_license_url %}Dieses Werk und dessen Inhalte sind - sofern nicht anders angegeben - lizenziert unter {{ document_license_short_name }}. Nennung dieses Werkes bitte wie folgt: {% if document_url %}<a href=\"{{ document_url }}\">{% endif %}{{ document_title }}{% if document_url %}</a>{% endif %} von {{ document_author }}, Lizenz: <a href=\"{{ document_license_url }}\">{{ document_license_short_name }}</a>. {% endif %}{% if document_url %}Die Quellen dieses Werks sind verfügbar auf <a href=\"{{ document_url }}\">{{ domain }}</a>.{% endif %}{% endif %}",
        "en": "{% if document_license_url or  document_url %}{% if document_license_url %}This work and its contents are licensed under {{ document_license_short_name }} unless otherwise noted. Please cite this work as follows: {% if document_url %}<a href=\"{{ document_url }}\">{% endif %}{{ document_title }}{% if document_url %}</a>{% endif %} by {{ document_author }}, license: <a href=\"{{ document_license_url }}\">{{ document_license_short_name }}</a>. {% endif %}{% if document_url %}The sources of this work are available on <a href=\"{{ document_url }}\">{{ domain }}</a>.{% endif %}{% endif %}"
    }
}

data = {}
with open("metadata.yml", 'r') as document_metadata:
    try:
        data = yaml.safe_load(document_metadata)
    except yaml.YAMLError as exc:
        print(exc)
        print("Cannot read metadata.yml")
        exit(1)

lngs = init_list(data, "inLanguage")
if "en" in lngs:
    output_lng = "en"
elif "de" in lngs:
    output_lng = "de"
else:
    output_lng = "en"

text = ""
with open(filename, "rt") as document_file:
    text = document_file.read()
# find wikimedia images
images = re.findall("!\[([^\]]*)\]\(([^\)]*)\)", text)
for treffer in images:
    description = treffer[0]
    link = treffer[1]
    if "wikimedia" in link:
        print("TREFFER : " + description + " " + link)
        image_name = re.findall("\/([^\/]*)$", link)[0]

        # get image_name metadata
        session = requests.Session()
        api_url = "https://en.wikipedia.org/w/api.php"
        params_image = {
            "action": "query",
            "format": "json",
            "prop" : "imageinfo",
            "iiprop": "user|userid|canonicaltitle|url|extmetadata",
            "titles": "File:" + image_name
        }

        image_data = session.get(url=api_url, params=params_image).json()
        # print(json.dumps(image_data, indent=4, ensure_ascii=0))

        IPAGES = image_data["query"]["pages"]

        for k, v in IPAGES.items():
            print("LIZENZ : " + v["imageinfo"][0]["extmetadata"]["LicenseShortName"]["value"])
            image_info = v["imageinfo"][0]
            image_title = image_info["extmetadata"]["ObjectName"]["value"]
            image_author = image_info["user"]
            image_author_link = "https://commons.wikimedia.org/wiki/User:" + image_author
            image_page = image_info["descriptionurl"]
            license_name = image_info["extmetadata"]["UsageTerms"]["value"]
            license_short_name = image_info["extmetadata"]["LicenseShortName"]["value"]
            if (license_short_name == "Public domain") :
                license_url = "https://creativecommons.org/publicdomain/zero/1.0/deed.de"
            else :
                license_url = image_info["extmetadata"]["LicenseUrl"]["value"]

            # machine readable TULLU string
            mtullu = Template(text_templates["mtullu"][output_lng]).render(
                link=link, image_page=image_page, image_title=image_title, image_author_link=image_author_link, image_author=image_author, license_url=license_url, license_short_name=license_short_name
            )

            # replace original image with image + citation
            text = re.sub("!\[" + description + "\]\(" + link + "\)", "![" + description + "](" + link + ")" + "  \n" + mtullu, text)

def get_min_heading_level(md_text):
    min_heading_level = None
    for elt in pandoc.iter(pandoc.read(md_text)):
        if isinstance(elt, Header):
            min_heading_level = min(elt[0], min_heading_level) if min_heading_level is not None else elt[0]
    return min_heading_level if min_heading_level is not None else 1
    
document_license_text = ""
if generate_reuse_note:
    document_title = data["name"]
    if "url" in data :
        document_url = data["url"]
        domain = urlparse(document_url).netloc
    else :
        document_url = ""
        domain = ""
    document_author = ", ".join(map(lambda a: get_name_string(a), init_list(data, 'creator')))

    document_license_url = get_license_url(data)
    if document_license_url:
        if "public-domain" in document_license_url or "zero" in document_license_url:
            document_license_short_name = "Public domain"
        else :
            document_license_components = re.findall("licenses\/([^\/]*)\/([^\/]*)", document_license_url)
            document_license_code = document_license_components[0][0]
            document_license_version = document_license_components[0][1]
            document_license_short_name = "CC " + document_license_code.upper() + " " + document_license_version
    else:
        document_license_short_name = None

    document_license_text = Template(text_templates["reusage_note"][output_lng]).render(
        reuse_note_heading_level=get_min_heading_level(text),
        document_author=document_author,
        document_license_short_name=document_license_short_name, document_license_url=document_license_url,
        document_title=document_title, document_url=document_url,
        domain=domain
    )

    landingpage_license_text = Template(text_templates["reusage_note_landingpage"][output_lng]).render(
        reuse_note_heading_level=get_min_heading_level(text),
        document_author=document_author,
        document_license_short_name=document_license_short_name, document_license_url=document_license_url,
        document_title=document_title, document_url=document_url,
        domain=domain
    )

with open(".pd-preparation-tagged.md", 'w', encoding='utf8') as document_tagged:
    document_tagged.write(text + document_license_text)

# Add the reuse notice to the landing page
if output_lng == "de":
    with open(".template-landingpage-de.yml", "a") as template_de:
        template_de.write("\nreuse: >\n " + landingpage_license_text)
elif output_lng == "en":
    with open(".template-landingpage-en.yml", "a") as template_en:
        template_en.write("\nreuse: >\n " + landingpage_license_text)
