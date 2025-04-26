#!/bin/bash

# エラー発生時に停止
set -e

echo "TOTP Generator Lambda デプロイスクリプト (Docker不要版)"
echo "========================================"

# 変数設定
FUNCTION_NAME="totp-generator"
RUNTIME="python3.9"
HANDLER="lambda_function.lambda_handler"
REGION="ap-northeast-1"  # 必要に応じて変更してください

# AWS アカウントIDの取得
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS アカウントID: $ACCOUNT_ID"

# Lambda関数のコードをパッケージ化
echo "Lambda関数をパッケージ化しています..."
zip -r lambda_function.zip lambda_function.py

# 実行ロールの作成（存在しない場合）
ROLE_NAME="lambda-totp-execution-role"
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

if ! aws iam get-role --role-name $ROLE_NAME > /dev/null 2>&1; then
  echo "Lambda実行ロールを作成しています..."
  
  # 信頼ポリシーを作成
  cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

  # ロールを作成
  aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file://trust-policy.json

  # 基本的なLambda実行ポリシーをアタッチ
  aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
  # ロールが伝播するまで少し待機
  echo "IAMロールが伝播するまで待機しています..."
  sleep 10
  
  ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query Role.Arn --output text)
else
  echo "既存のLambda実行ロールを使用します: $ROLE_NAME"
fi

echo "ロールARN: $ROLE_ARN"

# Lambda関数が存在するか確認
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION > /dev/null 2>&1; then
  echo "既存のLambda関数を更新しています..."
  aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://lambda_function.zip \
    --region $REGION
else
  echo "新しいLambda関数を作成しています..."
  aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime $RUNTIME \
    --handler $HANDLER \
    --zip-file fileb://lambda_function.zip \
    --role $ROLE_ARN \
    --region $REGION
    
  # Function URLを設定
  echo "Lambda Function URLを設定しています..."
  URL_CONFIG=$(aws lambda create-function-url-config \
    --function-name $FUNCTION_NAME \
    --auth-type NONE \
    --region $REGION \
    --query FunctionUrl \
    --output text)
    
  echo "Function URL: $URL_CONFIG"
  
  # Function URLへのパブリックアクセスを許可
  echo "Lambda Function URLへのアクセス権限を設定しています..."
  aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id FunctionURLAllowPublicAccess \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE \
    --region $REGION
fi

echo "デプロイが完了しました！"
