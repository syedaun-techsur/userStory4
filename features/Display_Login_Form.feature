@ui @validation
Feature: Display Login Form
  As a user
  I want to see a login form with email and password fields
  So that I can enter my credentials to access the app

  @ui @validation
  Scenario Outline: Login form displays all required fields and login button
    Given the user navigates to the login page
    Then the login form is visible
    And the email input field is present
    And the password input field is present
    And the login button is present

  @ui @validation
  Scenario Outline: Submit login form with missing email and/or password shows required field errors
    Given the user is on the login page
    When the user enters "<email>" into the email field
    And the user enters "<password>" into the password field
    And the user clicks the login button
    Then the error message for the email field is "<email_error>"
    And the error message for the password field is "<password_error>"

    Examples:
      | email   | password   | email_error          | password_error             |
      | <empty> | <empty>    | Email is required    | Password is required       |
      | <empty> | validpass  | Email is required    | <empty>                   |
      | user@example.com | <empty> | <empty>           | Password is required       |

  @ui @validation
  Scenario Outline: Submit login form with invalid email format shows proper error
    Given the user is on the login page
    When the user enters "<email>" into the email field
    And the user enters "<password>" into the password field
    And the user clicks the login button
    Then the error message for the email field is "Please enter a valid email address"
    And no password field error is displayed

    Examples:
      | email            | password   |
      | invalid-email     | validpass  |
      | user@@example.com | validpass  |
      | userexample.com   | validpass  |

  @ui @validation
  Scenario Outline: Submit login form with too short password shows password length error
    Given the user is on the login page
    When the user enters "<email>" into the email field
    And the user enters "<password>" into the password field
    And the user clicks the login button
    Then the error message for the password field is "Password must be at least 6 characters"
    And no email field error is displayed

    Examples:
      | email            | password |
      | user@example.com | 123     |
      | test@domain.com  | 12345   |

  @ui @success
  Scenario Outline: Submit login form with valid email and password
    Given the user is on the login page
    When the user enters "<email>" into the email field
    And the user enters "<password>" into the password field
    And the user clicks the login button
    Then no error messages are shown
    And the user is authenticated successfully

    Examples:
      | email            | password  |
      | user@example.com | password1 |
      | test@domain.com  | abcdef12  |