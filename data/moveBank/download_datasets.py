import os
import requests
import csv

BASE_URL = 'https://www.movebank.org/movebank/service'

# Ensure environment variables are set for authentication
MOVEBANK_USERNAME = os.getenv('MOVEBANK_USERNAME')
MOVEBANK_PASSWORD = os.getenv('MOVEBANK_PASSWORD')

if not MOVEBANK_USERNAME or not MOVEBANK_PASSWORD:
    raise EnvironmentError("Environment variables MOVEBANK_USERNAME and MOVEBANK_PASSWORD must be set.")

def get_studies():
    response = requests.get(
        f'{BASE_URL}/public/json?entity_type=study&i_have_download_access=true', 
        auth=(MOVEBANK_USERNAME, MOVEBANK_PASSWORD)
    )
    json_response = response.json()
    parsed_ids = [study['id'] for study in json_response]
    return parsed_ids

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
    header.append("dataset_id")  # Add 'dataset_id' to the header
    data_rows = [line.split(",") for line in lines[1:]]
    
    # Add dataset ID to each data row
    for row in data_rows:
        row.append(str(id))

    # Write to CSV
    with open(f'datasets/{id}.csv', "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)  # Write header row
        writer.writerows(data_rows)  # Write data rows

    return lines

def create_dataset_folder():
    if not os.path.exists('datasets/'):
        os.makedirs('datasets/')
        print(f"Directory '{'datasets/'}' created.")
    else:
        print(f"Directory '{'datasets/'}' already exists.")

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
    print("Welcome to the dataset downloader!")
    while True:
        try:
            # Ask user for the number of rows to download
            num_rows = int(input("Enter the number of rows you want to download: "))
            if num_rows <= 0:
                print("Please enter a positive number.")
                continue
            
            # Call the download function
            download_rows(num_rows)
            break
        
        except ValueError:
            print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()
