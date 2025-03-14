"""
Nie wiem czym konkretnie mają zajmować się agenci, więc 
napisałem prosty prototyp z podlaczeniem do Mongo.

Zrobiłem agenta, który w kolekcji danych szuka anomalii i analizuje je z ai za pomoca api OpenAI.
"""

from fastapi import FastAPI
from pymongo import MongoClient
import numpy as np
import openai
import os

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client["data_db"]

openai.api_key = os.getenv("OPENAI_API_KEY")
retrievals_endpoint = "https://api.openai.com/v1/retrievals"
retrievals_vector_store_id = os.getenv("RETRIEVALS_VECTOR_STORE_ID")    

class DataAnalysisAgent:
    def __init__(self, db):
        self.db = db
    
    def detect_anomalies(self, collection_name, field, threshold=1.5):
        # Szukanie anomalii
        data = list(self.db[collection_name].find({}, {"_id": 0, field: 1}))
        values = [item[field] for item in data if field in item]
        if not values:
            return {"status": "error", "message": "Brak danych"}
        
        mean = np.mean(values)
        std = np.std(values)
        anomalies = [v for v in values if abs(v - mean) > threshold * std]
        
        return {"status": "success", "anomalies": anomalies}

    def retrieve_similar_cases(self, anomalies):
        #S zukanie podobnych za pomocą retrieve
        if not anomalies:
            return "Brak anomalii do analizy."
        
        query_text = f"Wykryte anomalie: {anomalies}. Znajdź podobne przypadki."
        
        response = openai.get(
            retrievals_endpoint,
            json={
                "vector_store_id": retrievals_vector_store_id,
                "queries": [{"query": query_text}]
            },
            headers={"Authorization": f"Bearer {openai.api_key}"}
        )
        
        return response.json()
    
    def analyze_with_ai(self, anomalies, similar_cases):
        # Analiza z OpenAI
        if not anomalies:
            return "Brak anomalii w danych."

        prompt = f"""
        Oto lista anomalii wykrytych w danych: {anomalies}.
        Oto podobne przypadki znalezione w bazie: {similar_cases}.
        Przeanalizuj dane i podaj możliwe przyczyny anomalii oraz sugestie dotyczące dalszej analizy.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": "Jesteś ekspertem ds. analizy danych."},
                      {"role": "user", "content": prompt}]
        )

        return response["choices"][0]["message"]["content"]

agent = DataAnalysisAgent(db)

@app.get("/analyze/{collection_name}/{field}")
def analyze_data(collection_name: str, field: str):
    anomalies_result = agent.detect_anomalies(collection_name, field)
    
    if anomalies_result["status"] == "error":
        return anomalies_result
    
    similar_cases = agent.retrieve_similar_cases(anomalies_result["anomalies"])
    ai_analysis = agent.analyze_with_ai(anomalies_result["anomalies"], similar_cases)
    
    return {"status": "success", "ai_analysis": ai_analysis, "similar_cases": similar_cases}
