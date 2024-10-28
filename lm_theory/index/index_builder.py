import ast
import json
import os
from llama_index.core import (
    Document,
    load_index_from_storage,
    Settings,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from typing import List

from lm_theory.config.config import (
    LLAMAINDEX_DATA_ROOT,
    DB_PATH,
)
from lm_theory.paper_extraction.builders.paper_database_builder import load_paper_database


PERSIST_DIR = os.path.join(LLAMAINDEX_DATA_ROOT, 'persist_index')
DOCUMENTS_PATH = os.path.join(LLAMAINDEX_DATA_ROOT, 'documents.json')
STATEMENT2LATEX_DEFS_PATH = os.path.join(LLAMAINDEX_DATA_ROOT, 'statement2latex_defs.json')


def db2documents_args(db_path=DB_PATH, documents_path=DOCUMENTS_PATH):
    documents = []
    paper_db = load_paper_database(db_path)
    for paper in paper_db.papers:
        for statement in paper.statements.all_statements():
            doc_data = {
                # 'text': f'"{statement.library_name}":\n{statement.statement_original_tex}',
                'text': statement.statement_original_tex,
                'metadata': {
                    'Statement label': statement.library_name,
                    'Statement title': statement.title,
                    # 'statement_id': statement.statement_id,
                    # 'paper': paper.title,
                    # 'paper_url': paper.source_url,
                }
            }
            # if hasattr(statement, 'proof'):
            #     proof = statement.proof
            #     if proof:
            #         doc_data['metadata']['proof'] = proof.statement_original_tex
            documents.append(doc_data)
    with open(documents_path, 'w') as documents_file:
        json.dump(documents, documents_file, indent=4)
    return documents


SPLIT_STR = ': '  # TODO: move up or to config
def mathjax2katex_macro(mathjax_macro: str):
    # E.g. "emph: [\"\\\\textit{#1}\", 1]" --> "\\emph", "\\textit{#1}"
    # E.g. "Tr: \"\\\\operatorname{Tr}\"" --> "\\Tr", "\\operatorname{Tr}"
    i = mathjax_macro.index(SPLIT_STR)
    mathjax_key, mathjax_val = mathjax_macro[:i], mathjax_macro[i+len(SPLIT_STR):]
    mathjax_val = ast.literal_eval(mathjax_val)
    if isinstance(mathjax_val, list):
        mathjax_val = mathjax_val[0]
    mathjax_val.replace('\\\\', '\\')
    mathjax_key = f'\\{mathjax_key}'
    return mathjax_key, mathjax_val


def mathjaxes2katexes_macros(mathjax_macros: List[str]):
    katex_macros = {}
    for mathjax_macro in mathjax_macros:
        key, value = mathjax2katex_macro(mathjax_macro)
        katex_macros[key] = value
    return katex_macros


def mathjaxes2katexes_environments(mathjax_environments: List[str]):
    return mathjax_environments  # TODO


def build_latex_defs(db_path=DB_PATH, write_path=STATEMENT2LATEX_DEFS_PATH):
    statement2latex_defs = {}
    paper_db = load_paper_database(db_path)
    for paper in paper_db.papers:
        defs = {
            'macros': mathjaxes2katexes_macros(paper.mathjax_macros),
            'environments': mathjaxes2katexes_environments(paper.mathjax_environments),
        }
        for statement in paper.statements.all_statements():
            statement_label = statement.library_name
            statement2latex_defs[statement_label] = defs
    with open(write_path, 'w') as file:
        json.dump(statement2latex_defs, file, indent=4)
    return statement2latex_defs


def init_llm():
    llm = AzureOpenAI(
        model=os.getenv('MODEL_NAME'),
        deployment_name=os.getenv('DEPLOYMENT_NAME'),
        api_key=os.getenv('OPENAI_API_KEY'),
        azure_endpoint=os.getenv('AZURE_ENDPOINT'),
        api_version=os.getenv('OPENAI_API_VERSION'),
    )
    Settings.llm = llm


def init_embed():
    embed_model = AzureOpenAIEmbedding(
        model=os.getenv('EMBEDDING_MODEL'),
        deployment_name=os.getenv('EMBEDDING_DEPLOYMENT'),
        api_key=os.getenv('OPENAI_API_KEY'),
        azure_endpoint=os.getenv('AZURE_ENDPOINT'),
        api_version=os.getenv('OPENAI_API_VERSION'),
    )
    Settings.embed_model = embed_model


def init_llm_and_embed():
    init_llm()
    init_embed()


def create_documents(db_path=DB_PATH, documents_path=DOCUMENTS_PATH):
    documents_args = db2documents_args(db_path, documents_path)
    documents = []
    for document_args in documents_args:
        document = Document(**document_args)
        documents.append(document)
    return documents


def build_index(db_path=DB_PATH, documents_path=DOCUMENTS_PATH, persist_dir: str = None):
    init_llm_and_embed()
    documents = create_documents(db_path, documents_path)
    index = VectorStoreIndex.from_documents(documents)#, embed_model=embed_model, llm=llm)
    index.storage_context.persist(persist_dir=persist_dir)


def query_index(query, persist_dir=PERSIST_DIR):
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return response


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    # build_index(persist_dir=PERSIST_DIR)
    build_latex_defs()
    # init_llm_and_embed()
    # print(query_index('Prove Theorem 1'))
