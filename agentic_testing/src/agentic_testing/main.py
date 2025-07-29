#!/usr/bin/env python
import sys
import warnings
import os
import re
from datetime import datetime
import json
import subprocess

from agentic_testing.crew import AgenticTesting
from agentic_testing.tools.git_clone_tool import clone_repo
from agentic_testing.tools.jira_fetch_tool import fetch_and_save_jira_stories
from agentic_testing.tools.message_extraction_tool import extract_messages
from agentic_testing.tools.environment_base_generator import generate_base_environment_file

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Set this variable to 'all' or a specific file name like 'LD-2_story.txt'
STORY_SELECTION = os.environ.get('STORY_SELECTION', 'all')  # Can be set via env var or hardcoded
FEATURE_SELECTION = os.environ.get('FEATURE_SELECTION', 'all')  # New env var for step definition selection

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def extract_title_from_story(story_content):
    # Look for a line like 'Title: ...' and extract the title
    match = re.search(r'^Title:\s*(.+)$', story_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Fallback: use first 10 words of the story
    return "_".join(story_content.split()[:10])

def save_feature_file(title, gherkin_content):
    features_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../features'))
    os.makedirs(features_dir, exist_ok=True)
    safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', title)[:50]
    file_path = os.path.join(features_dir, f"{safe_title}.feature")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(gherkin_content)
    print(f"✅ Saved feature: {file_path}")

def save_step_definition_file(title, step_def_content):
    steps_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../features/steps'))
    os.makedirs(steps_dir, exist_ok=True)
    safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', title)[:50]
    file_path = os.path.join(steps_dir, f"{safe_title}_steps.py")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(step_def_content)
    print(f"✅ Saved step definitions: {file_path}")


def process_feature_file(feature_file):
    print(f"📝 Generating step definitions for feature file {feature_file}")
    with open(feature_file, 'r', encoding='utf-8') as f:
        feature_content = f.read()
    title = os.path.splitext(os.path.basename(feature_file))[0]
    try:
        # Only run the step_definition_generation task here
        from agentic_testing.crew import AgenticTesting
        step_def_agent = AgenticTesting().step_definition_generator()
        step_def_task = AgenticTesting().step_definition_generation()
        from crewai import Crew, Process
        crew = Crew(
            agents=[step_def_agent],
            tasks=[step_def_task],
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff(inputs={
            "feature_content": feature_content
        })
        # Post-process to remove ```python and ``` code fences
        result_str = str(result)
        match = re.search(r'```python\s*([\s\S]+?)```', result_str)
        if match:
            code_content = match.group(1).strip()
        else:
            code_content = result_str.strip()
        save_step_definition_file(title, code_content)
    except Exception as e:
        print(f"❌ Error generating step definitions for {feature_file}: {e}")

def process_selenium_test_file(feature_file):
    print(f"📝 Generating Selenium Behave test for feature file {feature_file}")
    import json
    # Prepare paths
    title = os.path.splitext(os.path.basename(feature_file))[0]
    steps_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../features/steps'))
    meta_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../features/meta_data'))
    # env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../features/environment.py'))
    # Read all required inputs
    step_def_path = os.path.join(steps_dir, f"{title}_steps.py")
    locators_path = os.path.join(meta_dir, "locators_babel.json")
    endpoints_path = os.path.join(meta_dir, "endpoints_babel.json")
    ui_endpoints_path = os.path.join(meta_dir, "ui_endpoints_babel.json")
    with open(feature_file, 'r', encoding='utf-8') as f:
        feature_content = f.read()
    with open(step_def_path, 'r', encoding='utf-8') as f:
        step_def_content = f.read()
    with open(locators_path, 'r', encoding='utf-8') as f:
        locators_json = f.read()
    with open(endpoints_path, 'r', encoding='utf-8') as f:
        endpoints_json = f.read()
    with open(ui_endpoints_path, 'r', encoding='utf-8') as f:
        ui_endpoints_json = f.read()
    try:
        from agentic_testing.crew import AgenticTesting
        selenium_agent = AgenticTesting().selenium_test_generator()
        selenium_task = AgenticTesting().selenium_test_generation()
        from crewai import Crew, Process
        crew = Crew(
            agents=[selenium_agent],
            tasks=[selenium_task],
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff(inputs={
            "step_def_content": step_def_content,
            "locators_json": locators_json,
            "endpoints_json": endpoints_json,
            "ui_endpoints_json": ui_endpoints_json,
            "feature_content": feature_content
        })
        # Only save the code part (no markdown/code fences)
        result_str = str(result)
        match = re.search(r'```python\s*([\s\S]+?)```', result_str)
        if match:
            code_content = match.group(1).strip()
        else:
            code_content = result_str.strip()
        # Overwrite the step definition file with the generated Selenium test code
        with open(step_def_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        print(f"✅ Overwrote step definition file with Selenium test: {step_def_path}")
    except Exception as e:
        print(f"❌ Error generating Selenium Behave test for {feature_file}: {e}")

def load_extracted_messages():
    messages_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../../features/meta_data/extracted_messages.json')
    )
    if os.path.exists(messages_path):
        with open(messages_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [m['message'] for m in data if 'message' in m]
    return []

def process_story_file(story_file):
    print(f"📝 CUSTOM PIPELINE: Processing story file {story_file}")
    with open(story_file, 'r', encoding='utf-8') as f:
        story_content = f.read()
    title = extract_title_from_story(story_content)
    messages = load_extracted_messages()
    try:
        # Only run the gherkin_generation task here with a Crew containing only the gherkin agent and task
        from agentic_testing.crew import AgenticTesting
        gherkin_agent = AgenticTesting().gherkin_generator()
        gherkin_task = AgenticTesting().gherkin_generation()
        from crewai import Crew, Process
        crew = Crew(
            agents=[gherkin_agent],
            tasks=[gherkin_task],
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff(inputs={
            "user_story": story_content,
            "messages": messages
        })
        gherkin_content = result
        match = re.search(r'```gherkin\s*([\s\S]+?)```', str(result))
        if match:
            gherkin_content = match.group(1).strip()
        save_feature_file(title, gherkin_content)
    except Exception as e:
        print(f"❌ Error generating feature for {story_file}: {e}")

def generate_environment_file():
    print("📝 Generating features/environment.py for Behave infrastructure setup")
    try:
        from agentic_testing.crew import AgenticTesting
        env_agent = AgenticTesting().environment_generator()
        env_task = AgenticTesting().generate_environment()
        from crewai import Crew, Process
        crew = Crew(
            agents=[env_agent],
            tasks=[env_task],
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff(inputs={})
        # Save to the correct location in the project root features/ directory
        features_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../features'))
        os.makedirs(features_dir, exist_ok=True)
        env_path = os.path.join(features_dir, 'environment.py')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(str(result))
        print(f"✅ Generated {env_path}")
    except Exception as e:
        print(f"❌ Error generating features/environment.py: {e}")

def run():
    """
    Run the pipeline for all or a specific user story file.
    """
    print("🚀 CUSTOM PIPELINE: Starting run() function")

    # Step 1: Fetch codebase
    print("[Step 1] Cloning repository...")
    clone_repo()
    
    # Step 2: Extract messages (Python) and metadata (Babel)
    print("[Step 2] Running Python message extraction...")
    extract_messages()##Alternative to this
    
    print("[Step 2] Running Babel AST parser for locators, endpoints, and UI routes...")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
    subprocess.run([
        "node", 
        os.path.join(os.path.dirname(__file__), 'tools', 'extract_all_metadata_babel.js')
    ], cwd=project_root)
    
    print("[Step 2] Running Java endpoint extraction...")
    subprocess.run([
        "node", 
        os.path.join(os.path.dirname(__file__), 'tools', 'extract_java_endpoints.js')
    ], cwd=project_root)
    print("Extraction complete. Check features/meta_data/ for outputs.")
    
    # Step 3: Fetch JIRA user stories
    print("[Step 3] Fetching JIRA user stories...")
    fetch_and_save_jira_stories()
    
    # Step 4: Process user stories based on STORY_SELECTION
    print("[Step 4] Generating Gherkin feature files from user stories...")
    user_stories_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../user_stories'))
    if not os.path.exists(user_stories_dir):
        print(f"No user_stories directory found at {user_stories_dir}")
        return
    if STORY_SELECTION == 'all':
        for filename in os.listdir(user_stories_dir):
            if filename.endswith('.txt'):
                story_file = os.path.join(user_stories_dir, filename)
                process_story_file(story_file)
    else:
        story_file = os.path.join(user_stories_dir, STORY_SELECTION)
        if not os.path.exists(story_file):
            print(f"User story file not found: {story_file}")
            return
        process_story_file(story_file)

    # Step 5: Generate Behave step definitions for each feature file based on FEATURE_SELECTION
    print("[Step 5] Generating Behave step definitions for feature files...")
    features_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../features'))
    if FEATURE_SELECTION == 'all':
        feature_files = [os.path.join(features_dir, f) for f in os.listdir(features_dir) if f.endswith('.feature')]
    else:
        feature_file = os.path.join(features_dir, FEATURE_SELECTION)
        feature_files = [feature_file] if os.path.exists(feature_file) else []
        if not feature_files:
            print(f"Feature file not found: {feature_file}")
    for feature_file in feature_files:
        process_feature_file(feature_file)

    # Step 6: Generate Selenium Behave test files for each feature file
    print("[Step 6] Generating Selenium Behave test files for feature files...")
    for feature_file in feature_files:
        process_selenium_test_file(feature_file)

    # Step 7: Generate environment.py only if it does not already exist
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../features/environment.py'))
    if not os.path.exists(env_path):
        print("[Step 7] Generating base environment.py (does not exist)...")
        generate_base_environment_file(env_path)
    else:
        print(f"[Step 7] Skipping environment.py generation (already exists at {env_path})")

    # Step 8: Enhance environment.py for each test file
    print("[Step 8] Enhancing environment.py for each test file...")
    steps_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../features/steps'))
    for feature_file in feature_files:
        title = os.path.splitext(os.path.basename(feature_file))[0]
        test_file_path = os.path.join(steps_dir, f"{title}_steps.py")
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                environment_base_code = f.read()
            with open(test_file_path, 'r', encoding='utf-8') as f:
                test_file_code = f.read()
            from agentic_testing.crew import AgenticTesting
            env_agent = AgenticTesting().environment_generator()
            enhance_task = AgenticTesting().enhance_environment_for_test()
            from crewai import Crew, Process
            crew = Crew(
                agents=[env_agent],
                tasks=[enhance_task],
                process=Process.sequential,
                verbose=True,
            )
            result = crew.kickoff(inputs={
                "environment_base_code": environment_base_code,
                "test_file_code": test_file_code
            })
            # Save the enhanced environment.py
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(str(result))
            print(f"✅ Enhanced environment.py for {title} at {env_path}")
        except Exception as e:
            print(f"❌ Error enhancing environment.py for {title}: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        AgenticTesting().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        AgenticTesting().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        AgenticTesting().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    run()
    #  PYTHONPATH=src STORY_SELECTION=LD-2_story.txt FEATURE_SELECTION=Display_Login_Form.feature crewai run
    #  PYTHONPATH=src STORY_SELECTION=all FEATURE_SELECTION=Display_Login_Form.feature crewai run
    #PYTHONPATH=src STORY_SELECTION=all FEATURE_SELECTION=all crewai run
