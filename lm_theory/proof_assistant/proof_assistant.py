import json
import os
import requests
import warnings

from lunarcore.core.data_models import WorkflowModel, ComponentModel

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

def load_workflow(path: str):
    with open(path, 'r') as workflow_json_file:
        workflow_json_str = workflow_json_file.read()
    workflow = WorkflowModel.model_validate_json(workflow_json_str)
    return workflow


def run_workflow(workflow: WorkflowModel):              # TODO: make sure this works when simultanous requests on same workflow (probably fails now)
    try:
        url = LUNAR_RUN_URL_TEMPLATE.format(user_id=workflow.user_id)       # TODO: change default user?
        response = requests.post(url, json=workflow.model_dump())
        if response.status_code == 200:
            component_outputs = json.loads(response.text)
            return component_outputs
        else:
            warnings.warn(f'Failed with status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        warnings.warn(f'Error making request: {e}')
    warnings.warn('Failed running workflow. Have you started the LunarCore server?')
    return None


def component_by_label(label: str, workflow: WorkflowModel):
    for component in workflow.components:
        if component.label == label:
            return component
    return None


def set_text_component_value(text: str, component_label: str, workflow: str):
    component = component_by_label(component_label, workflow)
    component_input = component.inputs[0]
    component_input.value = text


def build_index():
    workflow = load_workflow(DB2LLAMAINDEX_JSON_PATH)
    set_text_component_value(
        DB_PATH,
        DB2LLAMAINDEX_DB_PATH_COMPONENT,
        workflow
    )
    set_text_component_value(
        INDEX_JSON_PATH,
        DB2LLAMAINDEX_INDEX_PATH_COMPONENT,
        workflow
    )
    component_outputs = run_workflow(workflow)
    return component_outputs


def db_query(query):
    workflow = load_workflow(LLAMAINDEX_QUEST_JSON_PATH)
    set_text_component_value(
        query,
        LLAMAINDEX_QUEST_QUERY_COMPONENT,
        workflow
    )
    set_text_component_value(
        INDEX_JSON_PATH,
        LLAMAINDEX_QUEST_INDEX_PATH_COMPONENT,
        workflow
    )
    component_outputs = run_workflow(workflow)

    response_component = ComponentModel(
        **component_outputs[LLAMAINDEX_OUTPUT_COMPONENT]           # TODO: is there a better way to do this?
    )
    response = response_component.output.value['Response']['response']
    return response


if __name__ == '__main__':
    # build_index()
    response = db_query("What does Lemma 22 say?")
    print(response)