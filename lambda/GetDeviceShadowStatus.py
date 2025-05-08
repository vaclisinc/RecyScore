import boto3
import json
import os

def lambda_handler(event, context):
    client = boto3.client('iot-data', region_name='us-east-1')
    thing_name = 'RaspberryPi_Cam'  # 你的裝置名稱

    response = client.get_thing_shadow(thingName=thing_name)
    streamingBody = response["payload"]
    json_state = json.loads(streamingBody.read())
    
    # 取出狀態與時間戳
    status = json_state["state"]["reported"].get("status", "unknown")
    timestamp = json_state["metadata"]["reported"]["status"]["timestamp"]

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': status,
            'timestamp': timestamp
        })
    }