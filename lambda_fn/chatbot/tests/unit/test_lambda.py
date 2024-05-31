import json
import os
from chromadb import Client
from openai import OpenAI
from lambda_fn.chatbot.src import lambda_handler   
from unittest.mock import patch, MagicMock
 
def mock_chromadb_query(query, top_k):
    return [
        {'metadata': {'text': 'Lambda functions are triggered by events such as changes to data in an S3 bucket, updates to a DynamoDB table, or an HTTP request from API Gateway.'}},
        {'metadata': {'text': 'Lambda can automatically scale from a few requests per day to thousands per second.'}}
    ]

def mock_openai_completion_create(engine, prompt, max_tokens):
    return {
        'choices': [
            {'text': 'To handle user queries in AWS Lambda, you need to set up an API Gateway to route the requests to the Lambda function. The function then processes the requests and generates responses.'}
        ]
    }

def main():
    # Load the test event
    with open('test_event.json') as f:
        event = json.load(f)

    # Mock the ChromaDB client
    with patch('lambda_function.chroma_client.query', side_effect=mock_chromadb_query):
        # Mock the OpenAI client
        with patch('lambda_function.openai.Completion.create', side_effect=mock_openai_completion_create):
            # Call the lambda handler
            response = lambda_handler(event, None)
            print(response)

if __name__ == '__main__':
    main()
