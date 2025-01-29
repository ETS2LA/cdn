import threading
import traceback
import datetime
import fastapi
import random
import string
import json
import time
import os


RED = "\033[91m"
DARK_GREY = "\033[90m"
NORMAL = "\033[0m"


DATASETS = {
    "Glas42": {
        "End-To-End"
    }
}

PATH = "./datasets"

MAX_STORAGE_SIZE = 25 * 1000 * 1000 * 1000 # 25GB


def Start():
    global PATH
    PATH = str(PATH).replace("\\", "/")
    if PATH[-1] != "/":
        PATH += "/"
    for Author in DATASETS:
        for Dataset in DATASETS[Author]:
            FolderExists(Author, Dataset)
            FolderExists(Author, f"{Dataset}#IDs")
    global StorageUsed
    StorageUsed = 0
    for Author in os.listdir(PATH):
        for Dataset in os.listdir(f"{PATH}{Author}"):
            if os.path.exists(f"{PATH}{Author}/{Dataset}"):
                for File in os.listdir(f"{PATH}{Author}/{Dataset}"):
                    StorageUsed += os.path.getsize(f"{PATH}{Author}/{Dataset}/{File}")
    threading.Thread(target=CheckUsedStorageThread, daemon=True).start()


def IsAvailable(Author, Dataset):
    try:
        if os.path.exists(f"./datasets/{Author}/{Dataset}"):
            return True
        else:
            return False
    except:
        print(RED + "Datasets - Error in function IsAvailable." + NORMAL)
        traceback.print_exc()
        return False


def GetDatasetDetails(Author, Dataset):
    try:
        return {"success": os.listdir(f"{PATH}{Author}/{Dataset}")}
    except:
        print(RED + "Datasets - Error in function GetDatasetDetails." + NORMAL)
        traceback.print_exc()
        return {"error": "Dataset or author not found."}


def GetDatasetFile(Author, Dataset, File):
    try:
        if os.path.exists(f"{PATH}{Author}/{Dataset}/{File}"):
            if File.endswith(".png") or File.endswith(".jpg") or File.endswith(".jpeg"):
                return fastapi.responses.FileResponse(f"{PATH}{Author}/{Dataset}/{File}")
            elif File.endswith(".txt"):
                with open(f"{PATH}{Author}/{Dataset}/{File}", "r") as File:
                    return {"success": File.read()}
            elif File.endswith(".json"):
                with open(f"{PATH}{Author}/{Dataset}/{File}", "r") as File:
                    return {"success": json.load(File)}
        else:
            return {"error": "File, dataset or author not found."}
    except:
        print(RED + "Datasets - Error in function GetDatasetFile." + NORMAL)
        traceback.print_exc()
        return {"error": "File, dataset or author not found."}


def GetID(Author, Dataset):
    try:
        if EnoughStorageLeft() == False:
            return {"error": "Server storage is full."}
        if os.path.exists(f"{PATH}{Author}/{Dataset}"):
            PossibleCharacters = str(string.ascii_letters + string.digits + "-_")
            ID = str("".join(random.choices(PossibleCharacters, k=15)))
            if os.path.exists(f"{PATH}{Author}/{Dataset}#IDs/{ID}.txt") == False:
                with open(f"{PATH}{Author}/{Dataset}#IDs/{ID}.txt", "w") as File:
                    File.write("")
            return {"success": ID}
        else:
            return {"error": "Dataset or author not found."}
    except:
        print(RED + "Datasets - Error in function GetDatasetID." + NORMAL)
        traceback.print_exc()
        return {"error": "Dataset or author not found."}


def DeleteByID(Author, Dataset, ID):
    try:
        if os.path.exists(f"{PATH}{Author}/{Dataset}"):
            if os.path.exists(f"{PATH}{Author}/{Dataset}#IDs/{ID}.txt"):
                with open(f"{PATH}{Author}/{Dataset}#IDs/{ID}.txt", "r") as File:
                    Data = str(File.read())
                    if Data.endswith(";"):
                        Data = Data[:-1]
                    Data = Data.replace("\n", "").split(";")
                for File in os.listdir(f"{PATH}{Author}/{Dataset}"):
                    if File.endswith(".png") or File.endswith(".jpg") or File.endswith(".jpeg") or File.endswith(".txt") or File.endswith(".json"):
                        if File in Data:
                            try:
                                os.remove(f"{PATH}{Author}/{Dataset}/{File}")
                            except:
                                pass
                try:
                    os.remove(f"{PATH}{Author}/{Dataset}#IDs/{ID}.txt")
                except:
                    pass
                return {"success": "All data uploaded using this ID has been deleted."}
            else:
                return {"success": "No data was uploaded using this ID."}
        else:
            return {"error": "Dataset or author not found."}
    except:
        print(RED + "Datasets - Error in function DeleteByID." + NORMAL)
        traceback.print_exc()
        return {"error": "Dataset or author not found."}


