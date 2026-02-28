import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root or instance folder
# Priority: 1. instance/.env  2. project root .env  3. environment variables
instance_env = Path(__file__).parent.parent / 'instance' / '.env'
root_env = Path(__file__).parent.parent / '.env'

if instance_env.exists():
    load_dotenv(instance_env)
elif root_env.exists():
    load_dotenv(root_env)
# If neither exists, rely on system environment variables (Docker env_file, etc.)

# =============================================================================
# FLASK/SQLALCHEMY CONFIGURATION
# =============================================================================
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_BINDS = {}

# Database connection - loaded from .env
SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    "mysql+pymysql://license_user:license_password@db:3306/license_tracker"
)

# Database pool settings
SQLALCHEMY_POOL_SIZE = int(os.getenv("SQLALCHEMY_POOL_SIZE", "10"))
SQLALCHEMY_POOL_TIMEOUT = int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "600"))
SQLALCHEMY_POOL_RECYCLE = int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "500"))

# Application secret key - MUST be changed in production!
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

# =============================================================================
# UTILITY PATHS
# =============================================================================
ALMTUTIL_PATH = os.getenv("ALMTUTIL_PATH", "/opt/license_tracker/utils/almutil")
LMTUTIL_PATH = os.getenv("LMTUTIL_PATH", "/opt/license_tracker/utils/lmutil")
RLMTUTIL_PATH = os.getenv("RLMTUTIL_PATH", "/opt/license_tracker/utils/rlmutil")
PARTICLEWORKS_LMUTIL_PATH = os.getenv("PARTICLEWORKS_LMUTIL_PATH", "")

# =============================================================================
# LICENSE SERVER CONFIGURATION
# =============================================================================
# MSC License Servers
APAC_MSC = os.getenv("APAC_MSC", "")
EU_MSC = os.getenv("EU_MSC", "")
AME_MSC = os.getenv("AME_MSC", "")
CLUSTER_MSC = os.getenv("CLUSTER_MSC", "")
MSC_PORT = int(os.getenv("MSC_PORT", "27500"))
AME_MSC_PORT = int(os.getenv("AME_MSC_PORT", "1700"))

# Altair License Servers
EU_ALTAIR = os.getenv("EU_ALTAIR", "")
APAC_ALTAIR = os.getenv("APAC_ALTAIR", "")
EU_UNLIMITED_ALTAIR = os.getenv("EU_UNLIMITED_ALTAIR", "")
APAC_UNLIMITED_ALTAIR = os.getenv("APAC_UNLIMITED_ALTAIR", "")
AME_ALTAIR = os.getenv("AME_ALTAIR", "")
ALTAIR_PORT = int(os.getenv("ALTAIR_PORT", "6200"))

# Other License Servers
PARTICLEWORKS = os.getenv("PARTICLEWORKS", "")
PW_PORT = int(os.getenv("PW_PORT", "27000"))
RECARDO = os.getenv("RECARDO", "")
RECARDO_PORT = int(os.getenv("RECARDO_PORT", "27006"))
MASTA = os.getenv("MASTA", "")
MASTA_PORT = int(os.getenv("MASTA_PORT", "5053"))
RLM = os.getenv("RLM", "")
RLM_PORT = int(os.getenv("RLM_PORT", "5053"))

# =============================================================================
# REDMINE INTEGRATION (SENSITIVE)
# =============================================================================
REDMINE_ADDRESS = os.getenv("REDMINE_ADDRESS", "")
REDMINE_API_KEY = os.getenv("REDMINE_API_KEY", "")
REDMINE_SAFELIST_TOKEN = os.getenv("REDMINE_SAFELIST_TOKEN", "")

# =============================================================================
# AUTHENTICATION CREDENTIALS (SENSITIVE)
# =============================================================================
MASTER_PASSWORD = os.getenv("MASTER_PASSWORD", "")
USERNAME = os.getenv("USERNAME", "")
PASSWORD = os.getenv("PASSWORD", "")
GUEST_SVN_USERNAME = os.getenv("GUEST_SVN_USERNAME", "")
GUEST_SVN_PASSWORD = os.getenv("GUEST_SVN_PASSWORD", "")
LINUX_USER_NAME = os.getenv("LINUX_USER_NAME", "")
LINUX_PASSWORD = os.getenv("LINUX_PASSWORD", "")

# =============================================================================
# OTHER SETTINGS
# =============================================================================
SERVER_IP = os.getenv("SERVER_IP", "")
PORT = int(os.getenv("BACKEND_PORT", "2324"))
DB_NAME = os.getenv("DB_NAME", "")
DB_TYPE = os.getenv("DB_TYPE", "")
SITECODE = os.getenv("SITECODE", "Site Short Code")

