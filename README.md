# PrintDeed AI Assignment

## Setup
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
python -m pytest

## URL
use this url http://127.0.0.1:8000/docs

## Features
- Validation service
- Matching service
- End-to-end pipeline

## Notes
- Mock LLM used
- Easily replaceable with OpenAI
