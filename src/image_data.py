from pydantic import BaseModel
import numpy as np
from PIL import Image, ImageChops
import io
import base64
import re

from tools.constants import MNIST_SCALE


class ImageModel(BaseModel):
    image: str

    def process_image(self) -> np.array:
        byte_image = self.__decode_image()

        image = Image.open(io.BytesIO(byte_image)).convert('L')
        image = self.__replace_digit_to_center(image)
        result = self.__normalize_image(image)

        return result

    def __decode_image(self):
        image_data = re.sub('^data:image/.+;base64,', '', self.image)
        byte_data = base64.b64decode(image_data)
        return byte_data

    def __replace_digit_to_center(self, image):
        bbox = ImageChops.invert(image).getbbox()

        cropped_img = image.crop(bbox)

        width, height = cropped_img.size
        scale = min(MNIST_SCALE / width, MNIST_SCALE / height)

        new_width = int(width * scale)
        new_height = int(height * scale)
        resized_img = cropped_img.resize((new_width, new_height))

        new_image = Image.new("L", (MNIST_SCALE, MNIST_SCALE), 255)

        x_center = (MNIST_SCALE - new_width) // 2
        y_center = (MNIST_SCALE - new_height) // 2

        new_image.paste(resized_img, (x_center, y_center))

        return new_image

    def __normalize_image(self, image: Image) -> np.array:
        image_array = np.array(image)
        image_array = 255 - image_array

        image_array = image_array.reshape((1, 28 * 28))
        image_array = image_array.astype('float32') / 255

        return image_array
