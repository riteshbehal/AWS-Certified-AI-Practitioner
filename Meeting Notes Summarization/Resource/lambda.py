import boto3
import botocore.config
import json
import base64
from datetime import datetime
from email import message_from_bytes


def extract_text_from_multipart(data):

    msg = message_from_bytes(data)

    text_content = ''

    if msg.is_multipart():

        for part in msg.walk():

            if part.get_content_type() == "text/plain":

                text_content += part.get_payload(
                    decode=True
                ).decode('utf-8') + "\n"

    else:

        if msg.get_content_type() == "text/plain":

            text_content = msg.get_payload(
                decode=True
            ).decode('utf-8')

    return text_content.strip() if text_content else None


def generate_summary_from_bedrock(content: str) -> str:

    try:

        bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-west-2",
            config=botocore.config.Config(
                read_timeout=300,
                retries={'max_attempts': 3}
            )
        )

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": f"""
Summarize the following meeting notes in simple points:

{content}
"""
                }
            ]
        }

        response = bedrock.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-6",
            body=json.dumps(body)
        )

        response_body = json.loads(
            response['body'].read()
        )

        summary = response_body['content'][0]['text']

        return summary.strip()

    except Exception as e:

        print(f"Error generating the summary: {e}")

        return ""


def save_summary_to_s3_bucket(summary, s3_bucket, s3_key):

    s3 = boto3.client('s3')

    try:

        s3.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=summary
        )

        print("Summary saved to S3")

    except Exception as e:

        print(f"Error saving summary to S3: {e}")


def lambda_handler(event, context):

    try:

        # Decode multipart/form-data body
        decoded_body = base64.b64decode(event['body'])

        # Extract uploaded text content
        text_content = extract_text_from_multipart(
            decoded_body
        )

        if not text_content:

            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Failed to extract content'
                })
            }

        # Generate summary
        summary = generate_summary_from_bedrock(
            text_content
        )

        if summary:

            current_time = datetime.now().strftime('%H%M%S')

            s3_key = f'summary-output/{current_time}.txt'

            s3_bucket = 'bedrock-course-bucket23'

            # Save summary in S3
            save_summary_to_s3_bucket(
                summary,
                s3_bucket,
                s3_key
            )

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'message': 'Summary generated successfully. Check your S3 bucket.'
                })
            }

        else:

            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Summary generation failed'
                })
            }

    except Exception as e:

        print(f"Lambda Error: {e}")

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': str(e)
            })
        }