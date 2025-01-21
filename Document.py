import re
from typing import List
from FileExtracter import PDFFile, IMGFile, FLOAT_2P, INT
from ErrorMessage import LOAD_ERROR, FAPIAO_NO_TITLE, FAPIAO_NO_SHUIHAO, FAPIAO_NO_SEAL

GOUMAIFANG_MINGCHENG = "香港中文大学（深圳）"
GOUMAIFANG_MINGCHENG_OCR = "香港中文大学(深圳)"
NASHUIREN_SHIBIEHAO = "12440300066312613F"
QUANGUOTONGYIFAPIAO_JIANZHIZHANG = "税务局"

FAPIAO_AMOUNT = r'[（(]小写[)）]\s*[¥￥]\s*' + FLOAT_2P
FLIGHT_INFO_AMOUNT = r'[¥￥]\s*' + INT
COMBINED_AMOUNT = r'CNY\s*' + FLOAT_2P
XINGCHENGDAN_AMOUNT = r"合计：\s*" + FLOAT_2P + r"元"

class Fapiao(PDFFile):
    has_title: bool = False
    has_shuihao: bool = False
    has_seal: bool = False

    total_amount: float = None
    extra_amount: float = None

    def load_info(self):
        if self.text is None:
            return

        self.has_title = self.find_substring(GOUMAIFANG_MINGCHENG)
        self.has_shuihao = self.find_substring(NASHUIREN_SHIBIEHAO)
        self.has_seal = self.find_subseq(QUANGUOTONGYIFAPIAO_JIANZHIZHANG)

        amount_item = re.search(FAPIAO_AMOUNT, self.text)
        if amount_item is None:
            self.total_amount = None
            return
        else:
            self.total_amount = float(amount_item.group(1))

        extra_item = re.search(r"代订附加\s+[^\s]+\s+[^\s]+\s+" + FLOAT_2P + r"\s+[^\s]+\s+" + FLOAT_2P, self.text)
        if extra_item is None:
            self.extra_amount = 0
        else:
            self.extra_amount = float(extra_item.group(1))

        self.total_amount -= self.extra_amount
        self.is_loaded = True

    def validate(self):
        self.__init__(self.path)

        error = []
        warning = []

        if not self.is_loaded:
            error.append(LOAD_ERROR.format(type='发票', path=self.path))
        else:
            if not self.has_title:
                error.append(FAPIAO_NO_TITLE.format(path=self.path))
            if not self.has_shuihao:
                error.append(FAPIAO_NO_SHUIHAO.format(path=self.path))
            if not self.has_seal:
                warning.append(FAPIAO_NO_SEAL.format(path=self.path))

        return error, warning

    @property
    def info(self):
        attri = ['类型', '路径', '金额']
        result = {}
        result['类型'] = '发票'

        if not self.is_loaded:
            result['金额'] = '加载错误'
        else:
            result['路径'] = self.path
            result['金额'] = self.total_amount
        return attri, result

    def print(self):
        # print(self.text)
        print("has_title = ", self.has_title)
        print("has_shuihao = ", self.has_shuihao)
        print("has_seal = ", self.has_seal)
        print("total_amount = ", self.total_amount)
        print("extra_amount = ", self.extra_amount)

class FlightInfo(IMGFile):
    docu_type = '舱位截图'
    total_amount: int = 0

    def load_info(self):
        if self.text is None:
            return

        self.total_amount = 0
        for amount in re.finditer(FLIGHT_INFO_AMOUNT, self.text):
            self.total_amount += int(amount.group(1))
        self.is_loaded = True

    def validate(self):
        error = []
        warning = []
        self.load_info()
        if not self.is_loaded:
            error.append(LOAD_ERROR.format(type='舱位截图', path=self.path))
        return error, warning

    def print(self):
        print("total_amount = ", self.total_amount)

FLIGHT_NUMBER = r'([A-Z][A-Z]\d\d\d\d)'
VALID_SEAT = 'BHKLMNQTXUEWROZVG'


class Combined(IMGFile):
    total_amount: int = None
    extra_amount: int = 0
    flight_number: str = None
    seat: str = None
    
    is_valid_seat: bool = False
    has_title: bool = False
    has_shuihao: bool = False


    def load_info(self):
        if self.text is None:
            return

        flight_item = re.search(FLIGHT_NUMBER + r'\s*' + '([A-Z])', self.text)

        if flight_item is None:
            self.flight_number = None
        else:
            self.flight_number = flight_item.group(1)
            self.seat = flight_item.group(2)

        amount_item = re.finditer(COMBINED_AMOUNT, self.text)
        if amount_item is None:
            self.total_amount = None
        else:
            self.total_amount = 0
            for amount in amount_item:
                self.total_amount = max(self.total_amount, float(amount.group(1)))

        self.is_valid_seat = (self.seat and (self.seat in VALID_SEAT))
        self.has_title = self.find_substring(GOUMAIFANG_MINGCHENG) or self.find_substring(GOUMAIFANG_MINGCHENG_OCR)
        self.has_shuihao = self.find_substring(NASHUIREN_SHIBIEHAO)

        self.is_loaded = True

    def validate(self):
        error = []
        warning = []
        self.load_info()
        if not self.is_loaded:
            error.append(LOAD_ERROR.format(type='合订单', path=self.path))
        return error, warning

    @property
    def info(self):
        attri = ['类型', '路径', '金额']
        result = {}
        result['类型'] = '合订单'

        if not self.is_loaded:
            result['金额'] = '加载错误'
        else:
            result['路径'] = self.path
            result['金额'] = self.total_amount
        return attri, result

    def print(self):
        # print(self.text)
        print("has_title = ", self.has_title)
        print("has_shuihao = ", self.has_shuihao)
        print("is_valid_seat = ", self.is_valid_seat)
        print('flight_number = ', self.flight_number)
        print('seat = ', self.seat)
        print("total_amount = ", self.total_amount)

class TaxiInfo(PDFFile):
    docu_type = '行程单'
    total_amount: float = None

    def load_info(self):
        if self.text is None:
            return

        amount_item = re.finditer(XINGCHENGDAN_AMOUNT, self.text)
        if amount_item is None:
            self.total_amount = None
        else:
            self.total_amount = 0
            for amount in amount_item:
                self.total_amount = max(self.total_amount, float(amount.group(1)))
        self.is_loaded = True

    def print(self):
        print("total_amount: ", self.total_amount)

    def validate(self):
        error = []
        warning = []
        self.load_info()
        if not self.is_loaded:
            error.append(LOAD_ERROR.format(type='行程单', path=self.path))
        return error, warning