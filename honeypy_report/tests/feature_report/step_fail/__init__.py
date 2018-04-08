
"""
    Define feature file
"""
FEATURE = {
    "path":"feature_report.feature",
    "host": "Localhost",
    "kind":"feature"
}

"""
    Define report
"""
REPORT = {
    "kind":"feature",
    "path":FEATURE["path"]
}

"""
    Define test steps
"""
STEPS = [
    {
        "kind":"feature",
        "type":"step",
        "test":"Given I do things",
        "text":"Given I do things",
        "result": True,
        "message": "Success"
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"Given I do other things",
        "text":"Given I do other things",
        "result": False,
        "message": "Failure"
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"When I stop things",
        "text":"When I stop things",
        "result": True,
        "message": "Success"
    }
]
