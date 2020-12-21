import os
import gzip
import csv
import hashlib

def save_tsv_gz_file_by_appending_method(path: str, file_name: str, data_filed_header: list, data_filed_dict: dict):
    with gzip.open(path + file_name, "at", newline="") as filetype:
        wcsv = csv.DictWriter(
            filetype,
            data_filed_header,
            delimiter = "\t",
        )
        wcsv.writerow(data_filed_dict)

def mkdir_force(destination_path: str):
    if not os.path.exists(destination_path):
        os.makedirs(destination_path, exist_ok=True)

def get_hash256(url: str):
    s = hashlib.sha256()
    s.update(url.encode('utf-8'))
    URLID = s.hexdigest()
    return URLID
