import yaml


def init_list(record, field_name):
    if field_name not in record:
        return []
    value = record[field_name]
    return value if isinstance(value, list) else [value]


def get_creator_string(creator):
    creator_items = []
    if "givenName" in creator and creator['givenName'] is not None:
        creator_items.append(creator['givenName'])
    if "familyName" in creator and creator['familyName'] is not None:
        creator_items.append(creator['familyName'])
    return " ".join(creator_items)


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
