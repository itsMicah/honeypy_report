# General Settingsf
DEBUG=False
PRODUCTION=True
PATH="/root/data"

IP="0.0.0.0"
PORT=80

# Test Service Configs
TEST_IP="test-service"
TEST_PORT=80
TEST_URL="http://" + TEST_IP
TEST_DB_NAME="test"
TEST_DB_COLLECTION="test"

# Report Service Configs
REPORT_IP="report-service"
REPORT_PORT=80
REPORT_URL="http://" + REPORT_IP
REPORT_DB_NAME="report"
REPORT_DB_COLLECTION="report"

# Host Service Configs
HOST_IP="host-service"
HOST_PORT=80
HOST_URL="http://" + HOST_IP
HOST_DB_NAME="host"
HOST_DB_COLLECTION="host"

# Set Service Configs
SET_IP="set-service"
SET_PORT=80
SET_URL="http://" + SET_IP
SET_DB_NAME="set"
SET_DB_COLLECTION="set"

# Environment Service Configs
ENVIRONMENT_IP="environment-service"
ENVIRONMENT_PORT=80
ENVIRONMENT_URL="http://" + ENVIRONMENT_IP + ":" + str(ENVIRONMENT_PORT)
ENVIRONMENT_DB_NAME="environment"
ENVIRONMENT_DB_COLLECTION="environment"

# Database Configs
DATABASE_IP="honeypy-db-mongodb"
DATABASE_PORT=27017

# Redis Configs
REDIS_HOST="honeypy-rds-redis"
REDIS_PORT=6379
REDIS_PASSWORD="P@r41LaX?!"

BROWSERS = [
    "chrome",
    "firefox",
    "safari",
    "ie11",
    "edge"
]

BASIC_AUTH_USERNAME = "honeypy_web_app"
BASIC_AUTH_PASSWORD = "P@r41LaX?!"
