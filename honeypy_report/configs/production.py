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
TEST_DB="test"

# Report Service Configs
REPORT_IP="report-service"
REPORT_PORT=80
REPORT_URL="http://" + REPORT_IP
REPORT_DB="report"

# Host Service Configs
HOST_IP="host-service"
HOST_PORT=80
HOST_URL="http://" + HOST_IP
HOST_DB="host"

# Set Service Configs
SET_IP="set-service"
SET_PORT=80
SET_URL="http://" + SET_IP
SET_DB="set"

# Database Configs
DATABASE_IP="honeypy-db-mongodb"
DATABASE_PORT=27017

# Redis Configs
REDIS_IP="honeypy-rds-redis"
REDIS_PORT=6379

BROWSERS = [
    "chrome",
    "firefox",
    "safari",
    "ie11",
    "edge"
]

BASIC_AUTH_USERNAME = "honeypy_web_app"
BASIC_AUTH_PASSWORD = "P@r41LaX?!"
