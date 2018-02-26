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
        "honeypy_report.tests",
        "honeypy_report.tests.set_report",
        "honeypy_report.tests.feature_report"
    ],
    install_requires = [
        "certifi",
        "chardet",
        "click",
        "Flask",
        "Flask-Cors",
        "idna",
        "Jinja2",
        "MarkupSafe",
        "py",
        "pymongo",
        "mongoengine",
        "flask-mongoengine",
        "pytest",
        "requests",
        "six",
        "urllib3",
        "Werkzeug",
        "itsdangerous"
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
