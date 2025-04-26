import json
import hmac
import hashlib
import base64
import struct
import time
import logging
import urllib.parse
import traceback

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_hotp_token(secret, intervals_no):
    """
    HOTP (HMAC-based One-Time Password) トークンを生成する
    
    Parameters:
    secret (str): Base32エンコードされた秘密鍵
    intervals_no (int): カウンタ値
    
    Returns:
    str: 6桁のHOTPコード
    """
    try:
        # Base32デコード
        secret = secret.upper()
        # パディングを追加
        secret = secret + '=' * ((8 - len(secret) % 8) % 8)
        decoded_secret = base64.b32decode(secret)
        
        # カウンタ値をバイト列に変換
        msg = struct.pack(">Q", intervals_no)
        
        # HMAC-SHA1
        h = hmac.new(decoded_secret, msg, hashlib.sha1).digest()
        
        # 動的切り捨て
        o = h[19] & 15
        
        # コードの生成
        code = ((h[o] & 127) << 24 |
                (h[o + 1] & 255) << 16 |
                (h[o + 2] & 255) << 8 |
                (h[o + 3] & 255))
        
        # 6桁のコードを返す
        return '{0:06d}'.format(code % 1000000)
    except Exception as e:
        logger.error(f"HOTP生成エラー: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def get_totp_token(secret):
    """
    TOTP (Time-based One-Time Password) トークンを生成する
    
    Parameters:
    secret (str): Base32エンコードされた秘密鍵
    
    Returns:
    str: 6桁のTOTPコード
    """
    # 30秒間隔でカウンタ値を計算
    intervals_no = int(time.time()) // 30
    return get_hotp_token(secret, intervals_no)

def lambda_handler(event, context):
    """
    Base32エンコードされた文字列を受け取り、TOTPコードを生成して返す関数
    
    Parameters:
    event (dict): Lambda関数のイベントデータ
    context (object): Lambda関数のコンテキスト
    
    Returns:
    dict: APIGatewayのレスポンス形式
    """
    try:
        # イベント全体をログに記録（デバッグ用）
        logger.info(f"受信イベント: {json.dumps(event)}")
        
        # クエリパラメータからbase32文字列を取得
        query_params = event.get('queryStringParameters', {})
        
        if not query_params or 'secret' not in query_params:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS'
                },
                'body': json.dumps({'error': 'secret parameter is required'})
            }
        
        # secretパラメータを取得してURLデコード
        base32_secret = urllib.parse.unquote(query_params['secret'])
        logger.info(f"処理中のシークレット長: {len(base32_secret)}")
        
        # TOTPコードを生成
        totp_code = get_totp_token(base32_secret)
        
        # 成功レスポンスを返す
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({'totp_code': totp_code})
        }
        
    except Exception as e:
        logger.error(f"エラー: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }
