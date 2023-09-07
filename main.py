from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
import time

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


def ocr_text(data:any):
    arr = []
    for idx in range(len(data)):
        res = data[idx]
        for line in res:
            item = {
                "content": line[1][0],
                "rect": line[0]
            }
            arr.append(item)
    return arr

@app.get("/ping")
def root():
    return {"message": "ok"}


@app.post("/ocr/text")
def create_upload_file(
    file: UploadFile = File(description="A file read as UploadFile"),
):
    global CURRENT_TASK_COUNT,MAX_TASK_COUNT
    print("CURRENT_TASK_COUNT",CURRENT_TASK_COUNT)
    if CURRENT_TASK_COUNT > MAX_TASK_COUNT:
        return resp("已达到最大任务数，请稍后再试",None,100)
    CURRENT_TASK_COUNT += 1
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang="ch",use_gpu=False)
        contents = file.file.read()
        result = ocr.ocr(contents, cls=True)
        return resp("操作成功", ocr_text(result),0)
    except Exception as e:
        print(e)
        return resp("操作失败",None,100)
    finally:
        CURRENT_TASK_COUNT -= 1
        file.file.close()
