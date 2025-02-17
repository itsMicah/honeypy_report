from copy import deepcopy
from honeypy.common import Common
from honeypy_report import api

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
                "default":""
            },
            "result": {
                "type": "boolean",
                "default": None,
                "nullable": True
            },
            "status": {
                "type": "string",
                "default": "Queued"
            },
            "message": {
                "type": "string",
                "nullable": True,
                "default": None
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
            "name": {
                "type": "string",
                "required": True
            },
            "environment": {
                "type": "string",
                "required": True,
                "default": None,
                "nullable": True
            },
            "queue": {
                "type": "string",
                "required": True,
                "default": "normal-queue"
            },
            "browser": {
                "type": "string",
                "required": True,
                "allowed": api.config["BROWSERS"],
                "default": api.config["BROWSERS"][0]
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
            "contents": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "string"
                }
            },
            "parentId": {
                "type": "string"
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
                "required": True,
                "default": False
            },
            "features": {
                "type": "list",
                "schema": {
                    "type": "string",
                    "regex": "^((?!\/\/).)+\.feature$"
                },
                "default":[]
            },
            "reports": {
                "type": "list",
                "default": []
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
                "required": True,
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

        self.search = {

            "search": {
                "type": "dict",
                "required": True,
                "schema": {
                    "kind": {
                        "type": "string",
                        "required": True,
                        "allowed": ["feature", "set"]
                    },
                    "name": {
                        "type": "string"
                    },
                    "path": {
                        "type": "string"
                    },
                    "fail": {
                        "type": "boolean"
                    },
                    "host": {
                        "type": "string"
                    },
                    "url": {
                        "type": "string"
                    },
                    "browser": {
                        "type": "string"
                    },
                    "created": {
                        "type": "dict",
                        "schema": {
                            "min": {
                                "type": "number",
                                "default": Common().get_timestamp() - 604800000
                            },
                            "max": {
                                "type": "number",
                                "default": Common().get_timestamp()
                            }
                        },
                        "default": {
                            "$gte": Common().get_timestamp() - 604800000,
                            "$lte": Common().get_timestamp()
                        }
                    }
                }
            },
            "pagination": {
                "type": "dict",
                "schema": {
                    "page": {
                        "type": "number",
                        "default": 1
                    },
                    "limit": {
                        "type": "number",
                        "default": 50
                    },
                    "sort": {
                        "type": "string",
                        "default": "_id"
                    }
                },
                "default": {
                    "page": 1,
                    "limit": 50,
                    "default": "_id"
                }
            }
        }

        self.dashboard = {
            "kind": {
                "type": "string",
                "default":"set",
                "allowed": ["set"]
            },
            "created": {
                "type": "dict",
                "schema": {
                    "min": {
                        "type": "number",
                        "default": Common().get_timestamp() - 604800000
                    },
                    "max": {
                        "type": "number",
                        "default": Common().get_timestamp()
                    }
                },
                "default": {
                    "$gte": Common().get_timestamp() - 604800000,
                    "$lte": Common().get_timestamp()
                }
            },
            "hosts": {
                "type": "list",
                "schema": {
                    "type":"string"
                }
            },
            "url": {
                "type": "string"
            },
            "browsers": {
                "type": "list",
                "default": api.config["BROWSERS"],
                "allowed": api.config["BROWSERS"]
            },
            "environment": {
                "type": "string",
                "required": True
            }
        }
