import os
import ast
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import pyembroidery

app = FastAPI()

# Ensure the embroidery_images directory exists before mounting
images_directory_path = "./embroidery_images/"
if not os.path.exists(images_directory_path):
    os.makedirs(images_directory_path)

# Serve the embroidery_images directory at the /embroidery_images URL path
app.mount("/embroidery_images", StaticFiles(directory=images_directory_path), name="embroidery_images")

@app.get('/')
def home():
    return {"status": 200}

@app.post("/embroidery-items")
async def create_file(
    file: UploadFile,
    colors: Optional[str] = Form(None)  # Allow colors to be optional
):
    try:
        dst_directory_path = "./embroidery_files/"
        images_directory_path = "./embroidery_images/"

        # Ensure the embroidery_files directory exists
        if not os.path.exists(dst_directory_path):
            os.makedirs(dst_directory_path)

        # Convert colors to a list, default to an empty list if not provided
        hex_colors: List[str] = ast.literal_eval(colors) if colors else []

        file_name = file.filename
        file_bytes = await file.read()

        dst_file_path = os.path.join(dst_directory_path, file_name)

        with open(dst_file_path, 'wb') as f:
            f.write(file_bytes)

        pattern = pyembroidery.read_dst(dst_file_path)
        png_file_name = file_name.replace('.DST', '.png')
        png_file_path = os.path.join(images_directory_path, png_file_name)

        # Add colors to the pattern if provided
        for hex_color in hex_colors:
            pattern.add_thread(pyembroidery.EmbThread.parse_string_color(hex_color))

        pattern.write_png(pattern, png_file_path)

        # Construct the URL path to return in the response
        url_path = f"/embroidery_images/{png_file_name}"

        return JSONResponse(content={"url": url_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
