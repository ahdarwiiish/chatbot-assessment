import json
import boto3
from botocore.stub import Stubber
from lambda_fn.ingestion.src import lambda_handler   

def create_s3_stub():
    s3_client = boto3.client('s3')
    stubber = Stubber(s3_client)

    # Define the file content  
    sample_pdf_content = b'%PDF-1.4 ... end of sample PDF ...'

    response = {
        'Body': sample_pdf_content,
        'ResponseMetadata': {
            'HTTPStatusCode': 200
        }
    }

    expected_params = {'Bucket': 'source-bucket', 'Key': 'FILE1.pdf'}
    stubber.add_response('get_object', response, expected_params)
    stubber.activate()

    return s3_client

def main():
    # Load the test event
    with open('test_event.json') as f:
        event = json.load(f)

    # Create the S3 client stub
    s3_client = create_s3_stub()

    # Inject the stubbed client into the boto3 session used by the Lambda function
    boto3.Session().client = lambda service_name: s3_client if service_name == 's3' else boto3.client(service_name)

    # Call the lambda handler
    lambda_handler(event, None)

if __name__ == '__main__':
    main()
