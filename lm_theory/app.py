import json
import os

from datetime import datetime
from fastapi import FastAPI, Form, File, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict

# from fastapi_sessions import SessionMiddleware   # TODO: remove from poetry
# from fastapi_sessions.cookie_storage import CookieStorage

from lm_theory.config.config import (
    ASSETS_ROOT,
    HTML_ROOT,
    TEMPLATES_ROOT,
    GENERATED_HTML_ROOT,
    JINJA2_TEMPLATES_ROOT,
    PKG_ROOT,
)
from lm_theory.generate_html.html_rendering.jinja2_env_filters import (
    add_html_tabs_newlines,
    add_root,
    capitalize_first,
    code_list,
    escape_backslashes,
    link_list,
    replace_tabs_by_spaces,
    text_list,
)
from lm_theory.proof_assistant.proof_assistant import db_query
from lm_theory.utils.utils import (
    db2mathjax_environments,
    db2mathjax_macros,
)


app = FastAPI()
# app.add_middleware(SessionMiddleware)

app.mount("/assets", StaticFiles(directory=ASSETS_ROOT), name="assets") 
app.mount("/html", StaticFiles(directory=HTML_ROOT), name="html")
app.mount("/templates", StaticFiles(directory=TEMPLATES_ROOT), name="templates")

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class CustomJinja2Templates(Jinja2Templates):
    def __init__(self, directory: str):
        super().__init__(directory=directory)
        self.env.filters['add_html_tabs_newlines'] = add_html_tabs_newlines
        self.env.filters['add_root'] = lambda s: add_root(s, '/')
        self.env.filters['add_pages_root'] = lambda s: add_root(s, '/')
        self.env.filters['add_assets_root'] = lambda s: add_root(s, '/')
        self.env.filters['capitalize_first'] = capitalize_first
        self.env.filters['code_list'] = code_list
        self.env.filters['escape_backslashes'] = escape_backslashes
        self.env.filters['link_list'] = lambda s: link_list(s, GENERATED_HTML_ROOT)
        self.env.filters['replace_tabs_by_spaces'] = replace_tabs_by_spaces
        self.env.filters['text_list'] = text_list
templates = CustomJinja2Templates(directory=JINJA2_TEMPLATES_ROOT)


@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "index.html")).read())


@app.get("/contact", response_class=HTMLResponse)
async def get_about():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "contact.html")).read())


@app.get("/examples", response_class=HTMLResponse)
async def get_about():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "examples.html")).read())


@app.get("/library", response_class=HTMLResponse)
async def get_other_pages():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "library/index.html")).read())


@app.get("/library/axioms", response_class=HTMLResponse)
@app.get("/library/axioms/index.html", response_class=HTMLResponse)   # TODO (also below): remove need of this
async def get_axioms():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "library/axioms/index.html")).read())


@app.get("/library/axioms/{library_name}/index.html", response_class=HTMLResponse)
async def get_axiom(library_name: str):
    return HTMLResponse(open(os.path.join(HTML_ROOT, f"library/axioms/{library_name}/index.html")).read())


@app.get("/library/corollaries", response_class=HTMLResponse)
@app.get("/library/corollaries/index.html", response_class=HTMLResponse)
async def get_corollaries():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "library/corollaries/index.html")).read())


@app.get("/library/corollaries/{library_name}/index.html", response_class=HTMLResponse)
async def get_corollary(library_name: str):
    return HTMLResponse(open(os.path.join(HTML_ROOT, f"library/corollaries/{library_name}/index.html")).read())


@app.get("/library/definitions", response_class=HTMLResponse)
@app.get("/library/definitions/index.html", response_class=HTMLResponse)
async def get_definitions():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "library/definitions/index.html")).read())


@app.get("/library/definitions/{library_name}/index.html", response_class=HTMLResponse)
async def get_definition(library_name: str):
    return HTMLResponse(open(os.path.join(HTML_ROOT, f"library/definitions/{library_name}/index.html")).read())


