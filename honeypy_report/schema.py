from copy import deepcopy
from honeypy_report import report_api

class Schemas(object):

    def __init__(self):

        """
            Verify the kind of report received from paylaod
        """
        self.kind = {
            "kind": {
                "type": "string",
                "allowed": ["feature", "set"],
                "required": True
            }
        }

        """
            Verify basic report object without defining if it is a 'feature' or a 'set'
        """
        self.report = {
            "kind": {
                "type": "string",
                "allowed": ["feature", "set"],
                "required": True
            },
            "host": {
                "type": "string",
                "required": True,
                "minlength": 1
            },
            "result": {
                "type": "boolean",
                "default": None,
                "nullable": True
            },
            "fail": {
                "type": "boolean",
                "default": False
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

        """
            Define a feature report
            It inherits from the 'report' object
        """
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
            },
            "message": {
                "type": "string",
                "default": "Queued"
            }
        }
        self.feature_report.update(self.report)

        """
            Define a set report
            It inherits from the 'report' object
        """
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
                "default": []
            },
            "message": {
                "type": "string",
                "default": "Running"
            }
        }
        self.set_report.update(self.report)

        """
            Define a test object
            Test objects are added to feature reports
        """
        self.test = {
            "text": {
                "type": "string",
                "required": True,
                "minlength": 1
            },
            "message": {
                "type": "string",
                "required": True
            },
            "result": {
                "type": "boolean",
                "required": True
            }
        }

        """
            Define a step object
            Steps inherit from the 'test' object
        """
        self.step = {
            "type": {
                "type": "string",
                "required": True,
                "allowed": ["step"]
            },
            "test": {
                "type": "string",
                "required": True,
                "minlength": 1
            },
            "variables": {
                "type": "dict",
                "default": {}
            },
            "scenarioId": {
                "type": "string"
            }
        }
        self.step.update(self.test)

        """
            Define a scenario object
            Scenarios inherit from the 'test' object
        """
        self.scenario = {
            "type": {
                "required": True,
                "type": "string",
                "allowed": ["scenario"]
            },
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
        self.scenario.update(self.test)

        """
            Verify a basic add payload received from the request
        """
        self.add = {
            "type": {
                "type": "string",
                "required": True,
                "allowed": ["step", "scenario"]
            },
            "scenarioId": {
                "type": "string",
                "minlength": 24,
                "maxlength": 24
            }
        }
