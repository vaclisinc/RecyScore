import json
import boto3
import os
from decimal import Decimal # 用於處理 DynamoDB 的 Decimal 類型

# 從環境變數讀取 DynamoDB 表名
dynamodb_table_name = os.environ.get('DYNAMODB_TABLE_NAME')
if not dynamodb_table_name:
    raise ValueError("Missing DYNAMODB_TABLE_NAME in environment variables")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table_name)

# 您要追蹤的分類
CATEGORIES = ["廢紙", "紙容器", "塑膠", "金屬", "玻璃"]

class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert a DynamoDB item to JSON."""
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0: # 檢查是否有小數
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    print("GetRecyclingStatsLambda invoked")
    category_counts = {category: 0 for category in CATEGORIES}
    total_score = 0
    items_processed_in_categories = 0 # 只計算屬於指定分類的項目數
    total_items_scanned = 0 # 記錄總共掃描了多少項目

    try:
        response = table.scan()
        items = response.get('Items', [])
        total_items_scanned = len(items)

        while 'LastEvaluatedKey' in response:
            print("Scanning for more items...")
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            new_items = response.get('Items', [])
            items.extend(new_items)
            total_items_scanned += len(new_items)

        print(f"Total items scanned from DynamoDB: {total_items_scanned}")

        for item in items:
            category = item.get('Category')
            score_str = item.get('Score') # 分數是字串

            # 只處理和累計屬於預定分類的項目
            if category in CATEGORIES: # <--- 修改點：檢查分類是否在列表中
                category_counts[category] += 1
                items_processed_in_categories += 1 # <--- 只為有效分類的項目計數

                if score_str:
                    try:
                        total_score += int(score_str) # <--- 修改點：只為有效分類的項目累加分數
                    except ValueError:
                        print(f"Warning: Could not convert score '{score_str}' to int for item with Category '{category}' and ImageKey: {item.get('ImageKey')}")
        
        print(f"Category counts: {category_counts}")
        print(f"Total score (for items in categories): {total_score}")
        print(f"Items processed (within categories): {items_processed_in_categories}")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*', 
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({
                'categories': category_counts,
                'totalScore': total_score,
                'itemsProcessed': items_processed_in_categories # 返回在分類內的項目總數
                # 'totalItemsScanned': total_items_scanned # 如果前端也想顯示這個，可以取消註解
            }, cls=DecimalEncoder)
        }

    except Exception as e:
        print(f"Error processing request: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }

