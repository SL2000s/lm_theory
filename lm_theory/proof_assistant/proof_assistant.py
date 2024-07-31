# import asyncio
import os
import requests
# import shutil

# from lunarcore.component_library import COMPONENT_REGISTRY
# from lunarcore.core.controllers.workflow_controller import WorkflowController
from lunarcore.core.data_models import WorkflowModel

from lm_theory.config.config import (
    DB_PATH,    
    PKG_ROOT,
)

LUNARCORE_ADDRESS="0.0.0.0"
LUNARCORE_PORT=8088
LUNAR_RUN_URL = f'http://{LUNARCORE_ADDRESS}:{LUNARCORE_PORT}/workflow/run'


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


def load_workflow(path: str):
    with open(path, 'r') as workflow_json_file:
        workflow_json_str = workflow_json_file.read()
    workflow = WorkflowModel.model_validate_json(workflow_json_str)
    return workflow


def run_workflow(workflow: WorkflowModel):              # TODO: make sure this works when simultanous requests on same workflow (probably fails now)
    try:
        data = {
            'workflow': workflow.model_dump(),
            # 'user_id': 'si5126lj-s@student.lu.se'                          # TODO: si5126lj-s@student.lu.se?
        }
        user_id = 'admin'
        response = requests.post(
            f'{LUNAR_RUN_URL}?user_id={user_id}',                     # TODO: make template string
            json=workflow.dict()
        )
        if response.status_code == 200:
            print('Success:', response.status_code)
            input(123)
            print('Response:', response.text)
            input(123)
            print(response)
        else:
            print('Failed with status code:', response.status_code)
            print(dir(response))
            print(response.text)
            print(response.raw)
    except requests.exceptions.RequestException as e:
        print('Error making request:', e)


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
    run_workflow(workflow)


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
    run_workflow(workflow)


if __name__ == '__main__':
    build_index()