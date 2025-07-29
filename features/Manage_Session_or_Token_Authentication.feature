@ui @api @success
Feature: Manage Session or Token Authentication
  In order to stay logged in securely
  As a user
  I want to receive and store a token or session cookie on login and have it validated on protected routes

  @ui @api @success
  Scenario Outline: Successful login issues JWT or session cookie and stores it securely
    Given the user is on the login page
    When the user submits valid credentials with email "<email>" and password "<password>"
    Then the backend issues a JWT or session cookie to the client
    And the client securely stores the token using "<storage_method>"
    And the user is redirected to the protected area

    Examples:
      | email                | password | storage_method             |
      | user@example.com     | Pass1234 | localStorage               |
      | user2@example.com    | Pa$$word | HTTPOnly cookie           |

  @ui @api @success
  Scenario Outline: Backend validates token on protected routes granting access
    Given the user has a valid token stored in "<storage_method>"
    When the user requests access to the protected route "<route>"
    Then the backend validates the token successfully
    And the user is granted access to "<route>"

    Examples:
      | storage_method       | route            |
      | localStorage         | /dashboard       |
      | HTTPOnly cookie      | /profile         |

  @ui @validation @negative
  Scenario Outline: Login fails when required fields are missing or invalid
    Given the user is on the login page
    When the user submits credentials with email "<email>" and password "<password>"
    Then the login is rejected with the error message "<error_message>"

    Examples:
      | email             | password | error_message                     |
      | <empty>           | Pass1234 | Email is required                 |
      | invalidemail.com  | Pass1234 | Please enter a valid email address|
      | user@example.com  | <empty>  | Password is required             |
      | user@example.com  | 123     | Password must be at least 6 characters |

  @ui @negative
  Scenario: Using authentication functionality outside AuthProvider raises error
    Given the user attempts to use useAuth hook outside an AuthProvider context
    Then the error message "useAuth must be used within an AuthProvider" is displayed