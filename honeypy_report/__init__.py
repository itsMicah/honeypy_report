from flask import Flask

report_api = Flask(__name__)
report_api.config.from_envvar('HONEYPY_CONFIG')
