# language: en
@ui @success
Feature: Implement Logout Functionality
  As a logged-in user,
  I want to log out of my account,
  So that no one else can access my data.

  @ui @success
  Scenario Outline: User successfully logs out and is redirected to login page
    Given the user is logged in with email "<email>" and password "<password>"
    When the user clicks the logout button
    Then the user's session or token is cleared from the browser
    And the user is redirected to the login page at "<login_url>"
    And the login page displays "Please enter your credentials to login"

    Examples:
      | email              | password     | login_url           |
      | admin@example.com  | password123  | /login              |

  @ui @api @negative
  Scenario Outline: Access to dashboard is denied after user has logged out
    Given the user is logged in with email "<email>" and password "<password>"
    And the user clicks the logout button
    When the user tries to access the dashboard at "<dashboard_url>"
    Then the user is redirected to the login page at "<login_url>"
    And the login page displays "Please enter your credentials to login"

    Examples:
      | email              | password     | dashboard_url  | login_url |
      | admin@example.com  | password123  | /dashboard    | /login    |

  @ui @negative
  Scenario Outline: User cannot see dashboard content after logout
    Given the user is logged in with email "<email>" and password "<password>"
    When the user clicks the logout button
    And the user attempts to view dashboard content
    Then the dashboard content is not visible
    And the login page is displayed with message "Please enter your credentials to login"

    Examples:
      | email              | password     |
      | admin@example.com  | password123  |