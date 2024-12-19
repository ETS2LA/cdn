import traceback
import datetime
import fastapi
import zipfile
import random
import string
import json
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


def Start():
    global PATH
    PATH = str(PATH).replace("\\", "/")
    if PATH[-1] != "/":
        PATH += "/"
    for Author in DATASETS:
        for Dataset in DATASETS[Author]:
            FolderExists(Author, Dataset)
            FolderExists(Author, f"{Dataset}#IDs")


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


def GetDataset(Author, Dataset):
    try:
        if os.path.exists(f"{PATH}{Author}/{Dataset}"):
            with zipfile.ZipFile(f"{PATH}{Dataset}.zip", "w") as zip:
                for File in os.listdir(f"{PATH}{Author}/{Dataset}"):
                    if File.endswith(".png") or File.endswith(".jpg") or File.endswith(".jpeg") or File.endswith(".txt") or File.endswith(".json"):
                        zip.write(f"{PATH}{Author}/{Dataset}/{File}", File)
            return fastapi.responses.FileResponse(path=f"{PATH}{Dataset}.zip", filename=f"{Dataset} - {datetime.datetime.now().strftime('%d.%m.%Y %H-%M-%S')}.zip")
        else:
            return {"error": "Dataset or author not found."}
    except:
        print(RED + "Datasets - Error in function GetDataset." + NORMAL)
        traceback.print_exc()
        return {"error": "Dataset or author not found."}


def GetID(Author, Dataset):
    try:
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