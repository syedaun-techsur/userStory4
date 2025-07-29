from dotenv import load_dotenv
import os
import json

# Load .env from project root and agentic_testing/
load_dotenv(dotenv_path=".env")
load_dotenv(dotenv_path="agentic_testing/.env")

from agentic_testing.crew import AgenticTesting
from agentic_testing.tools.environment_base_generator import generate_base_environment_file
from crewai import Crew, Process

# Paths to the base environment file and a test step definition file
env_path = "features/environment.py"
test_file_path = "features/steps/Display_Login_Form_steps.py"
feature_file_path = "features/Display_Login_Form.feature"
locators_path = "features/meta_data/locators_babel.json"
endpoints_path = "features/meta_data/endpoints_babel.json"
ui_endpoints_path = "features/meta_data/ui_endpoints_babel.json"

# Step 0: Generate the step definition file using the step_definition_generator agent
print("[Debug] Generating step definition file from feature file using agent...")
with open(feature_file_path, "r", encoding="utf-8") as f:
    feature_content = f.read()
step_def_agent = AgenticTesting().step_definition_generator()
step_def_task = AgenticTesting().step_definition_generation()
step_def_crew = Crew(
    agents=[step_def_agent],
    tasks=[step_def_task],
    process=Process.sequential,
    verbose=True,
)
step_def_result = step_def_crew.kickoff(inputs={"feature_content": feature_content})
with open(test_file_path, "w", encoding="utf-8") as f:
    f.write(str(step_def_result))
print(f"✅ Generated step definition file at {test_file_path}")

# Step 1: Load all required metadata and generate the working Selenium test file using the agent
print("[Debug] Generating working Selenium test file from feature file and metadata using agent...")
with open(test_file_path, "r", encoding="utf-8") as f:
    step_def_content = f.read()
with open(locators_path, "r", encoding="utf-8") as f:
    locators_json = f.read()
with open(endpoints_path, "r", encoding="utf-8") as f:
    endpoints_json = f.read()
with open(ui_endpoints_path, "r", encoding="utf-8") as f:
    ui_endpoints_json = f.read()

selenium_agent = AgenticTesting().selenium_test_generator()
selenium_task = AgenticTesting().selenium_test_generation()
selenium_crew = Crew(
    agents=[selenium_agent],
    tasks=[selenium_task],
    process=Process.sequential,
    verbose=True,
)
selenium_result = selenium_crew.kickoff(inputs={
    "feature_content": feature_content,
    "step_def_content": step_def_content,
    "locators_json": locators_json,
    "endpoints_json": endpoints_json,
    "ui_endpoints_json": ui_endpoints_json
})
with open(test_file_path, "w", encoding="utf-8") as f:
    f.write(str(selenium_result))
print(f"✅ Generated working Selenium test file at {test_file_path}")

# Step 2: Generate the base environment.py
print("[Debug] Generating base environment.py...")
generate_base_environment_file(env_path)

# Step 3: Load the base environment and test file
with open(env_path, "r", encoding="utf-8") as f:
    environment_base_code = f.read()
with open(test_file_path, "r", encoding="utf-8") as f:
    test_file_code = f.read()

inputs = {
    "environment_base_code": environment_base_code,
    "test_file_code": test_file_code
}

env_agent = AgenticTesting().environment_generator()
env_task = AgenticTesting().enhance_environment_for_test()

env_crew = Crew(
    agents=[env_agent],
    tasks=[env_task],
    process=Process.sequential,
    verbose=True,
)

env_result = env_crew.kickoff(inputs=inputs)

# Save the enhanced environment.py to the correct location
with open(env_path, "w", encoding="utf-8") as f:
    f.write(str(env_result))
print(f"✅ Enhanced environment.py saved to {env_path}") 