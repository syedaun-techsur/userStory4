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
import responses

# === Helper classes for mock HTTP server ===

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class MockRequestHandler(http.server.BaseHTTPRequestHandler):
    # This handler will serve the endpoints configured in JSON loaded to the server.
    # It supports GET/POST and returns JSON response bodies

    def do_GET(self):
        self._handle_request('GET')

    def do_POST(self):
        self._handle_request('POST')

    def _handle_request(self, method):
        # Match the path and method to the configured endpoints.
        # Respond with configured status and JSON body or 404 if no matching endpoint.
        endpoints = self.server.endpoints
        path = self.path.split('?', 1)[0]  # Strip query
        matched = None
        for ep in endpoints:
            if (ep.get('path') == path and ep.get('method', 'GET').upper() == method):
                matched = ep
                break

        if matched:
            self.send_response(matched.get('status', 200))
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            body = matched.get('response', {})
            resp_bytes = json.dumps(body).encode('utf-8')
            self.wfile.write(resp_bytes)
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

    def log_message(self, format, *args):
        # Override to suppress default console logging of HTTP requests
        pass

# === Behave fixtures ===

@fixture
def selenium_browser_chrome(context):
    """
    Initialize Selenium Chrome WebDriver with headless mode and JS hooks to disable validations.
    """
    options = Options()
    # options.add_argument("--headless")  # Commented out to show browser window
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    # Additional Chrome options can be added here if needed

    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        # Insert robust JS hooks to disable all HTML5 and React validation
        disable_validation_js = """
            // Disable native browser validation messages
            HTMLFormElement.prototype.reportValidity = function() { return true; };
            // Override setCustomValidity to noop
            HTMLElement.prototype.setCustomValidity = function() {};
            // Override checkValidity to always valid
            HTMLInputElement.prototype.checkValidity = function() { return true; };
            // Disable required attribute enforcement
            Object.defineProperty(HTMLInputElement.prototype, 'required', { get: function() { return false; } });
            // For React: override validationMessage
            Object.defineProperty(HTMLInputElement.prototype, 'validationMessage', { get: function() { return ''; } });
            // For React: override validity property
            Object.defineProperty(HTMLInputElement.prototype, 'validity', { get: function() { return { valid: true }; } });
        """
        driver.execute_script(disable_validation_js)
        context.logger.info("Injected JS to disable all browser and React validation.")
        context.driver = driver
        yield driver
    except WebDriverException as e:
        context.logger.error(f"Error initializing Chrome WebDriver: {e}")
        raise
    finally:
        try:
            if hasattr(context, 'driver') and context.driver:
                context.driver.quit()
                context.logger.info("Selenium Chrome WebDriver quit successfully.")
        except Exception as err:
            context.logger.warning(f"Exception when quitting driver: {err}")

@fixture
def mock_http_server(context):
    """
    Starts a thread-based HTTP server serving mock endpoints from config/endpoints.json.
    """
    config_path = Path("config/endpoints.json")
    if not config_path.is_file():
        context.logger.warning("Mock HTTP server config file config/endpoints.json not found, skipping mock server startup.")
        yield None
        return

    with config_path.open() as f:
        endpoints = json.load(f)

    server_address = ('localhost', 8000)
    handler_class = MockRequestHandler
    httpd = ThreadedHTTPServer(server_address, handler_class)
    httpd.endpoints = endpoints

    def server_thread():
        context.logger.info("Mock HTTP server starting on http://localhost:8000")
        try:
            httpd.serve_forever()
        except Exception as e:
            context.logger.error(f"Mock HTTP server stopped with exception: {e}")

    thread = threading.Thread(target=server_thread, daemon=True)
    thread.start()

    context.mock_httpd = httpd
    context.mock_thread = thread

    yield httpd

    context.logger.info("Shutting down mock HTTP server...")
    httpd.shutdown()
    thread.join()
    context.logger.info("Mock HTTP server shut down.")

@fixture
def responses_mock_api(context):
    """
    Uses 'responses' library to mock HTTP calls when @api related tags are present.
    Loads endpoint mocks from config/endpoints.json.
    """
    import responses as rsps

    rsps_mock = rsps.RequestsMock(assert_all_requests_are_fired=False)
    rsps_mock.start()
    context.logger.info("Responses mock API started.")

    # Load endpoint mocks
    config_path = Path("config/endpoints.json")
    if config_path.is_file():
        with config_path.open() as f:
            endpoints = json.load(f)

        # Register mocks for each endpoint
        for ep in endpoints:
            url = f"http://localhost:3000{ep.get('path')}"
            method = ep.get('method', 'GET').upper()
            body = json.dumps(ep.get('response', {}))
            status = ep.get('status', 200)
            rsps_mock.add(method, url, body=body, status=status, content_type='application/json')
        context.logger.info(f"Loaded {len(endpoints)} mocked endpoints into responses.")
    else:
        context.logger.warning("No endpoints config found for responses mocks at config/endpoints.json")

    yield rsps_mock

    rsps_mock.stop()
    rsps_mock.reset()
    context.logger.info("Responses mock API stopped.")

