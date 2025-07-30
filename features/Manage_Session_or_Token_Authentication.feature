@ui @api @success
Feature: Manage Session or Token Authentication
  As a user,
  I want to stay logged in securely,
  So that I don’t have to log in repeatedly.

  @ui @api @success
  Scenario Outline: Successful login issues JWT or session cookie and client stores it securely
    Given a login page is displayed
    When the user submits login credentials with email "<email>" and password "<password>"
    Then the backend issues a JWT or session cookie
    And the client securely stores the issued token
    Examples:
      | email               | password    |
      | admin@example.com   | password123 |

  @ui @api @success
  Scenario Outline: Backend validates token on protected routes after login
    Given a user is logged in with email "<email>" and password "<password>"
    When the user requests a protected route with the stored token
    Then the backend validates the token successfully
    And the user can access the protected content
    Examples:
      | email               | password    |
      | admin@example.com   | password123 |

  @ui @validation @negative
  Scenario Outline: Login fails when email or password inputs are invalid
    Given the login page is displayed
    When the user enters email "<email>" and password "<password>"
    And submits the login form
    Then the system shows validation message "<validation_message>"
    Examples:
      | email           | password      | validation_message                  |
      | <empty>         | password123   | Email is required                  |
      | invalid-email   | password123   | Please enter a valid email address |
      | admin@example.com | <empty>     | Password is required               |
      | admin@example.com | short      | Password must be at least 6 characters |

  @ui @api @negative
  Scenario Outline: Login fails with invalid credentials
    Given the login page is displayed
    When the user submits login credentials with email "<email>" and password "<password>"
    Then the login is rejected with error message "useAuth must be used within an AuthProvider"
    Examples:
      | email             | password    |
      | user@example.com  | wrongpass   |
      | test@domain.com   | 123456      |
      | admin@example.com | wrongpass   |