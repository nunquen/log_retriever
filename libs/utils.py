import json
import pandas as pd
from typing import Dict, List

def read_csv_file(csv_file: str, columns=List, has_header=False, field_separators=str)-> pd:
    try:
        df = pd.read_csv(
            csv_file,
            names=columns,
            header=has_header,
            sep=field_separators,
            on_bad_lines="skip")
        return df
    except Exception as e:
        print(f"read_csv_file.Exception: {e}")
        return None

def write_json_file(output_path: str, data: List[Dict]):
    try:
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4,  sort_keys=True, separators=(',',':'))
            json_file.close()
    except Exception as e:
        print(f"write_json_file.Exception: {e}")
        return

def bytes_formatter(size):
    power = 2**10
    n = 0
    power_tags = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return size, power_tags[n]+'b'
