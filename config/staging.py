import os

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# MySQL database connection via Docker (default)
SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    "mysql+pymysql://license_user:license_password@db:3306/license_tracker"
)

SQLALCHEMY_BINDS = {}

SECRET_KEY = os.getenv("SECRET_KEY", default="change-me")
import datetime
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_POOL_TIMEOUT = 600
SQLALCHEMY_POOL_RECYCLE = 500 
ALMTUTIL_PATH=os.getenv("ALMTUTIL_PATH", default="/opt/license_tracker/utils/almutil")
LMTUTIL_PATH=os.getenv("LMTUTIL_PATH", default="/opt/license_tracker/utils/lmutil")
RLMTUTIL_PATH=os.getenv("RLMTUTIL_PATH", default="/opt/license_tracker/utils/rlmutil")
APAC_MSC=os.getenv("APAC_MSC", default="")
EU_MSC=os.getenv("EU_MSC", default="")
AME_MSC=os.getenv("AME_MSC", default="")
CLUSTER_MSC=os.getenv("CLUSTER_MSC", default="")
MSC_PORT = 27500
AME_MSC_PORT= 1700
ALTAIR_PORT = 6200
PW_PORT = 27000
RECARDO_PORT = 27006
MASTA_PORT = 5053
RLM_PORT = 5053
EU_ALTAIR= os.getenv("EU_ALTAIR", default="")
APAC_ALTAIR= os.getenv("APAC_ALTAIR", default="")
EU_UNLIMITED_ALTAIR= os.getenv("EU_UNLIMITED_ALTAIR", default="")
APAC_UNLIMITED_ALTAIR= os.getenv("APAC_UNLIMITED_ALTAIR", default="")
AME_ALTAIR=os.getenv("AME_ALTAIR", default="")
PARTICLEWORKS = os.getenv("PARTICLEWORKS", default="")
RECARDO = os.getenv("RECARDO", default="")
MASTA = os.getenv("MASTA", default="")
RLM = os.getenv("RLM", default="")


#login credentials

MASTER_PASSWORD = os.getenv("MASTER_PASSWORD", default="")
REDMINE_ADDRESS = os.getenv("REDMINE_ADDRESS", default="")
REDMINE_API_KEY = os.getenv("REDMINE_API_KEY", default="")
SERVER_IP = os.getenv("SERVER_IP", default="")
REDMINE_SAFELIST_TOKEN = os.getenv("REDMINE_SAFELIST_TOKEN", default="")
PORT = int(os.getenv("PORT", default="3306"))
DB_NAME = os.getenv("DB_NAME", default="")
DB_TYPE = os.getenv("DB_TYPE", default="")
USERNAME = os.getenv("USERNAME", default="")
PASSWORD = os.getenv("PASSWORD", default="")
GUEST_SVN_USERNAME = os.getenv("GUEST_SVN_USERNAME", default="")
GUEST_SVN_PASSWORD = os.getenv("GUEST_SVN_PASSWORD", default="")


# MASTER_PASSWORD = ""
SITECODE = "Site Short Code"

LINUX_USER_NAME = os.getenv("LINUX_USER_NAME", default="")
LINUX_PASSWORD = os.getenv("LINUX_PASSWORD", default="")
PARTICLEWORKS_LMUTIL_PATH = os.getenv("PARTICLEWORKS_LMUTIL_PATH", default="")