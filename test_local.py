#!/usr/bin/env python3

import json
import hmac
import hashlib
import base64
import struct
import time
import urllib.parse

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
        print(f"エラー発生: {e}")
        return None

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

if __name__ == "__main__":
    # テスト用の秘密鍵
    test_secret = "A654ICF6XJD3ASSPT62IW53UU2ZPKTXAI3MJWS3J2FY6L33VRAB3ZCFHXMHNLOER"
    
    print(f"秘密鍵: {test_secret}")
    print(f"現在時刻: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    
    try:
        totp_code = get_totp_token(test_secret)
        print(f"生成されたTOTPコード: {totp_code}")
    except Exception as e:
        print(f"エラー発生: {e}")
