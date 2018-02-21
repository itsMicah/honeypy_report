import datetime
from mongoengine import *
from honeypy_report import report_api

class Test(EmbeddedDocument):
    _type = StringField(required = True, choices = ["test", "scenario"])
    created = DateTimeField(default=datetime.datetime.now, editable = False, required = True)
    result = BooleanField(required = True, null = True)
    message = StringField(required = True)
    text = StringField(required = True)
    path = StringField()
    meta = {'allow_inheritance': True, 'strict': False}

class Step(Test):
    test = StringField(required = True)
    variables = DictField(default = {})
    scenarioId = StringField()
    meta = {'strict': False}

class Scenario(Test):
    name = StringField(required = True, default = "")
    loop = DictField(default = {})
    tests = EmbeddedDocumentListField(Test)
    scenarioId = ObjectIdField(required = True)
    meta = {'indexes': [{'fields': ['scenarioId'], 'unique': True}], 'strict': False}

class Report(Document):
    tests = ListField(default = [])
    created = DateTimeField(default=datetime.datetime.now, editable = False, required = True)
    end = DateTimeField(default = None)
    modified = DateTimeField(default=datetime.datetime.now)
    name = StringField()
    reportId = StringField()
    kind = StringField(required = True, choices = ["set", "feature"], default = "feature")
    host = StringField(default = "Localhost")
    url = StringField(default = "")
    browser = StringField(default = report_api.config["BROWSERS"][0], choices = report_api.config["BROWSERS"], required = True)
    result = BooleanField(null = True, default = None)
    message = StringField(default = "Incomplete")
    fail = BooleanField(default = False)
    errors = ListField(default = [])
    tickets = ListField(StringField())
    meta = {'strict': False, 'allow_inheritance': True}

class FeatureReport(Report):
    kind = StringField(required = True, choices = ["feature"], default = "feature")
    path = StringField(required = True, regex = r"^.*\.feature")
    name = StringField(regex = r"^.*\.feature")
    setId = StringField()
    contents = ListField(StringField(), default = [])

class SetReport(Report):
    kind = StringField(required = True, choices = ["set"], default = "set")
    features = ListField(StringField(regex=r"^.*\.feature$"))
    inherit = BooleanField(default = False, required = True)
