
# Report Service Tests

----

## Test Scenario:
Test the ability to create a new report

## Endpoint Specs
URL: "/"  
METHOD: POST

### Acceptance Criteria:
  - Verify the POST HTTP Method works when attempting to create a new report
  - Verify only two report kinds are supported, feature and set
    - Feature report: is a report kind used for feature test runs
    - Set report: is a report kind used for set runs
  - Verify field properties and validation adhere to the report schema
  - Verify the ability to create different reports while providing varying payloads

### Test Workflow:
  1. TestCreateValidation - `test_create_validations.py`
    - Verify different field validations for reports
  2. TestCreateDefault - `test_create_default.py`
    - Verify the ability to create reports while only providing the minimum required values
  3. TestCreateSet - `test_create_set.py`
    - Verify the ability to create a set report with feature files
