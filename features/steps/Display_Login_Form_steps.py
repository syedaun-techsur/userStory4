from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@given("the user navigates to the login page")
@given("the user is on the login page")
def step_user_navigates_to_login_page(context):
    url = context.base_url + "/login"
    context.driver.get(url)
    # Wait for login form or page to be loaded
    by, selector = context.get_locator("login-form")
    WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )


@then("the login form is visible")
def step_login_form_visible(context):
    by, selector = context.get_locator("login-form")
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )
    assert element.is_displayed(), "Expected login form to be visible"


@then("the email input field is present")
def step_email_field_present(context):
    by, selector = context.get_locator("email-input")
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((by, selector))
    )
    assert element.is_displayed(), "Expected email input field to be present"


@then("the password input field is present")
def step_password_field_present(context):
    by, selector = context.get_locator("password-input")
    element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((by, selector))
    )
    assert element.is_displayed(), "Expected password input field to be present"


@then("the login button is present")
def step_login_button_present(context):
    by, selector = context.get_locator("login-button")
    element = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    assert element.is_displayed(), "Expected login button to be present"


@when('the user enters "{text}" into the email field')
def step_enter_email_field(context, text):
    text = text.strip()
    if text == "<empty>":
        text = ""
    by, selector = context.get_locator("email-input")
    element = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    element.clear()
    element.send_keys(text)


@when('the user enters "{text}" into the password field')
def step_enter_password_field(context, text):
    text = text.strip()
    if text == "<empty>":
        text = ""
    by, selector = context.get_locator("password-input")
    element = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    element.clear()
    element.send_keys(text)


@when("the user clicks the login button")
def step_click_login_button(context):
    by, selector = context.get_locator("login-button")
    element = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((by, selector))
    )
    element.click()


@then('the error message for the email field is "{error_message}"')
def step_email_field_error_message(context, error_message):
    error_message = error_message.strip()
    if error_message == "<empty>":
        # Check no email error shown
        step_no_email_field_error(context)
        return
    by, selector = context.get_locator("email-error")
    try:
        element = WebDriverWait(context.driver, 5).until(
            EC.visibility_of_element_located((by, selector))
        )
        actual_message = element.text.strip()
        assert actual_message == error_message, f"Expected email error '{error_message}' but got '{actual_message}'"
    except TimeoutException:
        assert False, "Expected email error message but none displayed"


@then('the error message for the password field is "{error_message}"')
def step_password_field_error_message(context, error_message):
    error_message = error_message.strip()
    if error_message == "<empty>":
        # Check no password error shown
        step_no_password_field_error(context)
        return
    by, selector = context.get_locator("password-error")
    try:
        element = WebDriverWait(context.driver, 5).until(
            EC.visibility_of_element_located((by, selector))
        )
        actual_message = element.text.strip()
        assert actual_message == error_message, f"Expected password error '{error_message}' but got '{actual_message}'"
    except TimeoutException:
        assert False, "Expected password error message but none displayed"


@then('no password field error is displayed')
def step_no_password_field_error(context):
    by, selector = context.get_locator("password-error")
    try:
        WebDriverWait(context.driver, 3).until(
            EC.visibility_of_element_located((by, selector))
        )
        # If visible, fail the test
        assert False, "Password error message is displayed but should not be"
    except TimeoutException:
        # Expected, no error message displayed
        pass


@then('no email field error is displayed')
def step_no_email_field_error(context):
    by, selector = context.get_locator("email-error")
    try:
        WebDriverWait(context.driver, 3).until(
            EC.visibility_of_element_located((by, selector))
        )
        assert False, "Email error message is displayed but should not be"
    except TimeoutException:
        pass


@then("no error messages are shown")
def step_no_error_messages_shown(context):
    # Check no email error
    step_no_email_field_error(context)
    # Check no password error
    step_no_password_field_error(context)
    # Also check no generic error messages are shown anywhere
    by, selector = context.get_locator("error-message")
    try:
        WebDriverWait(context.driver, 3).until(
            EC.visibility_of_element_located((by, selector))
        )
        assert False, "Generic error message displayed but should not be"
    except TimeoutException:
        pass


@then("the user is authenticated successfully")
def step_user_authenticated_successfully(context):
    # According to UI routes, the app should redirect to "/dashboard"
    # Wait for URL to change to dashboard route
    WebDriverWait(context.driver, 10).until(
        lambda d: d.current_url.startswith(context.base_url + "/dashboard")
    )
    # Verify visible dashboard element
    by, selector = context.get_locator("dashboard")
    element = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((by, selector))
    )
    assert element.is_displayed(), "Expected dashboard to be visible after successful login"