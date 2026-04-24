import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AUTOTASK_USERNAME = os.getenv("AUTOTASK_USERNAME", "")
AUTOTASK_INTEGRATION_CODE = os.getenv("AUTOTASK_INTEGRATION_CODE", "")
AUTOTASK_ZONE_URL = os.getenv("AUTOTASK_ZONE_URL", "")
AUTOTASK_QUEUE_ID = os.getenv("AUTOTASK_QUEUE_ID", "")
ITGLUE_API_KEY = os.getenv("ITGLUE_API_KEY", "")
ITGLUE_BASE_URL = os.getenv("ITGLUE_BASE_URL", "https://api.itglue.com")
PASSPORTAL_API_KEY = os.getenv("PASSPORTAL_API_KEY", "")
PASSPORTAL_BASE_URL = os.getenv("PASSPORTAL_BASE_URL", "https://vault.passportal.com")
VSA_BASE_URL = os.getenv("VSA_BASE_URL", "")
VSA_USERNAME = os.getenv("VSA_USERNAME", "")
VSA_PASSWORD = os.getenv("VSA_PASSWORD", "")