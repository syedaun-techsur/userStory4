@ui @api @success
Feature: Implement Logout Functionality
  As a logged-in user,
  I want to log out of my account,
  So that no one else can access my data.

  @ui @api @success
  Scenario Outline: User clicks on the logout button and is successfully logged out
    Given the user is logged in with a valid session token "<token>"
    When the user clicks on the logout button
    Then the session token is cleared from the client storage
    And the user is redirected to the login page at "<login_url>"
    And the user sees the login page title "<login_title>"

    Examples:
      | token         | login_url        | login_title          |
      | abcdef123456  | /login           | Login to your account|

  @ui @api @negative
  Scenario Outline: User tries to access the dashboard after logout and access is denied
    Given the user has logged out and the session token is cleared
    When the user navigates to the dashboard page at "<dashboard_url>"
    Then the user is redirected to the login page at "<login_url>"
    And the user sees an access denied message "<access_denied_message>"

    Examples:
      | dashboard_url | login_url | access_denied_message                   |
      | /dashboard    | /login    | Please log in to access your dashboard |