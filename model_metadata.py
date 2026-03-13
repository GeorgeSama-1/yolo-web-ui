import re


DATA_VERSION_PATTERN = re.compile(r"^datav\d+$")
CLASS_PATTERN = re.compile(r"^(\d+)class$")
BASELINE_PATTERN = re.compile(r"^base\d+$")


def normalize_data_version(tokens, index):
    token = tokens[index]

    if DATA_VERSION_PATTERN.match(token):
        return token, 1

    if token == "newdata":
        return "newdata", 1

    if token == "data":
        next_token = tokens[index + 1] if index + 1 < len(tokens) else None
        if next_token and re.fullmatch(r"v\d+", next_token):
            return f"data{next_token}".replace("datav", "datav"), 2
        return "data", 1

    if token.startswith("data_v"):
        suffix = token[len("data_v"):]
        if suffix:
            return f"datav{suffix}", 1

    return None, 0


def parse_experiment_name(exp_name):
    tokens = exp_name.split("_")
    info = {
        "timestamp": "_".join(tokens[:2]) if len(tokens) >= 2 else exp_name,
        "task": tokens[2] if len(tokens) > 2 else "unknown",
        "model": tokens[3] if len(tokens) > 3 else "unknown",
        "num_classes": None,
        "exp": None,
        "batch_size": None,
        "img_size": None,
        "gpu": None,
        "data_version": "unknown",
        "is_baseline": False,
        "baseline_tag": None,
        "raw_name": exp_name,
    }

    index = 4
    while index < len(tokens):
        token = tokens[index]

        class_match = CLASS_PATTERN.match(token)
        if class_match:
            info["num_classes"] = int(class_match.group(1))
            index += 1
            continue

        if token.startswith("exp"):
            info["exp"] = token
            index += 1
            continue

        if token.startswith("bs") and len(token) > 2:
            info["batch_size"] = token[2:]
            index += 1
            continue

        if token.startswith("is") and len(token) > 2:
            info["img_size"] = token[2:]
            index += 1
            continue

        if token.startswith("gpu") and len(token) > 3:
            info["gpu"] = token
            index += 1
            continue

        normalized_data_version, consumed = normalize_data_version(tokens, index)
        if consumed:
            info["data_version"] = normalized_data_version
            index += consumed
            continue

        if BASELINE_PATTERN.match(token):
            info["is_baseline"] = True
            info["baseline_tag"] = token
            index += 1
            continue

        index += 1

    return info


def summarize_model_info(info):
    model_type = (info.get("model") or "unknown").upper()
    class_count = info.get("num_classes")
    exp = info.get("exp")
    data_version = info.get("data_version")
    baseline_tag = info.get("baseline_tag")

    name_parts = [model_type]
    if class_count is not None:
        name_parts.append(f"{class_count}类")
    if data_version and data_version != "unknown":
        name_parts.append(data_version)
    if exp:
        name_parts.append(exp)
    if baseline_tag:
        name_parts.append(baseline_tag)

    description_parts = []
    if class_count is not None:
        description_parts.append(f"{class_count}类")
    if baseline_tag:
        description_parts.append("baseline")
        description_parts.append(baseline_tag)
    if exp:
        description_parts.append(exp)
    if info.get("batch_size"):
        description_parts.append(f"BS{info['batch_size']}")
    if info.get("img_size"):
        description_parts.append(f"IS{info['img_size']}")
    if info.get("gpu"):
        description_parts.append(info["gpu"])
    if data_version and data_version != "unknown":
        description_parts.append(data_version)

    return {
        "name": " | ".join(name_parts),
        "description": " ".join(description_parts).strip() or "未识别的实验配置",
    }
