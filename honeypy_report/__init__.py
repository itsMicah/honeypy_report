from flask import Flask

reportApi = Flask(__name__)
reportApi.config.from_object('honeypy_report.configs.development')
reportApi.config.from_envvar('honeypyReportEnvironment', silent = True)
