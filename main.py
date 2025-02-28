from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
import translations
import datasets
import frontend
import asyncio
import fastapi
import uvicorn
import models

translations.Start()
datasets.Start()
frontend.Start()
models.Start()

DEVELOPMENT = False
SPEEDLIMIT = 5000 # 5mb/s

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return HTMLResponse(content="<p>Hi! I don't know why you're here, but if you are looking for the source then check out the <a href='https://github.com/ETS2LA/cdn'>github repository</a>.</p>")

# MARK: Translations

@app.get('/translations')
async def return_translations():
    if translations.IsAvailable():
        content_length = str(translations.GetSize())
        file_path = f'./translations/translations.zip'
        return FileResponse(path=file_path, media_type="application/octet-stream", headers={"content-length": content_length})
    else:
        return {'error': 'Translations on the server are currently being updated.'}

# MARK: UI

@app.get('/frontend')
async def return_frontend():
    if frontend.IsAvailable():
        content_length = str(frontend.GetSize())
        file_path = f'./frontend/frontend.zip'
        return FileResponse(path=file_path, media_type="application/octet-stream", headers={"content-length": content_length})
    else:
        return {'error': 'Frontend on the server is currently being updated.'}

# MARK: Datasets

@app.post('/datasets/{author}/{dataset}/upload/{id}')
async def upload_to_dataset(author: str, dataset: str, id, files: list[UploadFile] = File(...)):
    if datasets.IsAvailable(author, dataset):
        return datasets.Upload(author, dataset, id, files)
    else:
        return {'error': 'Dataset or author not found.'}

@app.get('/datasets/{author}/{dataset}')
def read_dataset_details(author: str, dataset: str):
    if datasets.IsAvailable(author, dataset):
        return datasets.GetDatasetDetails(author, dataset)
    else:
        return {'error': 'Dataset or author not found.'}


@app.get('/datasets/{author}/{dataset}/get-id')
def get_dataset_id(author: str, dataset: str):
    if datasets.IsAvailable(author, dataset):
        return datasets.GetID(author, dataset)
    else:
        return {'error': 'Dataset or author not found.'}


@app.get('/datasets/{author}/{dataset}/{file}')
async def read_dataset_file(author: str, dataset: str, file: str):
    if datasets.IsAvailable(author, dataset):
        return datasets.GetDatasetFile(author, dataset, file)
    else:
        return {'error': 'Dataset or author not found.'}


@app.get('/datasets/{author}/{dataset}/delete/{id}')
async def get_dataset_id(author: str, dataset: str, id):
    if datasets.IsAvailable(author, dataset):
        return datasets.DeleteByID(author, dataset, id)
    else:
        return {'error': 'Dataset or author not found.'}

# MARK: Models

@app.get('/models/{author}/{model}/{folder:path}/download')
def return_model(author: str, model: str, folder: str):
    if models.IsAvailable(author, model, folder):
        content_length = str(models.GetSize(author, model, folder))
        file_path = f'./models/{author}/{model}/{folder}/{models.GetName(author, model, folder)}'
        return FileResponse(path=file_path, media_type="application/octet-stream", headers={"content-length": content_length})
    else:
        return {'error': 'Model or author not found.'}

@app.get('/models/{author}/{model}/{folder:path}')
def return_model(author: str, model: str, folder: str):
    print(folder)
    if models.IsAvailable(author, model, folder):
        return {'success': models.GetName(author, model, folder)}
    else:
        return {'error': 'Model or author not found.'}

# MARK: Run    
    
@app.get('/heartbeat')
def heartbeat():
    return {'status': 'ok'}

if __name__ == '__main__':
    if DEVELOPMENT:
        print("WARNING: Running on localhost")
        uvicorn.run(app, host='localhost', port=8000)
    else:
        uvicorn.run(app, host='0.0.0.0', port=8000)