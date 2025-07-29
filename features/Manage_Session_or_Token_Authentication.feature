@session_authentication
Feature: Manage Session or Token Authentication
  As a user
  I want to stay logged in securely
  So that I don’t have to log in repeatedly

  @ui @api @success
  Scenario Outline: Issue JWT or session cookie on login with valid credentials
    Given the login page is displayed
    When I enter a valid email "<email>"
    And I enter a valid password "<password>"
    And I submit the login form
    Then I should receive a JWT or session cookie from the backend
    And the token or cookie should be securely stored on the client
    And I should be redirected to the authenticated user homepage

    Examples:
      | email               | password   |
      | user@example.com    | Password1  |
      | test.user@mail.com  | Secret123  |

  @ui @api @negative @validation
  Scenario Outline: Validate login form inputs and show appropriate validation messages
    Given the login page is opened
    When I enter email "<email>"
    And I enter password "<password>"
    And I submit the login form
    Then I should see the validation message "<validation_message>"

    Examples:
      | email             | password  | validation_message                     |
      | <empty>           | Password1 | Email is required                     |
      | invalid-email     | Password1 | Please enter a valid email address   |
      | user@example.com  | <empty>   | Password is required                  |
      | user@example.com  | short     | Password must be at least 6 characters|

  @api
  Scenario Outline: Backend validates token on protected routes
    Given I am logged in with a valid token issued after login with email "<email>" and password "<password>"
    When I request access to protected resource "<resource>"
    Then the backend should verify the token validity
    And the backend should allow access to the resource if token is valid

    Examples:
      | email             | password  | resource              |
      | user@example.com  | Password1 | /dashboard            |
      | test.user@mail.com| Secret123 | /account/settings     |

  @api @negative
  Scenario Outline: Backend denies access on protected routes with invalid or missing token
    Given I am not logged in or have an invalid token
    When I request access to protected resource "<resource>"
    Then the backend should reject the request with an authentication error

    Examples:
      | resource         |
      | /dashboard       |
      | /account/settings|