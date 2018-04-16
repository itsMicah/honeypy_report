from setuptools import setup

setup(
    name = "honeypy_report",
    version = "0.1",
    description = "Honeypy Report Service",
    url = "https://bitbucket.org/Micerbeats/honeypy-report",
    author = "Micah Prescott",
    author_email = "prescottmicah@gmail.com",
    packages = [
        "honeypy_report",
        "honeypy_report.configs",
        "honeypy_report.tests",
        "honeypy_report.tests.set_report",
        "honeypy_report.tests.crud",
        "honeypy_report.tests.crud.create",
        "honeypy_report.tests.feature_report",
        "honeypy_report.tests.feature_report.scenario_fail",
        "honeypy_report.tests.feature_report.scenario_pass",
        "honeypy_report.tests.feature_report.step_fail",
        "honeypy_report.tests.feature_report.step_pass",
        "honeypy_report.tests.set_report.scenario_fail",
        "honeypy_report.tests.set_report.scenario_pass"
    ],
    install_requires = [
        "Flask",
        "Flask-Cors",
        "cerberus",
        "pymongo",
        "Flask-BasicAuth",
        "pytest",
        "requests"
    ],
    classifiers = [
        "'Programming Language :: Python :: 3.6'"
    ],
    entry_points = {
        "console_scripts": [
            "honeypy_report = honeypy_report.report:main"
        ]
    }
)
