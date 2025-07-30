from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

@given('the user is logged in with email "{email}" and password "{password}"')
def step_given_user_logged_in(context, email, password):
    email = email.strip('"').strip()
    password = password.strip('"').strip()
    # Navigate to login page
    context.driver.get(context.base_url + "/login")
    # Wait for login form
    by, selector = context.get_locator("login-form")
    WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((by, selector))
    )
    # Enter email
    by_email, selector_email = context.get_locator("email-input")
    email_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by_email, selector_email))
    )
    email_input.clear()
    email_input.send_keys(email)
    # Enter password
    by_password, selector_password = context.get_locator("password-input")
    password_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by_password, selector_password))
    )
    password_input.clear()
    password_input.send_keys(password)
    # Submit form
    by_submit, selector_submit = context.get_locator("login-button")
    submit_button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by_submit, selector_submit))
    )
    submit_button.click()
    # Wait until dashboard or login form is loaded, timeout 15 sec
    try:
        by_dash, selector_dash = context.get_locator("dashboard")
        WebDriverWait(context.driver, 15).until(
            EC.presence_of_element_located((by_dash, selector_dash))
        )
    except TimeoutException:
        # Login failed or other error, fail the step explicitly
        raise AssertionError("Login failed: dashboard page did not load after login attempt.")

@given('the user has a "{tokenStatus}" token/session')
def step_given_user_token_status(context, tokenStatus):
    tokenStatus = tokenStatus.strip('"').strip()
    # Handle token management by cookie or local storage
    # Clear existing cookies/local storage first
    context.driver.delete_all_cookies()
    if tokenStatus == "invalid":
        # Set invalid token cookie
        context.driver.get(context.base_url + "/")
        context.driver.add_cookie({"name": "session_token", "value": "invalidtoken123", "path": "/"})
    elif tokenStatus == "expired":
        # Set expired token cookie
        context.driver.get(context.base_url + "/")
        context.driver.add_cookie({"name": "session_token", "value": "expiredtoken123", "path": "/"})
    elif tokenStatus == "<empty>" or tokenStatus == "":
        # No token set, just ensure cookies cleared
        pass
    else:
        # For any other status, TODO to adjust if needed
        pass
    # Refresh page after setting cookies to apply session state
    context.driver.refresh()

@given('the login page is displayed')
def step_given_login_page_displayed(context):
    context.driver.get(context.base_url + "/login")
    # Wait for login form visible
    by, selector = context.get_locator("login-form")
    WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )

@when('the user navigates to the /dashboard route')
def step_when_user_navigates_dashboard(context):
    context.driver.get(context.base_url + "/dashboard")

@when('the user requests the /dashboard route')
def step_when_user_requests_dashboard(context):
    # This can be interpreted as UI navigation to /dashboard or API call
    # As per instructions and metadata, we perform UI navigation via Selenium
    context.driver.get(context.base_url + "/dashboard")

@when('the user enters email "{emailInput}" and password "{passwordInput}"')
def step_when_user_enters_credentials(context, emailInput, passwordInput):
    emailInput = emailInput.strip('"').strip()
    passwordInput = passwordInput.strip('"').strip()
    if emailInput == "<empty>":
        emailInput = ""
    if passwordInput == "<empty>":
        passwordInput = ""
    # Wait for email input
    by_email, selector_email = context.get_locator("email-input")
    email_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by_email, selector_email))
    )
    email_input.clear()
    email_input.send_keys(emailInput)
    # Wait for password input
    by_password, selector_password = context.get_locator("password-input")
    password_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by_password, selector_password))
    )
    password_input.clear()
    password_input.send_keys(passwordInput)

@when('submits the login form')
def step_when_user_submits_login_form(context):
    by_submit, selector_submit = context.get_locator("login-button")
    submit_button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by_submit, selector_submit))
    )
    submit_button.click()

@then('the dashboard page is displayed with personalized content for "{email}"')
def step_then_dashboard_displayed_with_content(context, email):
    email = email.strip('"').strip()
    # Wait for dashboard presence
    by_dash, selector_dash = context.get_locator("dashboard")
    dashboard = WebDriverWait(context.driver, 15).until(
        EC.presence_of_element_located((by_dash, selector_dash))
    )
    # Verify welcome message or user info card contains email customized content

    # Check welcome message
    by_welcome, selector_welcome = context.get_locator("welcome-message")
    welcome_msg = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by_welcome, selector_welcome))
    )
    # Verify email is shown in welcome message text (case insensitive)
    welcome_text = welcome_msg.text.lower()
    assert email.lower() in welcome_text, f"Dashboard does not contain personalized email '{email}'."

@then('the user is redirected to the login page with message "Please login to continue"')
def step_then_redirected_to_login_with_message(context):
    # Wait for URL to be login page URL
    WebDriverWait(context.driver, 10).until(
        EC.url_matches(context.base_url + "/login")
    )
    # Ensure the message "Please login to continue" is visible on page
    # Try to locate error-message element and verify text
    by_error, selector_error = context.get_locator("error-message")
    error_element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by_error, selector_error))
    )
    error_text = error_element.text.strip()
    assert "Please login to continue" in error_text, \
        f'Expected message "Please login to continue" not found, actual: "{error_text}"'

@then('the login fails with error message "{errorMessage}"')
def step_then_login_fails_with_error(context, errorMessage):
    errorMessage = errorMessage.strip('"').strip()
    # Choose locator key based on error message keywords
    # Map error messages to appropriate error locator keys
    lower_msg = errorMessage.lower()
    locator_key = None
    if "email" in lower_msg:
        if "required" in lower_msg or "valid" in lower_msg:
            # Use email-error locator if present
            # confirm locator exists
            try:
                context.get_locator("email-error")
                locator_key = "email-error"
            except Exception:
                locator_key = "error-message"
    elif "password" in lower_msg:
        try:
            context.get_locator("password-error")
            locator_key = "password-error"
        except Exception:
            locator_key = "error-message"
    else:
        # Default fallback locator
        locator_key = "error-message"
    if locator_key is None:
        locator_key = "error-message"
    by_err, selector_err = context.get_locator(locator_key)
    error_element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by_err, selector_err))
    )
    text = error_element.text.strip()
    # Allow partial match if full doesn't match (depends on wording)
    assert errorMessage in text, f"Expected error message '{errorMessage}' not found. Actual message: '{text}'"