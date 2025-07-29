from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEFAULT_TIMEOUT = 10
BASE_URL = "http://localhost:3000"  # As per instructions


def get_locator(context, key):
    if not hasattr(context, "locators"):
        raise AssertionError("Locators not loaded in context.")
    locators = context.locators
    if key not in locators:
        raise AssertionError(f"Locator for key '{key}' not found in locators.")
    locator_info = locators[key]
    by_raw = locator_info.get("by")
    selector = locator_info.get("selector")
    if not by_raw or not selector:
        raise AssertionError(f"Locator for key '{key}' is missing 'by' or 'selector' attributes.")
    # The 'by' value in locators.json is lowercased version of By enum keys generally,
    # but some locators use custom strings like 'data-testid'.
    # We must map them accordingly:
    # Selenium By supports 'id', 'xpath', 'css selector', 'class name', 'name', 'tag name', 'link text', 'partial link text'
    # And supports By.CSS_SELECTOR, By.ID, etc.
    # The locators.json uses "data-testid" as "by" string, which is not standard By enum.
    # However, we can use By.CSS_SELECTOR with the selector "[data-testid='value']".
    # So if 'by' is 'data-testid' we must treat as CSS_SELECTOR.
    # If 'by' is a standard By enum member, use it.
    # Also handle 'type', 'placeholder' which are CSS selectors as well.
    by_map = {
        "id": By.ID,
        "css": By.CSS_SELECTOR,
        "css selector": By.CSS_SELECTOR,
        "xpath": By.XPATH,
        "class name": By.CLASS_NAME,
        "name": By.NAME,
        "tag name": By.TAG_NAME,
        "link text": By.LINK_TEXT,
        "partial link text": By.PARTIAL_LINK_TEXT,
        "data-testid": By.CSS_SELECTOR,
        "type": By.CSS_SELECTOR,
        "placeholder": By.CSS_SELECTOR,
    }
    if by_raw not in by_map:
        raise AssertionError(f"Locator 'by' value '{by_raw}' for key '{key}' is not supported.")
    by = by_map[by_raw]
    return (by, selector)


@given('the user navigates to the login page')
def step_user_navigates_to_login_page(context):
    url = BASE_URL + "/login"
    context.driver.get(url)
    context.logger.info(f"Navigated to {url}")


@given('the user is on the login page')
def step_user_on_login_page(context):
    url = BASE_URL + "/login"
    context.driver.get(url)
    context.logger.info(f"Ensuring user is on login page at {url}")


@then('the login form is visible')
def step_login_form_visible(context):
    locator = get_locator(context, "login-form")
    login_form = WebDriverWait(context.driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(locator)
    )
    assert login_form.is_displayed(), "Login form is not displayed"
    context.logger.info("Login form is visible on the page.")


@then('the email input field is visible and empty')
def step_email_input_visible_empty(context):
    # Prefer using "email-input" key, fallback on "email" keys present
    possible_keys = ["email-input", "email"]
    email_element = None
    for key in possible_keys:
        try:
            locator = get_locator(context, key)
            email_element = WebDriverWait(context.driver, DEFAULT_TIMEOUT).until(
                EC.visibility_of_element_located(locator)
            )
            if email_element:
                break
        except AssertionError:
            continue
    if not email_element:
        raise AssertionError("Email input field locator not found or visible.")

    value = email_element.get_attribute("value")
    assert value == "" or value is None, f"Expected email input to be empty but got '{value}'"
    context.logger.info("Email input field is visible and empty.")


@then('the password input field is visible and empty')
def step_password_input_visible_empty(context):
    # Use password-input data-testid if present else fallback to 'password'
    possible_keys = ["password-input", "password"]
    password_element = None
    for key in possible_keys:
        try:
            locator = get_locator(context, key)
            password_element = WebDriverWait(context.driver, DEFAULT_TIMEOUT).until(
                EC.visibility_of_element_located(locator)
            )
            if password_element:
                break
        except AssertionError:
            continue
    if not password_element:
        raise AssertionError("Password input field locator not found or visible.")

    value = password_element.get_attribute("value")
    assert value == "" or value is None, f"Expected password input to be empty but got '{value}'"
    context.logger.info("Password input field is visible and empty.")


@then('the login button is visible and enabled')
def step_login_button_visible_enabled(context):
    # Use "login-button" key primarily, then "login-btn" or "submit" or "login-button" alternative keys
    possible_keys = ["login-button", "login-btn", "submit"]
    button_element = None
    for key in possible_keys:
        try:
            locator = get_locator(context, key)
            button_element = WebDriverWait(context.driver, DEFAULT_TIMEOUT).until(
                EC.visibility_of_element_located(locator)
            )
            if button_element:
                break
        except AssertionError:
            continue
    if not button_element:
        raise AssertionError("Login button locator not found or visible.")
    assert button_element.is_enabled(), "Login button is not enabled"
    context.logger.info("Login button is visible and enabled.")


