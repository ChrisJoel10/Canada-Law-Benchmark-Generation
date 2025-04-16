import json 
import argparse
import os
import json
import re 

total = 0

parser = argparse.ArgumentParser(description="Save datasets to a JSON file by types.")
parser.add_argument('--datasetpath', type=str, required=True, help='Path to the dataset JSON file')
parser.add_argument('--outputdir', type=str, required=True, help='output directory')
args = parser.parse_args()
datasetpath = args.datasetpath
outputdir = args.outputdir

os.makedirs(outputdir, exist_ok=True)


with open(datasetpath, "r", encoding='utf8') as file:
    links_data = json.load(file)

jsonarray = []
mcq = []
true_false = []
short_answer = []
case_analysis = []
legal_intent = []
outcome_prediction = []
document_classification = []

error_count = 0
for i, data in enumerate(links_data):
    try:
        cleaned_json_response  = re.sub(r'\n', ' ', data["response"]["JsonResponse"])
        print(i + 1)

        jsonobj = json.loads(cleaned_json_response)


        if(type(jsonobj) == dict):
            jsonobj = [jsonobj]
        for strjson in jsonobj:
            jsonarray.append(strjson)
            
            # Use .get() to safely access keys, defaulting to None if the key doesn't exist
            if strjson.get('mcq') is not None:
                mcq.append(strjson["mcq"])
            if strjson.get('true_false') is not None:
                true_false.append(strjson["true_false"])
            if strjson.get('short_answer') is not None:
                short_answer.append(strjson["short_answer"])
            if strjson.get('case_analysis') is not None:
                case_analysis.append(strjson["case_analysis"])
            if strjson.get('legal_intent') is not None:
                legal_intent.append(strjson["legal_intent"])
            if strjson.get('outcome_prediction') is not None:
                outcome_prediction.append(strjson["outcome_prediction"])
            if strjson.get('document_classification') is not None:
                document_classification.append(strjson["document_classification"])
    except Exception as e:
        error_count = error_count + 1
    
    print(f"Error: {error_count}")

with open(outputdir + "/mcq.json", "w") as output_file:
    json.dump(mcq, output_file, indent=4)
with open(outputdir + "/true_false.json", "w") as output_file:
    json.dump(true_false, output_file, indent=4)
with open(outputdir + "/short_answer.json", "w") as output_file:
    json.dump(short_answer, output_file, indent=4)
with open(outputdir + "/case_analysis.json", "w") as output_file:
    json.dump(case_analysis, output_file, indent=4)
with open(outputdir + "/legal_intent.json", "w") as output_file:
    json.dump(legal_intent, output_file, indent=4)
with open(outputdir + "/outcome_prediction.json", "w") as output_file:
    json.dump(outcome_prediction, output_file, indent=4)
with open(outputdir + "/document_classification.json", "w") as output_file:
    json.dump(document_classification, output_file, indent=4)


    