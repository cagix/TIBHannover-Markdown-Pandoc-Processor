#!/usr/bin/env python3
import yaml
import json
import requests
import re
import sys
from jinja2 import Template
from urllib.parse import urlparse
from helper import init_list, get_config, get_creator_string, get_license_url


filename = sys.argv[1]
config = get_config()
reuse_note = config["reuse_note"] if "reuse_note" in config else {}
create_license = reuse_note["generate_license_note"] if "generate_license_note" in reuse_note else True
create_attribution = reuse_note["generate_tullu_tasll_note"] if "generate_tullu_tasll_note" in reuse_note else True
create_sources_link = reuse_note["generate_sources_note"] if "generate_sources_note" in reuse_note else True

text_templates = {
    "mtullu": {
        "de": "<div about=\"{{ link }}\"><a rel=\"dc:source\" href=\"{{ image_page }}\"><span property=\"dc:title\">{{ image_title }}</span></a> von <a rel=\"cc:attributionURL dc:creator\" href=\"{{ image_author_link }}\" property=\"cc:attributionName\">{{ image_author }}</a> unter <a rel=\"license\" href=\"{{ license_url }}\">{{ license_short_name }}</a></div>",
        "en": "<div about=\"{{ link }}\"><a rel=\"dc:source\" href=\"{{ image_page }}\"><span property=\"dc:title\">{{ image_title }}</span></a> by <a rel=\"cc:attributionURL dc:creator\" href=\"{{ image_author_link }}\" property=\"cc:attributionName\">{{ image_author }}</a> under <a rel=\"license\" href=\"{{ license_url }}\">{{ license_short_name }}</a></div>"
    },
    "reusage_note": {
        "de": """

---
## Hinweis zur Nachnutzung

{%if create_license %}Dieses Werk und dessen Inhalte sind - sofern nicht anders angegeben - lizenziert unter {{ course_license_short_name }}.{% endif %}
{%if create_attribution %}Nennung gemäß [TULLU-Regel](https://open-educational-resources.de/oer-tullu-regel/) bitte wie folgt: "[{{ course_title }}]({{ course_url }})" von {{ course_author }}, Lizenz: [{{ course_license_short_name }}]({{ course_license_url }}).{% endif %}
{%if create_sources_link %}Die Quellen dieses Werks sind verfügbar auf [{{ domain }}]({{ course_url }}).{% endif %}
""",
        "en": """

---
## Note on reuse

{%if create_license %}This work and its contents are licensed under {{ course_license_short_name }} unless otherwise noted.{% endif %}
{%if create_attribution %}Attribution according to [TASLL rule](https://open-educational-resources.de/wp-content/uploads/graphic_TASLL-rule_OER-2.pdf) please as follows: "[{{ course_title }}]({{ course_url }})" by {{ course_author }}, license: [{{ course_license_short_name }}]({{ course_license_url }}).{% endif %}
{%if create_sources_link %}The sources of this work are available on [{{ domain }}]({{ course_url }}).{% endif %}
"""
    }
}

data = {}
with open("metadata.yml", 'r') as course_metadata:
    try:
        data = yaml.safe_load(course_metadata)
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

# find wikimedia images
course = open(filename + ".md", "rt")
text = course.read()
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
            # print(mtullu)

            # replace original image with image + citation
            text = re.sub("!\[" + description + "\]\(" + link + "\)", "![" + description + "](" + link + ")" + "  \n" + mtullu, text)

course_license_text = ""
if create_license or create_attribution or create_sources_link:
    course_title = data["name"]
    if "url" in data :
        course_url = data["url"]
        domain = urlparse(course_url).netloc
    else :
        course_url = ""
        domain = ""
    course_author = ", ".join(map(lambda a: get_creator_string(a), init_list(data, 'creator')))
    # course_author_url =

    course_license_url = get_license_url(data)
    if "public-domain" in course_license_url or "zero" in course_license_url :
        course_license_short_name = "Public domain"
    else :
        course_license_components = re.findall("licenses\/([^\/]*)\/([^\/]*)", course_license_url)
        course_license_code = course_license_components[0][0]
        course_license_version = course_license_components[0][1]
        course_license_short_name = "CC " + course_license_code.upper() + " " + course_license_version

    course_license_text = Template(text_templates["reusage_note"][output_lng]).render(
        create_license=create_license, create_attribution=create_attribution, create_sources_link=create_sources_link,
        course_author=course_author,
        course_license_short_name=course_license_short_name, course_license_url=course_license_url,
        course_title=course_title, course_url=course_url,
        domain=domain
    )

with open(filename + "-tagged.md", 'w', encoding='utf8') as course_tagged:
    course_tagged.write(text + course_license_text)

course.close()
