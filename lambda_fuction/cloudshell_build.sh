#!/bin/bash

# 🚀 TruJobs Lambda Deployment Builder
# Run this script in AWS CloudShell or Amazon Linux 2 EC2 instance

echo "🚀 Setting up Lambda deployment environment..."

# Create build directory
mkdir -p /tmp/lambda-build
cd /tmp/lambda-build

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --target ./package \
    boto3==1.34.162 \
    PyPDF2==3.0.1 \
    pdfplumber==0.10.3 \
    requests==2.31.0

# Download your lambda function (replace with your actual code)
echo "📄 Add your lambda_function.py to the package directory..."
echo "You need to copy your lambda_function.py into ./package/"

# Create zip file
echo "🗜️ Creating deployment package..."
cd package
zip -r ../lambda_function.zip .
cd ..

echo "✅ Deployment package created: $(pwd)/lambda_function.zip"
echo "📊 Package size: $(du -h lambda_function.zip | cut -f1)"
echo ""
echo "🎯 Instructions:"
echo "1. Copy your lambda_function.py to ./package/"
echo "2. Run: cd package && zip -r ../lambda_function.zip ."
echo "3. Download lambda_function.zip"
echo "4. Upload to Lambda function"
