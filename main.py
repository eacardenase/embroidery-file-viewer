from __future__ import annotations

from typing import Annotated
import ast

from fastapi import FastAPI, HTTPException, Form, UploadFile
from fastapi.responses import FileResponse
from typing import List, Union
from pydantic import BaseModel, Field
import pyembroidery

import json
import os

app = FastAPI()

class Extras(BaseModel):
    name: str
    ST: str
    CO: str
    X_positive: str = Field(..., alias='+X')
    X_negative: str = Field(..., alias='-X')
    Y_positive: str = Field(..., alias='+Y')
    Y_negative: str = Field(..., alias='-Y')
    AX: str
    AY: str
    MX: str
    MY: str
    PD: str


class EmbroideryFileData(BaseModel):
    threadlist: List
    stitches: List[List[Union[int, str]]]
    extras: Extras

class EmbroideryData(BaseModel):
    name: str
    colors: list[str]
    embroidery_file_data: EmbroideryFileData 

@app.get("/embroidery-items/")
async def read_embroidery_data():
    try:
        with open("./embroidery_files/embroidery_data.json", "r") as file:
            pattern = pyembroidery.read_json(file)
            directory_path = "./embroidery_images/"

            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            file_path = os.path.join(directory_path, "embroidery_data.png")

            pattern.write_png(pattern, file_path)

        return FileResponse(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Error decoding JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embroidery-items/")
async def create_file(
    embroidery_data: EmbroideryData,
):
    try:
        item_data = embroidery_data.embroidery_file_data.dict()
        directory_path = "./embroidery_files/"
        
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        
        file_path = os.path.join(directory_path, "embroidery_data.json")
        
        with open(file_path, 'w') as f:
            json.dump(item_data, f, indent=4)

        return {"message": "Embroidery data saved successfully!", "filename": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/embroidery-items-2")
async def create_file(
    file: UploadFile,
    colors: Annotated[str, Form()]
):
    try:
        dst_directory_path = "./embroidery_files/"
        images_directory_path = "./embroidery_images/"

        hex_colors = ast.literal_eval(colors)

        file_name = file.filename

        file_bytes = await file.read()

        if not os.path.exists(dst_directory_path):
            os.makedirs(dst_directory_path)
        
        dst_file_path = os.path.join(dst_directory_path, file_name)

        with open(dst_file_path, 'wb') as f:
            f.write(file_bytes)

        pattern = pyembroidery.read_dst(dst_file_path)

        png_file_path = os.path.join(images_directory_path, file_name.replace('.DST', '.png'))

        for hex_color in hex_colors:
            pattern.add_thread(pyembroidery.EmbThread.parse_string_color(hex_color))

        pattern.write_png(pattern, png_file_path)

        return FileResponse(png_file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))