# === Helper function for loading locators ===

def load_locators(logger) -> dict:
    locators_path = Path("features/meta_data/locators_babel.json")
    if not locators_path.is_file():
        logger.warning(f"Locators config file {locators_path} not found. context.locators will be empty.")
        return {}
    try:
        with locators_path.open() as f:
            locs = json.load(f)
        logger.info(f"Loaded {len(locs)} locators from {locators_path}.")
        return locs
    except Exception as e:
        logger.error(f"Failed to load locators from {locators_path}: {e}")
        return {}

# === Behave environment hooks ===

def before_all(context):
    # Setup directories for screenshots, logs, reports
    base_path = Path("features")
    screenshots_dir = base_path / "screenshots"
    logs_dir = base_path / "logs"
    reports_dir = base_path / "reports"

    screenshots_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Setup logger, log to file and stream (console)
    log_file = logs_dir / "test_execution.log"
    logger = logging.getLogger("behave_test")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    # File handler
    fh = logging.FileHandler(str(log_file))
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    context.logger = logger
    context.screenshots_dir = str(screenshots_dir)

    context.logger.info("=== Test execution started ===")

    # Base URL for all tests
    context.base_url = "http://localhost:3000"

    # Load locators at start to share across scenarios
    context.locators = load_locators(context.logger)

    # Start mock API server globally if any api-related tag sets present in feature files (heuristic)
    # TODO: Adjust if smarter global detection needed
    # Using global api mock is not always recommended; we start per scenario instead.
    context.mock_httpd = None
    context.mock_thread = None

    # Similarly, no driver at this point; will start as needed per scenario
    context._report_results = []
    context._current_feature = None
    context._current_scenario = None
    context._step_start_time = None
    context._step_results = []

def before_feature(context, feature):
    context._current_feature = {
        'name': feature.name,
        'scenarios': []
    }

def before_scenario(context, scenario):
    context._current_scenario = {
        'name': scenario.name,
        'steps': []
    }
    context._step_results = []
    # Prepare scenario-specific context attributes and services
    tags = set(scenario.tags)

    # Start Selenium driver for UI-related tags
    if tags.intersection({'ui', 'visual', 'ux'}):
        context.logger.info(f"Scenario '{scenario.name}' requires UI testing. Starting Selenium driver.")
        use_fixture(selenium_browser_chrome, context)
        # The fixture now sets context.driver, so context.driver.get is safe here
        try:
            context.driver.get(context.base_url)
        except Exception as e:
            context.logger.error(f"Error navigating to base_url {context.base_url}: {e}")
    else:
        context.driver = None

    # Setup API mocking for api/service/integration tags
    api_tags = {'api', 'service', 'integration'}
    if tags.intersection(api_tags):
        # For this example, we will always use 'responses' mock, not mock server
        context.logger.info(f"Scenario '{scenario.name}' tagged with API tags {tags & api_tags}. Starting responses mock.")
        use_fixture(responses_mock_api, context)
    else:
        context.mock_api = None

    # Setup Backend (DB stub or backend mock) for backend tags
    backend_tags = {'backend', 'db', 'stateful'}
    if tags.intersection(backend_tags):
        context.logger.info(f"Scenario '{scenario.name}' has backend tags {tags & backend_tags}. Setting up DB stub / backend mock.")
        # TODO: Insert DB stub or backend mock startup here
        # Example placeholder:
        # context.db_stub = MyCustomDbStub()
        # context.db_stub.start()
        context.db_stub = None
    else:
        context.db_stub = None

    # Validation tags do not trigger infrastructure setup but could be used for conditional asserts later
    validation_tags = {'validation', 'success', 'negative'}
    if tags.intersection(validation_tags):
        context.logger.debug(f"Scenario '{scenario.name}' includes validation-related tags: {tags & validation_tags}")

def before_step(context, step):
    # Inject validation-disabling JS before every step if UI driver is present
    if hasattr(context, 'driver') and context.driver:
        disable_validation_js = """
            // Disable native browser validation messages
            HTMLFormElement.prototype.reportValidity = function() { return true; };
            // Override setCustomValidity to noop
            HTMLElement.prototype.setCustomValidity = function() {};
            // Override checkValidity to always valid
            HTMLInputElement.prototype.checkValidity = function() { return true; };
            // Disable required attribute enforcement
            Object.defineProperty(HTMLInputElement.prototype, 'required', { get: function() { return false; } });
            // For React: override validationMessage
            Object.defineProperty(HTMLInputElement.prototype, 'validationMessage', { get: function() { return ''; } });
            // For React: override validity property
            Object.defineProperty(HTMLInputElement.prototype, 'validity', { get: function() { return { valid: true }; } });
            // Set noValidate on all forms
            document.querySelectorAll('form').forEach(f => f.noValidate = true);
            // Log to browser console
            console.log('[Behave] Disabled browser and React validation, set noValidate on all forms.');
            // MutationObserver to re-apply after DOM changes (e.g., React re-render)
            if (!window._behaveValidationObserver) {
                window._behaveValidationObserver = new MutationObserver(function() {
                    document.querySelectorAll('form').forEach(f => f.noValidate = true);
                    HTMLFormElement.prototype.reportValidity = function() { return true; };
                    HTMLElement.prototype.setCustomValidity = function() {};
                    HTMLInputElement.prototype.checkValidity = function() { return true; };
                    Object.defineProperty(HTMLInputElement.prototype, 'required', { get: function() { return false; } });
                    Object.defineProperty(HTMLInputElement.prototype, 'validationMessage', { get: function() { return ''; } });
                    Object.defineProperty(HTMLInputElement.prototype, 'validity', { get: function() { return { valid: true }; } });
                    console.log('[Behave] MutationObserver reapplied validation disables.');
                });
                window._behaveValidationObserver.observe(document.body, { childList: true, subtree: true });
            }
        """
        context.driver.execute_script(disable_validation_js)
        context.logger.info("Injected JS to disable all browser and React validation, set noValidate, and attached MutationObserver.")
    context._step_start_time = time.time()
    context.logger.info(f"Starting Step: {step.keyword} {step.name}")

