#1 imports 
import json
import boto3
#2 Create a client connection - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
client = boto3.client('dynamodb')

def lambda_handler(event, context):
    
#3 Store the user input - date to check room availability 
    print(f"The user input is {event}")
    user_input_date = event['parameters'][0]['value']

#4 Reference the dynamodb table and retrieve data - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/get_item.html
    response = client.get_item (TableName='hotelRoomAvailabilityTable', Key={'date': {'S': user_input_date}})
    #print(response)
    room_inventory_data = response['Item']
    print(room_inventory_data)
    
#5 Format the response as per the requirement of Bedrock Agent Action Group - https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html    
    agent = event['agent']
    actionGroup = event['actionGroup']
    api_path = event['apiPath']
    # get parameters
    get_parameters = event.get('parameters', [])
    

    response_body = {
        'application/json': {
            'body': json.dumps(room_inventory_data)
        }
    }
    
    print(f"The response to agent is {response_body}")
    
    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }
    
    session_attributes = event['sessionAttributes']
    prompt_session_attributes = event['promptSessionAttributes']
    
    api_response = {
        'messageVersion': '1.0', 
        'response': action_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }
        
    return api_response
    print(f"The final response is {api_response}")