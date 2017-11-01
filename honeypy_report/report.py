import json
from bson import json_util
from flask import Flask, Response
from flask import request
from flask_cors import CORS, cross_origin
from os.path import dirname, abspath

from honeypy_report.controller import ReportController

reportApi = Flask(__name__)
CORS(reportApi, resources={r'\/report\/?.*': {'origins': 'http://localhost:4200'}})

reportApi.config.from_object('honeypy_report.configs.development')
reportApi.config.from_envvar('honeypyReportEnvironment', silent = True)
reportController = ReportController(config = reportApi.config)

def createResponse(data):
    response = {
        "data":data["data"],
        "errors":data["errors"],
        "result":data["result"]
    }
    return Response(
        response=json.dumps(response),
        status=data["status"],
        mimetype="application/json"
    )

@reportApi.route("/report", methods = ["POST"])
def postReport():
    data = request.get_json()
    response = ReportController().createReport(data)
    return createResponse(response)

@reportApi.route("/report/<reportId>", methods = ["GET"])
def getReport(reportId):
    response = ReportController(reportId).getReport()
    return createResponse(response)

@reportApi.route("/report/search", methods = ["POST"])
def getReportsByDate():
    data = request.get_json()
    results = ReportController().getReportsByDate(data)
    return createResponse(results)

@reportApi.route("/report/<reportId>", methods = ["PATCH"])
def patchReport(reportId):
    data = request.get_json()
    results = ReportController(reportId).patchReport(data)
    return createResponse(results)

@reportApi.route("/report/<reportId>/add", methods = ["PATCH"])
def addToReport(reportId):
    data = request.get_json()
    response = ReportController(reportId).addReport(data)
    return createResponse(response)

@reportApi.route("/report/<reportId>/finish", methods = ["GET"])
def finishReport(reportId):
    test = request.args.get('test')
    response = ReportController(reportId, test).finished()
    return createResponse(response)

@reportApi.route("/report/<reportId>", methods = ["DELETE"])
def deleteReport(reportId):
    response = ReportController(reportId).deleteReport()
    return createResponse(response)


def main():
    reportApi.run(host=reportApi.config["IP"], port=reportApi.config["PORT"], threaded=True)

# Run service
if __name__ == "__main__":
    main()
