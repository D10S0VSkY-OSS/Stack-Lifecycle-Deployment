import ast


def convert_to_dict(data):
    result = []
    for key, val in data.items():
        try:
            check = ast.literal_eval(val)
        except:
            continue
        if isinstance(check, dict):
            data[key] = check
            result.append(data)
        elif isinstance(check, list):
            data[key] = check
            result.append(data)
    if not len(result):
        return data
    return result[0]
