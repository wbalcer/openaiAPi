docker run -d --name mongo -p 27017:27017 mongo

python3 test.py

export OPENAI_API_KEY="!KLUCZ_API!"
export RETRIEVALS_VECTOR_STORE_ID="!ID!"

uvicorn asystent:app --reload

output -> http://127.0.0.1:8000/docs


