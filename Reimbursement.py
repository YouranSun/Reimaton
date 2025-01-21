
import os
import re
from datetime import datetime
import itertools
import shutil
import pandas as pd
import numpy as np
from openpyxl import Workbook


from typing import List, Optional
from collections import Counter
from Document import Fapiao, Combined, TaxiInfo, FlightInfo

from ErrorMessage import LOAD_ERROR, TRIP_NOT_COVERED, AMOUNT_NOT_COVERED, REPEATED_FAPIAO, UNTYPICAL_REGISTRATION_FEE, TRIP_NOT_INVOLVED, COMBINED_NO_TRIP, FAPIAO_FOR_FLIGHT_NO_TRIP, TRIP_REPEATED

class Certificate:
    def __init__(self, path):
        self.cert: Optional[TaxiInfo | FlightInfo]
        self.path = path

        filename, fileextension = os.path.splitext(path)
        if fileextension == ".pdf":
            self.cert = TaxiInfo(path)
        else:
            self.cert = FlightInfo(path)
        self.cert.load_info()

    def validate(self):
        return self.cert.validate()

    def to_str(self):
        return self.cert.path + ' 金额：' + str(self.cert.total_amount)


class Record:

    def __init__(self, path):
        self.fapiao: Optional[Fapiao | Combined] = None
        self.certificates: List[Certificate] = []
        self.trips: List[tuple] = []

        filename, fileextension = os.path.splitext(path)
        if fileextension == ".pdf":
            self.fapiao = Fapiao(path)
        else:
            self.fapiao = Combined(path)
        self.fapiao.load_info()

    @property
    def info(self):
        if self.fapiao is None:
            attri = ['错误']
            result = {}
            result['错误'] = '没有发票'
            return attri, result
        return self.fapiao.info
    
    def trip_to_str(trip):
        contestant, city1, city2 = trip
        return contestant + ' ' + city1 + '-' + city2

    def add_trip(self, trip: str, contestant: str):
        city1, city2 = map(str, trip.split('-'))
        if (contestant, city1, city2) not in self.trips:
            self.trips.append((contestant, city1, city2))
        
    def del_trip(self, trip: tuple):
        self.trips.remove(trip)

    def add_cert(self, cert: Certificate):
        if cert not in self.certificates:
            self.certificates.append(cert)

    def del_cert(self, cert: Certificate):
        self.certificates.remove(cert)

    def validate(self, parent_type: str):
        error = []
        warning = []
        e, w = self.fapiao.validate()
        error.extend(e)
        warning.extend(w)

        for cert in self.certificates:
            e, w = cert.validate()
            error.extend(e)
            warning.extend(w)

        if parent_type == 'traffic':
            if type(self.fapiao) == Fapiao:
                if self.fapiao.total_amount > 400 and not self.trips:
                    warning.append(FAPIAO_FOR_FLIGHT_NO_TRIP.format(path=self.fapiao.path))
                current_amount = 0
                for cert in self.certificates:
                    current_amount += cert.cert.total_amount
                if current_amount < self.fapiao.total_amount:
                    error.append(AMOUNT_NOT_COVERED.format(path=self.fapiao.path, total_amount=self.fapiao.total_amount, current_amount=current_amount))

                for trip in self.trips:
                    contestant, city1, city2 = trip
                    covered = False
                    for cert in self.certificates:
                        contestant_found = (re.search(contestant, cert.cert.text) is not None)
                        trip_found = (re.search(city1 + r'.*' + city2, cert.cert.text) is not None)
                        if contestant_found and trip_found:
                            covered = True
                    if not covered:
                        warning.append(TRIP_NOT_COVERED.format(path=self.fapiao.path, trip=Record.trip_to_str(trip)))
            else:
                if not self.trips:
                    error.append(COMBINED_NO_TRIP.format(path=self.fapiao.path))
                for trip in self.trips:
                    contestant, city1, city2 = trip
                    contestant_found = (re.search(contestant, self.fapiao.text) is not None)
                    trip_found = self.fapiao.find_subseq(contestant + city1 + city2)
                    if not contestant_found or not trip_found:
                        warning.append(TRIP_NOT_COVERED.format(path=self.fapiao.path, trip=Record.trip_to_str(trip)))

        if parent_type == 'registration':
            if self.fapiao.total_amount % 1500 != 0 and self.fapiao.total_amount % 1600 != 0:
                warning.append(UNTYPICAL_REGISTRATION_FEE.format(path=self.fapiao.path))
        return error, warning

