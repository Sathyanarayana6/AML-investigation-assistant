import json
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

# Load credentials from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get values from .env file
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-6")

# Create Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)


def call_claude(prompt, system_prompt=None, max_tokens=1024, temperature=0.7):
    """
    Send a message to Claude and get a response.
    """
    try:
        # Build messages
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Build request body
        request_body = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
            "anthropic_version": "bedrock-2023-05-31"
        }

        # Add system prompt if provided
        if system_prompt:
            request_body["system"] = system_prompt

        # Call Claude via AWS Bedrock
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )

        # Parse response
        response_body = json.loads(response['body'].read())

        if 'content' in response_body and len(response_body['content']) > 0:
            result_text = response_body['content'][0]['text']
            logger.info(f"Claude responded successfully")
            return result_text
        else:
            raise ValueError("No content in Claude response")

    except ClientError as e:
        logger.error(f"Bedrock API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise


def call_claude_with_json_response(prompt, system_prompt=None, max_tokens=1024):
    """
    Call Claude and parse response as JSON.
    """
    response_text = call_claude(prompt, system_prompt, max_tokens)

    try:
        # Try direct JSON parse
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Handle ```json ... ``` blocks
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
            return json.loads(json_str)
        else:
            raise


# TEST
if __name__ == "__main__":
    print("🧪 Testing Bedrock Connection...")
    print(f"   Region: {AWS_REGION}")
    print(f"   Model: {BEDROCK_MODEL_ID}")
    print("")

    try:
        response = call_claude("Respond with exactly this word: SUCCESS")

        if "SUCCESS" in response:
            print("✅ Bedrock connection working!")
            print(f"   Claude responded: {response}")
        else:
            print(f"⚠️  Unexpected response: {response}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("")
        print("Troubleshooting:")
        print("  1. Check .env has correct AWS credentials")
        print("  2. Verify Bedrock access in AWS Console")
        print("  3. Confirm region is us-east-1")