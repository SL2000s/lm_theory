from .paper_database_builder import load_paper_database
from ..html_rendering.html_renderer import HTMLGenerator


def build_html_files(pages_root: str, root: str, db_path: str = None):
    db = load_paper_database(db_path)
    html_generator = HTMLGenerator(db, pages_root, root)
    html_generator.build_html_files()