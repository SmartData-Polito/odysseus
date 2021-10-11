import requests
import urllib.parse
import urllib.request
import os
import time
import zipfile
from pathlib import Path
import xmltodict

class LouisvilleScooterDataGatherer:
    """
    Class for automatically downloading data relating to the New York Citi bike sharing operator from a remote database.

    :param output_path: path in which to store the file
    :type output_path: str
    :param structured_dataset_name:
            """
    def __init__(self, output_path):
        self.output_path = Path(output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.download_urls = [
            'https://data.louisvilleky.gov/sites/default/files/Louisville-Dockless-Trips%20.csv',
            'https://data.louisvilleky.gov/sites/default/files/DocklessTripOpenData_10.csv',
        ]

    def download_data(self):
        start = time.time()
        for url in self.download_urls:
            print('Start download from %s' % url)
            r = requests.get(url)
            end = time.time()
            print('download completed in %.2f' % (end-start))
            with open(self.output_path.joinpath(url.rsplit('/', 1)[-1]), mode='wb') as localfile:
                localfile.write(r.content)

