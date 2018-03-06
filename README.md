# Honeypy Report Service #

Honeypy reoprt service for managing test service reports

## Requirements:  

* Install [Python 3.6](https://www.python.org/downloads/)
* Install [Virtualenv](https://virtualenv.pypa.io/en/stable/)  
  * Run `pip install virtualenv`

## VirtualEnv:
* Create a virtual python environment   
  * Run `virtualenv {{environment name}} -p python3`
* Assuming the above command executed correctly, activate the environment   
  * Run `source {{environment name}}/bin/activate`
* Running the above command should create an isolated python environment


## Project Setup for Development

* Clone the report service repo  
* Navigate to the project root
* Set the environment variable `HONEYPY_CONFIG` and set it's value to the path of a honeypy config file
* Run ```python setup.py develop```
* Run ```honeypy_report``` to start the server  