@when('the user submits the login form with email "{email}" and password "{password}"')
def step_submit_login_form(context, email, password):
    # Find email field
    possible_email_keys = ["email-input", "email"]
    email_element = None
    for key in possible_email_keys:
        try:
            locator = get_locator(context, key)
            email_element = WebDriverWait(context.driver, DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(locator)
            )
            if email_element:
                break
        except AssertionError:
            continue
    if not email_element:
        raise AssertionError("Email input field not found to fill.")

    # Clear and send keys - treat "<empty>" as empty string
    value_email = "" if email.strip().lower() == "<empty>" else email
    email_element.clear()
    email_element.send_keys(value_email)
    context.logger.info(f"Entered email: '{value_email}'")

    # Find password field
    possible_password_keys = ["password-input", "password"]
    password_element = None
    for key in possible_password_keys:
        try:
            locator = get_locator(context, key)
            password_element = WebDriverWait(context.driver, DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(locator)
            )
            if password_element:
                break
        except AssertionError:
            continue
    if not password_element:
        raise AssertionError("Password input field not found to fill.")

    value_password = "" if password.strip().lower() == "<empty>" else password
    password_element.clear()
    password_element.send_keys(value_password)
    context.logger.info(f"Entered password: '{value_password}'")

    # Find and click login button
    possible_button_keys = ["login-button", "login-btn", "submit"]
    button_element = None
    for key in possible_button_keys:
        try:
            locator = get_locator(context, key)
            button_element = WebDriverWait(context.driver, DEFAULT_TIMEOUT).until(
                EC.element_to_be_clickable(locator)
            )
            if button_element:
                break
        except AssertionError:
            continue
    if not button_element:
        raise AssertionError("Login button not found or not clickable.")
    button_element.click()
    context.logger.info("Login button clicked to submit form.")


@then('the following validation messages are shown:')
def step_validation_messages_shown(context):
    # context.table contains expected messages, column 'message'
    # We will map known validation messages to error-message elements displayed
    # Expect these validation messages appear in elements with keys "email-error" and "password-error"
    expected_messages = [row["message"] for row in context.table]

    # Collect all visible validation messages on page by known error message locators
    error_keys = ["email-error", "password-error", "error-message"]
    actual_messages = []

    for key in error_keys:
        try:
            locator = get_locator(context, key)
            elements = context.driver.find_elements(*locator)
            for elem in elements:
                if elem.is_displayed():
                    text = elem.text.strip()
                    if text:
                        actual_messages.append(text)
        except Exception:
            # If locator missing or no elements, skip silently
            pass

    # Check each expected message is among the actual displayed messages
    missing_messages = []
    for expected in expected_messages:
        if not any(expected.lower() in actual.lower() for actual in actual_messages):
            missing_messages.append(expected)
    assert not missing_messages, f"Validation messages missing on page: {missing_messages}"
    context.logger.info(f"Validation messages verified: {expected_messages}")


@then('the validation message "{expected_message}" is shown')
def step_single_validation_message_shown(context, expected_message):
    # Look for any error-message or email-error or password-error elements containing the expected_message text
    error_keys = ["email-error", "password-error", "error-message"]
    found = False
    for key in error_keys:
        try:
            locator = get_locator(context, key)
            elements = context.driver.find_elements(*locator)
            for elem in elements:
                if elem.is_displayed():
                    if expected_message.lower() in elem.text.strip().lower():
                        found = True
                        break
        except Exception:
            continue
        if found:
            break
    assert found, f"Expected validation message '{expected_message}' not found on page."
    context.logger.info(f"Validation message shown on page: '{expected_message}'")


@then('the login form is submitted successfully')
def step_login_form_submitted_successfully(context):
    # Upon successful login, the app likely navigates to /dashboard and shows the dashboard page
    # Wait for dashboard page element to be visible

    # We'll wait maximum 8 seconds for the dashboard page element (key: "dashboard-page")
    # Alternative: check URL contains /dashboard
    try:
        locator = get_locator(context, "dashboard-page")
        dashboard_page = WebDriverWait(context.driver, 8).until(
            EC.visibility_of_element_located(locator)
        )
        assert dashboard_page.is_displayed(), "Dashboard page is not displayed after login."
    except Exception:
        # Fallback check on URL
        current_url = context.driver.current_url
        assert "/dashboard" in current_url, f"Login not successful, expected dashboard URL but got {current_url}"
    context.logger.info("Login form submitted successfully and dashboard page is displayed.")