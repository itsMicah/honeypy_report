from flask import Flask

api = Flask(__name__)
api.config.from_envvar('HONEYPY_CONFIG')
