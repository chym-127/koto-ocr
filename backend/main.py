from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from utils import save_upload_file_tmp
from image_tools import remove_image_bg
from pathlib import Path
import os



ocr = PaddleOCR(use_angle_cls=True, lang="ch",use_gpu=False)

MAX_TASK_COUNT = 2
CURRENT_TASK_COUNT = 0


app = FastAPI()
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def resp(message:str="操作成功",data:any=None,code:int=0):
    return {
        "message": message,
        "data": data,
        "code": code,
    }


@app.get("/ping")
def root():
    return resp()


@app.post("/ocr/text")
def ocr(
    file: UploadFile = File(description="A file read as UploadFile"),
):
    global CURRENT_TASK_COUNT,MAX_TASK_COUNT
    if CURRENT_TASK_COUNT > MAX_TASK_COUNT:
        return resp("已达到最大任务数，请稍后再试",None,100)
    CURRENT_TASK_COUNT += 1
    try:
        contents = file.file.read()
        result = ocr.ocr(contents, cls=True)
        arr = []
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                item = {
                    "content": line[1][0],
                    "rect": line[0]
                }
                arr.append(item)
        return resp("操作成功", arr,0)
    except Exception as e:
        print(e)
        return resp("操作失败",None,100)
    finally:
        CURRENT_TASK_COUNT -= 1
        file.file.close()



@app.post("/image/rm-bg")
def image_remove_bg(
    file: UploadFile = File(description="Image File"),
):
    global CURRENT_TASK_COUNT,MAX_TASK_COUNT
    if CURRENT_TASK_COUNT > MAX_TASK_COUNT:
        return resp("已达到最大任务数，请稍后再试",None,100)
    CURRENT_TASK_COUNT += 1
    tmp_path = None
    try:
        tmp_path = save_upload_file_tmp(file)
        data = remove_image_bg(tmp_path)
        return FileResponse(data['rgba'])
    except Exception as e:
        print(e)
        return resp("操作失败",None,100)
    finally:
        CURRENT_TASK_COUNT -= 1
        if tmp_path is not None:
            tmp_path.unlink()  # Delete the temp file
        file.file.close()    