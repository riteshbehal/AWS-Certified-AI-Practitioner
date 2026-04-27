import boto3
import json

def lambda_handler(event, context):

    # 🔹 Step 1: Create Bedrock client
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # 🔹 Step 2: Model ID (Titan Embeddings V2)
    model_id = "amazon.titan-embed-text-v2:0"

    # 🔹 Step 3: Get input text (dynamic or default)
    input_text = event.get("text", "What is the price of apple?")

    # 🔹 Step 4: Create request
    request_body = {
        "inputText": input_text
    }

    # 🔹 Step 5: Convert to JSON
    request = json.dumps(request_body)

    # 🔹 Step 6: Call Bedrock model
    response = client.invoke_model(
        modelId=model_id,
        body=request
    )

    # 🔹 Step 7: Read response
    response_body = json.loads(response["body"].read())

    embedding = response_body["embedding"]
    token_count = response_body["inputTextTokenCount"]

    # 🔥 Step 8: Print logs (CloudWatch)
    print("===== DEBUG LOGS =====")
    print("Input Text:", input_text)
    print("Token Count:", token_count)
    print("Embedding Size:", len(embedding))
    print("First 10 Embedding Values:", embedding[:10])

    # 🔹 Step 9: Return response (avoid full embedding)
    return {
        "statusCode": 200,
        "body": {
            "input": input_text,
            "token_count": token_count,
            "embedding_size": len(embedding),
            "sample_embedding": embedding[:10]   # only sample
        }
    }
