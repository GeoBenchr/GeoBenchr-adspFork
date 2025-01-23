import os
import requests
import csv
import sys
from datetime import datetime

BASE_URL = 'https://www.movebank.org/movebank/service'

MOVEBANK_USERNAME = os.getenv('MOVEBANK_USERNAME')
MOVEBANK_PASSWORD = os.getenv('MOVEBANK_PASSWORD')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(SCRIPT_DIR, 'datasets')
GEOMESA_DIR = os.path.join(DATASETS_DIR, 'geomesa')

if not MOVEBANK_USERNAME or not MOVEBANK_PASSWORD:
    raise EnvironmentError("Environment variables MOVEBANK_USERNAME and MOVEBANK_PASSWORD must be set. Create an account at movebank.org")

def get_studies():
    response = requests.get(
        f'{BASE_URL}/public/json?entity_type=study&i_have_download_access=true', 
        auth=(MOVEBANK_USERNAME, MOVEBANK_PASSWORD)
    )
    json_response = response.json()
    parsed_ids = [study['id'] for study in json_response]
    return parsed_ids

def format_timestamp(timestamp):
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]  # Trim to milliseconds
    except ValueError:
        return timestamp  # Return original if parsing fails

def download_study(id):
    print(f'Downloading dataset with ID {id}')
    response = requests.get(
        f'{BASE_URL}/direct-read?entity_type=event&study_id={id}', 
        auth=(MOVEBANK_USERNAME, MOVEBANK_PASSWORD)
    )
    raw_data = response.text
    lines = raw_data.strip().split("\n")
    lines = [line.replace('\r', '') for line in lines] 

    header = lines[0].split(",")
    header.append("dataset_id") # add dataset id to keep track of which dataset it was part before merging
    data_rows = [line.split(",") for line in lines[1:]]
    
    for row in data_rows:
        row.append(str(id))

    dataset_file = os.path.join(DATASETS_DIR, f'moveBank_{id}.csv')
    with open(dataset_file, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(data_rows)

    geomesa_file = os.path.join(GEOMESA_DIR, f'moveBank_geomesa_{id}.csv')
    with open(geomesa_file, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        for row in data_rows:
            row[0] = format_timestamp(row[0])  # timestamp format for geoMesa
            writer.writerow(row)

    return lines

def create_dataset_folder():
    for folder in [DATASETS_DIR, GEOMESA_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Directory '{folder}' created.")
        else:
            print(f"Directory '{folder}' already exists.")

def download_rows(num_rows):
    create_dataset_folder()

    # study_ids = get_studies()
    study_ids = [1169957016]
    acc = 0
    exited = False

    for id in study_ids:
        lines = download_study(id)
        acc += len(lines)
        if acc >= num_rows: 
            print(f'{acc} lines were downloaded. Exiting...')
            exited = True
            break

    if not exited:
        print(f'All ids were downloaded. {acc} lines were reached.')

def main():
    try:
        if len(sys.argv) != 2:
            print("Usage: python script.py <number_of_rows>")
            sys.exit(1)

        num_rows = int(sys.argv[1])
        if num_rows <= 0:
            print("Please enter a positive number.")
            sys.exit(1)
        
        download_rows(num_rows)
    except ValueError:
        print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()
