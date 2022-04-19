from PIL import Image, ImageDraw
from random import randint
import numpy as np


class ImageSizeError(Exception):
    def __init__(self, text):
        self.txt = text


def text_to_binary(text):
    return ''.join(format(ord(sym),'08b') for sym in text)


def binary_to_text(bin_str):
    return ''.join(chr(int(bin_str[i*8:i*8+8],2)) for i in range(len(bin_str)//8))


class SteganoImg():
    def __init__(self, image):
        self.path = image
        self.width = Image.open(image).width
        self.height = Image.open(image).height
        self.array = np.asarray(Image.open(image).getdata())

    def lsb_encrypt(self, text):
        text = text_to_binary(text + '$end')
        try:
            if len(text) > (self.width * self.height * 3):
                raise ImageSizeError('Слишком большой текст')
        except ValueError:
            pass
        else:
            index = 0
            for i in range(0, self.width * self.height):
                for j in range(0, 3):
                    if index < len(text):
                        self.array[i][j] = int(bin(self.array[i][j])[2:9] + text[index], 2)
                        index = index + 1

    def lsb_decrypt(self):
        last_bits = ''
        for pixel in self.array:
            for color in pixel:
                last_bits = last_bits + str(bin(color)[-1])
        text = binary_to_text(last_bits)
        return text[:text.find('$end')]

    def save_pic(self, name):
        arr = self.array.reshape(self.height, self.width, 3)
        img = Image.fromarray(arr.astype('uint8'), mode='RGB')
        img.save(name)

