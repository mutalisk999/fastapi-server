#!/usr/bin/env python
# encoding: utf-8

import io
import base64
import string
import random
from captcha.image import ImageCaptcha


def generate_random_string(gen_type: int = 1, size: int = 4):
    if gen_type == 1:
        choice = string.digits
    elif gen_type == 2:
        choice = string.ascii_letters
    else:
        choice = string.ascii_letters + string.digits
    return ''.join(random.choice(choice) for _ in range(size))


def get_image_captcha(captcha_code: str) -> bytes:
    ic = ImageCaptcha(width=100, height=40, font_sizes=(30,))
    image = ic.generate_image(captcha_code)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG")
    return img_bytes.getbuffer().tobytes()


def get_image_captcha_base64(captcha_code: str) -> str:
    bs = get_image_captcha(captcha_code)
    return "data:image/jpeg;base64," + base64.b64encode(bs).decode()
