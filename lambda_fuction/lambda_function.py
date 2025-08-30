import PyPDF2
import pdfplumber
import json
import boto3
import base64
import uuid
import os
import io
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime')

# Environment variables
S3_BUCKET = os.environ.get('S3_BUCKET', 'trujobs-documents-test-ganesh')  # Replace with your bucket
BEDROCK_EMBEDDING_MODEL = os.environ.get('BEDROCK_EMBEDDING_MODEL', 'amazon.titan-embed-text-v1')
BEDROCK_TEXT_MODEL = os.environ.get('BEDROCK_TEXT_MODEL', 'anthropic.claude-3-haiku-20240307-v1:0')

def lambda_handler(event, context):
    """
    Lambda handler for processing job description PDFs
    
    Expected event structure:
    {
        "body": "{
            \"pdf_content\": \"base64_encoded_pdf\",
            \"document_id\": \"optional_id\", 
            \"metadata\": {
                \"company_name\": \"Example Corp\",
                \"job_title\": \"Senior Software Engineer\"
            }
        }"
    }
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        pdf_content_b64 = body.get('pdf_content', '')
        user_metadata = body.get('metadata', {})
        document_id = body.get('document_id', f"job-{uuid.uuid4()}")
        
        # Extract text from PDF
        logger.info(f"Processing job description document: {document_id}")
        pdf_bytes = base64.b64decode(pdf_content_b64)
        
        # Extract text from PDF
        text_content = extract_text_from_pdf(pdf_bytes)
        if not text_content:
            return create_response(400, {'error': 'Could not extract text from PDF'})
        
        # Extract structured data from job description
        structured_data = extract_job_description_data(text_content, user_metadata)
        
        # Generate embeddings for search
        embeddings = generate_embeddings(text_content, structured_data)
        
        # Create complete job description document
        job_document = {
            'document_id': document_id,
            'document_type': 'job_description',
            'created_at': datetime.utcnow().isoformat(),
            'raw_text': text_content[:10000],  # Store truncated text to save space
            'job_metadata': structured_data.get('job_metadata', {}),
            'requirements': structured_data.get('requirements', {}),
            'job_details': structured_data.get('job_details', {}),
            **embeddings  # Add all embeddings to document
        }
        
        # Save PDF to S3
        s3_uri = save_pdf_to_s3(pdf_bytes, document_id)
        job_document['s3_uri'] = s3_uri
        
        # Calculate job document score based on completeness
        job_document['quality_score'] = calculate_document_quality(job_document)
        
        # Save processed job data to JSON file in S3
        json_uri = save_json_to_s3(job_document, document_id)
        
        return create_response(200, {
            'document_id': document_id,
            'message': 'Job description processed successfully',
            'document': {
                'job_title': structured_data.get('job_metadata', {}).get('job_title', 'Untitled Job'),
                'company_name': structured_data.get('job_metadata', {}).get('company_name', 'Unknown Company'),
                'required_skills': structured_data.get('requirements', {}).get('required_skills', []),
                'experience_required': structured_data.get('job_metadata', {}).get('min_experience_years', 0),
                's3_uri': s3_uri,
                'json_uri': json_uri,
                'quality_score': job_document['quality_score']
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing job description: {str(e)}")
        return create_response(500, {'error': f'Internal server error: {str(e)}'})

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a PDF using PyPDF2"""
    try:
        # Import here to reduce cold start time when function is reused
        import PyPDF2
        
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + " "
            
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        
        # Fallback to another method if available
        try:
            import pdfplumber
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + " "
                return text.strip()
        except Exception as e2:
            logger.error(f"Backup PDF extraction also failed: {str(e2)}")
            return ""