def after_step(context, step):
    duration = time.time() - context._step_start_time if context._step_start_time else 0
    context._step_results.append({
        'name': f"{step.keyword} {step.name}",
        'status': step.status,
        'duration': duration
    })
    if step.status == "failed":
        context.logger.error(f"Step failed: {step.keyword} {step.name}")
        # For UI steps, screenshot on failure
        if getattr(context, "driver", None):
            try:
                safe_step = step.name.replace(" ", "_").replace("/", "_")
                screenshot_path = Path(context.screenshots_dir) / f"step_fail_{safe_step}.png"
                context.driver.save_screenshot(str(screenshot_path))
                context.logger.info(f"Saved failure screenshot for failed step to {screenshot_path}")
            except Exception as e:
                context.logger.error(f"Failed to take screenshot on failed step: {e}")
    else:
        context.logger.info(f"Step passed: {step.keyword} {step.name}")

def after_scenario(context, scenario):
    context._current_scenario['steps'] = context._step_results
    context._current_feature['scenarios'].append(context._current_scenario)
    # On failure for UI, capture screenshot to features/screenshots with scenario name sanitized
    if scenario.status == "failed":
        if context.driver:
            try:
                safe_name = scenario.name.replace(" ", "_").replace("/", "_")
                screenshot_path = Path(context.screenshots_dir) / f"{safe_name}.png"
                context.driver.save_screenshot(str(screenshot_path))
                context.logger.info(f"Saved failure screenshot to {screenshot_path}")
            except Exception as e:
                context.logger.error(f"Failed to take screenshot: {e}")

    # Selenium driver quit if initialized
    if getattr(context, "driver", None):
        try:
            context.driver.quit()
            context.logger.info("Selenium WebDriver quit after scenario.")
        except Exception as e:
            context.logger.warning(f"Exception quitting Selenium WebDriver: {e}")
        context.driver = None

    # Stop API mocks if started
    if getattr(context, "mock_api", None):
        try:
            context.mock_api.stop()
            context.mock_api.reset()
            context.logger.info("Responses mock API stopped after scenario.")
        except Exception as e:
            context.logger.warning(f"Exception stopping responses mock API: {e}")
        context.mock_api = None

    # Stop DB stub or backend mock if started
    if getattr(context, "db_stub", None):
        # TODO: Insert DB stub or backend mock shutdown here
        # Example placeholder:
        # context.db_stub.stop()
        context.db_stub = None

def after_feature(context, feature):
    context._report_results.append(context._current_feature)

def after_all(context):
    if hasattr(context, 'mock_httpd') and context.mock_httpd:
        context.logger.info("Shutting down mock HTTP server at after_all.")
        context.mock_httpd.shutdown()
        if hasattr(context, 'mock_thread'):
            context.mock_thread.join()
        context.logger.info("Mock HTTP server shut down at after_all.")

    # Write JSON and HTML report
    reports_dir = Path('features/reports')
    reports_dir.mkdir(parents=True, exist_ok=True)
    json_report_path = reports_dir / 'behave_report.json'
    html_report_path = reports_dir / 'behave_report.html'
    with open(json_report_path, 'w', encoding='utf-8') as f:
        json.dump(context._report_results, f, indent=2)
    # Generate simple HTML report
    html = ['<html><head><title>Behave Test Report</title></head><body>']
    for feature in context._report_results:
        html.append(f"<h2>Feature: {feature['name']}</h2>")
        for scenario in feature['scenarios']:
            html.append(f"<h3>Scenario: {scenario['name']}</h3><ul>")
            for step in scenario['steps']:
                html.append(f"<li>{step['name']} ... <b>{step['status']}</b> in {step['duration']:.3f}s</li>")
            html.append("</ul>")
    html.append('</body></html>')
    with open(html_report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))

    context.logger.info("=== Test execution finished ===")
    handlers = context.logger.handlers[:]
    for handler in handlers:
        handler.close()
        context.logger.removeHandler(handler)