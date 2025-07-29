from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

@given("the user navigates to the login page")
def step_navigate_login_page(context):
    url = context.base_url + "/login"
    context.driver.get(url)
    # Wait for login form or page to be ready (presence of login form)
    by, selector = context.get_locator("login-form")
    WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((by, selector)))

@then("the login form is displayed")
def step_login_form_displayed(context):
    by, selector = context.get_locator("login-form")
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )
    assert element.is_displayed(), "Login form is not displayed"

@then("the email input field is visible")
def step_email_field_visible(context):
    # Prefer data-testid selector if available for email input
    keys_to_try = ["email-input", "email"]
    for key in keys_to_try:
        try:
            by, selector = context.get_locator(key)
            element = WebDriverWait(context.driver, 10).until(
                EC.visibility_of_element_located((by, selector))
            )
            if element.is_displayed():
                return
        except TimeoutException:
            continue
    assert False, "Email input field is not visible"

@then("the password input field is visible")
def step_password_field_visible(context):
    keys_to_try = ["password-input", "password"]
    for key in keys_to_try:
        try:
            by, selector = context.get_locator(key)
            element = WebDriverWait(context.driver, 10).until(
                EC.visibility_of_element_located((by, selector))
            )
            if element.is_displayed():
                return
        except TimeoutException:
            continue
    assert False, "Password input field is not visible"

@then("the login button is visible")
def step_login_button_visible(context):
    # Prefer login-button data-testid locator
    keys_to_try = ["login-button"]
    for key in keys_to_try:
        try:
            by, selector = context.get_locator(key)
            element = WebDriverWait(context.driver, 10).until(
                EC.visibility_of_element_located((by, selector))
            )
            if element.is_displayed():
                return
        except TimeoutException:
            continue
    assert False, "Login button is not visible"

@when("the user leaves the email field as \"{email}\"")
def step_leave_email_field(context, email):
    email_value = email.strip('"').strip()
    if email_value == "<empty>":
        email_value = ""
    by, selector = context.get_locator("email-input")
    email_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    email_input.clear()
    if email_value:
        email_input.send_keys(email_value)

@when("the user leaves the password field as \"{password}\"")
def step_leave_password_field(context, password):
    password_value = password.strip('"').strip()
    if password_value == "<empty>":
        password_value = ""
    by, selector = context.get_locator("password-input")
    password_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    password_input.clear()
    if password_value:
        password_input.send_keys(password_value)

@when("the user clicks the login button")
def step_click_login_button(context):
    by, selector = context.get_locator("login-button")
    login_button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    login_button.click()

@then("the error message \"{error_message}\" is displayed")
def step_error_message_displayed(context, error_message):
    error_message_text = error_message.strip('"').strip()
    # Determine locator key for error message by matching known keywords
    error_key = None
    message_lower = error_message_text.lower()
    if "email" in message_lower:
        # Use email-error locator first if possible
        try:
            context.get_locator("email-error")
            error_key = "email-error"
        except KeyError:
            error_key = "error-message"
    elif "password" in message_lower:
        try:
            context.get_locator("password-error")
            error_key = "password-error"
        except KeyError:
            error_key = "error-message"
    else:
        error_key = "error-message"
    by, selector = context.get_locator(error_key)
    error_element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )
    displayed_text = error_element.text.strip()
    assert error_message_text == displayed_text, f"Expected error message '{error_message_text}', got '{displayed_text}'"

@when("the user enters the email as \"{email}\"")
def step_enter_email(context, email):
    email_value = email.strip('"').strip()
    if email_value == "<empty>":
        email_value = ""
    by, selector = context.get_locator("email-input")
    email_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    email_input.clear()
    if email_value:
        email_input.send_keys(email_value)

@when("the user enters the password as \"{password}\"")
def step_enter_password(context, password):
    password_value = password.strip('"').strip()
    if password_value == "<empty>":
        password_value = ""
    by, selector = context.get_locator("password-input")
    password_input = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    password_input.clear()
    if password_value:
        password_input.send_keys(password_value)

@then("no error message is displayed")
def step_no_error_message(context):
    # Check no error messages visible on the page
    error_keys = ["error-message", "email-error", "password-error"]
    for key in error_keys:
        try:
            by, selector = context.get_locator(key)
            elements = context.driver.find_elements(by, selector)
            for element in elements:
                if element.is_displayed() and element.text.strip():
                    assert False, f"Unexpected error message displayed: {element.text.strip()}"
        except KeyError:
            # If locator not found, ignore and continue
            continue

@then("the user is logged in successfully")
def step_user_logged_in(context):
    # Heuristic: User redirected to /dashboard and dashboard element visible
    expected_path = "/dashboard"
    # Wait for URL to contain dashboard path
    WebDriverWait(context.driver, 10).until(
        EC.url_contains(expected_path)
    )
    current_url = context.driver.current_url
    assert expected_path in current_url, f"User not redirected to dashboard; current URL: {current_url}"
    # Validate presence of dashboard element
    by, selector = context.get_locator("dashboard")
    dashboard_element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )
    assert dashboard_element.is_displayed(), "Dashboard element not displayed after login"