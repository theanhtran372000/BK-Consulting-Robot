import base64
from io import BytesIO
from PIL import Image

# Convert Image to Base64 
def im_2_b64(image):
    buff = BytesIO()
    image.save(buff, format="JPEG")
    img_str = base64.b64encode(buff.getvalue())
    return img_str.decode('utf-8')

# Convert Base64 to Image
def b64_2_img(data):
    buff = BytesIO(base64.b64decode(data))
    return Image.open(buff)

image = Image.open('save/tmps/face.jpg')
img_str = im_2_b64(image)

new_image = b64_2_img(img_str)
new_image.save('save/tmps/decode.jpg')

print('String: ' + img_str)
print('Type: ' + str(type(img_str)))