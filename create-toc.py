#!/usr/bin/env python3
import yaml
from pandoc.types import *
from helper import get_pandoc_header

filename = sys.argv[1]
#print(pandoc.configure(read=True))
with open(filename) as f:
    content = f.read()

def to_text(data):
    text = ""
    for word in data:
        if isinstance(word, Space):
            text += " "
        elif isinstance(word, Str):
            for arg in word:
                text += arg
    return text

def to_hierarchical_list(headers, result_list=[], cur_level=None):
    if cur_level is None:
        cur_level = headers[0]["level"] if len(headers) > 0 else None
    while True:
        if len(headers) == 0:
            return result_list
        header_level = headers[0]["level"]
        if header_level == cur_level:
            result_list.append(headers.pop(0))
        elif header_level > cur_level:
            result_list[-1]["children"] = to_hierarchical_list(headers, [], header_level)
        else:
            return result_list
        

headers = get_pandoc_header(content)
toc = to_hierarchical_list([{"level": elt[0], "link": elt[1][0], "title": to_text(elt[-1]), "id": i} for i,elt in enumerate(headers)])

with open('.toc.yml', 'w', encoding='utf8') as tocfile:
    yaml.dump({"table-of-contents": toc}, tocfile, allow_unicode=True)
