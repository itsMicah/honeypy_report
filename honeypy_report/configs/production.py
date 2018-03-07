# General Settingsf
DEBUG=False
PRODUCTION=True
APPLICATION_ROOT="/api"
PATH="/root/data"

IP="0.0.0.0"
PORT=80

# Test Service Configs
TEST_IP="test-service"
TEST_PORT=80
TEST_URL="http://" + TEST_IP + "/api"
TEST_DB="test"

# Report Service Configs
REPORT_IP="report-service"
REPORT_PORT=80
REPORT_URL="http://" + REPORT_IP + "/api"
REPORT_DB="report"

# Host Service Configs
HOST_IP="host-service"
HOST_PORT=80
HOST_URL="http://" + HOST_IP + "/api"
HOST_DB="host"

# Set Service Configs
SET_IP="set-service"
SET_PORT=80
SET_URL="http://" + SET_IP + "/api"
SET_DB="set"

# Database Configs
DATABASE_IP="honeypy-db-mongodb"
DATABASE_PORT=27017

BROWSERS = [
    "chrome",
    "firefox",
    "safari",
    "ie11",
    "edge"
]

BASIC_AUTH_USERNAME = "honeypy_web_app"
BASIC_AUTH_PASSWORD = "P@r41LaX?!"
