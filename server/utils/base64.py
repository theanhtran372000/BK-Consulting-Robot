import base64
from io import BytesIO
from PIL import Image

# Convert PIL Image to Base64 
def image_to_base64(pil_image):
    buff = BytesIO()
    pil_image.save(buff, format="JPEG")
    img_str = base64.b64encode(buff.getvalue())
    return img_str.decode('utf-8')

# Convert Base64 to Image
def base64_to_image(b64_str):
    buff = BytesIO(base64.b64decode(b64_str))
    return Image.open(buff)