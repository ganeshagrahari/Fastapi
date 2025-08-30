#!/bin/bash

# Build Lambda deployment package using Docker
echo "🚀 Building Lambda deployment package with Amazon Linux 2..."

# Create output directory
mkdir -p output

# Build Docker image
echo "📦 Building Docker image..."
docker build -t lambda-builder .

# Run container and extract zip
echo "🔧 Creating deployment package..."
docker run --rm -v $(pwd)/output:/output lambda-builder

# Check if zip was created
if [ -f "output/lambda_function.zip" ]; then
    echo "✅ Success! Deployment package created: output/lambda_function.zip"
    echo "📊 Package size: $(du -h output/lambda_function.zip | cut -f1)"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Upload output/lambda_function.zip to your Lambda function"
    echo "2. Set handler to: lambda_function.lambda_handler"
    echo "3. Set timeout to at least 30 seconds"
    echo "4. Add environment variables for S3_BUCKET, etc."
else
    echo "❌ Failed to create deployment package"
    exit 1
fi
