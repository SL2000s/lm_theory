from ..paper_extraction.builders.paper_database_builder import load_paper_database
from .html_rendering.html_renderer import HTMLGenerator


def build_html_files(root: str, pages_root: str, db_path: str = None,
                     assets_root: str = None):
    db = load_paper_database(db_path)
    html_generator = HTMLGenerator(db, root, pages_root, assets_root)
    html_generator.build_html_files()