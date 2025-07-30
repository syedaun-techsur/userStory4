@ui @api @success
Feature: Display User Dashboard After Login
  As a logged-in user,
  I want to see a personalized dashboard,
  So that I can view relevant information immediately after login.

  @ui @api @success
  Scenario Outline: Authorized user accesses dashboard and sees user-specific content
    Given the user is logged in with email "<email>" and password "<password>"
    When the user navigates to the /dashboard route
    Then the dashboard page is displayed with personalized content for "<email>"

    Examples:
      | email              | password    |
      | admin@example.com   | password123 |

  @ui @api @negative
  Scenario Outline: Unauthorized user attempts to access dashboard and is redirected to login
    Given the user has a "<tokenStatus>" token/session
    When the user requests the /dashboard route
    Then the user is redirected to the login page with message "Please login to continue"

    Examples:
      | tokenStatus  |
      | invalid      |
      | expired      |
      | <empty>     |

  @ui @validation @negative
  Scenario Outline: Login failure due to missing or invalid credentials
    Given the login page is displayed
    When the user enters email "<emailInput>" and password "<passwordInput>"
    And submits the login form
    Then the login fails with error message "<errorMessage>"

    Examples:
      | emailInput        | passwordInput | errorMessage                               |
      | <empty>           | password123   | Email is required                          |
      | invalid-email     | password123   | Please enter a valid email address         |
      | admin@example.com | <empty>       | Password is required                        |
      | admin@example.com | short         | Password must be at least 6 characters    |