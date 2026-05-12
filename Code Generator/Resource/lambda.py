import boto3
import botocore.config
import json
from datetime import datetime


def generate_code_using_bedrock(message: str, language: str) -> str:

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
            "max_tokens": 2048,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": f"""
Generate only clean {language} code.

Do not add explanations.
Do not add markdown.
Do not add triple backticks.

Task:
{message}
"""
                }
            ]
        }

        response = bedrock.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-6",
            body=json.dumps(body)
        )

        response_body = json.loads(response['body'].read())

        generated_code = response_body['content'][0]['text']

        # Remove markdown formatting if present
        generated_code = generated_code.replace("```python", "")
        generated_code = generated_code.replace("```", "")
        generated_code = generated_code.strip()

        return generated_code

    except Exception as e:
        print(f"Error generating the code: {e}")
        return ""


def save_code_to_s3_bucket(code, s3_bucket, s3_key):

    s3 = boto3.client('s3')

    try:
        s3.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=code
        )

        print("Code saved to S3")

    except Exception as e:
        print(f"Error saving code to S3: {e}")


def lambda_handler(event, context):

    try:

        # Read API request body
        event_body = json.loads(event['body'])

        message = event_body['message']
        language = event_body['key']

        print(message, language)

        # Generate code using Bedrock
        generated_code = generate_code_using_bedrock(
            message,
            language
        )

        if generated_code:

            # Create unique file name
            current_time = datetime.now().strftime('%H%M%S')

            extension = language.lower()

            s3_key = f'code-output/{current_time}.{extension}'

            s3_bucket = 'bedrock-course-bucket23'

            # Save generated code in S3
            save_code_to_s3_bucket(
                generated_code,
                s3_bucket,
                s3_key
            )

            # Simple success response
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'message': 'Code generated successfully. Check your S3 bucket.'
                })
            }

        else:

            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Code generation failed'
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