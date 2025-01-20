
import os
import re

from typing import List, Optional
from collections import Counter
from Document import Fapiao, Combined, TaxiInfo, FlightInfo

from ErrorMessage import TRIP_NOT_COVERED, AMOUNT_NOT_COVERED, REPEATED_FAPIAO, UNTYPICAL_REGISTRATION_FEE

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
        attri = ['类型', '金额']
        result = {}

        if self.fapiao is None:
            result['类型'] = result['金额'] = '加载错误'
        else:
            if type(self.fapiao) is Fapiao: result['类型'] = '发票'
            else: result['类型'] = '合订单'
            result['金额'] = self.fapiao.total_amount

        return attri, result
    
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

        if parent_type == 'traffic':
            if type(self.fapiao) == Fapiao:
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
                for trip in self.trips:
                    contestant, city1, city2 = trip
                    contestant_found = (re.search(contestant, cert.cert.text) is not None)
                    trip_found = (re.search(city1 + r'.*' + city2, cert.cert.text) is not None)
                    if not contestant_found or not trip_found:
                        warning.append(TRIP_NOT_COVERED.format(path=self.fapiao.path, trip=Record.trip_to_str(trip)))

        if parent_type == 'registration':
            if self.fapiao.total_amount % 1500 != 0 or self.fapiao.total_amount % 1600 != 0:
                warning.append(UNTYPICAL_REGISTRATION_FEE.format(path=self.fapiao.path))
        print(warning)
        return error, warning

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

        all_fapiao_paths = Counter([record.fapiao.path for record in self.traffic + self.hostel + self.registration])
        self.error.extend([REPEATED_FAPIAO.format(path=path) for path, cnt in all_fapiao_paths.items() if cnt > 1])

        errors_warnings = [record.validate('traffic') for record in self.traffic]
        self.error.extend(e for e, _ in errors_warnings)
        self.warning.extend(w for _, w in errors_warnings)
        errors_warnings = [record.validate('hostel') for record in self.hostel]
        self.error.extend(e for e, _ in errors_warnings)
        self.warning.extend(w for _, w in errors_warnings)
        errors_warnings = [record.validate('registration') for record in self.registration]
        self.error.extend(e for e, _ in errors_warnings)
        self.warning.extend(w for _, w in errors_warnings)
