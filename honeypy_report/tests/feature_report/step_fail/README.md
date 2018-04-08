
# Report Service Tests

----

## Test Scenario:
Test a failed feature report


### ACCEPTANCE CRITERIA:
  - Verify the ability to add steps to a feature report without scenarios
  - Verify the report status/result changes upon adding a failed step

### Test Workflow:
  1. Setup test data
  2. Create a new feature report and save the response ID
  3. Add a passing step to the feature report
    - Verify the step was added to the 'tests' array of the report
  5. Add a *failing* second step to the report
    - Verify the step was added to the 'tests' array of the report
    - Verify the overall report result was changed to a failing status
  8. Add a third passing step to the report
    - Verify the step was added to the 'tests' array of the report
  10. Verify the ability to "finish" the feature report
    - Verify the overall result of the test is a failure
