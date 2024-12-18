from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi import UploadFile, File
import fastapi
import uvicorn

import datasets
datasets.Start()


DEVELOPMENT = True


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


@app.get('/datasets/{author}/{dataset}/download')
async def read_dataset(author: str, dataset: str):
    if datasets.IsAvailable(author, dataset):
        return datasets.GetDataset(author, dataset)
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
    
    
@app.get('/heartbeat')
def heartbeat():
    return {'status': 'ok'}

if __name__ == '__main__':
    if DEVELOPMENT:
        print("WARNING: Running on localhost")
        uvicorn.run(app, host='localhost', port=8000)
    else:
        uvicorn.run(app, host='0.0.0.0', port=8000)