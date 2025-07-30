import os
import logging
import json
import threading
import socketserver
import http.server
import time
from pathlib import Path

from behave import fixture, use_fixture
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
import responses

# --- Locator strategy mapping ---
def map_locator_strategy(by, value):
    """
    Maps custom locator strategies to valid Selenium By attributes and values.
    Extend this function as needed for new strategies.
    """
    if by == "data-testid":
        return (By.CSS_SELECTOR, f'[data-testid="{value}"]')
    elif by == "css selector":
        return (By.CSS_SELECTOR, value)
    elif by == "id":
        return (By.ID, value)
    elif by == "name":
        return (By.NAME, value)
    elif by == "xpath":
        return (By.XPATH, value)
    elif by == "class name":
        return (By.CLASS_NAME, value)
    elif by == "tag name":
        return (By.TAG_NAME, value)
    elif by == "link text":
        return (By.LINK_TEXT, value)
    elif by == "partial link text":
        return (By.PARTIAL_LINK_TEXT, value)
    else:
        raise ValueError(f"Unknown locator strategy: {by}")

# --- Robust locator helpers ---
def get_by_strategy(by_value):
    """
    Normalize locator strategy key to Selenium By attribute.
    This supports locator definitions that use lower or mixed case keys.
    """
    key = by_value.strip().lower()
    mapping = {
        "id": By.ID,
        "css_selector": By.CSS_SELECTOR,
        "css selector": By.CSS_SELECTOR,
        "xpath": By.XPATH,
        "class_name": By.CLASS_NAME,
        "class name": By.CLASS_NAME,
        "tag_name": By.TAG_NAME,
        "tag name": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "link text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
        "partial link text": By.PARTIAL_LINK_TEXT,
        "data-testid": By.CSS_SELECTOR,  # Already handled by map_locator_strategy may be used separately
    }
    if key in mapping:
        return mapping[key]
    else:
        raise ValueError(f"Unknown locator strategy in locators file: {by_value}")

def load_locators(logger) -> dict:
    locators_path = Path("features/meta_data/locators_babel.json")
    if not locators_path.is_file():
        logger.warning(f"Locators file {locators_path} not found.")
        return {}
    try:
        with locators_path.open() as f:
            locs = json.load(f)
        logger.info(f"Loaded {len(locs)} locators.")
        result = {}
        for item in locs:
            key = item.get('key')
            if not key:
                continue
            if key in result:
                if isinstance(result[key], list):
                    result[key].append(item)
                else:
                    result[key] = [result[key], item]
            else:
                result[key] = item
        return result
    except Exception as e:
        logger.error(f"Failed to load locators: {e}")
        return {}

def get_locator(context, key):
    locators = context.locators.get(key)
    if not locators:
        context.logger.warning(f"Locator key '{key}' not found in locators.")
        return None
    if not isinstance(locators, list):
        locators = [locators]
    for locator in locators:
        by_raw = locator.get("by")
        selector = locator.get("selector")
        if not by_raw or not selector:
            continue
        try:
            by = get_by_strategy(by_raw)
            return (by, selector)
        except ValueError:
            continue  # skip unsupported strategies
    context.logger.error(f"No valid locator found for key '{key}'.")
    return None

# Patch context after loading locators in before_all

def patch_context_with_get_locator(context):
    context.get_locator = lambda key: get_locator(context, key)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class MockRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request('GET')

    def do_POST(self):
        self._handle_request('POST')

    def _handle_request(self, method):
        endpoints = self.server.endpoints
        path = self.path.split('?', 1)[0]
        matched = next((ep for ep in endpoints if ep.get('path') == path and ep.get('method', 'GET').upper() == method), None)

        self.send_response(matched.get('status', 200) if matched else 404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        body = matched.get('response', {}) if matched else {"error": "Endpoint not found"}
        self.wfile.write(json.dumps(body).encode('utf-8'))

    def log_message(self, format, *args):
        pass

@fixture
def selenium_browser_chrome(context):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        context.logger.info("Chrome WebDriver initialized.")
        context.driver = driver
        yield driver
    except WebDriverException as e:
        context.logger.error(f"Error initializing Chrome WebDriver: {e}")
        raise
    finally:
        if getattr(context, 'driver', None):
            context.driver.quit()
            context.logger.info("Selenium Chrome WebDriver quit.")

@fixture
def responses_mock_api(context):
    rsps_mock = responses.RequestsMock(assert_all_requests_are_fired=False)
    rsps_mock.start()
    context.logger.info("Responses mock API started.")

    config_path = Path("config/endpoints.json")
    if config_path.is_file():
        with config_path.open() as f:
            endpoints = json.load(f)
    else:
        endpoints = [
            {"path": "/api/login", "method": "POST", "status": 200, "response": {"success": true, "token": "validtoken123"}},
            {"path": "/api/dashboard", "method": "GET", "status": 200, "response": {"user": "admin@example.com", "dashboardData": {}}},
            {"path": "/api/unauthorized", "method": "GET", "status": 401, "response": {"error": "Unauthorized"}}
        ]
    for ep in endpoints:
        url = f"http://localhost:3000{ep.get('path')}"
        method = ep.get('method', 'GET').upper()
        body = json.dumps(ep.get('response', {}))
        status = ep.get('status', 200)
        rsps_mock.add(method, url, body=body, status=status, content_type='application/json')
    context.logger.info(f"Loaded {len(endpoints)} mocked endpoints.")

    context.mock_api = rsps_mock

# Additional environment hooks, such as before_all, after_all, could also be here
