from pydantic import BaseModel

class ReviewResponse(BaseModel):
    Correctness_Score: int
    Factual_Accuracy_Score: int
    Correctness_feedback: str
    Factual_Accuracy_feedback: str