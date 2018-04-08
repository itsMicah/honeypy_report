from bson.objectid import ObjectId

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
    Create scenario ids
"""

SCENARIO_ID_1 = str(ObjectId())
SCENARIO_ID_2 = str(ObjectId())


"""
    Define SCENARIO_1
"""
SCENARIO_1 = {
    "type":"scenario",
    "text":"Scenario: Test Things",
    "name":"Test Things",
    "scenarioId": SCENARIO_ID_1,
    "tests":[],
    "result": True,
    "message": "Success"
}

"""
    Define SCENARIO_1 steps
"""
SCENARIO_1_STEPS = [
    {
        "kind":"feature",
        "type":"step",
        "test":"Given I do things",
        "text":"Given I do things",
        "result": True,
        "message": "Success",
        "scenarioId": SCENARIO_ID_1
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"When I do things",
        "text":"When I do things",
        "result": True,
        "message": "Pass The Things",
        "scenarioId": SCENARIO_ID_1
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"Then I do things",
        "text":"Then I do things",
        "result": True,
        "message": "Success",
        "scenarioId": SCENARIO_ID_1
    }
]

"""
    Define SCENARIO_2 steps
"""
SCENARIO_2 = {
    "kind":"feature",
    "type":"scenario",
    "text":"Scenario: 2 Test Things",
    "name":"2 Test Things",
    "scenarioId": SCENARIO_ID_2,
    "tests":[],
    "result": True,
    "message": "Success"
}

"""
    Define SCENARIO_2 steps
"""
SCENARIO_2_STEPS = [
    {
        "kind":"feature",
        "type":"step",
        "test":"Given I do things again",
        "text":"Given I do things again",
        "result": True,
        "message": "Success",
        "scenarioId": SCENARIO_ID_2
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"When I do failed things again",
        "text":"When I do failed things again",
        "result": False,
        "message": "Failure",
        "scenarioId": SCENARIO_ID_2
    }
]
