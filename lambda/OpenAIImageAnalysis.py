import json
import boto3
import os
import base64
from openai import OpenAI
import urllib.parse
import time # <--- 新增 time 模組，用於記錄時間戳

# 從環境變數讀取 OpenAI API Key 和 DynamoDB 表名
openai_api_key = os.environ.get('OPENAI_API_KEY')
dynamodb_table_name = os.environ.get('DYNAMODB_TABLE_NAME') # <--- 讀取表名
if not openai_api_key:
    raise ValueError("Missing OpenAI API Key in environment variables")
if not dynamodb_table_name:
    raise ValueError("Missing DYNAMODB_TABLE_NAME in environment variables")

# 初始化 S3、OpenAI 和 DynamoDB 客戶端
s3 = boto3.client('s3')
client = OpenAI(api_key=openai_api_key)
dynamodb = boto3.resource('dynamodb') # <--- 改用 resource 更方便操作 Item
table = dynamodb.Table(dynamodb_table_name) # <--- 取得 Table 物件

# 您要使用的特定 Prompt (保持不變)
RECYCLING_PROMPT = """
你現在是一個環保專家，要檢測使用者是不是有正常做資源回收
你的工作有三個：
1. 分辨照片中的物品是否可回收
2. 若是可回收，將回收物品分類成：廢紙、紙容器、塑膠、金屬、玻璃；否則，分類成：
2. 利用你對資源回收的知識，判斷照片中要拿去資源回收的物品是不是已經有經過妥當的處理，像是將內部清洗乾淨、飲料封膜是否有撕等等，並打 1 ~ 10 的分數
最後請你只要輸出一個 json 格式的結果就好，例如：{"分類": "紙容器", "分數": "5"}，不要輸出其他任何文字或符號！
"""

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))
    image_key_for_db = None # 初始化變數以存儲 S3 Key

    # 1. 從 S3 事件中取得儲存貯體名稱和物件金鑰
    try:
        # ... (解析 S3 event 的程式碼保持不變) ...
        s3_record = event['Records'][0]['s3']
        bucket_name = s3_record['bucket']['name']
        object_key = s3_record['object']['key']
        object_key = urllib.parse.unquote_plus(object_key)
        image_key_for_db = object_key # <--- 儲存 object key 以用作主鍵

        print(f"Processing object '{object_key}' from bucket '{bucket_name}'")

    except (KeyError, IndexError) as e:
        # ... (錯誤處理保持不變) ...
        return {'statusCode': 400, 'body': json.dumps('Error parsing S3 event structure.')}

    # 確保我們有 image_key 可用
    if not image_key_for_db:
         print("Could not determine ImageKey from S3 event.")
         return {'statusCode': 400, 'body': json.dumps('Could not determine ImageKey.')}

    try:
        # 2. 從 S3 下載圖片 (保持不變)
        # ... (下載 S3 圖片的程式碼) ...
        s3_response = s3.get_object(Bucket=bucket_name, Key=object_key)
        image_content = s3_response['Body'].read()

        # 3. 將圖片轉換為 Base64 編碼 (保持不變)
        # ... (Base64 編碼的程式碼) ...
        base64_image = base64.b64encode(image_content).decode('utf-8')
        image_type = "jpeg" if object_key.lower().endswith((".jpg", ".jpeg")) else "png"

        # 4. 呼叫 OpenAI Vision API (使用 gpt-4o 或其他可用模型)
        print("Calling OpenAI Vision API...")
        response = client.chat.completions.create(
            model="gpt-4o", # <--- 確保使用有效的視覺模型
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": RECYCLING_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=150 # 稍微減少 tokens 以節省成本，確保能容納 JSON 即可
        )
        print("OpenAI API call successful.")

        # 5. 取得並處理回應
        analysis_result_str = response.choices[0].message.content.strip() # 去除可能的首尾空白
        print("Raw OpenAI Analysis Result String:")
        print(analysis_result_str)

        # 6. *** 新增：解析 JSON 並寫入 DynamoDB ***
        try:
            print("Parsing OpenAI result string as JSON...")
            analysis_data = json.loads(analysis_result_str) # <--- 解析 JSON 字串
            print("Parsed JSON data:", analysis_data)

            # 從解析後的字典中獲取分類和分數
            category = analysis_data.get("分類")
            score = analysis_data.get("分數")

            if category is None or score is None:
                 raise ValueError("Parsed JSON is missing '分類' or '分數' key.")

            print(f"Category: {category}, Score: {score}")

            # 準備寫入 DynamoDB 的項目
            timestamp = str(time.time()) # 記錄處理時間戳
            item_to_put = {
                'ImageKey': image_key_for_db, # 使用 S3 物件鍵作為主鍵
                'Category': category,
                'Score': score, # 根據您的 Prompt，分數是字串
                # 'ScoreAsNumber': int(score), # 可選：如果想存儲數字版本
                'ProcessingTimestamp': timestamp,
                'RawAnalysis': analysis_result_str # 儲存原始分析結果以供參考
            }

            print("Putting item into DynamoDB table:", dynamodb_table_name)
            print("Item data:", item_to_put)

            # 執行寫入操作
            put_response = table.put_item(Item=item_to_put)

            print("Successfully put item to DynamoDB.")
            print("DynamoDB Put Response:", put_response)

        except json.JSONDecodeError as json_err:
            print(f"Error parsing OpenAI result as JSON: {json_err}")
            print("OpenAI Result that caused error:", analysis_result_str)
            # 即使解析失敗，可能也想記錄原始數據或其他操作
            # 這裡我們先返回錯誤，或者您可以選擇儲存部分信息
            return {'statusCode': 500, 'body': json.dumps(f'Failed to parse OpenAI JSON response: {analysis_result_str}')}
        except ValueError as val_err:
             print(f"Error processing parsed JSON: {val_err}")
             return {'statusCode': 500, 'body': json.dumps(f'Invalid JSON content: {str(val_err)}')}
        except Exception as db_err: # 捕捉 Boto3 可能的錯誤
            print(f"Error putting item to DynamoDB: {db_err}")
            import traceback
            traceback.print_exc()
            return {'statusCode': 500, 'body': json.dumps(f'Error saving to DynamoDB: {str(db_err)}')}


        # 7. 返回成功回應
        return {
            'statusCode': 200,
            # 在 body 中返回解析後的數據或原始數據都可以
            'body': json.dumps({
                'message': 'Image analyzed and result saved successfully!',
                'saved_data': { # 返回寫入資料庫的內容，方便前端或呼叫者確認
                     'ImageKey': image_key_for_db,
                     'Category': category,
                     'Score': score
                }
                # 'analysis': analysis_result_str # 或者返回原始分析字串
            })
        }

    # ... (處理 NoSuchKey 和其他通用 Exception 的程式碼保持不變) ...
    except s3.exceptions.NoSuchKey:
        print(f"Error: Object '{image_key_for_db}' not found in bucket '{bucket_name}'.")
        return {'statusCode': 404, 'body': json.dumps('Image file not found.')}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing image: {str(e)}')
        }

