# Use Amazon Linux 2 - same as Lambda runtime
FROM amazonlinux:2

# Install Python 3.9 (default for Amazon Linux 2) and development tools
RUN yum update -y && \
    yum install -y python3 python3-pip python3-devel gcc zip && \
    yum clean all

# Set working directory
WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt -t ./package/

# Copy Lambda function
COPY lambda_function.py ./package/

# Create deployment zip
RUN cd package && zip -r ../lambda_function.zip .

# Set entrypoint to copy zip to mounted volume
CMD ["cp", "/build/lambda_function.zip", "/output/"]
