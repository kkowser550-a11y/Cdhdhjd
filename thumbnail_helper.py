import os
import requests
from PIL import Image, ImageDraw, ImageOps
import io

def generate_music_thumbnail(thumbnail_url, output_path="thumb.png"):
    try:
        response = requests.get(thumbnail_url, timeout=10)
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        
        size = (500, 500)
        img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
        
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        
        output = Image.new("RGBA", size, (0, 0, 0, 0))
        output.paste(img, (0, 0), mask=mask)
        
        output.save(output_path, "PNG")
        return output_path
    except Exception as e:
        print(f"Thumbnail generation error: {e}")
        return None
