
# Report Service Tests

----

## Test Scenario:
Verify a passing set report


### ACCEPTANCE CRITERIA:
  - Verify the ability to create a set report
  - Verify feature reports are created within the set report
  - Verify the ability to add scenarios and steps to specific features within the set report
  - Verify the ability to finish an individual feature report
    - Verify the specific feature report is finished
    - Verify other feature reports are not finished
  - Verify the ability to finish a set report
    - Verify the overall set report is a success
    - Verify all the feature reports are a success

### Test Workflow:
  1. Setup test data
  2. Add scenario 1 to feature 1
    - Verify the scenario was added to the report
  2. Add a step to scenario 1
    - Verify the step was added to the scenario
  3. Add scenario 2 to feature 1
    - Add a step to scenario 2
  4. Add a step to scenario 2
    - Verify the step was added to the scenario
  5. Add a step to scenario 2
    - Verify the step was added to the scenario
  6. Add scenario 1 to feature 2
    - Verify the scenario was added to the report
  7. Add a step to scenario 1 in feature 2
    - Verify the step was added to the scenario
  8. Add a step to scenario 1 in feature 2
    - Verify the step was added to the scenario
  9. Add scenario 2 to feature 2
    - Verify the scenario was added to the report
  10. Add a step to scenario 2 in feature 2
  11. Add a step to scenario 2 in feature 2
  12. Add scenario 1 to feature 3
  13. Finish feature 1
    - Verify feature 1 was finished
  14. Add a step to scenario 1 in feature 3
  15. Finish feature 2
    - Verify feature 2 was finished
  16. Finish feature 3
    - Verify feature 3 was finished
