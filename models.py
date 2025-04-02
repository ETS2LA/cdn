from bs4 import BeautifulSoup
import threading
import traceback
import datetime
import requests
import time
import os


RED = "\033[91m"
DARK_GREY = "\033[90m"
NORMAL = "\033[0m"


# MODELS = {Huggingface User: {Repository: Folder which contains the model file}}
MODELS = {
    "OleFranz": {
        "End-To-End": "model",
        "NavigationDetectionAI": "model",
        "TrafficLightDetectionAI": "model",
        "RouteAdvisorClassification": "model",
        "MLVSS": "models/mapping",
        "AdaptiveCruiseControl": "model"
    }
}

PATH = "./models"

UPDATE_CHECK_RATE_HOURS = 24


def Start():
    global PATH
    global UPDATING
    PATH = str(PATH).replace("\\", "/")
    if PATH[-1] != "/":
        PATH += "/"
    UPDATING = []
    threading.Thread(target=RunThread, daemon=True).start()


def RunThread():
    while True:
        try:
            for Author in MODELS:
                for Model in MODELS[Author]:
                    try:
                        Response = requests.get("https://huggingface.co/", timeout=5)
                        Response = Response.status_code
                    except requests.exceptions.RequestException:
                        Response = None

                    if Response == 200:
                        print(DARK_GREY + f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {Author}/{Model}/{MODELS[Author][Model]}] " + NORMAL + "Checking for model updates...")

                        Url = f'https://huggingface.co/{Author}/{Model}/tree/main/{MODELS[Author][Model]}'
                        Response = requests.get(Url)
                        Soup = BeautifulSoup(Response.content, 'html.parser')

                        LatestModel = None
                        for Link in Soup.find_all("a", href=True):
                            HREF = Link["href"]
                            if HREF.startswith(f'/{Author}/{Model}/blob/main/{MODELS[Author][Model]}'):
                                LatestModel = HREF.split("/")[-1]
                                break

                        CurrentModel = GetName(Author, Model, MODELS[Author][Model])

                        if str(LatestModel) != str(CurrentModel):
                            UPDATING.append(f"{Author}/{Model}/{MODELS[Author][Model]}")
                            print(DARK_GREY + f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {Author}/{Model}/{MODELS[Author][Model]}] " + NORMAL + "Updating the model...")
                            Delete(Author, Model, MODELS[Author][Model])
                            Response = requests.get(f'https://huggingface.co/{Author}/{Model}/resolve/main/{MODELS[Author][Model]}/{LatestModel}?download=true', stream=True)
                            with open(os.path.join(f"{PATH}{Author}/{Model}/{MODELS[Author][Model]}", f"{LatestModel}"), "wb") as ModelFile:
                                ChunkSize = 1024
                                for Data in Response.iter_content(chunk_size=ChunkSize):
                                    ModelFile.write(Data)
                            print(DARK_GREY + f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {Author}/{Model}/{MODELS[Author][Model]}] " + NORMAL + "Successfully updated the model!")
                            UPDATING.remove(f"{Author}/{Model}/{MODELS[Author][Model]}")
                        else:
                            print(DARK_GREY + f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {Author}/{Model}/{MODELS[Author][Model]}] " + NORMAL + "No model updates available!")
        except:
            print(RED + "Models - Error in function RunThread:" + NORMAL)
            traceback.print_exc()
        time.sleep(UPDATE_CHECK_RATE_HOURS * 3600)


def IsAvailable(Author, Model, Folder):
    try:
        if os.path.exists(f'./models/{Author}/{Model}/{Folder}') and os.listdir(f'./models/{Author}/{Model}/{Folder}') != [] and f"{Author}/{Model}/{Folder}" not in str(UPDATING):
            return True
        else:
            return False
    except:
        print(RED + "Models - Error in function IsAvailable." + NORMAL)


def GetSize(Author, Model, Folder):
    try:
        if IsAvailable(Author, Model, Folder):
            return os.path.getsize(f'./models/{Author}/{Model}/{Folder}/{GetName(Author, Model, Folder)}')
        else:
            return 1
    except:
        print(RED + "Models - Error in function GetSize." + NORMAL)
        traceback.print_exc()


def FolderExists(Author, Model, Folder):
    try:
        if os.path.exists(f"{PATH}{Author}/{Model}/{Folder}") == False:
            os.makedirs(f"{PATH}{Author}/{Model}/{Folder}")
    except:
        print(RED + "Models - Error in function FolderExists." + NORMAL)
        traceback.print_exc()


def GetName(Author, Model, Folder):
    try:
        FolderExists(Author, Model, Folder)
        for File in os.listdir(f"{PATH}{Author}/{Model}/{Folder}"):
            if File.endswith(".pt"):
                return File
        return None
    except:
        print(RED + "Models - Error in function GetName." + NORMAL)
        traceback.print_exc()


def Delete(Author, Model, Folder):
    try:
        FolderExists(Author, Model, Folder)
        for File in os.listdir(f"{PATH}{Author}/{Model}/{Folder}"):
            if File.endswith(".pt"):
                os.remove(os.path.join(f"{PATH}{Author}/{Model}/{Folder}", File))
    except:
        print(RED + "Models - Error in function Delete." + NORMAL)
        traceback.print_exc()