import json
import os

from datetime import datetime
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/html", StaticFiles(directory="html"), name="html")          # TODO: don't hardcode   # TODO: works only when cwd is here
app.mount("/assets", StaticFiles(directory="assets"), name="assets")    # TODO: don't hardcode   # TODO: works only when cwd is here

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTMLResponse(open("html/index.html").read())   # TODO (also below): works only when cwd is here


@app.get("/contact", response_class=HTMLResponse)
async def get_about():
    return HTMLResponse(open("html/contact.html").read())


@app.get("/examples", response_class=HTMLResponse)
async def get_about():
    return HTMLResponse(open("html/examples.html").read())


@app.get("/library", response_class=HTMLResponse)
async def get_other_pages():
    return HTMLResponse(open("html/library/index.html").read())


@app.get("/library/axioms", response_class=HTMLResponse)
@app.get("/library/axioms/index.html", response_class=HTMLResponse)   # TODO (also below): remove need of this
async def get_other_pages():
    return HTMLResponse(open("html/library/axioms/index.html").read())


@app.get("/library/axioms/{library_name}/index.html", response_class=HTMLResponse)
async def get_other_pages(library_name: str):
    return HTMLResponse(open(f"html/library/axioms/{library_name}/index.html").read())


@app.get("/library/corollaries", response_class=HTMLResponse)
@app.get("/library/corollaries/index.html", response_class=HTMLResponse)
async def get_other_pages():
    return HTMLResponse(open("html/library/corollaries/index.html").read())


@app.get("/library/corollaries/{library_name}/index.html", response_class=HTMLResponse)
async def get_other_pages(library_name: str):
    return HTMLResponse(open(f"html/library/corollaries/{library_name}/index.html").read())


@app.get("/library/definitions", response_class=HTMLResponse)
@app.get("/library/definitions/index.html", response_class=HTMLResponse)
async def get_other_pages():
    return HTMLResponse(open("html/library/definitions/index.html").read())


@app.get("/library/definitions/{library_name}/index.html", response_class=HTMLResponse)
async def get_other_pages(library_name: str):
    return HTMLResponse(open(f"html/library/definitions/{library_name}/index.html").read())


@app.get("/library/lemmas", response_class=HTMLResponse)
@app.get("/library/lemmas/index.html", response_class=HTMLResponse)
async def get_other_pages():
    return HTMLResponse(open("html/library/lemmas/index.html").read())


@app.get("/library/lemmas/{library_name}/index.html", response_class=HTMLResponse)
async def get_other_pages(library_name: str):
    return HTMLResponse(open(f"html/library/lemmas/{library_name}/index.html").read())


@app.get("/library/theorems", response_class=HTMLResponse)
@app.get("/library/theorems/index.html", response_class=HTMLResponse)
async def get_other_pages():
    return HTMLResponse(open("html/library/theorems/index.html").read())


@app.get("/library/theorems/{library_name}/index.html", response_class=HTMLResponse)
async def get_other_pages(library_name: str):
    return HTMLResponse(open(f"html/library/theorems/{library_name}/index.html").read())


@app.get("/library/papers", response_class=HTMLResponse)
@app.get("/library/papers/index.html", response_class=HTMLResponse)
async def get_other_pages():
    return HTMLResponse(open("html/library/papers/index.html").read())


@app.get("/library/papers/{paper_name}.html", response_class=HTMLResponse)
async def get_other_pages(paper_name: str):
    return HTMLResponse(open(f"html/library/papers/{paper_name}/index.html").read())


@app.get("/contribute", response_class=HTMLResponse)
async def get_contribute_form():
    return HTMLResponse(open("html/contribute.html").read())


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
