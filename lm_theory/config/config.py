import os


PKG_ROOT = os.path.dirname(os.path.dirname(__file__))

GENERATED_HTML_DIR = 'html'
GENERATED_HTML_ROOT = os.path.join(PKG_ROOT, GENERATED_HTML_DIR)

ENV_PATH_LUNAR = os.path.join(PKG_ROOT, '.env_lunar')

DB_PATH = os.path.join(PKG_ROOT, 'data', 'paper_database.json')