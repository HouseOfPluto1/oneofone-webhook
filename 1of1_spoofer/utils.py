# utils.py

import os, zipfile, shutil
import magic
from spoof_image import spoof_image
from spoof_video import spoof_video

def valid_file_type(filename):
    return filename.lower().endswith((".jpg", ".jpeg", ".png", ".mp4", ".mov", ".heic", ".webp"))

def spoof_and_zip_files(files, folder, settings):
    output_dir = os.path.join(folder, "spoofed")
    os.makedirs(output_dir, exist_ok=True)

    for file in files:
        kind = magic.from_file(file, mime=True)
        if "image" in kind:
            spoof_image(file, output_dir, settings)
        elif "video" in kind:
            spoof_video(file, output_dir)

    zip_path = os.path.join(folder, "spoofed.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        for f in os.listdir(output_dir):
            zf.write(os.path.join(output_dir, f), f)
    return zip_path

def clean_user_temp_folder(user_id):
    shutil.rmtree(f"temp/{user_id}", ignore_errors=True)

def convert_if_needed(filepath):
    # Optional: add .heic/.webp conversion using Pillow
    return filepath
