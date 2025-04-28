
---

# 📄 `/app/main.py`

```python
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import shutil, os, csv
from app.pdf_generator import generate_pdfs

app = FastAPI()

UPLOADS_DIR = 'uploads'
OUTPUTS_DIR = 'outputs'

@app.post("/generate")
async def generate(
    csv_file: UploadFile = File(...),
    images: list[UploadFile] = File(...),
    logo: UploadFile = File(None),
    template: str = Form('default'),
    merge: bool = Form(False)
):
    # Clean previous
    shutil.rmtree(UPLOADS_DIR, ignore_errors=True)
    shutil.rmtree(OUTPUTS_DIR, ignore_errors=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # Save CSV
    csv_path = os.path.join(UPLOADS_DIR, csv_file.filename)
    with open(csv_path, 'wb') as f:
        f.write(await csv_file.read())

    # Save Images
    image_paths = {}
    for img in images:
        path = os.path.join(UPLOADS_DIR, img.filename)
        with open(path, 'wb') as f:
            f.write(await img.read())
        image_paths[img.filename] = path

    # Save Logo
    logo_path = None
    if logo:
        logo_path = os.path.join(UPLOADS_DIR, logo.filename)
        with open(logo_path, 'wb') as f:
            f.write(await logo.read())

    # Parse CSV
    entries = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(row)

    pdf_files = generate_pdfs(entries, image_paths, logo_path, OUTPUTS_DIR, template, merge)

    if merge:
        return FileResponse(pdf_files[0], media_type='application/pdf', filename='All_Adverts.pdf')
    else:
        return FileResponse(pdf_files[0], media_type='application/zip', filename='adverts.zip')
