# General Settings
DEBUG=False
PRODUCTION=False

IP="0.0.0.0"
PORT=80

# Test Service Configs
TEST_IP="127.0.0.1"
TEST_PORT=30001
TEST_URL="http://" + TEST_IP + ":" + str(TEST_PORT)
TEST_DB="test"

# Report Service Configs
REPORT_IP="127.0.0.1"
REPORT_PORT=30002
REPORT_URL="http://" + REPORT_IP + ":" + str(REPORT_PORT)
REPORT_DB="report"

# Host Service Configs
HOST_IP="127.0.0.1"
HOST_PORT=30003
HOST_URL="http://" + HOST_IP + ":" + str(HOST_PORT)
HOST_DB="host"

# Set Service Configs
SET_IP="127.0.0.1"
SET_PORT=30004
SET_URL="http://" + SET_IP + ":" + str(SET_PORT)
SET_DB="set"

# Database Configs
DATABASE_IP="127.0.0.1"
DATABASE_PORT=27017

# Redis Configs
REDIS_IP="127.0.0.1"
REDIS_PORT=6379

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
