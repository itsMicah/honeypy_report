from flask import Flask

reportApi = Flask(__name__)
reportApi.config.from_envvar('HONEYPY_CONFIG')
