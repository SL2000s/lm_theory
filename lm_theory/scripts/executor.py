import os


from lm_theory.paper_extraction.builders.paper_database_builder import create_paper_database, load_paper_database
from lm_theory.generate_html.html_pages_builder import build_html_files


PAGES_ROOT = '/'
ASSETS_ROOT = '/'

SRC_ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'paper_database.json')


if __name__ == '__main__':
    from dotenv import load_dotenv
    DOTENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    load_dotenv(DOTENV_PATH)

    arxiv_papers = [
        '2006.04710',
        # '2406.17837',
        # '2406.01506',
        # '2206.03126',
    ]


    db = load_paper_database(DB_PATH)
    # db.add_arxiv_papers(arxiv_papers)
    db.extend(overwrite=False)
    db.extend_urls()
    db.save()

    build_html_files(SRC_ROOT, PAGES_ROOT, DB_PATH)