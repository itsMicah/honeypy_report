# General Settings
DEBUG=False
PRODUCTION=False

IP="0.0.0.0"
PORT=80

# Test Service Configs
TEST_IP="127.0.0.1"
TEST_PORT=30001
TEST_URL="http://" + TEST_IP + ":" + str(TEST_PORT)
TEST_DB_NAME="test"
TEST_DB_COLLECTION="test"

# Report Service Configs
REPORT_IP="127.0.0.1"
REPORT_PORT=30002
REPORT_URL="http://" + REPORT_IP + ":" + str(REPORT_PORT)
REPORT_DB_NAME="report"
REPORT_DB_COLLECTION="report"

# Host Service Configs
HOST_IP="127.0.0.1"
HOST_PORT=30003
HOST_URL="http://" + HOST_IP + ":" + str(HOST_PORT)
HOST_DB_NAME="host"
HOST_DB_COLLECTION="host"

# Set Service Configs
SET_IP="127.0.0.1"
SET_PORT=30004
SET_URL="http://" + SET_IP + ":" + str(SET_PORT)
SET_DB_NAME="set"
SET_DB_COLLECTION="set"

# Environment Service Configs
ENVIRONMENT_IP="127.0.0.1"
ENVIRONMENT_PORT=30005
ENVIRONMENT_URL="http://" + ENVIRONMENT_IP + ":" + str(ENVIRONMENT_PORT)
ENVIRONMENT_DB_NAME="environment"
ENVIRONMENT_DB_COLLECTION="environment"

# Database Configs
DATABASE_IP="127.0.0.1"
DATABASE_PORT=27017

# Redis Configs
REDIS_HOST="127.0.0.1"
REDIS_PORT=6379
REDIS_PASSWORD="P@r41LaX?!"

# supported browsers
BROWSERS = [
    "chrome",
    "firefox",
    "safari",
    "ie11",
    "edge"
]

BASIC_AUTH_USERNAME = "honeypy_web_app"
BASIC_AUTH_PASSWORD = "P@r41LaX?!"
