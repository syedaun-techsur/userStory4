from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

@given('I open the login page')
def step_open_login_page(context):
    login_url = context.base_url + "/login"
    context.driver.get(login_url)
    # Wait until login-form is visible to ensure page is loaded
    by, selector = context.get_locator("login-form")
    WebDriverWait(context.driver, 10).until(EC.visibility_of_element_located((by, selector)))

@then('I should see the email input field')
def step_see_email_input_field(context):
    # Check presence and visibility of email input field
    by, selector = context.get_locator("email-input")
    element = WebDriverWait(context.driver, 10).until(EC.visibility_of_element_located((by, selector)))
    assert element.is_displayed()

@then('I should see the password input field')
def step_see_password_input_field(context):
    # Check presence and visibility of password input field
    by, selector = context.get_locator("password-input")
    element = WebDriverWait(context.driver, 10).until(EC.visibility_of_element_located((by, selector)))
    assert element.is_displayed()

@then('I should see the login button')
def step_see_login_button(context):
    # Check presence and visibility of login button
    by, selector = context.get_locator("login-button")
    element = WebDriverWait(context.driver, 10).until(EC.visibility_of_element_located((by, selector)))
    assert element.is_displayed()

@when('I fill the email field with {email}')
def step_fill_email_field(context, email):
    # Replace <empty> with empty string and strip quotes if any
    val = email.strip()
    if val == "<empty>":
        val = ""
    elif val.startswith('"') and val.endswith('"'):
        val = val[1:-1]
    by, selector = context.get_locator("email-input")
    input_field = WebDriverWait(context.driver, 10).until(EC.element_to_be_clickable((by, selector)))
    input_field.clear()
    input_field.send_keys(val)

@when('I fill the email field with "{email}"')
def step_fill_email_field_quoted(context, email):
    val = email.strip()
    if val == "<empty>":
        val = ""
    by, selector = context.get_locator("email-input")
    input_field = WebDriverWait(context.driver, 10).until(EC.element_to_be_clickable((by, selector)))
    input_field.clear()
    input_field.send_keys(val)

@when('I fill the password field with {password}')
def step_fill_password_field(context, password):
    val = password.strip()
    if val == "<empty>":
        val = ""
    elif val.startswith('"') and val.endswith('"'):
        val = val[1:-1]
    by, selector = context.get_locator("password-input")
    input_field = WebDriverWait(context.driver, 10).until(EC.element_to_be_clickable((by, selector)))
    input_field.clear()
    input_field.send_keys(val)

@when('I click the login button')
def step_click_login_button(context):
    by, selector = context.get_locator("login-button")
    button = WebDriverWait(context.driver, 10).until(EC.element_to_be_clickable((by, selector)))
    button.click()

@then('I should see error message "{error_message}"')
def step_see_error_message(context, error_message):
    error_lower = error_message.lower()
    # Determine the error message locator key based on error_message content keywords
    locator_key = None
    if "email" in error_lower:
        # Try specific email error locator first
        try:
            context.get_locator("email-error")
            locator_key = "email-error"
        except KeyError:
            locator_key = "error-message"
    elif "password" in error_lower:
        try:
            context.get_locator("password-error")
            locator_key = "password-error"
        except KeyError:
            locator_key = "error-message"
    else:
        locator_key = "error-message"
    by, selector = context.get_locator(locator_key)
    # Wait for error message element to be visible, and verify text contains the expected error_message
    try:
        error_elem = WebDriverWait(context.driver, 10).until(EC.visibility_of_element_located((by, selector)))
    except TimeoutException:
        assert False, f"Expected error message '{error_message}' not visible on page"
    elem_text = error_elem.text.strip()
    assert error_message in elem_text, f"Expected error message '{error_message}', found '{elem_text}'"

@then('I should not see any error messages related to email or password')
def step_no_email_password_errors(context):
    # Check that email-error and password-error elements are not visible or not present
    def is_visible(locator_key):
        try:
            by, selector = context.get_locator(locator_key)
        except KeyError:
            return False
        elems = context.driver.find_elements(by, selector)
        return any(e.is_displayed() for e in elems)
    email_error_visible = is_visible("email-error")
    password_error_visible = is_visible("password-error")
    # Also check generic error messages that mention email or password if email-error or password-error is not present
    if not email_error_visible and not password_error_visible:
        try:
            by, selector = context.get_locator("error-message")
            elems = context.driver.find_elements(by, selector)
            for e in elems:
                if e.is_displayed():
                    # Check if text contains mention of email or password errors
                    txt = e.text.lower()
                    if "email" in txt or "password" in txt:
                        assert False, "Error message related to email or password is visible"
        except KeyError:
            pass  # no generic error-message locator
    assert not email_error_visible and not password_error_visible, "Email or password error message is visible when none expected"