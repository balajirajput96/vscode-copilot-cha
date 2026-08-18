from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import numpy as np
from typing import List
import logging

app = FastAPI(title="ML Model API")

class PredictionInput(BaseModel):
    features: List[float] = Field(..., max_length=100)

@app.get("/")
def home():
    return {"message": "API Running!", "status": "active"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
def predict(data: PredictionInput):
    try:
        input_data = np.array([data.features])
        # Load your model: prediction = model.predict(input_data)
        prediction = np.random.random() * 100
        return {"prediction": float(prediction)}
    except Exception as e:
        logging.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")