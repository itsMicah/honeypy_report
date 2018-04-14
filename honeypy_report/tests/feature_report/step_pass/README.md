
# Report Service Tests

----

## Test Scenario:
Test a passing feature report


### ACCEPTANCE CRITERIA:
  - Verify the ability to add steps to a feature report
  - Verify the feature report result is True while adding passing steps
  - Verify the ability to finish the report
  - Verify finishing the report makes the overall feature report pass

### Test Workflow:
  1. Setup test data
  2. Create a new feature report and save the response ID
  3. Add a passing step to the feature report
    - Verify the step was added to the 'tests' array of the report
    - Verify the new length of the 'tests' list
  4. Add a passing step to the feature report
    - Verify the step was added to the 'tests' array of the report
    - Verify the new length of the 'tests' list
  5. Add a passing step to the feature report
    - Verify the step was added to the 'tests' array of the report
    - Verify the new length of the 'tests' list
  6. Finish the report
    - Verify the overall result of the feature run is a success
