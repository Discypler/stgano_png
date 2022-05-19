from PIL import Image
from random import randint
import numpy as np


class ImageSizeError(Exception):
    def __init__(self, text):
        self.txt = text


def text_to_binary(text):
    return ''.join(format(ord(sym), '08b') for sym in text)


def binary_to_text(bin_str):
    return ''.join(chr(int(bin_str[i*8:i*8+8], 2)) for i in range(len(bin_str)//8))


class SteganoImg():
    def __init__(self, image):
        self.path = image
        self.width = Image.open(image).width
        self.height = Image.open(image).height
        self.array = np.asarray(Image.open(image).getdata())

    def lsb_encrypt(self, text, t):
        text = text_to_binary('%start' + text + '$end')
        try:
            if len(text) > (self.width * self.height * 3 * t):
                raise ImageSizeError('Текст слишком длинный')
        except ValueError:
            pass
        else:
            index = 0
            for i in range(0, self.width * self.height):
                for j in range(0, 3):
                    if index < len(text):
                        self.array[i][j] = int(bin(self.array[i][j])[2:-t] + text[index: index + t], 2)
                        index = index + t
                    else:
                        self.array[i][j] = int(bin(self.array[i][j])[2:-t] +
                                               ''.join([str(randint(0, 1)) for t in range(t)]), 2)

    def lsb_decrypt(self, t):
        last_bits = ''
        for i in range(0, self.width * self.height):
            for j in range(3):
                if len(bin(self.array[i][j])) - 2 < t:
                    last_bits = last_bits + '0' * (t - len(bin(self.array[i][j])) + 2) + str(bin(self.array[i][j])[2:])
                else:
                    last_bits = last_bits + str(bin(self.array[i][j])[-t:])
        text = binary_to_text(last_bits)
        return text[:text.find('$end')]

    def pvd_encrypt(self, text, t):
        text = text_to_binary('%start' + text + '$end')
        try:
            if len(text) > (self.width * self.height * 9 // 8 * t):
                raise ImageSizeError('Текст слишком длинный')
        except ValueError:
            pass
        else:
            index = 0
            for i in range(1, self.width * self.height - self.width * self.height % 3 - 1, 3):
                if self.array[i][1] >= 8:
                    self.array[i][1] = int(bin(self.array[i][1])[2:-t] + '0' * t, 2)
                else:
                    self.array[i][1] = 0
                if index < len(text):
                    for j in range(-1, 2):
                        for k in range(3):
                            if j != 0 and k != 1:
                                diff = abs(self.array[i + j][k] - self.array[i][1])
                                if diff >= 2**t:
                                    new_diff = int(bin(diff)[2:-t] + text[index: index + t], 2)
                                else:
                                    new_diff = int(text[index: index + t], 2)
                                new_value_1 = self.array[i][1] - new_diff
                                new_value_2 = self.array[i][1] + new_diff
                                if (abs(self.array[i + j][k] - new_value_1) <= abs(self.array[i + j][k] + new_value_2)
                                        and 0 <= new_value_1 <= 255):
                                    self.array[i + j][k] = new_value_1
                                else:
                                    self.array[i + j][k] = new_value_2
                                index = index + t

    def pvd_decrypt(self, t):
        last_bits = ''
        for i in range(1, self.width * self.height - self.width * self.height % 3 - 1, 3):
            for j in range(-1, 2):
                for k in range(3):
                    if j != 0 and k != 1:
                        diff = abs(self.array[i + j][k] - self.array[i][1])
                        if len(bin(diff)) - 2 < t:
                            last_bits = last_bits + '0' * (t - len(bin(diff)) + 2) + str(bin(diff)[2:])
                        else:
                            last_bits = last_bits + str(bin(abs(self.array[i + j][k] - self.array[i][1]))[-t:])
        text = binary_to_text(last_bits)
        return text[:text.find('$end')]

    def save_pic(self, name):
        arr = self.array.reshape(self.height, self.width, 3)
        img = Image.fromarray(arr.astype('uint8'), mode='RGB')
        img.save(name)
