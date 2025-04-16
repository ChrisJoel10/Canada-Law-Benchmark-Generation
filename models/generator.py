from pydantic import BaseModel
# Define the Pydantic schema for the JSON response
class JsonResponse(BaseModel):
    JsonResponse: str