@app.get("/library/lemmas", response_class=HTMLResponse)
@app.get("/library/lemmas/index.html", response_class=HTMLResponse)
async def get_lemmas():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "library/lemmas/index.html")).read())


@app.get("/library/lemmas/{library_name}/index.html", response_class=HTMLResponse)
async def get_lemma(library_name: str):
    return HTMLResponse(open(os.path.join(HTML_ROOT, f"library/lemmas/{library_name}/index.html")).read())


@app.get("/library/theorems", response_class=HTMLResponse)
@app.get("/library/theorems/index.html", response_class=HTMLResponse)
async def get_theorems():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "library/theorems/index.html")).read())


@app.get("/library/theorems/{library_name}/index.html", response_class=HTMLResponse)
async def get_theorem(library_name: str):
    return HTMLResponse(open(os.path.join(HTML_ROOT, f"library/theorems/{library_name}/index.html")).read())


@app.get("/library/papers", response_class=HTMLResponse)
@app.get("/library/papers/index.html", response_class=HTMLResponse)
async def get_papers():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "library/papers/index.html")).read())


@app.get("/library/papers/{paper_name}/index.html", response_class=HTMLResponse)
async def get_paper(paper_name: str):
    return HTMLResponse(open(os.path.join(HTML_ROOT, f"library/papers/{paper_name}/index.html")).read())


@app.get("/contribute", response_class=HTMLResponse)
async def get_contribute_form():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "contribute/index.html")).read())

@app.get("/contribute/add_statement", response_class=HTMLResponse)
async def get_contribute_form():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "contribute/add_statement.html")).read())

@app.get("/contribute/add_paper", response_class=HTMLResponse)
async def get_contribute_form():
    return HTMLResponse(open(os.path.join(HTML_ROOT, "contribute/add_paper.html")).read())


@app.post("/submit_contribution")
async def submit_contribution(
    contributor_name: str = Form(...),
    contributor_affiliation: str = Form(None),
    contributor_email: str = Form(None),
    contribution_type: str = Form(...),
    contribution_title: str = Form(...),
    contribution_content: str = Form(...),
    contribution_proof: str = Form(None),
    contribution_keywords: str = Form(None),
    contribution_field: str = Form(None),
    contribution_references: str = Form(None),
    contribution_file: UploadFile = File(None)
):
    data = {
        'contributor_name': contributor_name,
        'contributor_affiliation': contributor_affiliation,
        'contributor_email': contributor_email,
        'contribution_type': contribution_type,
        'contribution_title': contribution_title,
        'contribution_content': contribution_content,
        'contribution_proof': contribution_proof,
        'contribution_keywords': contribution_keywords,
        'contribution_field': contribution_field,
        'contribution_references': contribution_references
    }
    
    # Save form data as JSON file
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    json_filename = f'contribution_{timestamp}.json'
    json_filepath = os.path.join(UPLOAD_FOLDER, json_filename)
    
    with open(json_filepath, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Save uploaded file
    if contribution_file:
        file_location = os.path.join(UPLOAD_FOLDER, contribution_file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(contribution_file.file.read())
    
    return RedirectResponse(url='/', status_code=303)


def generate_reply(prompt: str):
    reply = (db_query(prompt))
    # reply = "TEST RESPONSE\n$$\lip a=b$$"
    return reply


class Query(BaseModel):
    prompt: str


@app.get("/proof_assistant", response_class=HTMLResponse)
async def proof_assistant(request: Request):
    return templates.TemplateResponse(
        'proof_assistant.html.jinja',
        {
            "request": request,
            "mathjax_macros": db2mathjax_macros(),
            "mathjax_environments": db2mathjax_environments(),
        }
    )


@app.post("/proof_assistant/query")
async def proof_assistant_query(query: Query):
    prompt = query.prompt
    reply = generate_reply(prompt)
    return {"reply": reply}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8800)  # TODO: get from .env
