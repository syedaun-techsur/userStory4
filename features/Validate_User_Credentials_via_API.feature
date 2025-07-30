Feature: Validate User Credentials via API
  As a system,
  I want to receive login credentials from the frontend,
  So that I can validate them against stored user data and provide appropriate responses.

  @api @ui @success
  Scenario Outline: Successfully authenticate user and receive token
    Given the user provides email "<email>" and password "<password>"
    When the frontend sends a POST request to "/api/login" with the credentials
    Then the API responds with status code 200
    And the response contains a valid authentication token

    Examples:
      | email              | password     |
      | admin@example.com  | password123  |

  @api @ui @negative
  Scenario Outline: Fail authentication due to invalid credentials
    Given the user provides email "<email>" and password "<password>"
    When the frontend sends a POST request to "/api/login" with the credentials
    Then the API responds with status code 401
    And the response contains error message "Unauthorized: Invalid email or password"

    Examples:
      # Invalid password for valid email
      | email             | password    |
      | admin@example.com | wrongpass   |
      # Invalid email with valid password
      | email             | password    |
      | wrong@example.com | password123 |
      # Both email and password invalid
      | email             | password    |
      | wrong@example.com | wrongpass   |

  @validation @ui @api @negative
  Scenario Outline: Fail login due to missing or invalid email input
    Given the user provides email "<email>" and password "<password>"
    When the frontend validates the input fields
    Then the email validation error "<email_error>" should be displayed

    Examples:
      | email     | password     | email_error                     |
      | <empty>   | password123  | Email is required               |
      | invalid   | password123  | Please enter a valid email address |

  @validation @ui @api @negative
  Scenario Outline: Fail login due to missing or invalid password input
    Given the user provides email "<email>" and password "<password>"
    When the frontend validates the input fields
    Then the password validation error "<password_error>" should be displayed

    Examples:
      | email              | password  | password_error                      |
      | admin@example.com   | <empty>   | Password is required                |
      | admin@example.com   | short    | Password must be at least 6 characters |

  @validation @ui @negative
  Scenario: Fail login when useAuth hook is used outside AuthProvider context
    Given the user is on the login interface without proper authentication context
    When an authentication action is attempted via useAuth hook
    Then the error message "useAuth must be used within an AuthProvider" should be shown