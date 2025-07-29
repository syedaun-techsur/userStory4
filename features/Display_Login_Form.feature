Feature: Display Login Form
  As a user,
  I want to see a login form with fields for email and password,
  So that I can enter my credentials to access the app.

  @ui @validation
  Scenario Outline: Display login form with required fields and login button
    Given the user navigates to the login page
    Then the login form is displayed
    And the email input field is visible
    And the password input field is visible
    And the login button is visible

  @ui @validation
  Scenario Outline: Validate required fields on empty submission
    Given the user navigates to the login page
    When the user leaves the email field as "<email>"
    And the user leaves the password field as "<password>"
    And the user clicks the login button
    Then the error message "<error_message>" is displayed

    Examples:
      | email   | password  | error_message           |
      | <empty> | valid123  | Email is required       |
      | user@example.com | <empty> | Password is required     |
      | <empty> | <empty> | Email is required       |

  @ui @validation
  Scenario Outline: Validate proper email format
    Given the user navigates to the login page
    When the user enters the email as "<email>"
    And the user enters the password as "valid123"
    And the user clicks the login button
    Then the error message "Please enter a valid email address" is displayed

    Examples:
      | email           |
      | invalid-email   |
      | user@example    |
      | user@.com       |
      | user@domain,com |

  @ui @validation
  Scenario Outline: Validate password minimum length requirement
    Given the user navigates to the login page
    When the user enters the email as "user@example.com"
    And the user enters the password as "<password>"
    And the user clicks the login button
    Then the error message "Password must be at least 6 characters" is displayed

    Examples:
      | password |
      | 123      |
      | abcde    |
      | 1a2b3    |

  @ui @success
  Scenario Outline: Successful login form submission with valid inputs
    Given the user navigates to the login page
    When the user enters the email as "<email>"
    And the user enters the password as "<password>"
    And the user clicks the login button
    Then no error message is displayed
    And the user is logged in successfully

    Examples:
      | email            | password  |
      | user@example.com | valid123  |
      | test.user@domain.com | password1 |