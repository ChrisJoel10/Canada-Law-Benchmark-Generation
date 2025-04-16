from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from google import genai
import os, json, time, re
from bs4 import BeautifulSoup
import argparse
from models.generator import JsonResponse
from models.reviewer import ReviewResponse

# --- Gemini Client Setup ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  # Set your API key as an env variable

# --- Input State Schema ---
class AgentState(TypedDict):
    title: str
    html: str
    input_text: Optional[str]
    generated: Optional[dict]
    scores: Optional[List[int]]
    final_output: Optional[dict]

# --- Utility Functions ---
def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    words = re.findall(r'\b\w+\b', text)
    return " ".join(words[:6000])



# --- Agent: Data Generator ---
def data_generator_agent(state: AgentState) -> AgentState:
    prompt = f"""
    Analyze this Canadian legal text and generate appropriate benchmark tasks.
    Return a JSON response in this format:
    {{
        "mcq": {{
            "question": "string",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "number"
        }},
        "true_false": {{
            "statement": "string",
            "correct_answer": "boolean"
        }},
        "short_answer": {{
            "question": "string",
            "answer": "string"
        }},
        "case_analysis": {{
            "task": "Identify: 1) Key issue 2) Decision 3) Precedent",
            "answers": ["issue", "decision", "precedent"]
        }},
        "legal_intent": {{
            "question": "string",
            "answer": "string"
        }},
        "outcome_prediction": {{
            "scenario": "string",
            "outcome": "string"
        }},
        "document_classification": {{
            "document_type": "type",
            "legal_domain": "domain"
        }}
    }}
    Only include tasks directly supported by the input text. Avoid any external or subjective interpretation.
    Text: {state['input_text']}
    """

    try:
        print("Generating...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt],
            config={'response_mime_type': 'application/json', 'response_schema': JsonResponse}
        )
        response_obj = response.parsed.model_dump()
        response_str = json.dumps(response_obj)
        print("Generated response:", response_str[:120], "...")
        return {**state, "generated": response_obj}
    except Exception as e:
        print(f"Error generating: {e}")
        return {**state, "generated": None}

# --- Agent: Reviewer (Shared for Reviewer 1 and 2) ---
def reviewer_agent(state: AgentState) -> int:
    prompt = f"""

    
    You are a legal data reviewer. Your task is to review the generated response and assign a score (0 to 5) for each criteria.
    Criteria:
    - Correctness: Does it follow the defined JSON structure?
    - Factual Accuracy: Is every part of the response grounded entirely supported by the original text? If a question or answer includes information not found in the input text, it should be penalized.


    Original Text:
    {state['input_text']}

    Generated Response:
    {json.dumps(state['generated'], indent=2)}
    """
    try:
        print("Reviewing...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt],
            config={'response_mime_type': 'application/json', 'response_schema': ReviewResponse}
        )
        response_obj = response.parsed
        correctness_score = response_obj.Correctness_Score
        factual_accuracy_score = response_obj.Factual_Accuracy_Score
        print("Reviewer Feedback:", response_obj.Correctness_feedback, response_obj.Factual_Accuracy_feedback)
        score = (correctness_score + factual_accuracy_score) / 2
        return score
    except Exception as e:
        print(f"Reviewer error: {e}")
        return 0

def reviewer_1(state: AgentState) -> AgentState:
    score = reviewer_agent(state)
    return {**state, "scores": [score]}

def reviewer_2(state: AgentState) -> AgentState:
    scores = state.get("scores", [])
    score = reviewer_agent(state)
    scores.append(score)
    return {**state, "scores": scores}

# --- Agent: Score Aggregator ---
def score_aggregator(state: AgentState) -> AgentState:
    avg_score = sum(state["scores"]) / len(state["scores"])
    if avg_score >= 4:
        print("Overall Score:", avg_score, "Adding generated content to dataset...")
        return {**state, "final_output": {"title": state["title"], "response": state["generated"]}}
    print("Overall Score:", avg_score, "Generated content not added to dataset.")
    return {**state, "final_output": None}

# --- Define LangGraph ---
builder = StateGraph(AgentState)
builder.add_node("DataGenerator", data_generator_agent)
builder.add_node("Reviewer1", reviewer_1)
builder.add_node("Reviewer2", reviewer_2)
builder.add_node("Scorer", score_aggregator)

# Add edges
builder.set_entry_point("DataGenerator")
builder.add_edge("DataGenerator", "Reviewer1")
builder.add_edge("Reviewer1", "Reviewer2")
builder.add_edge("Reviewer2", "Scorer")
builder.add_edge("Scorer", END)

# Final Graph
graph = builder.compile()

parser = argparse.ArgumentParser(description="Generate structured dataset from HTML files.")
parser.add_argument('--outputJSON', type=str, required=True, help='Path to save the JSON file')
parser.add_argument('--HTMLpath', type=str, required=True, help='Path to HTML files')
args = parser.parse_args()
html_dir = args.HTMLpath
output_json_path = args.outputJSON

# --- Load and Run on HTML Files ---
files = os.listdir(html_dir)
results = []

for i, fname in enumerate(files):
    print()
    print(f"Processing HTML File Count: {i + 1 }")
    with open(os.path.join(html_dir, fname), "r", encoding='utf8') as f:
        html = f.read()
        input_text = extract_text_from_html(html)

        state = {
            "title": fname,
            "html": html,
            "input_text": input_text,
            "generated": None,
            "scores": [],
            "final_output": None
        }

        final_state = graph.invoke(state)
        if final_state["final_output"]:
            results.append(final_state["final_output"])

        if (i + 1) % 5 == 0 or (i + 1) == len(files):
            with open(output_json_path, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Checkpointed {i + 1} results.")

        time.sleep(5)
