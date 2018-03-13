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

from honeypy.api.common import Common
from honeypy.errors import ValidationError

from honeypy_report import report_api
from honeypy_report.controller import ReportController

"""
    Allow Cross origin requests while in development
"""
CORS(report_api, resources={r'\/?.*': {'origins': 'http://localhost:4200'}})

"""
    Instantiate Common
"""
common = Common()
basic_auth = BasicAuth(report_api)

"""
    Create a report endpoint
"""
@report_api.route("/", methods = ["POST"])
@basic_auth.required
def post_report():
    try:
        return ReportController().create(request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

"""
    Get a report by ID endpoint
"""
@report_api.route("/<report_id>", methods = ["GET"])
@basic_auth.required
def get_report(report_id):
    return ReportController().get(report_id)

@report_api.route("/<report_id>", methods = ["PATCH"])
@basic_auth.required
def patch_report(report_id):
    try:
        return ReportController().save(report_id, request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

"""
    Add test objects to a feature report
"""
@report_api.route("/<report_id>/add", methods = ["POST"])
@basic_auth.required
def add_test(report_id):
    try:
        return ReportController().add(report_id, request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

"""
    Finish a feature report
    Also update a set report result if the feature is part of a set run
"""
@report_api.route("/<report_id>/finish", methods = ["GET"])
@basic_auth.required
def finish(report_id):
    try:
        path = request.args.get('path')
        return ReportController().finish(report_id, path)
    except ValidationError as error:
        return Common().create_response(400, error.errors)

@report_api.route("/search", methods = ["POST"])
@basic_auth.required
def search():
    try:
        return ReportController().search(request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

def main():
    """
        Start the service
    """
    report_api.run(host=report_api.config["REPORT_IP"], port=report_api.config["REPORT_PORT"], threaded=True)
