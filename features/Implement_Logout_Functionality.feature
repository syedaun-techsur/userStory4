@ui @api @success
Feature: Implement Logout Functionality
  As a logged-in user,
  I want to log out of my account,
  So that no one else can access my data.

  @ui @api @success
  Scenario Outline: User logs out and session/token is cleared successfully
    Given the user is logged in with a valid session token "<session_token>"
    When the user clicks on the logout button
    Then the session token should be cleared from the system
    And the user should be redirected to the login page at "<login_page_url>"
    And the login page should be displayed with title "<login_page_title>"

    Examples:
      | session_token                 | login_page_url       | login_page_title    |
      | abcdef1234567890token         | /login              | Login to your account |

  @ui @api @success
  Scenario Outline: Access to dashboard is denied after the user logs out
    Given the user has logged out and the session token is cleared
    When the user attempts to access the dashboard page at "<dashboard_url>"
    Then the user should be redirected to the login page at "<login_page_url>"
    And the login page should be displayed with title "<login_page_title>"

    Examples:
      | dashboard_url   | login_page_url       | login_page_title    |
      | /dashboard      | /login              | Login to your account |