Feature: Validate User Credentials via API
  As a system,
  I want to receive login credentials from the frontend,
  So that I can validate them against stored user data and return appropriate responses.

  @api @ui @validation @negative
  Scenario Outline: Fail login due to missing or invalid email input
    Given the user provides "<email>" as email
    And the user provides "<password>" as password
    When the client calls the POST /api/login endpoint with credentials
    Then the response status code should be 401
    And the response error message should be "<error_message>"

    Examples:
      | email      | password   | error_message                     |
      | <empty>    | validPass1 | Email is required                 |
      | invalid@   | validPass1 | Please enter a valid email address|

  @api @ui @validation @negative
  Scenario Outline: Fail login due to missing or invalid password input
    Given the user provides a valid email "user@example.com"
    And the user provides "<password>" as password
    When the client calls the POST /api/login endpoint with credentials
    Then the response status code should be 401
    And the response error message should be "<error_message>"

    Examples:
      | password  | error_message                       |
      | <empty>   | Password is required                |
      | short    | Password must be at least 6 characters |

  @api @ui @negative
  Scenario Outline: Fail login due to incorrect credentials
    Given the user provides a valid email "user@example.com"
    And the user provides an invalid password "<password>"
    When the client calls the POST /api/login endpoint with credentials
    Then the response status code should be 401
    And the response error message should be "Unauthorized: Invalid email or password"

    Examples:
      | password     |
      | wrongpass123 |
      | anotherbad   |

  @api @ui @success
  Scenario Outline: Successful login with valid credentials
    Given the user provides a valid email "<email>"
    And the user provides a valid password "<password>"
    When the client calls the POST /api/login endpoint with credentials
    Then the response status code should be 200
    And the response body should contain a token key
    And the response token should be a valid JWT or session ID

    Examples:
      | email            | password    |
      | user1@example.com | correctPass |
      | user2@example.com | s3curePwd   |