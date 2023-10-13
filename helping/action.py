from PIL import Image
from io import BytesIO
import openai

def generate_variation(image_temp, size="1024x1024"):
    with Image.open(image_temp.name) as image_pil:
        byte_stream = BytesIO()
        image_pil.save(byte_stream, format='PNG')
        byte_array = byte_stream.getvalue()
    response = openai.Image.create_variation(
        image=byte_array,
        n=1,
        size=size
    )
    image_url = response['data'][0]['url']
    response_data = {
        "message": "image variation created successfully",
        "image_url": image_url
    }
    return response_data

def generate_image(prompt, size="1024x1024"):
    response = openai.Image.create(prompt=prompt, n=1, size=size)
    image_url = response['data'][0]['url']
    response_data = {
        "message": "image created successfully",
        "image_url": image_url
    }
    return response_data

def edit_image(prompt, image_temp, mask_temp, size="1024x1024"):
    with Image.open(image_temp.name) as image_pil:
        if mask_temp:
            with Image.open(mask_temp.name) as mask_pil:
                if image_pil.size != mask_pil.size:
                    return 'Image and mask dimensions must match'
        if mask_temp:
            response = openai.Image.create_edit(
                image=open(image_temp.name, "rb"),
                mask=open(mask_temp.name, "rb"),
                prompt=prompt,
                n=1,
                size=size
            )
        else:
            response = openai.Image.create(prompt=prompt, n=1, size=size)
        image_url = response['data'][0]['url']
        response_data = {
            "message": "image edited successfully",
            "image_url": image_url
        }
        return response_data