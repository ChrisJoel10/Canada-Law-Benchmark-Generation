import json
import requests
import argparse


constitution = "https://www.canlii.org/ca/laws/const/items"
consolidated_stat = "https://www.canlii.org/ca/laws/stat/items"
annual_stat = "https://www.canlii.org/ca/laws/astat/items"
regulations = "https://www.canlii.org/ca/laws/regu/items"

courts = ["https://www.canlii.org/ca/scc/nav/date/{year}/items", "https://www.canlii.org/ca/fc/nav/date/{year}/items"]


def get_json_response(url):
    response = requests.get(url)
    return response.json()

response = []

for link in [constitution, consolidated_stat, annual_stat, regulations]:
    print("Fetching:", link)
    response = response + get_json_response(link)
    print("Fetched:", len(response), "Links") 

for link in courts:
    for year in range(2015, 2023):
        json_response = get_json_response(link.format(year=year))
        for obj in json_response:
            obj["title"] = obj["styleOfCause"]
            obj["path"] = obj["url"]
        
        response = response + json_response

save_path = "links.json"

print("Total links:", len(response))   


parser = argparse.ArgumentParser(description="Save response links to a JSON file.")
parser.add_argument('--savepath', type=str, required=True, help='Path to save the JSON file')
args = parser.parse_args()

with open(args.savepath, "w", encoding='utf8') as f:
    json.dump(response, f, ensure_ascii=False, indent=4)

