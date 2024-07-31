import asyncio
import os
import shutil

from lunarcore.component_library import COMPONENT_REGISTRY
from lunarcore.core.controllers.workflow_controller import WorkflowController
from lunarcore.core.data_models import WorkflowModel

from lm_theory.config.config import (
    DB_PATH,    
    ENV_PATH_LUNAR,
    PKG_ROOT,
)


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


if len(COMPONENT_REGISTRY.components) == 0:                     # TODO: Is this thread-safe?
    asyncio.run(COMPONENT_REGISTRY.register(fetch=True))


def _clear_venv(workflow: WorkflowModel, workflow_controller: WorkflowController):
    venv_dir = os.path.join(
        workflow_controller.config.FLOW_STORAGE_BASE_PATH,
        workflow.user_id,
        workflow_controller.config.FLOW_ROOT_DIR,
        workflow_controller.config.FLOW_DEFAULT_VENV_ROOT,
        workflow.id,
    )
    shutil.rmtree(venv_dir)


def load_workflow(path: str):
    with open(path, 'r') as workflow_json_file:
        workflow_json_str = workflow_json_file.read()
    workflow = WorkflowModel.model_validate_json(workflow_json_str)
    return workflow


def run_workflow(workflow: WorkflowModel):
    workflow_controller = WorkflowController(ENV_PATH_LUNAR)
    run_result = asyncio.run(workflow_controller.run(workflow, workflow.user_id))
    _clear_venv(workflow)
    return run_result


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