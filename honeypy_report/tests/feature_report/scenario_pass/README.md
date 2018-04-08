
# Report Service Tests

----

## Test Scenario:
Test a successful feature report


### ACCEPTANCE CRITERIA:
  - Verify the ability to add scenarios to a feature report
  - Verify the ability to add steps to existing scenarios within the report
  - Verify the ability to finish a report with scenarios
  - Verify finishing the report makes the overall feature report pass

### Test Workflow:
  1. Setup test data
  2. Create a new feature report and save the response ID
  3. Add a passing scenario to the report
    - We will label this scenario as 'SCENARIO_1'
    - Verify the scenario was added successfully
  4. Add a passing step to SCENARIO_1
    - Verify the step was added to the 'tests' array of SCENARIO_1
    - Verify the result of SCENARIO_1 is not falsy
  5. Add another passing step to SCENARIO_1
    - Verify the step was added to the 'tests' array of SCENARIO_1
    - Verify the result of SCENARIO_1 is not falsy
  6. Add another passing step to SCENARIO_1
    - Verify the step was added to the 'tests' array of SCENARIO_1
    - Verify the result of SCENARIO_1 is not falsy
  7. Add a passing scenario to the report
    - We will label this scenario as 'SCENARIO_2'
    - Verify the scenario was added successfully
  8. Add a passing step to SCENARIO_2
    - Verify the step was added to the 'tests' array of SCENARIO_2
    - Verify the result of SCENARIO_2 is not falsy
  9. Add another passing step to SCENARIO_2
    - Verify the step was added to the 'tests' array of SCENARIO_2
    - Verify the result of SCENARIO_2 is not falsy
  10. Add another passing step to SCENARIO_2
    - Verify the step was added to the 'tests' array of SCENARIO_2
    - Verify the result of SCENARIO_2 is not falsy
  11. Finish the feature report
    - Verify the overall report result is a success
    - Verify there is an end time added to the report
