from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

@given("the login page is opened")
def step_impl(context):
    login_route = "/login"
    context.driver.get(context.base_url + login_route)
    # Wait until the login form is present on the page after navigating
    by, selector = context.get_locator("login-form")
    WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((by, selector))
    )

@then("the login form is visible")
def step_impl(context):
    by, selector = context.get_locator("login-form")
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )
    assert element.is_displayed(), "Login form is not visible"

@then("the login form includes an email input field")
def step_impl(context):
    # Prefer locator with data-testid for email input; fallback to id or type
    try:
        by, selector = context.get_locator("email-input")
    except KeyError:
        try:
            by, selector = context.get_locator("email")
        except KeyError:
            # fallback to type=email selector
            by, selector = 'css selector', "[type='email']"
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )
    assert element.is_displayed(), "Email input field is not visible"

@then("the login form includes a password input field")
def step_impl(context):
    # Prefer locator with data-testid for password input; fallback to id or placeholder
    try:
        by, selector = context.get_locator("password-input")
    except KeyError:
        try:
            by, selector = context.get_locator("password")
        except KeyError:
            # fallback to css placeholder selector
            by, selector = 'css selector', "[placeholder='Enter your password']"
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )
    assert element.is_displayed(), "Password input field is not visible"

@then("the login form includes a login button")
def step_impl(context):
    by, selector = context.get_locator("login-button")
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )
    assert element.is_displayed(), "Login button is not visible"

@when("I leave the email field as {email}")
def step_impl(context, email):
    value = "" if email.strip() == "<empty>" else email.strip()
    # Clear and set email input accordingly
    try:
        by, selector = context.get_locator("email-input")
    except KeyError:
        try:
            by, selector = context.get_locator("email")
        except KeyError:
            by, selector = 'css selector', "[type='email']"
    email_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    email_input.clear()
    email_input.send_keys(value)

@when("I leave the password field as {password}")
def step_impl(context, password):
    value = "" if password.strip() == "<empty>" else password.strip()
    try:
        by, selector = context.get_locator("password-input")
    except KeyError:
        try:
            by, selector = context.get_locator("password")
        except KeyError:
            by, selector = 'css selector', "[type='password']"
    password_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    password_input.clear()
    password_input.send_keys(value)

@when("I enter the email {email}")
def step_impl(context, email):
    value = email.strip().strip('"').strip("'")
    try:
        by, selector = context.get_locator("email-input")
    except KeyError:
        try:
            by, selector = context.get_locator("email")
        except KeyError:
            by, selector = 'css selector', "[type='email']"
    email_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    email_input.clear()
    email_input.send_keys(value)

@when("I enter the password {password}")
def step_impl(context, password):
    value = password.strip().strip('"').strip("'")
    try:
        by, selector = context.get_locator("password-input")
    except KeyError:
        try:
            by, selector = context.get_locator("password")
        except KeyError:
            by, selector = 'css selector', "[type='password']"
    password_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    password_input.clear()
    password_input.send_keys(value)

@when("I click the login button")
def step_impl(context):
    by, selector = context.get_locator("login-button")
    button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    button.click()

@then('I see the error message "{error_message}"')
def step_impl(context, error_message):
    error_message = error_message.strip()
    # Heuristic: find a locator key matching the error message keywords, otherwise use generic error-message locator
    # Check for "email" or "password" keywords in error_message to select field-specific error element
    message_lower = error_message.lower()
    error_locator_key = None
    
    if "email" in message_lower:
        if "email-error" in context.locators:
            error_locator_key = "email-error"
        elif "email" in context.locators:
            error_locator_key = "email"
    elif "password" in message_lower:
        if "password-error" in context.locators:
            error_locator_key = "password-error"
        elif "password" in context.locators:
            error_locator_key = "password"
    
    if not error_locator_key:
        # Use generic error message locator
        if "error-message" in context.locators:
            error_locator_key = "error-message"
        else:
            # Fallback to css selector for some error container if exist or raise error
            error_locator_key = None

    if error_locator_key:
        by, selector = context.get_locator(error_locator_key)
        try:
            error_element = WebDriverWait(context.driver, 10).until(
                EC.visibility_of_element_located((by, selector))
            )
        except TimeoutException:
            assert False, f"Error message element '{error_locator_key}' not visible"
        assert error_element.is_displayed(), "Error message is not displayed"
        # Strip and normalize text for comparison to avoid whitespace issues
        actual_text = error_element.text.strip()
        assert actual_text == error_message, f"Expected error '{error_message}', but got '{actual_text}'"
    else:
        # No specific error locator found
        raise AssertionError("No appropriate error message locator found for the message: " + error_message)

@then("I should be redirected to the dashboard")
def step_impl(context):
    # Wait until URL contains /dashboard
    expected_path = "/dashboard"
    try:
        WebDriverWait(context.driver, 10).until(
            EC.url_contains(expected_path)
        )
    except TimeoutException:
        current_url = context.driver.current_url
        assert False, f"Expected URL to contain '{expected_path}', but current URL is '{current_url}'."
    # Additionally, verify dashboard element presence
    by, selector = context.get_locator("dashboard")
    dashboard_element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )
    assert dashboard_element.is_displayed(), "Dashboard page content is not visible"