def Upload(Author, Dataset, ID, Files):
    try:
        if EnoughStorageLeft() == False:
            return {"error": "Server storage is full."}
        if os.path.exists(f"{PATH}{Author}/{Dataset}"):
            for File in Files:
                with open(f"{PATH}{Author}/{Dataset}#IDs/{ID}.txt", "a") as F:
                    F.write(File.filename + ";")
                FileExtension = str(File.filename).split('.')[-1]
                if FileExtension == "png" or FileExtension == "jpg" or FileExtension == "jpeg":
                    with open(f"{PATH}{Author}/{Dataset}/{File.filename}", "wb") as F:
                        F.write(File.file.read())
                elif FileExtension == "txt":
                    with open(f"{PATH}{Author}/{Dataset}/{File.filename}", "w") as F:
                        F.write(File.file.read().decode('utf-8'))
                elif FileExtension == "json":
                    with open(f"{PATH}{Author}/{Dataset}/{File.filename}", "w") as F:
                        F.write(json.dumps(json.load(File.file), indent=4))
            return {"success": "Saved!"}
        else:
            return {"error": "Dataset or author not found."}
    except:
        print(RED + "Datasets - Error in function Upload." + NORMAL)
        traceback.print_exc()
        return {"error": "Dataset or author not found."}


def FolderExists(Author, Dataset):
    try:
        if os.path.exists(f"{PATH}{Author}/{Dataset}") == False:
            os.makedirs(f"{PATH}{Author}/{Dataset}")
    except:
        print(RED + "Datasets - Error in function FolderExists." + NORMAL)
        traceback.print_exc()


def EnoughStorageLeft():
    try:
        return StorageUsed < MAX_STORAGE_SIZE
    except:
        print(RED + "Datasets - Error in function EnoughStorageLeft." + NORMAL)
        traceback.print_exc()
        return False


def ClearStorage():
    try:
        def ClearStorageThread():
            try:
                global StorageUsed
                AllFiles = []
                for Author in os.listdir(PATH):
                    for Dataset in os.listdir(f"{PATH}{Author}"):
                        if os.path.exists(f"{PATH}{Author}/{Dataset}") and "#IDs" not in Dataset:
                            for File in os.listdir(f"{PATH}{Author}/{Dataset}"):
                                if File.endswith(".png") or File.endswith(".jpg") or File.endswith(".jpeg"):
                                    AllFiles.append([f"{PATH}{Author}/{Dataset}/{File}", os.path.getsize(f"{PATH}{Author}/{Dataset}/{File}"), os.path.getmtime(f"{PATH}{Author}/{Dataset}/{File}")])
                AllFiles.sort(key=lambda x: x[2], reverse=True)
                for File in AllFiles:
                    Path, Size, Time = File
                    if StorageUsed - Size > MAX_STORAGE_SIZE:
                        Success = True
                        try:
                            if os.path.exists(Path):
                                os.remove(Path)
                        except: Success = False
                        try: 
                            if os.path.exists(Path.replace(".png", ".txt").replace(".jpg", ".txt").replace(".jpeg", ".txt")):
                                os.remove(Path.replace(".png", ".txt").replace(".jpg", ".txt").replace(".jpeg", ".txt"))
                        except: Success = False
                        try:
                            if os.path.exists(Path.replace(".png", ".json").replace(".jpg", ".json").replace(".jpeg", ".json")):
                                os.remove(Path.replace(".png", ".json").replace(".jpg", ".json").replace(".jpeg", ".json"))
                        except: Success = False
                        if Success:
                            StorageUsed -= Size
                    else:
                        break
            except:
                print(RED + "Datasets - Error in function ClearStorageThread." + NORMAL)
                traceback.print_exc()
        threading.Thread(target=ClearStorageThread, daemon=True).start()
    except:
        print(RED + "Datasets - Error in function ClearStorage." + NORMAL)
        traceback.print_exc()


def CheckUsedStorageThread():
    try:
        global StorageUsed
        LastFiles = ""
        for Author in os.listdir(PATH):
            for Dataset in os.listdir(f"{PATH}{Author}"):
                if os.path.exists(f"{PATH}{Author}/{Dataset}"):
                    LastFiles += f"#{len(os.listdir(f'{PATH}{Author}/{Dataset}'))}"
        while True:
            while True:
                time.sleep(60)
                Files = ""
                for Author in os.listdir(PATH):
                    for Dataset in os.listdir(f"{PATH}{Author}"):
                        if os.path.exists(f"{PATH}{Author}/{Dataset}"):
                            Files += f"#{len(os.listdir(f'{PATH}{Author}/{Dataset}'))}"
                if Files != LastFiles:
                    LastFiles = Files
                    break
            TempStorageUsed = 0
            for Author in os.listdir(PATH):
                for Dataset in os.listdir(f"{PATH}{Author}"):
                    if os.path.exists(f"{PATH}{Author}/{Dataset}"):
                        for File in os.listdir(f"{PATH}{Author}/{Dataset}"):
                            TempStorageUsed += os.path.getsize(f"{PATH}{Author}/{Dataset}/{File}")
            StorageUsed = TempStorageUsed
            if StorageUsed > MAX_STORAGE_SIZE:
                ClearStorage()
    except:
        print(RED + "Datasets - Error in function CheckAvailableStorageSize." + NORMAL)
        traceback.print_exc()