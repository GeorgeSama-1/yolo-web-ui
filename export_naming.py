from pathlib import Path


def build_labelme_json_filename(image_filename: str) -> str:
    return f'{Path(image_filename).stem}.json'
