from copy import deepcopy
from honeypy_report import report_api

class Schemas(object):

    def __init__(self):
        self.report = {
            "kind": {
                "type": "string",
                "allowed": ["feature", "set"],
                "required": True
            },
            "host": {
                "type": "string",
                "required": True
            },
            "result": {
                "type": "boolean",
                "default": False
            },
            "fail": {
                "type": "boolean",
                "default": False
            },
            "message": {
                "type": "string",
                "default": "Incomplete"
            },
            "tickets": {
                "type": "list",
                "default": []
            },
            "url": {
                "type": "string",
                "default": ""
            },
            "browser": {
                "type": "string",
                "required": True,
                "allowed": report_api.config["BROWSERS"]
            }
        }

        self.feature_report = {
            "path": {
                "type": "string",
                "required": True
            },
            "tests": {
                "type": "list",
                "default": []
            },
            "parentId": {
                "type": "string"
            }
        }

        self.feature_report.update(self.report)

        self.set_report = {
            "inherit": {
                "type": "boolean",
                "default": False
            },
            "features": {
                "type": "list",
                "schema": {
                    "type": "string",
                    "regex": "^((?!\/\/).)+\.feature$"
                }
            },
            "reports": {
                "type": "list",
                "default": [],
                "schema": self.feature_report
            }
        }

        self.set_report.update(self.report)

        self.step = {
            "test": {
                "type": "string",
                "required": True
            },
            "variables": {
                "type": "dict",
                "default": {}
            },
            "scenarioId": {
                "type": "string"
            }
        }

        self.scenario = {
            "name": {
                "type": "string",
                "default": ""
            },
            "loop": {
                "type": "dict",
                "default": {}
            },
            "tests": {
                "type": "list",
                "default": [],
                "required": True,
                "schema": self.step
            },
            "scenarioId": {
                "type": "string",
                "required": True
            }
        }
