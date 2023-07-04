import yaml


def init_list(record, field_name):
    if field_name not in record:
        return []
    value = record[field_name]
    return value if isinstance(value, list) else [value]


def get_name_string(person):
    name_items = []
    if "name" in person and person['name'] is not None:
        return person['name']
    if "givenName" in person and person['givenName'] is not None:
        name_items.append(person['givenName'])
    if "familyName" in person and person['familyName'] is not None:
        name_items.append(person['familyName'])
    return " ".join(name_items)


def get_license_url(record):
    if "license" in record:
        val = record["license"]
        return val if isinstance(val, str) else val["id"]
    return None


def get_config():
    with open("config.yml", "r") as config_file:
        try:
            return yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            print(exc)
    return {}
