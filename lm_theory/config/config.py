import os
from dotenv import load_dotenv


load_dotenv()

PKG_ROOT = os.path.dirname(os.path.dirname(__file__))
JINJA2_TEMPLATES_ROOT = os.path.join(PKG_ROOT, 'templates')

GENERATED_HTML_DIR = 'html'
GENERATED_HTML_ROOT = os.path.join(PKG_ROOT, GENERATED_HTML_DIR)

ASSETS_ROOT = os.path.join(PKG_ROOT, 'assets')
DATA_ROOT = os.path.join(PKG_ROOT, 'data')
LLAMAINDEX_DATA_ROOT = os.path.join(DATA_ROOT, 'llama_index')
os.makedirs(LLAMAINDEX_DATA_ROOT, exist_ok=True)
HTML_ROOT = os.path.join(PKG_ROOT, 'html')
TEMPLATES_ROOT = os.path.join(PKG_ROOT, 'templates')

DB_PATH = os.path.join(PKG_ROOT, 'data', 'paper_database.json')
SRC_ROOT = os.path.dirname(os.path.dirname(__file__))
PAGES_ROOT = '/'
