import requests
import urllib.parse
import urllib.request
import os
import shutil
import time
import zipfile
from pathlib import Path
import xmltodict


class ChicagoScooterDataGatherer:
    def __init__(self, output_path):
        self.output_path = Path(output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.download_urls = [
            'https://data.cityofchicago.org/api/views/2kfw-zvte/rows.csv?accessType=DOWNLOAD'
        ]

    def download_data(self):
        start = time.time()
        for url in self.download_urls:
            print('Start download from %s' % url)
            r = requests.get(url)
            end = time.time()
            print('download completed in %.2f' % (end-start))
            with open(self.output_path.joinpath("E-Scooter_Trips_-_2019_Pilot.csv"), mode='wb') as localfile:
                localfile.write(r.content)


class ChicagoScooterGeoDataGatherer1:
    def __init__(self, output_path):
        self.output_path = Path(output_path)
        shutil.rmtree(self.output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.download_urls = [
            "https://data.cityofchicago.org/api/geospatial/5jrd-6zik?method=export&format=Shapefile",
        ]

    def download_data(self):
        url = self.download_urls[0]
        r = requests.get(url)
        with open(os.path.join(self.output_path, "Boundaries - Census Tracts - 2010.zip"), mode='wb') as localfile:
            localfile.write(r.content)
            with zipfile.ZipFile(os.path.join(self.output_path, "Boundaries - Census Tracts - 2010.zip"), 'r') as myzip:
                myzip.extractall(self.output_path)


class ChicagoScooterGeoDataGatherer2:
    def __init__(self, output_path):
        self.output_path = Path(output_path)
        shutil.rmtree(self.output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.download_urls = [
            "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=Shapefile"
        ]

    def download_data(self):

        url = self.download_urls[0]
        r = requests.get(url)
        with open(os.path.join(self.output_path, "Boundaries - Community Areas (current).zip"), mode='wb') as localfile:
            localfile.write(r.content)
            with zipfile.ZipFile(os.path.join(self.output_path, "Boundaries - Community Areas (current).zip"), 'r') as myzip:
                myzip.extractall(self.output_path)
