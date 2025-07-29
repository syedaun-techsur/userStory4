Feature: Display User Dashboard After Login
  As a logged-in user,
  I want to see a personalized dashboard,
  So that I can view relevant information after login.

  @ui @success @api
  Scenario Outline: Authorized user accesses dashboard and views personalized content
    Given the user has logged in with a valid token "<token>"
    When the user navigates to the "/dashboard" route
    Then the user should remain on the "/dashboard" page
    And the dashboard should display the personalized content for user "<username>"

    Examples:
      | token          | username     |
      | valid-token-123| alice        |
      | valid-token-456| bob          |

  @ui @negative
  Scenario Outline: Unauthorized user is redirected to login when accessing dashboard
    Given the user has not logged in or has an invalid token "<token>"
    When the user attempts to navigate to the "/dashboard" route
    Then the user should be redirected to the "/login" page
    And an error message "You must be logged in to access the dashboard" should be displayed

    Examples:
      | token         |
      | <empty>       |
      | invalid-token |