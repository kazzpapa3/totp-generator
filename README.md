# TOTP Generator Lambda Function

このプロジェクトは、Base32エンコードされた秘密鍵を使用してTOTPコードを生成するAWS Lambda関数を提供します。

## 機能

- Base32エンコードされた秘密鍵をクエリパラメータとして受け取る
- 標準的なTOTPアルゴリズム（RFC 6238）に基づいてコードを生成
- Lambda Function URLを通じてアクセス可能
## 使用方法

Lambda Function URLにアクセスし、`secret`クエリパラメータにBase32エンコードされた秘密鍵を指定します：

```
https://${your-lambda-function}.lambda-url.ap-northeast-1.on.aws/?secret=JBSWY3DPEHPK3PXP
```

レスポンス例：

```json
{
  "totp_code": "123456"
}
```

## デプロイ方法

新しい環境にデプロイする場合は、以下のスクリプトを実行します：

```bash
./deploy-without-docker.sh
```

このスクリプトは以下の処理を行います：
- Lambda関数のコードをパッケージ化
- Lambda実行ロールを作成（存在しない場合）
- Lambda関数をデプロイ
- Lambda Function URLを設定

### 注意: Function URLのアクセス権限設定

デプロイ後、Lambda Function URLにアクセスできない場合（"Forbidden"エラーが発生する場合）は、以下のコマンドを実行して Function URLへのパブリックアクセスを許可する必要があります：

```bash
aws lambda add-permission \
  --function-name totp-generator \
  --statement-id FunctionURLAllowPublicAccess \
  --action lambda:InvokeFunctionUrl \
  --principal "*" \
  --function-url-auth-type NONE \
  --region ap-northeast-1
```

このコマンドは、Lambda Function URLへのパブリックアクセスを許可するリソースベースのポリシーを追加します。

## ファイル構成

- `lambda_function.py` - Lambda関数のメインコード
- `deploy-without-docker.sh` - デプロイスクリプト
- `test_local.py` - ローカルでのTOTP生成テスト用スクリプト
- `README.md` - このドキュメント
- `init.md` - 元の要件定義

## セキュリティ上の注意

- 本番環境では、適切な認証と認可を設定してください
- 秘密鍵は安全に管理し、ログに記録しないようにしてください
- 必要に応じてHTTPS通信を強制してください

## 追記

本リポジトリは全て、Amazon Q Developer for CLI によって作成されたものとなります。
この追記部分以外、全て生成 AI による生成物ですので、適宜リスク判断ください。
