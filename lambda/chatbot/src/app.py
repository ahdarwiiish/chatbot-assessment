import json
import boto3
from chromadb import Client
from openai import OpenAI

# Initialize ChromaDB client
chroma_client = Client()
# Initialize OpenAI client
openai = OpenAI(api_key='YOUR_OPENAI_API_KEY')

def lambda_handler(event, context):
    # Parse the incoming request
    body = json.loads(event['body'])
    query = body['query']
    
    # Retrieve the top-k relevant chunks from ChromaDB
    results = chroma_client.query(query, top_k=5)
    context = " ".join([res['metadata']['text'] for res in results])
    
    # Generate a response using the LLM
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Context: {context}\n\nQuestion: {query}\n\nAnswer:",
        max_tokens=150
    )
    
    # Extract the answer from the LLM response
    answer = response['choices'][0]['text'].strip()
    
    # Return the answer as a JSON response
    return {
        'statusCode': 200,
        'body': json.dumps({'answer': answer})
    }