def extract_job_description_data(text_content: str, user_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract structured data from job description text using Claude"""
    
    # Start with user provided metadata
    company_name = user_metadata.get('company_name', 'Unknown Company')
    job_title = user_metadata.get('job_title', 'Untitled Position')
    
    # Define prompt for Claude to extract job details
    extraction_prompt = f"""
    Analyze this job description and extract key information into a structured JSON format.
    
    Job Description:
    {text_content[:8000]}
    
    Return valid JSON with the following structure:
    {{
        "job_metadata": {{
            "job_title": "Full job title",
            "company_name": "{company_name}",
            "location": "Job location",
            "employment_type": "Full-time/Contract/etc",
            "remote_option": "Remote/Hybrid/On-site",
            "min_experience_years": 0,
            "max_experience_years": 0,
            "salary_range": {{
                "min": 0,
                "max": 0,
                "currency": "USD"
            }},
            "industry": "Industry sector"
        }},
        "requirements": {{
            "required_skills": ["skill1", "skill2"],
            "preferred_skills": ["skill1", "skill2"],
            "programming_languages": ["language1", "language2"],
            "frameworks_tools": ["framework1", "tool1"],
            "databases": ["database1", "database2"],
            "cloud_platforms": ["platform1", "platform2"],
            "certifications": ["cert1", "cert2"],
            "education_requirements": {{
                "degree_level": "Bachelor's/Master's/PhD",
                "field_of_study": "Computer Science, etc.",
                "required": true
            }}
        }},
        "job_details": {{
            "key_responsibilities": ["responsibility1", "responsibility2"],
            "benefits": ["benefit1", "benefit2"],
            "company_description": "Brief company description"
        }}
    }}
    
    Extract as much information as possible from the job description. For fields where no information is available, use appropriate default values (empty arrays for lists, 0 for numbers, empty strings for text).
    """
    
    try:
        request_body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": extraction_prompt}]
        })
        
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_TEXT_MODEL,
            contentType='application/json',
            accept='application/json',
            body=request_body
        )
        
        response_body = json.loads(response['body'].read())
        extracted_text = response_body['content'][0]['text']
        
        # Extract JSON from Claude's response
        try:
            # Try direct parsing
            extracted_data = json.loads(extracted_text)
            
        except json.JSONDecodeError:
            # Try finding JSON block in markdown
            import re
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', extracted_text, re.DOTALL)
            if json_match:
                try:
                    extracted_data = json.loads(json_match.group(1))
                except:
                    # Fallback to default structure
                    extracted_data = get_default_job_structure(job_title, company_name)
            else:
                extracted_data = get_default_job_structure(job_title, company_name)
        
        # Ensure the extracted data has the expected structure
        if not all(key in extracted_data for key in ['job_metadata', 'requirements', 'job_details']):
            extracted_data = get_default_job_structure(job_title, company_name)
            
        return extracted_data
        
    except Exception as e:
        logger.error(f"Error extracting job data with Claude: {str(e)}")
        return get_default_job_structure(job_title, company_name)

def get_default_job_structure(job_title: str, company_name: str) -> Dict[str, Any]:
    """Return default job structure when extraction fails"""
    return {
        "job_metadata": {
            "job_title": job_title,
            "company_name": company_name,
            "location": "",
            "employment_type": "Full-time",
            "remote_option": "Unknown",
            "min_experience_years": 0,
            "max_experience_years": 0,
            "salary_range": {
                "min": 0,
                "max": 0,
                "currency": "USD"
            },
            "industry": ""
        },
        "requirements": {
            "required_skills": [],
            "preferred_skills": [],
            "programming_languages": [],
            "frameworks_tools": [],
            "databases": [],
            "cloud_platforms": [],
            "certifications": [],
            "education_requirements": {
                "degree_level": "",
                "field_of_study": "",
                "required": False
            }
        },
        "job_details": {
            "key_responsibilities": [],
            "benefits": [],
            "company_description": ""
        }
    }

def generate_embeddings(text_content: str, structured_data: Dict[str, Any]) -> Dict[str, List[float]]:
    """Generate embeddings for different aspects of the job description"""
    embeddings = {}
    
    # Full content embedding (for general search)
    full_content_embedding = generate_embedding(text_content[:8000])
    if full_content_embedding:
        embeddings['full_content_embedding'] = full_content_embedding
    
    # Requirements embedding (for skills-based search)
    requirements = structured_data.get('requirements', {})
    req_text = " ".join([
        " ".join(requirements.get('required_skills', [])),
        " ".join(requirements.get('preferred_skills', [])),
        " ".join(requirements.get('programming_languages', [])),
        " ".join(requirements.get('frameworks_tools', []))
    ])
    if req_text.strip():
        embeddings['requirements_embedding'] = generate_embedding(req_text)
    
    # Technology stack embedding
    tech_text = " ".join([
        " ".join(requirements.get('programming_languages', [])),
        " ".join(requirements.get('frameworks_tools', [])),
        " ".join(requirements.get('databases', [])),
        " ".join(requirements.get('cloud_platforms', []))
    ])
    if tech_text.strip():
        embeddings['technologies_embedding'] = generate_embedding(tech_text)
    
    # Job title and responsibilities embedding
    job_metadata = structured_data.get('job_metadata', {})
    job_details = structured_data.get('job_details', {})
    title_resp_text = f"{job_metadata.get('job_title', '')} {' '.join(job_details.get('key_responsibilities', []))}"
    if title_resp_text.strip():
        embeddings['title_summary_embedding'] = generate_embedding(title_resp_text)
    
    return embeddings

def generate_embedding(text: str) -> List[float]:
    """Generate embeddings using Amazon Bedrock Titan Embeddings"""
    if not text.strip():
        return []
    
    try:
        request_body = json.dumps({
            "inputText": text[:8000]  # Limit text to 8000 chars
        })
        
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_EMBEDDING_MODEL,
            contentType='application/json',
            accept='application/json',
            body=request_body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['embedding']
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        return []

def save_pdf_to_s3(pdf_bytes: bytes, document_id: str) -> str:
    """Save PDF file to S3"""
    s3_key = f"job_descriptions/{document_id}/{document_id}.pdf"
    
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=pdf_bytes,
            ContentType='application/pdf',
            Metadata={
                'document_type': 'job_description',
                'document_id': document_id,
                'created_at': datetime.utcnow().isoformat()
            }
        )
        
        return f"s3://{S3_BUCKET}/{s3_key}"
        
    except Exception as e:
        logger.error(f"Error saving PDF to S3: {str(e)}")
        return ""

def save_json_to_s3(data: Dict[str, Any], document_id: str) -> str:
    """Save processed job data as JSON to S3"""
    s3_key = f"job_descriptions/{document_id}/{document_id}.json"
    
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(data),
            ContentType='application/json',
            Metadata={
                'document_type': 'job_description_data',
                'document_id': document_id,
                'created_at': datetime.utcnow().isoformat()
            }
        )
        
        return f"s3://{S3_BUCKET}/{s3_key}"
        
    except Exception as e:
        logger.error(f"Error saving JSON to S3: {str(e)}")
        return ""

def calculate_document_quality(job_document: Dict[str, Any]) -> float:
    """Calculate quality score for job document based on completeness"""
    score = 0.0
    
    # Check required skills
    required_skills = job_document.get('requirements', {}).get('required_skills', [])
    if required_skills and len(required_skills) > 0:
        score += 25
    
    # Check experience requirements
    if job_document.get('job_metadata', {}).get('min_experience_years', 0) > 0:
        score += 15
    
    # Check key responsibilities
    key_responsibilities = job_document.get('job_details', {}).get('key_responsibilities', [])
    if key_responsibilities and len(key_responsibilities) > 0:
        score += 20
    
    # Check location information
    if job_document.get('job_metadata', {}).get('location', ''):
        score += 10
    
    # Check remote option information
    if job_document.get('job_metadata', {}).get('remote_option', '') not in ['', 'Unknown']:
        score += 10
    
    # Check tech stack information
    tech_count = len(job_document.get('requirements', {}).get('programming_languages', [])) + \
                 len(job_document.get('requirements', {}).get('frameworks_tools', [])) + \
                 len(job_document.get('requirements', {}).get('databases', [])) + \
                 len(job_document.get('requirements', {}).get('cloud_platforms', []))
    if tech_count > 0:
        score += 20
    
    return min(100.0, score)

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(body)
    }