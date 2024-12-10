import os


from lm_theory.paper_extraction.data_models.paper_database import PaperDatabase
from lm_theory.paper_extraction.builders.paper_database_builder import create_paper_database, load_paper_database
from lm_theory.generate_html.html_pages_builder import build_html_files


PAGES_ROOT = '/'
ASSETS_ROOT = '/'   # TODO: remove

SRC_ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'paper_database.json')


def print_db_structure():  # TODO: get this working
    def resolve_ref(ref, schema):
        ref_path = ref.split('/')[1:]
        ref_schema = schema
        for part in ref_path:
            ref_schema = ref_schema[part]
        return ref_schema

    def print_descriptions(properties, schema, prefix=''):
        for field, details in properties.items():
            print(field, details)
            input()
            if 'allOf' in details:  # Nested model         # TODO: misses eg. items, anyOf etc
                for ref in details['allOf']:
                    if '$ref' in ref:
                        nested_schema = resolve_ref(ref['$ref'], schema)
                        print(f"{prefix}{field}: {details.get('description', 'No description')}")
                        print_descriptions(nested_schema['properties'], schema, prefix=prefix + '  ')
            else:
                print(f"{prefix}{field}: {details.get('description', 'No description')}")

    schema = PaperDatabase.model_json_schema()
    print_descriptions(schema['properties'], schema)


if __name__ == '__main__':
    from dotenv import load_dotenv
    DOTENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    load_dotenv(DOTENV_PATH)

    # print_db_structure()
    # input()

    # arxiv_papers = [
    #     # '2006.04710',
    #     # '2406.17837',
    #     # '2406.01506',
    #     # '2206.03126',
    #     '2308.16898',
    # ]


    # db = load_paper_database(DB_PATH)
    # # db.add_arxiv_papers(arxiv_papers)
    # db.extend(overwrite=False)
    # db.extend_statement_nrs()
    # db.extend_mathjax_macros()
    # db.extend_mathjax_environments()
    # db.extend_urls()
    # db.save()

    build_html_files(SRC_ROOT, PAGES_ROOT, DB_PATH)