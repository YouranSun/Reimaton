import pdfplumber
import os
from pdfplumber.page import Page

from typing import List

INT = r"(\d+)"
FLOAT_2P = r"(\d+\.\d\d)"

class BaseFile:
    def __init__(self):
        pass
    
    @property
    def extension(self):
        return os.path.splitext(self.path)[1]

    def load_info(self):
        pass

    def find_substring(self, pattern: str) -> bool:
        return pattern in self.text
    
    def find_subseq(self, pattern: str) -> bool:
        i = 0
        for c in self.text:
            if c == pattern[i]:
                i += 1
                if i == len(pattern):
                    return True
        return False

class PDFFile(BaseFile):
    def __init__(self, path):
        self.path = path
        self.is_loaded = False
        try:
            with pdfplumber.open(path) as file:
                self.pages = file.pages
                self.text = ""
                for page in self.pages:
                    self.text += page.extract_text()
            self.load_info()
        except Exception:
            return
        # self.text = ''.join([char for char in self.text if char not in string.whitespace])

from PIL import Image
import pytesseract
import cv2

import string

import numpy as np

# CHI_SIM_PATH = os.path.abspath('Tesseract-OCR\\tessdata\\chi_sim.traineddata')
# ENG_PATH = os.path.abspath('Tesseract-OCR\\tessdata\\eng.traineddata')

# pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\\tesseract.exe'
tessdata_dir = os.path.abspath('').replace('\\', '/')

class IMGFile(BaseFile):
    def __init__(self, path):
        # print(CHI_SIM_PATH)
        self.path = path
        self.is_loaded = False

        try:
            image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)  # 以灰度模式读取图片

            # 调整对比度
            alpha = 1.5  # 对比度系数
            beta = 0     # 亮度调整
            adjusted_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

            # 二值化处理
            _, adjusted_image = cv2.threshold(adjusted_image, 254, 255, cv2.THRESH_BINARY)

            # 保存处理后的图片

            # cv2.imwrite('temp.png', adjusted_image)

            self.img = adjusted_image
            self.text = pytesseract.image_to_string(self.img, lang='chi_sim+eng', config=f'--tessdata-dir {tessdata_dir}')
            self.text = ''.join([c for c in self.text if c not in string.whitespace])

            self.load_info()
        except Exception:
            return