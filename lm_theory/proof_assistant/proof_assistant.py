import json
import os
import requests
import warnings

from typing import Dict

from lm_theory.config.config import (
    DB_PATH,    
    PKG_ROOT,
)

LUNARCORE_ADDRESS="0.0.0.0"
LUNARCORE_PORT=8088
LUNAR_RUN_URL_TEMPLATE = f'http://{LUNARCORE_ADDRESS}:{LUNARCORE_PORT}/workflow/run?user_id={{user_id}}'


INDEX_JSON_PATH = os.path.join(PKG_ROOT, 'data', 'db_llamaindex_data.json')
DB2LLAMAINDEX_JSON_PATH = os.path.join(
    PKG_ROOT,
    'lunar_workflows',
    'db2llamaindex.json'
)
LLAMAINDEX_QUEST_JSON_PATH = os.path.join(
    PKG_ROOT,
    'lunar_workflows',
    'llamaindex_quest.json'
)
DB2LLAMAINDEX_DB_PATH_COMPONENT = 'TEXTINPUT-0'
DB2LLAMAINDEX_INDEX_PATH_COMPONENT = 'TEXTINPUT-7'
LLAMAINDEX_QUEST_QUERY_COMPONENT = 'TEXTINPUT-0'
LLAMAINDEX_QUEST_INDEX_PATH_COMPONENT = 'TEXTINPUT-3'
LLAMAINDEX_OUTPUT_COMPONENT = 'LLAMAINDEXQUERYING-1'


def load_json(path: str):
    with open(path, 'r') as json_file:
        json_data = json.load(json_file)
    return json_data


def run_workflow(workflow_json: Dict):              # TODO: make sure this works when simultanous requests on same workflow (probably fails now)
    try:
        url = LUNAR_RUN_URL_TEMPLATE.format(user_id=workflow_json['userId'])       # TODO: change default user?
        response = requests.post(url, json=workflow_json)
        if response.status_code == 200:
            component_outputs = json.loads(response.text)
            return component_outputs
        else:
            warnings.warn(f'Failed with status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        warnings.warn(f'Error making request: {e}')
    warnings.warn('Failed running workflow. Have you started the LunarCore server?')
    return None


def component_by_label(label: str, workflow_json: Dict):
    for component_json in workflow_json['components']:
        if component_json['label'] == label:
            return component_json
    return None


def set_text_component_value(text: str, component_label: str, workflow_json: Dict):
    component = component_by_label(component_label, workflow_json)
    component_input = component['inputs'][0]
    component_input['value'] = text


def build_index():
    workflow_json = load_json(DB2LLAMAINDEX_JSON_PATH)
    set_text_component_value(
        DB_PATH,
        DB2LLAMAINDEX_DB_PATH_COMPONENT,
        workflow_json
    )
    set_text_component_value(
        INDEX_JSON_PATH,
        DB2LLAMAINDEX_INDEX_PATH_COMPONENT,
        workflow_json
    )
    component_outputs = run_workflow(workflow_json)
    return component_outputs


def db_query(query):
    workflow_json = load_json(LLAMAINDEX_QUEST_JSON_PATH)
    set_text_component_value(
        query,
        LLAMAINDEX_QUEST_QUERY_COMPONENT,
        workflow_json
    )
    set_text_component_value(
        INDEX_JSON_PATH,
        LLAMAINDEX_QUEST_INDEX_PATH_COMPONENT,
        workflow_json
    )
    component_outputs = run_workflow(workflow_json)
    response_component_json = component_outputs[LLAMAINDEX_OUTPUT_COMPONENT]
    response = response_component_json['output']['value']['Response']['response']
    return response


if __name__ == '__main__':
    # build_index()
    response = db_query("What does Lemma 22 say?")
    print(response)