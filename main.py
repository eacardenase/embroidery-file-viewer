from __future__ import annotations

from typing import Annotated
import os
import ast

from fastapi import FastAPI, HTTPException, Form, UploadFile
from fastapi.responses import FileResponse
import pyembroidery

app = FastAPI()

@app.get('/')
def home():
    return {"status": 200}
    
@app.post("/embroidery-items")
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

        print(hex_colors)

        if not os.path.exists(dst_directory_path):
            os.makedirs(dst_directory_path)
        
        dst_file_path = os.path.join(dst_directory_path, file_name)

        with open(dst_file_path, 'wb') as f:
            f.write(file_bytes)

        pattern = pyembroidery.read_dst(dst_file_path)
        png_file_path = os.path.join(images_directory_path, file_name.replace('.DST', '.png'))

        for hex_color in hex_colors:
            pattern.add_thread(pyembroidery.EmbThread.parse_string_color(f"#{hex_color}"))

        pattern.write_png(pattern, png_file_path)

        return FileResponse(png_file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))