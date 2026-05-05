#1 imports - For room booking - Boto3, json and uuid
import json
import boto3
import uuid

#2 Create a client connection -  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
client = boto3.client('dynamodb')

#3 Store the user input - Print the event details from agent
def lambda_handler(event, context):
    print(f"The user input from Agent is {event}")
    input_data = event

#4 Retrieve the data from event- guestName, checkInDate, numberofNights and roomType (print out event if required)    
    input_data = event['requestBody']['content']['application/json']['properties']
    print(type(input_data))
    print(input_data)
    for item in input_data:
        if item['name'] == 'guestName':
            guestName = item['value']
        elif item['name'] == 'checkInDate':a
            checkInDate = item['value']
        elif item['name'] == 'numberofNights':
            numberofNights = item['value']
        elif item['name'] == 'roomType':
            roomType = item['value']    
    print(guestName)    

    #5. Get Room Availability from hotelRoomAvailabilityTable using get_item method https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/get_item.html
    response = client.get_item (TableName='hotelRoomAvailabilityTable', Key={'date': {'S': checkInDate}})
    print(response)
    room_inventory_data = response['Item']
    print(room_inventory_data)

    #6. Get room inventory data for SeaView Rooms and GardenView rooms, convert to string and print values
    current_gardenViewInventory = int (room_inventory_data['gardenView']['S'])
    current_seaViewInventory = int(room_inventory_data['seaView']['S'])
    print(f"The garden view inventory is : {current_gardenViewInventory}")
    print(f"Sea view inventory is : {current_seaViewInventory}")

    #7 If inventory for gardenview and seaview = 0; send error message to user - No rooms available for the specified date
    if current_gardenViewInventory == 0 and current_seaViewInventory == 0:
        response = {
            'statusCode': 404,
            'body': json.dumps({'error': 'No rooms available for the specified date'})}
        print(response)
        return response  

    else:  
    #8 Generate unique booking ID to store in dynamodb table along with booking and send back booking id to user
        bookingID = str(uuid.uuid4())
    
    #9 Create booking record by inserting this data into hotelRoomBookingTable using boto3 put_item method - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/put_item.html
        response_booking = client.put_item(
        TableName='hotelRoomBookingTable',
        Item={
                'bookingID':{"S" : bookingID},
                'checkInDate':{"S" : checkInDate},
                'roomType': {"S" : roomType},
                'guestName': {"S" : guestName},
                'numberofNights':{"S" : numberofNights}})

    #10 Print return bookingID    
        print(f"The response from Lambda is {bookingID}")   


    #11 Add attributes the Bedrock Agents expects -  https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html   
        agent = event['agent']
        actionGroup = event['actionGroup']
        api_path = event['apiPath']

        # post parameters
        post_parameters = event['requestBody']['content']['application/json']['properties']

        response_body = {
            'application/json': {
                'body': json.dumps(bookingID)
            }
        }
        
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


