# Canadian Law Benchmark Dataset Generation

Dataset: [here](https://github.com/ChrisJoel10/Canada-Law-Benchmark-Generation/tree/main/Dataset)

## Usage

Install Libraries
```

pip install langgraph google-generativeai beautifulsoup4 webdriver-manager requests

```

### 1. Fetch Links and Store in a JSON file
Command Line
```
python get_links.py --savepath=links.json
```

Example Output
```
Fetching: https://www.canlii.org/ca/laws/const/items
Fetched: 2 Links
Fetching: https://www.canlii.org/ca/laws/stat/items
Fetched: 972 Links
Fetching: https://www.canlii.org/ca/laws/astat/items
Fetched: 1649 Links
Fetching: https://www.canlii.org/ca/laws/regu/items
Fetched: 6724 Links
Total links: 18767
```

### 2. Access the links, fetch the HTML Pages and store locally

This step requires ChromeWebDriver installed. 

Command Line
```
python link_scraping.py --linkpath=links.json --HTMLsavepath=html_output
```

Example Output
```
Processing: https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-c-2/latest/rsc-1985-c-c-2.html
Saved HTML for https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-c-2/latest/rsc-1985-c-c-2.html to html_output2\www.canlii.org_en_ca_laws_stat_rsc-1985-c-c-2_latest_rsc-1985-c-c-2.html.html
Processing: https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-c-3/latest/rsc-1985-c-c-3.html
Saved HTML for https://www.canlii.org/en/ca/laws/stat/rsc-1985-c-c-3/latest/rsc-1985-c-c-3.html to html_output2\www.canlii.org_en_ca_laws_stat_rsc-1985-c-c-3_latest_rsc-1985-c-c-3.html.html
Processing: https://www.canlii.org/en/ca/laws/stat/sc-1985-c-49/latest/sc-1985-c-49.html
Captcha detected on https://www.canlii.org/en/ca/laws/stat/sc-1985-c-49/latest/sc-1985-c-49.html
Please solve the captcha in the browser window...
Press Enter after solving the captcha...
```
Enter Captcha in the browser window if prompted, to continue fetching HTML Files

### 3. Generate dataset using Multi-Agent Framework

Command Line
```
python generate.py --outputJSON=dataset.json --HTMLpath=html_output
```

Example Output

```
Processing HTML File Count: 1
Generating...
Generated response: {"JsonResponse": "[{\"mcq\": {\"question\": \"According to the Constitution Act 1867, which of the following positions i ...
Reviewing...
Reviewer Feedback: The JSON is valid and follows the defined structure, including the nested objects for each question type (MCQ, true_false, short_answer, etc.). The response is well-formed and machine-readable. All parts of the response are accurately grounded in the provided text of the Constitution Act, 1867.  The questions and answers do not include information that is not found within the document.  The analysis of Section 9, the stated purpose of the Act, and the prediction based on the Governor General's actions are all directly supported by the text.
Reviewing...
Reviewer Feedback: The JSON response is valid and follows the defined structure, with each question type (MCQ, True/False, Short Answer, Case Analysis, Legal Intent, Outcome Prediction, and Document Classification) correctly formatted. Every part of the response is grounded in the original text of the Constitution Act 1867. The answers provided are accurate and directly supported by the document, with no external information included.
Overall Score: 5.0 Adding generated content to dataset...

Processing HTML File Count: 2
Generating...
Generated response: {"JsonResponse": "[{\"document_classification\": {\"document_type\": \"Act\", \"legal_domain\": \"Canadian Law\"}}, {\"m ...
Reviewing...
Reviewer Feedback: The response adheres to the JSON structure, presenting a single JSON object with a "JsonResponse" field containing a JSON array of legal analysis objects. All components of the response, including document classification, MCQ, true/false statements, short answers, legal intent, outcome prediction, and case analysis, are accurately derived from and entirely supported by the provided text. No external information is introduced, maintaining strict adherence to the source material.
Reviewing...
Reviewer Feedback: The response follows the defined JSON structure perfectly. Every element is correctly formatted and placed according to the instructions. Each part of the response is accurately grounded in the provided text. The questions are directly related to the content of the text, and the answers are derived solely from the information contained within it. There is no inclusion of external or unsupported information.
Overall Score: 5.0 Adding generated content to dataset...

```

### 4. Store the generated tasks by types


Command line

```
python classify_dataset.py --datasetpath=dataset_temp.json --output
dir=output
```
