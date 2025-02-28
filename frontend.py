import threading
import traceback
import requests
import time
import os


RED = "\033[91m"
DARK_GREY = "\033[90m"
NORMAL = "\033[0m"


PATH = "./frontend"
REPOSITORY = "https://github.com/ETS2LA/frontend/archive/refs/heads/main.zip"

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
            FolderExists()
            Response = requests.get(REPOSITORY, stream=True)
            with open(f"{PATH}frontend_temp.zip", "wb") as FrontendFile:
                ChunkSize = 1024
                for Data in Response.iter_content(chunk_size=ChunkSize):
                    FrontendFile.write(Data)
        except:
            pass
        if os.path.exists(f"{PATH}frontend_temp.zip"):
            try:
                os.remove(f"{PATH}frontend.zip")
            except:
                pass
            try:
                os.rename(f"{PATH}frontend_temp.zip", f"{PATH}frontend.zip")
            except:
                pass
        if os.path.exists(f"{PATH}frontend.zip"):
            time.sleep(UPDATE_CHECK_RATE_HOURS * 3600)
        else:
            time.sleep(1)


def IsAvailable():
    try:
        if os.path.exists(f"{PATH}frontend.zip"):
            return True
        else:
            return False
    except:
        print(RED + "Frontend - Error in function IsAvailable." + NORMAL)
        traceback.print_exc()
        return False


def GetSize():
    try:
        if IsAvailable():
            return os.path.getsize(f"{PATH}frontend.zip")
        else:
            return 1
    except:
        print(RED + "Frontend - Error in function GetSize." + NORMAL)
        traceback.print_exc()


def FolderExists():
    try:
        if os.path.exists(f"{PATH}") == False:
            os.makedirs(f"{PATH}")
    except:
        print(RED + "Frontend - Error in function FolderExists." + NORMAL)
        traceback.print_exc()