# spoof_image.py

from PIL import Image, ImageOps
import random, os
import piexif

def spoof_image(filepath, output_folder, settings):
    image = Image.open(filepath).convert("RGB")
    width, height = image.size

    crop_px = settings.get("crop", 10)
    image = image.crop((crop_px, crop_px, width - crop_px, height - crop_px))

    delta = random.choice([-2, -1, 0, 1, 2])
    image = image.resize((width + delta, height + delta))

    pixels = image.load()
    noise_level = 0.003
    for i in range(image.width):
        for j in range(image.height):
            if random.random() < noise_level:
                r, g, b = pixels[i, j]
                pixels[i, j] = (
                    min(255, max(0, r + random.randint(-5, 5))),
                    min(255, max(0, g + random.randint(-5, 5))),
                    min(255, max(0, b + random.randint(-5, 5)))
                )

    if settings.get("flip"):
        image = ImageOps.mirror(image)

    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
    exif_bytes = piexif.dump(exif_dict)

    base = os.path.basename(filepath)
    name, _ = os.path.splitext(base)

    for i in range(settings.get("copies", 1)):
        out_path = os.path.join(output_folder, f"{name}_spoofed_{i+1}.jpg")
        image.save(out_path, "JPEG", quality=random.randint(94, 97), exif=exif_bytes)
