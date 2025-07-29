Feature: Validate User Credentials via API
  As a system
  I want to receive login credentials from the frontend
  So that I can validate them against stored user data via the API endpoint

  @api @validation @ui @negative
  Scenario Outline: User fails to login with missing or invalid credentials
    Given the user provides email "<email>" and password "<password>"
    When the user sends a POST request to "/api/login" with the provided credentials
    Then the API response status code should be 401
    And the API response should contain error message "<error_message>"

    Examples:
      | email          | password    | error_message                   |
      | <empty>        | password123 | Email is required               |
      | invalid-email  | password123 | Please enter a valid email address |
      | user@example.com | <empty>    | Password is required            |
      | user@example.com | short    | Password must be at least 6 characters |

  @api @success @ui
  Scenario Outline: User logs in successfully with valid credentials
    Given the user provides email "<email>" and password "<password>"
    When the user sends a POST request to "/api/login" with the provided credentials
    Then the API response status code should be 200
    And the API response should contain an authentication token

    Examples:
      | email            | password   |
      | validuser@test.com | correctpassword |

  @api @negative
  Scenario: Invalid credentials return unauthorized error
    Given the user provides email "validuser@test.com" and password "wrongpassword"
    When the user sends a POST request to "/api/login" with the provided credentials
    Then the API response status code should be 401
    And the API response should contain error message "Invalid email or password"