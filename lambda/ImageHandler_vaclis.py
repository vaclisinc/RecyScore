import base64
import boto3

def lambda_handler(event, context):
    print("Received event:", event)
    
    image_data = base64.b64decode(event['image_data'])
    filename = event.get('filename', f"{event['timestamp']}.jpg")
    
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket='trashcan10', #這裡改成我們的s3 bucket name
        Key=f"iot-images/{filename}",
        Body=image_data,
        ContentType='image/jpeg'
    )
    
    return { "status": "success", "filename": filename }