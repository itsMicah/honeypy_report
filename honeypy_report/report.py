"""

    HONEYPY REPORT SERVICE

    Honeypy Report Service maintains reports, organization, and statuses

"""


"""
    Import dependencies
"""
from flask import Flask, request
from flask_cors import CORS
from flask_basicauth import BasicAuth

from honeypy.common import Common
from honeypy.errors import ValidationError

from honeypy_report import api
from honeypy_report.controller import ReportController

"""
    Allow Cross origin requests while in development
"""
CORS(api, resources={r'\/?.*': {'origins': ['http://localhost:4200', "http://frontend-service.default.svc.cluster.local"]}})

"""
    Instantiate Common
"""
common = Common()
basic_auth = BasicAuth(api)

"""
    Create a report endpoint
"""
@api.route("/", methods = ["POST"])
@basic_auth.required
def post_report():
    try:
        return ReportController().create(request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

"""
    Get a report by ID endpoint
"""
@api.route("/<report_id>", methods = ["GET"])
@basic_auth.required
def get_report(report_id):
    return ReportController().get(report_id)

@api.route("/<report_id>", methods = ["PATCH"])
@basic_auth.required
def patch_report(report_id):
    try:
        return ReportController().save(report_id, request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

"""
    Add test objects to a feature report
"""
@api.route("/<report_id>/add", methods = ["POST"])
@basic_auth.required
def add_test(report_id):
    try:
        return ReportController().add(report_id, request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

@api.route("/<report_id>/start", methods = ["GET"])
@basic_auth.required
def start(report_id):
    try:
        path = request.args.get('path')
        return ReportController().start(report_id, path)
    except ValidationError as error:
        return Common().create_response(400, error.errors)

"""
    Finish a feature report
    Also update a set report result if the feature is part of a set run
"""
@api.route("/<report_id>/status", methods = ["GET"])
@basic_auth.required
def finish(report_id):
    try:
        path = request.args.get('path')
        type = request.args.get('type')
        return ReportController().update_status(type, report_id, path)
    except ValidationError as error:
        return Common().create_response(400, error.errors)

@api.route("/search", methods = ["POST"])
@basic_auth.required
def search():
    try:
        deep = request.args.get('deep')
        return ReportController().search(request.get_json(), deep)
    except ValidationError as error:
        return Common().create_response(400, error.errors)

@api.route("/dashboard", methods = ["POST"])
@basic_auth.required
def dashboard():
    try:
        return ReportController().get_dashboard(request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

def main():
    """
        Start the service
    """
    if api.config["PRODUCTION"]:
        api.run(host=api.config["IP"], port=api.config["PORT"])
    else:
        api.run(host=api.config["REPORT_IP"], port=api.config["REPORT_PORT"])
