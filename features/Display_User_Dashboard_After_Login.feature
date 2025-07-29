Feature: Display User Dashboard After Login
  As a logged-in user,
  I want to see a personalized dashboard,
  so that I can view relevant information after login.

  @ui @api @success
  Scenario Outline: Authorized users access dashboard and see user-specific content
    Given the user is logged in with a valid session token "<token>"
    When the user navigates to the dashboard page at "/dashboard"
    Then the dashboard page is displayed
    And the dashboard shows personalized content for user "<username>"

    Examples:
      | token          | username    |
      | valid-token-01 | alice       |
      | valid-token-02 | bob         |

  @ui @api @negative
  Scenario Outline: Unauthorized users are redirected to login when accessing dashboard
    Given the user has a session token "<token>"
    When the user navigates to the dashboard page at "/dashboard"
    Then the user is redirected to the login page
    And the login page displays the message "Please log in to continue"

    Examples:
      | token        |
      | <empty>      |
      | invalid-token|