@ui @api @loading @success
Feature: Login Submission
  As a user,
  I want to submit my credentials,
  so that the system can validate them and log me in.

  @ui @api @loading @success
  Scenario Outline: Successful login redirects user to dashboard
    Given the user is on the login page
    When the user enters email "<email>" and password "<password>"
    And the user clicks the login button
    Then a login request is sent to the backend
    And a loading indicator is displayed
    And the user is redirected to the dashboard

    Examples:
      | email                 | password    |
      | admin@example.com     | password123 |

  @ui @api @loading @negative
  Scenario Outline: Failed login shows relevant error message
    Given the user is on the login page
    When the user enters email "<email>" and password "<password>"
    And the user clicks the login button
    Then a login request is sent to the backend
    And a loading indicator is displayed
    And an error message "<error_message>" is displayed on the login form

    Examples:
      | email             | password       | error_message               |
      | invalid@example.com | wrongpass     | Invalid email or password.  |
      | admin@example.com  | wrongpass     | Invalid email or password.  |
      | <empty>           | password123   | Email is required           |
      | admin@example.com  | <empty>       | Password is required        |

  @ui @validation @negative
  Scenario Outline: Validation errors are displayed for invalid input before submission
    Given the user is on the login page
    When the user enters email "<email>" and password "<password>"
    And the user clicks the login button
    Then the following validation messages are shown on the login form:
      | message                     |
      | "<validation_message>"      |

    Examples:
      | email          | password    | validation_message                  |
      | <empty>        | password123 | Email is required                   |
      | invalidemail   | password123 | Please enter a valid email address |
      | admin@example.com | <empty>  | Password is required                |
      | admin@example.com | short   | Password must be at least 6 characters |