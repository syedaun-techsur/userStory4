Feature: Display Login Form
  As a user, I want to see a login form with fields for email and password,
  so that I can enter my credentials to access the app.

  @ui @validation
  Scenario Outline: Validate presence of login form fields and login button
    Given the user is on the login page
    Then the login form should contain an email input field
    And the login form should contain a password input field
    And the login form should contain a login button

  @ui @validation @negative
  Scenario Outline: Validate required field errors when submitting empty form
    Given the user is on the login page
    When the user submits the login form with email "<email>" and password "<password>"
    Then the error message for email should be "<emailError>"
    And the error message for password should be "<passwordError>"

    Examples:
      | email    | password  | emailError          | passwordError              |
      | <empty>  | <empty>   | Email is required   | Password is required       |
      | <empty>  | password123| Email is required  |                             |
      | admin@example.com | <empty>    |                   | Password is required       |

  @ui @validation @negative
  Scenario Outline: Validate email format error message on invalid emails
    Given the user is on the login page
    When the user enters an invalid email "<email>" in the email input field
    And the user enters a valid password "password123" in the password input field
    And the user submits the login form
    Then the error message for email should be "Please enter a valid email address"
    And no error message should be shown for password

    Examples:
      | email               |
      | invalid-email       |
      | user@domain         |
      | user@domain,com     |
      | admin@example       |

  @ui @validation @negative
  Scenario Outline: Validate password length requirement error
    Given the user is on the login page
    When the user enters a valid email "admin@example.com" in the email input field
    And the user enters a password "<password>" in the password input field
    And the user submits the login form
    Then the error message for password should be "Password must be at least 6 characters"

    Examples:
      | password |
      | 123     |
      | abc     |
      | 12      |

  @ui @success
  Scenario Outline: Successful login with valid credentials
    Given the user is on the login page
    When the user enters the email "admin@example.com" in the email input field
    And the user enters the password "password123" in the password input field
    And the user submits the login form
    Then the user is successfully logged in

  @negative
  Scenario: Error when attempting to use authentication outside of provider
    When the app is initialized without an AuthProvider
    Then the error message "useAuth must be used within an AuthProvider" should be shown