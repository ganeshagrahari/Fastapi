## 🚀 TruJobs Lambda Deployment Guide

### ✅ Problem Fixed
Your GLIBC compatibility issue is resolved! The deployment package was built using Amazon Linux 2 (same as Lambda runtime).

### 📦 Deployment Package Ready
- **File**: `output/lambda_function.zip` (29MB)
- **Runtime**: Python 3.9 (compatible with Lambda)
- **Dependencies**: All native libraries compiled for Amazon Linux 2

### 🔧 Lambda Function Configuration

#### Basic Settings:
- **Handler**: `lambda_function.lambda_handler`
- **Runtime**: Python 3.9
- **Timeout**: 60 seconds (for PDF processing)
- **Memory**: 512MB minimum

#### Environment Variables:
```bash
S3_BUCKET=trujobs-documents-test-ganesh
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
BEDROCK_TEXT_MODEL=anthropic.claude-3-haiku-20240307-v1:0
```

#### IAM Permissions Required:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::trujobs-documents-test-ganesh/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*:*:foundation-model/amazon.titan-embed-text-v1",
                "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

### 🧪 Test Event (Job Description):
```json
{
    "body": "{\"pdf_content\": \"JVBERi0xLjMKJcTl8uXrp/Og0MTGCjQgMCBvYmoKPDwKL0xlbmd0aCA2NDEKL0ZpbHRlciAvRmxhdGVEZWNvZGUKPj4Kc3RyZWFtCnicPY9BDsIwDESvEuUAVhzbSXKEqgiJA3CArqr2/tvE/QD+N5r3JL8lJZRSSimllP+QNTdz1dzMVf+QNTdz1dzMVXMzV83NXDVz1dzMVXMzV83N\",\"metadata\":{\"company_name\":\"TechCorp\",\"job_title\":\"Senior Data Engineer\"}}"
}
```

### 🔄 Build Process (for future updates):
```bash
# In your project directory:
./build.sh

# Or manually with Docker:
sudo docker build -t lambda-builder .
sudo docker run --rm -v $(pwd)/output:/output lambda-builder
```

### ⚡ Quick Upload Commands:
```bash
# Via AWS CLI (if configured):
aws lambda update-function-code \
    --function-name YourLambdaFunctionName \
    --zip-file fileb://output/lambda_function.zip

# Or upload via AWS Console > Lambda > Functions > Your Function > Code > Upload from > .zip file
```

### 🎯 Success Indicators:
1. No import errors in CloudWatch logs
2. Function executes without GLIBC errors  
3. PDF text extraction works
4. S3 upload succeeds
5. Bedrock API calls succeed
