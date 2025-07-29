Feature: Login Submission
  As a user,
  I want to submit my credentials,
  So that the system can validate them and log me in.

  @ui @api @loading
  Scenario Outline: Clicking the login button triggers request and shows loading state
    Given I am on the login page
    When I enter email "<email>" and password "<password>"
    And I click the login button
    Then a request to the backend is triggered
    And I see the loading state displayed
    Examples:
      | email               | password       |
      | user@example.com    | validPass123   |

  @ui @api @success
  Scenario Outline: Successful login redirects to dashboard
    Given I am on the login page
    When I enter email "<email>" and password "<password>"
    And I click the login button
    And the backend response is successful
    Then I am redirected to the dashboard
    Examples:
      | email              | password     |
      | user@example.com   | validPass123 |

  @ui @validation @negative
  Scenario Outline: Email field validation errors on login submission
    Given I am on the login page
    When I enter email "<email>" and password "validPass123"
    And I click the login button
    Then I see the error message displayed "<error_message>"
    Examples:
      | email          | error_message                  |
      | <empty>        | Email is required              |
      | invalid_email  | Please enter a valid email address |

  @ui @validation @negative
  Scenario Outline: Password field validation errors on login submission
    Given I am on the login page
    When I enter email "user@example.com" and password "<password>"
    And I click the login button
    Then I see the error message displayed "<error_message>"
    Examples:
      | password    | error_message                   |
      | <empty>     | Password is required            |
      | short      | Password must be at least 6 characters |

  @ui @api @negative
  Scenario: Backend returns authentication failure error
    Given I am on the login page
    When I enter email "user@example.com" and password "wrongPassword"
    And I click the login button
    And the backend response is failure with message "Invalid email or password"
    Then I see the error message displayed "Invalid email or password"