FAPIAO_FILE_NAME = "{type}-{index}-发票-{amount}{ext}"
CERT_FILE_NAME = "{type1}-{index1}-{type2}-{index2}{ext}"
EXTRA_AMOUNT = "扣除代订附加费用{amount}元"

class Schema:
    def __init__(self):
        self.home_city: str = '深圳'
        self.dest_city: str = ''
        self.contestants: List[str] = []
        self.traffic: List[Record] = []
        self.hostel: List[Record] = []
        self.registration: List[Record] = []
        self.error: List[str] = []
        self.warning: List[str] = []
        self.last_gen_time = None

    def add_contestant(self, name: str):
        if name in self.contestants:
            return
        self.contestants.append(name)
    
    def del_contestant(self, name: str):
        if name in self.contestants:
            self.contestants.remove(name)
        for record in self.traffic:
            record.trips = [(contestant, city1, city2) for (contestant, city1, city2) in record.trips if x != name]

    def upd_city(self, city: str):
        self.dest_city = city
        for record in self.traffic:
            record.trips = []

    def add_traffic(self, record: Record):
        self.traffic.append(record)

    def del_traffic(self, record: Record):
        self.traffic.remove(record)

    def add_hostel(self, record: Record):
        self.hostel.append(record)

    def del_hostel(self, record: Record):
        self.hostel.remove(record)

    def add_registration(self, record: Record):
        self.registration.append(record)

    def del_registration(self, record: Record):
        self.registration.remove(record)

    def validate(self):
        self.error = []
        self.warning = []

        all_trips = list(itertools.chain.from_iterable([record.trips for record in self.traffic]))

        for contestant in self.contestants:
            for city1, city2 in [(self.home_city, self.dest_city), (self.dest_city, self.home_city)]:
                count = all_trips.count((contestant, city1, city2))
                if count == 0:
                    self.warning.append(TRIP_NOT_INVOLVED.format(trip=Record.trip_to_str((contestant, city1, city2))))
                elif count > 1:
                    self.warning.append(TRIP_REPEATED.format(trip=Record.trip_to_str((contestant, city1, city2))))

        all_fapiao_paths = Counter([record.fapiao.path for record in self.traffic + self.hostel + self.registration])
        self.error.extend([REPEATED_FAPIAO.format(path=path) for path, cnt in all_fapiao_paths.items() if cnt > 1])

        errors_warnings = [record.validate('traffic') for record in self.traffic]
        self.error.extend(list(itertools.chain.from_iterable([e for e, _ in errors_warnings])))
        # print(list(itertools.chain.from_iterable([w for _, w in errors_warnings])))
        self.warning.extend(list(itertools.chain.from_iterable([w for _, w in errors_warnings])))
        errors_warnings = [record.validate('hostel') for record in self.hostel]
        self.error.extend(list(itertools.chain.from_iterable([e for e, _ in errors_warnings])))
        self.warning.extend(list(itertools.chain.from_iterable([w for _, w in errors_warnings])))
        errors_warnings = [record.validate('registration') for record in self.registration]
        self.error.extend(list(itertools.chain.from_iterable([e for e, _ in errors_warnings])))
        self.warning.extend(list(itertools.chain.from_iterable([w for _, w in errors_warnings])))

    def _copy_files(self, path):

        for i, record in enumerate(self.traffic):
            shutil.copy(record.fapiao.path, os.path.join(path, FAPIAO_FILE_NAME.format(type='交通', index=i+1, amount=record.fapiao.total_amount, ext=record.fapiao.extension)))
            for j, cert in enumerate(record.certificates):
                shutil.copy(cert.cert.path, os.path.join(path, CERT_FILE_NAME.format(type1='交通', index1=i+1, index2=j+1, type2=cert.cert.docu_type, ext=cert.cert.extension)))
        
        for i, record in enumerate(self.hostel):
            shutil.copy(record.fapiao.path, os.path.join(path, FAPIAO_FILE_NAME.format(type='住宿', index=i+1, amount=record.fapiao.total_amount, ext=record.fapiao.extension)))

        for i, record in enumerate(self.registration):
            shutil.copy(record.fapiao.path, os.path.join(path, FAPIAO_FILE_NAME.format(type='报名费', index=i+1, amount=record.fapiao.total_amount, ext=record.fapiao.extension)))

    def _write_table(self, path):
        table_path = os.path.join(path, '报销表.xlsx')
        data = pd.DataFrame(columns=['发票', '金额', '行程', '证明文件', '说明'])

        sum_amount = 0
        cell_to_merge = []

        for i, record in enumerate(self.traffic):
            sum_amount += record.fapiao.total_amount
            result = {
                '发票': [FAPIAO_FILE_NAME.format(type='交通', index=i+1, amount=record.fapiao.total_amount, ext=record.fapiao.extension)],
                '金额': [record.fapiao.total_amount],
                '行程': [Record.trip_to_str(trip) for trip in record.trips],
                '证明文件': [CERT_FILE_NAME.format(type1='交通', index1=i+1, index2=j+1, type2=cert.cert.docu_type, ext=cert.cert.extension) for j, cert in enumerate(record.certificates)]
                            if type(record.fapiao) == Fapiao else ['该文件为合订单，已包含行程信息'],
                '说明': [''] if record.fapiao.extra_amount == 0 else [EXTRA_AMOUNT.format(amount=record.fapiao.extra_amount)]
            }
            block = pd.DataFrame.from_dict(result, orient='index').T
            cell_to_merge.append((len(data), len(data) + len(block)))
            data = pd.concat([data, block])

        for i, record in enumerate(self.hostel):
            sum_amount += record.fapiao.total_amount
            result = {
                '发票': [FAPIAO_FILE_NAME.format(type='住宿', index=i+1, amount=record.fapiao.total_amount, ext=record.fapiao.extension)],
                '金额': [record.fapiao.total_amount],
                '证明文件': ['水单请见纸质报销材料']
            }
            block = pd.DataFrame.from_dict(result, orient='index').T
            cell_to_merge.append((len(data), len(data) + len(block)))
            data = pd.concat([data, block])

        for i, record in enumerate(self.registration):
            sum_amount += record.fapiao.total_amount
            result = {
                '发票': [FAPIAO_FILE_NAME.format(type='报名费', index=i+1, amount=record.fapiao.total_amount, ext=record.fapiao.extension)],
                '金额': [record.fapiao.total_amount]
            }
            block = pd.DataFrame.from_dict(result, orient='index').T
            cell_to_merge.append((len(data), len(data) + len(block)))
            data = pd.concat([data, block], ignore_index=True)

        data = pd.concat([data, pd.DataFrame({'发票': ['总金额'], '金额': [sum_amount]})], ignore_index=True)

        print(data.head)

        with pd.ExcelWriter(table_path, engine="xlsxwriter") as writer:
            worksheet = writer.book.add_worksheet('报销表')
            data.to_excel(writer, index=False, sheet_name='报销表')
            worksheet = writer.sheets['报销表']
            for start, end in cell_to_merge:
                if start + 1 != end:
                    worksheet.merge_range('A{start}:A{end}'.format(start=start+1, end=end), data.iloc[0, start+1])

    def generate(self, path):
        path=os.path.join(path, '报销'+datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        os.mkdir(path)
        self.validate()
        # sprint(self.warning)
        for record in self.traffic + self.hostel + self.registration:
            if not record.fapiao.is_loaded:
                raise FileNotFoundError(LOAD_ERROR.format(type='发票', path=record.fapiao.path) + '，不能继续生成')
            for cert in record.certificates:
                if not cert.cert.is_loaded:
                    raise FileNotFoundError(LOAD_ERROR.format(type='证明文件', path=cert.cert.path) + '有未能成功加载的文件，不能继续生成')
                
        if not os.access(path, os.W_OK):
            raise PermissionError('目标目录没有写入权限')

        self._copy_files(path)
        self._write_table(path)
        self.last_gen_time = datetime.now()


        