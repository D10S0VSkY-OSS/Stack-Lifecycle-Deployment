import hcl2


def convert_to_json(file_path):
    with open(file_path, "r") as f:
        hcl_data = hcl2.load(f)
        clean_data = remove_interpolations(hcl_data)
        json_data = list_to_dict(clean_data["variable"])
    return json_data


def remove_interpolations(data):
    if isinstance(data, dict):
        return {k: remove_interpolations(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [remove_interpolations(elem) for elem in data]
    elif isinstance(data, str):
        return data.replace("${", "").replace("}", "")
    else:
        return data


def is_interpolation(value):
    return isinstance(value, str) and "${" in value


def list_to_dict(variables_list: list) -> dict:
    variables_dict = {k: v for d in variables_list for k, v in d.items()}
    return variables_dict