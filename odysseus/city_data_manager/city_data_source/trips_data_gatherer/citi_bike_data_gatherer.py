import requests
import urllib.parse
import urllib.request
import io
import time
import zipfile
from pathlib import Path
import xmltodict


class DataGatherer:
    """
    Class for automatically downloading data relating to the New York Citi bike sharing operator from a remote database.

    :param output_path: path in which to store the file
    :type output_path: str
    :param structured_dataset_name:
            """
    def __init__(self, output_path, structured_dataset_name):
        self.root_url = 'https://s3.amazonaws.com/tripdata/'

        self.output_path = Path(output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.structured_dataset_name = structured_dataset_name

        '''
        get from official website the lists of all downloadable csvs
        dataset_names[yyyymm] = dataset_name_to_attach_to_root_url
        '''
        f = requests.get(self.root_url)
        xml = f.text
        self.dataset_names = {}
        available_datasets_dict = xmltodict.parse(xml)
        for entry in available_datasets_dict['ListBucketResult']['Contents']:
            key = entry['Key']
            if key == '201307-201402-citibike-tripdata.zip' or 'JC' in key or '.html' in key:
                continue
            else:
                self.dataset_names[key[0:6]] = key

        return

    def download_data(self, year, month):
        """
        Download data for a specific month and year.

        :param year: year expressed as a four-digit number (e.g. 1999)
        :type year: int
        :param month: month expressed as a number (e.g. for November the method expects to receive 11)
        :type month: int
        :return: nothing
        """
        year = str(year)
        month = str(month)

        structured_output_path = self.output_path

        try:
            structured_dataset_name = self.dataset_names['%s%s' % (year, month.zfill(2))]
            full_url = urllib.parse.urljoin(self.root_url, structured_dataset_name)
        except KeyError:
            print('Any available dataset for %s %s' % (year, month))
            return

        if not os.path.isfile(structured_output_path.joinpath(structured_dataset_name)):

            start = time.time()
            print('Start download of %s' % structured_dataset_name)
            r = requests.get(full_url)
            end = time.time()
            print('download completed in %.2f' % (end-start))

            with open(structured_output_path.joinpath(structured_dataset_name), mode='wb') as localfile:
                localfile.write(r.content)

        try:
            with zipfile.ZipFile(structured_output_path.joinpath(structured_dataset_name), 'r') as myzip:
                myzip.extractall(structured_output_path)
            print('%s extracted' % structured_dataset_name)
        except zipfile.BadZipfile:
            print('%s problem to unzip' % structured_dataset_name)

        return

    '''
    download all the datasets available at official citi bike website
    '''
    def bulk_download(self, standardize=False):
        """
        download all the datasets available at official citi bike website
        :param standardize:
        :type standardize: bool, optional
        :return:
        """
        for key in self.dataset_names:
            year, month = int(key[0:4]), int(key[4:6])
            self.download_data(year, month)
            if standardize:
                self.standarzide_data(year, month)
        return

import os
from odysseus.city_data_manager.config.config import data_paths_dict

raw_data_path = os.path.join(data_paths_dict["New_York_City"]["raw"]["trips"], "citi_bike")
os.makedirs(raw_data_path, exist_ok=True)

for month in range(1, 13):
    gatherer = DataGatherer(
        raw_data_path,
        "-".join([str(month), str(2017)]) + "-citibike-tripdata.csv"
    )
    gatherer.download_data(2017, month)
