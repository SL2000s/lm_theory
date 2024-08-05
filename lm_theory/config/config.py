import os


PKG_ROOT = os.path.dirname(os.path.dirname(__file__))
JINJA2_TEMPLATES_ROOT = os.path.join(PKG_ROOT, 'templates')

GENERATED_HTML_DIR = 'html'
GENERATED_HTML_ROOT = os.path.join(PKG_ROOT, GENERATED_HTML_DIR)

ASSETS_ROOT = os.path.join(PKG_ROOT, 'assets')

DB_PATH = os.path.join(PKG_ROOT, 'data', 'paper_database.json')