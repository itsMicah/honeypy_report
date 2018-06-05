from bson.objectid import ObjectId

"""
    Define Feature 1, 2, 3
"""
FEATURE_1 = {
    "path":"feature_report_1.feature",
    "kind":"feature"
}

FEATURE_2 = {
    "path":"feature_report_2.feature",
    "kind":"feature"
}

FEATURE_3 = {
    "path":"feature_report_3.feature",
    "kind":"feature"
}

"""
    Define a test set using the feature files above
"""
SET = {
    "kind": "set",
    "name": "Test Set",
    "host": "Localhost",
    "features": [
        FEATURE_1["path"],
        FEATURE_2["path"],
        FEATURE_3["path"]
    ]
}

"""
    Generate ObjectId's to be used by scenarios and steps in the report
"""
SCENARIO_ID_1 = str(ObjectId())
SCENARIO_ID_2 = str(ObjectId())

"""
    Define SCENARIO_1
"""
SCENARIO_1 = {
    "kind":"set",
    "type":"scenario",
    "text":"Scenario: Test Things",
    "name":"Test Things",
    "scenarioId": SCENARIO_ID_1,
    "tests":[],
    "result": True,
    "message": "Success"
}

"""
    Define SCENARIO_1's steps
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
        "result": False,
        "message": "Failure",
        "scenarioId": SCENARIO_ID_1
    }
]

"""
    Define SCENARIO_2
"""
SCENARIO_2 = {
    "kind":"set",
    "type":"scenario",
    "text":"Scenario: 2 Test Things",
    "name":"2 Test Things",
    "scenarioId": SCENARIO_ID_2,
    "tests":[],
    "result": True,
    "message": "Success"
}

"""
    Define SCENARIO_2's steps
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
        "test":"When I do things again",
        "text":"When I do things again",
        "result": True,
        "message": "Success",
        "scenarioId": SCENARIO_ID_2
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"Then I do things again",
        "text":"Then I do things again",
        "result": True,
        "message": "Success",
        "scenarioId": SCENARIO_ID_2
    }
]
