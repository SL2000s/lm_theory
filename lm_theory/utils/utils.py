import json

from lm_theory.config.config import DB_PATH


def load_json(path: str):
    with open(path, 'r') as json_file:
        json_data = json.load(json_file)
    return json_data


def db2mathjax_macros():
    db_json = load_json(DB_PATH)
    macros = []
    for paper_data in db_json['papers']:
        macros += paper_data['mathjax_macros']
    return macros


def db2mathjax_environments():
    db_json = load_json(DB_PATH)
    environments = []
    for paper_data in db_json['papers']:
        environments += paper_data['mathjax_environments']
    return environments