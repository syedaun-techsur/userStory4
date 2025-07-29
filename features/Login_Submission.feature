@ui @api @loading
Feature: Login Submission
  As a user,
  I want to submit my credentials,
  So that the system can validate them and log me in.

  @ui @api @loading
  Scenario Outline: Submitting login credentials triggers backend request and displays loading state
    Given I am on the login page
    When I enter email "<email>"
    And I enter password "<password>"
    And I click the login button
    Then a request to the backend is sent
    And I should see a loading indicator
    Examples:
      | email               | password    |
      | user@example.com    | correctPwd1 |

  @ui @success @api
  Scenario Outline: Successful login redirects user to the dashboard
    Given I am on the login page
    When I enter email "<email>"
    And I enter password "<password>"
    And I click the login button
    And the backend responds with success
    Then I am redirected to the dashboard
    Examples:
      | email            | password    |
      | user@example.com | correctPwd1 |

  @ui @negative @api
  Scenario Outline: Login failure shows relevant error message
    Given I am on the login page
    When I enter email "<email>"
    And I enter password "<password>"
    And I click the login button
    And the backend responds with failure and error message "<error_message>"
    Then I see the error message "<error_message>" displayed
    Examples:
      | email            | password    | error_message                   |
      | user@example.com | wrongPwd    | Incorrect email or password.    |
      | user@example.com | <empty>     | Password is required            |
      | <empty>          | correctPwd1 | Email is required              |
      | invalid-email    | somePwd    | Please enter a valid email address |
      | user@example.com | short      | Password must be at least 6 characters |