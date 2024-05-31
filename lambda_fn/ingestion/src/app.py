import boto3
import fitz  # PyMuPDF
import io 
from docx import Document
from sentence_transformers import SentenceTransformer
from chromadb import Client

s3 = boto3.client('s3')
chroma_client = Client()
model = SentenceTransformer('all-MiniLM-L6-v2')

def lambda_handler(event, context):
    # Get the bucket and object key from the S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Retrieve the file from S3
    file_obj = s3.get_object(Bucket=bucket, Key=key)
    file_content = file_obj['Body'].read()
    
    # Determine the file type and extract text
    if key.endswith('.pdf'):
        text = extract_text_from_pdf(file_content)
    elif key.endswith('.docx'):
        text = extract_text_from_docx(file_content)
    else:
        raise ValueError("Unsupported file type")
    
    # Split the text into chunks
    chunks = split_into_chunks(text)
    
    # Generate vectors for each chunk
    vectors = model.encode(chunks)
    
    # Store the vectors and their corresponding text chunks in ChromaDB
    for chunk, vector in zip(chunks, vectors):
        chroma_client.insert(vector=vector, metadata={'text': chunk, 'source': key})

def extract_text_from_pdf(content):
    # Open the PDF file
    pdf = fitz.open(stream=content, filetype='pdf')
    text = ""
    # Extract text from each page
    for page in pdf:
        text += page.get_text()
    return text

def extract_text_from_docx(content):
    # Open the DOCX file
    doc = Document(io.BytesIO(content))
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def split_into_chunks(text, chunk_size=512):
    # Split text into words
    words = text.split()
    # Create chunks of the specified size
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
