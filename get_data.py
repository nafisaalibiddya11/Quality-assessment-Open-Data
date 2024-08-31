import os
import random
import time
import requests
from pathlib import Path
import json
from pprint import pprint
from tqdm import tqdm
from urllib.parse import urlparse

# URL of the Leipzig open data portal
BASE_URL = "https://opendata.leipzig.de"
DOWNLOAD_FOLDER_PATH = "datasets"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def get_data_for_dataset(dataset_id: str):
    dataset_response = requests.get(
        f"{BASE_URL}/api/3/action/package_show?id={dataset_id}"
    )
    if dataset_response.status_code == 200:
        dataset_response_json = dataset_response.json()
        dataset_info = dataset_response_json.get("result")
        return dataset_info
    else:
        print(f"ERROR: Could not get the data of dataset_id: {dataset_id}")
        print(f"RESPONSE_CODE: {dataset_response.status_code}")

    # dataset_data.append(dataset_data["result"])
    # print("IN get_data_for_dataset")
    # print(dataset_data)
    # print("OUT get_data_for_dataset")


""" 
def download_csv(url: str, folder_path: str = DOWNLOAD_FOLDER_PATH):
    # Create the folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes

    filename = os.path.basename(urlparse(url).path)
    
    # If the filename is empty or doesn't end with .csv, use a default name
    if not filename or not filename.lower().endswith('.csv'):
        filename = f'downloaded_file_{str(random.randint(111,9999999))}.csv'

    # Combine the folder path and filename
    file_path = os.path.join(folder_path, filename)

    # Write the content to the file
    with open(file_path, 'wb') as file:
        file.write(response.content)

    return file_path
 """


def download_csv(url: str, folder_path: str = DOWNLOAD_FOLDER_PATH):
    os.makedirs(folder_path, exist_ok=True)

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            filename = os.path.basename(urlparse(url).path)
            if not filename or not filename.lower().endswith(".csv"):
                filename = f"downloaded_file_{str(random.randint(111,9999999))}.csv"

            file_path = os.path.join(folder_path, filename)

            with open(file_path, "wb") as file:
                file.write(response.content)

            return file_path
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Max retries reached. Skipping {url}")
                return None


def get_data_for_gorup_dataset(dataset_id: str):
    url = (
        f"{BASE_URL}/api/3/action/group_show?id={dataset_id}&include_dataset_count=True"
    )
    print("CALLING ", url)
    dataset_response = requests.get(url)
    dataset_data = dataset_response.json()
    # dataset_data.append(dataset_data["result"])
    print(dataset_data)


# Function to fetch datasets from the CKAN API
def fetch_datasets(datset_list_name: str = None):
    datasets = []
    PACKAGE_LIST_URL = f"{BASE_URL}/api/3/action/package_list"
    URL = f"{BASE_URL}/api/3/action/group_list"

    if datset_list_name == "PACKAGE_LIST_URL":
        URL = PACKAGE_LIST_URL

    # Get JSON-formatted list of datasets
    response = requests.get(URL)

    data = response.json()
    # print("*"*80)
    # pprint(response)
    # print("data: ",data)
    # print("*"*80)

    if data["success"]:
        count = 0
        dataset_ids = data.get("result")
        dataset_count = len(dataset_ids)
        print(f"TOTAL DATASET COUNT: {dataset_count}")
        csv_count = 0
        print("Fetching datasets information...")
        for dataset_id in tqdm(dataset_ids):
            info_about_dataset = get_data_for_dataset(dataset_id)
            datasets.append(info_about_dataset)

            csv_count += 1
            # if csv_count == 10:
            # break
            """
            print("="*80)
            resources = info_about_dataset.get("resources")
            pprint(resources)
            for resource in resources:
                if resource.get("format") == "csv":
                    csv_count += 1
                    # print(resource)
            # pprint(info_about_dataset.get)
            print("="*80)
            """
        # print(f"CSV COUNT: {csv_count}")
    else:
        print("Error fetching datasets")
    print("================= DATASETS LIST FETCHING DONE =================")
    return datasets


# Main function
def main():
    # datasets = fetch_datasets()  # To get group list of the site
    data_info = []
    dataset_download_list = []
    """
    datasets_info_list = fetch_datasets("PACKAGE_LIST_URL")  # To get all the dataset list
    csv_count = 0
    for dataset in datasets_info_list:
        print("=" * 80)
        dataset_title = dataset.get("title")
        print("Title:", dataset_title)
        # print("Description:", dataset["notes"])
        print("Resources:")
        formats = {}
        for resource in dataset["resources"]:
            print("*" * 80)
            resource_format = resource.get("format")
            pprint(resource)
            if formats.get(resource_format):
                formats[resource_format] = formats[resource_format] + 1
            else:
                formats[resource_format] = 0

            if resource_format in ["csv", "CSV"]:
                csv_count += 1
                download_url = resource.get("download_url")
                url = resource.get("url")
                download_object = {
                    "dataset_display_title": dataset_title,
                    "download_url": download_url,
                    "url": url,
                }
                dataset_download_list.append(download_object)
            print("*" * 80)
        print("=" * 80)
        print(f"FORMATS: {formats}")
    pprint(dataset_download_list)
    Path("dataset_download_list.json").write_text(
        json.dumps(dataset_download_list, indent=4) + "\n"
    )
    print(f"CSV COUNT: {csv_count}")
    """
    with open("dataset_download_list.json", "r") as f:
        dataset_download_list = json.load(f)

    # Load existing data_info if it exists
    data_info_path = Path("data_info.json")
    if data_info_path.exists():
        with open(data_info_path, "r") as f:
            data_info = json.load(f)
    else:
        data_info = []

    # Find the index to start from
    start_index = len(data_info)
    # start_index = 99

    for item in tqdm(
        dataset_download_list[start_index:],
        initial=start_index,
        total=len(dataset_download_list),
    ):
        file_path = download_csv(item.get("url"))
        if file_path:
            data = {
                "dataset_display_name": item.get("dataset_display_title"),
                "dataset_file_name": file_path,
            }
            data_info.append(data)

            # Save progress after each successful download
            data_info_path.write_text(json.dumps(data_info, indent=4) + "\n")

    # pprint(data_info)
    # print(type(data_info))

    # for item in tqdm(dataset_download_list):
    # pass
    # if item.get("dataset_display_title")
    print(f"Download completed. Total datasets processed: {len(data_info)}")


"""  
    dataset_download_list = json.load(open(dataset_download_list.json))

    for item in tqdm(dataset_download_list):
        file_path = download_csv(item.get("url"))
        data = {
            "dataset_display_name": item.get("dataset_display_title"),
            "dataset_file_name": file_path
        }
        data_info.append(data)
    Path("data_info.json").write_text(
        json.dumps(data_info, indent=4) + "\n"
    )


def dataset_download(dataset_download_list: list[dict]):
 """

if __name__ == "__main__":
    main()
