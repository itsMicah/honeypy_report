from setuptools import setup

setup(
    name = "honeypy_report",
    version = "0.1",
    description = "Honeypy Report Service",
    url = "https://github.com/DevCoHealth/honeypy-report",
    author = "Micah Prescott",
    author_email = "mprescott@sharecare.com",
    packages = [
        "honeypy_report",
        "tests"
    ],
    install_requires = [
        "certifi",
        "chardet",
        "click",
        "Flask",
        "Flask-Cors",
        "honeypyDB",
        "idna",
        "Jinja2",
        "MarkupSafe",
        "py",
        "pymongo",
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
