Sure! Here's a clean README for your project:

---

# RAG Chatbot Application with AWS

This project demonstrates how to build a Retrieval-Augmented Generation (RAG) chatbot application using AWS services. The application consists of two AWS Lambda functions:

1. **Data Ingestion and Preprocessing Lambda**: Handles file uploads, processes PDF and DOC files, splits them into chunks, and stores them in ChromaDB.
2. **Query Handling Lambda**: Handles user queries, retrieves relevant chunks from ChromaDB, and generates responses using an LLM (e.g., OpenAI GPT-3).

## Architecture

![chatbot_architecture drawio(2)](https://github.com/ahdarwiiish/chatbot-assessment/assets/137199275/677b0d87-7559-4249-857f-369509f9a206)

The architecture involves the following AWS services:
- **Amazon S3**: Stores PDF and DOC files.
- **AWS Lambda**: Executes the backend logic.
- **Amazon API Gateway**: Exposes the query handling endpoint.
- **ChromaDB**: Vector database to store and retrieve document chunks.
- **OpenAI API**: Generates responses using a language model.

## Prerequisites

- AWS account
- Python 3.x
- AWS CLI
- OpenAI API key

## Setup

### Step 1: Data Ingestion and Preprocessing Lambda

1. **Create a Lambda Function**

    ```bash
    aws lambda create-function \
        --function-name DataIngestionLambda \
        --runtime python3.8 \
        --role <IAM_ROLE_ARN> \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://package.zip
    ```

2. **Set Up S3 Trigger**

    - Go to the S3 bucket and create an event notification to trigger the Lambda function on object creation.

3. **Lambda Function Code**

    ```python
    import boto3
    import fitz  # PyMuPDF
    from docx import Document
    from sentence_transformers import SentenceTransformer
    from chromadb import Client

    s3 = boto3.client('s3')
    chroma_client = Client()
    model = SentenceTransformer('all-MiniLM-L6-v2')

    def lambda_handler(event, context):
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        file_obj = s3.get_object(Bucket=bucket, Key=key)
        file_content = file_obj['Body'].read()

        if key.endswith('.pdf'):
            text = extract_text_from_pdf(file_content)
        elif key.endswith('.docx'):
            text = extract_text_from_docx(file_content)
        else:
            raise ValueError("Unsupported file type")

        chunks = split_into_chunks(text)
        vectors = model.encode(chunks)

        for chunk, vector in zip(chunks, vectors):
            chroma_client.insert(vector=vector, metadata={'text': chunk, 'source': key})

    def extract_text_from_pdf(content):
        pdf = fitz.open(stream=content, filetype='pdf')
        text = ""
        for page in pdf:
            text += page.get_text()
        return text

    def extract_text_from_docx(content):
        doc = Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])

    def split_into_chunks(text, chunk_size=512):
        words = text.split()
        return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    ```

### Step 2: Query Handling Lambda

1. **Create a Lambda Function**

    ```bash
    aws lambda create-function \
        --function-name QueryHandlingLambda \
        --runtime python3.8 \
        --role <IAM_ROLE_ARN> \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://package.zip
    ```

2. **Set Up API Gateway**

    - Create a new REST API in API Gateway.
    - Create a new resource `/query` and a POST method.
    - Integrate the POST method with the QueryHandlingLambda function.
    - Deploy the API to a stage (e.g., `dev`).

3. **Lambda Function Code**

    ```python
    import json
    import boto3
    from chromadb import Client
    from openai import OpenAI

    chroma_client = Client()
    openai = OpenAI(api_key='YOUR_OPENAI_API_KEY')

    def lambda_handler(event, context):
        body = json.loads(event['body'])
        query = body['query']

        results = chroma_client.query(query, top_k=5)
        context = " ".join([res['metadata']['text'] for res in results])

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Context: {context}\n\nQuestion: {query}\n\nAnswer:",
            max_tokens=150
        )

        answer = response['choices'][0]['text'].strip()
        return {
            'statusCode': 200,
            'body': json.dumps({'answer': answer})
        }
    ```

## Deployment

1. **Package Dependencies**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install boto3 fitz PyMuPDF python-docx sentence-transformers chromadb openai
    cd venv/lib/python3.*/site-packages
    zip -r9 ${OLDPWD}/package.zip .
    cd $OLDPWD
    zip -g package.zip lambda_function.py
    ```

2. **Upload to Lambda**

    - Upload the `package.zip` file for both Lambda functions using the AWS Lambda Console.

## Testing

1. **Upload Files**

    - Upload PDF and DOCX files to the S3 bucket.

2. **Invoke API**

    - Send a POST request to the API Gateway endpoint with a JSON body containing a query. For example:

    ```json
    {
      "query": "What is the process for handling user queries in AWS Lambda?"
    }
    ```

3. **Check Responses**

    - Verify that the responses are relevant and correctly generated by the LLM.

## Notes

- Ensure your ChromaDB instance is accessible from your Lambda functions.
- Adjust the chunk size and other parameters as needed based on your specific use case.

## License

This project is licensed under the MIT License.
 
