import requests
import urllib.parse
import urllib.request
import io
import time
import zipfile
import os
import pandas as pd
from haversine import haversine, Unit
from pathlib import Path
import xmltodict


class DataGatherer:

    def __init__(self, output_path, structured_dataset_name):
        self.root_url = 'https://s3.amazonaws.com/tripdata/'

        self.output_path = Path(output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.max_lon = -73.90
        self.min_lon = -74.04
        self.max_lat = 40.76
        self.min_lat = 40.66
        self.structured_dataset_name = structured_dataset_name

        '''
        get from official website the lists of all downlodahle csvs
        dataset_names[yyyymm] = dataset_name_to_attach_to_root_url
        '''
        f = urllib.request.urlopen(self.root_url)
        xml = f.read().decode('utf8')
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
        year = str(year)
        month = str(month)

        structured_output_path = self.output_path.joinpath(year).joinpath(month)

        if os.path.isfile(structured_output_path.joinpath(self.structured_dataset_name)):
            print(str(structured_output_path.joinpath(self.structured_dataset_name)),
                  'already present. Delete it to redownload')
            return

        try:
            dataset_name = self.dataset_names['%s%s' % (year, month.zfill(2))]
            full_url = urllib.parse.urljoin(self.root_url, dataset_name)
        except KeyError:
            print('Any available dataset for %s %s' % (year, month))
            return

        start = time.time()
        print('Start download of %s' % dataset_name)
        r = requests.get(full_url)
        end = time.time()
        print('download completed in %.2f' % (end-start))

        with open(self.output_path.joinpath(dataset_name), mode='wb') as localfile:
            localfile.write(r.content)

        # Try catch for corrupted files
        try:
            z = zipfile.ZipFile(io.BytesIO(r.content))
            extracted = z.namelist()

            z.extractall(structured_output_path)
            os.rename(
                structured_output_path.joinpath(extracted[0]),
                structured_output_path.joinpath(self.structured_dataset_name)
            )
            print('%s extracted' % (dataset_name))

            os.remove(self.output_path.joinpath(dataset_name))
        except zipfile.BadZipfile:
            print('%s problem to unzip' % (dataset_name))

        return

    def standarzide_data(self, year, month):
        year = str(year)
        month = str(month)

        file_path = self.output_path.joinpath(year).joinpath(month).joinpath(self.structured_dataset_name)

        start = time.time()

        if 'distance' in pd.read_csv(file_path, nrows=10).columns:
            print(str(file_path), 'already standardized.')
            return

        df = pd.read_csv(file_path)

        new_columns = {}
        for column in df.columns:
            new_columns[column] = column.lower().replace(' ', '').strip().replace('station', '_station_')
        df = df.rename(columns=new_columns)

        df['count'] = 0
        df['tripduration'] = df['tripduration']

        # df = df[(~df['start_station_longitude'].isna()) & (~df['start_station_latitude'].isna()) &
        #         (~df['end_station_longitude'].isna()) & (~df['end_station_latitude'].isna())
        #         ]

        # limit to new york
        df = df[(df['start_station_latitude'] >= self.min_lat) & (df['start_station_latitude'] <= self.max_lat)]
        df = df[(df['start_station_longitude'] >= self.min_lon) & (df['start_station_longitude'] <= self.max_lon)]
        df = df[(df['end_station_latitude'] >= self.min_lat) & (df['end_station_latitude'] <= self.max_lat)]
        df = df[(df['end_station_longitude'] >= self.min_lon) & (df['end_station_longitude'] <= self.max_lon)]

        # faster than using creates geodatafrems and use the distance to compute
        df['distance'] = df.apply(
            lambda x: haversine(
                (x.start_station_latitude, x.start_station_longitude),
                (x.end_station_latitude, x.end_station_longitude),
                unit=Unit.METERS),
            axis=1
        )

        df['starttime'] = pd.to_datetime(df['starttime'])
        df['stoptime'] = pd.to_datetime(df['stoptime'])

        df.to_csv(file_path, index=False)
        end = time.time()
        print(file_path, ' augmented in %.2f' % (end - start))
        print()
        return

    '''
    download all the datasets available at offical citi bike website
    '''
    def bulk_download(self, standardize=False):
        for key in self.dataset_names:
            year, month = int(key[0:4]), int(key[4:6])
            self.download_data(year, month)
            if standardize:
                self.standarzide_data(year, month)
        return
