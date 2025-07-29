import os
import requests
from requests.auth import HTTPBasicAuth
import re
from dotenv import load_dotenv

def get_jira_session(jira_url, username, api_token):
    session = requests.Session()
    session.auth = HTTPBasicAuth(username, api_token)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    return session

def fetch_ticket(session, jira_url, ticket_key):
    url = f"{jira_url.rstrip('/')}/rest/api/3/issue/{ticket_key}"
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching ticket {ticket_key}: {e}")
        return None

def fetch_epic_children(session, jira_url, epic_key):
    jql_patterns = [
        f'"Epic Link" = {epic_key}',
        f'parent = {epic_key}',
        f'issue in linkedIssues({epic_key})',
        f'issue in subtasksOf({epic_key})'
    ]
    url = f"{jira_url.rstrip('/')}/rest/api/3/search"
    for jql in jql_patterns:
        params = {
            'jql': jql,
            'maxResults': 100,
            'fields': 'summary,description,issuetype,status,priority,assignee,reporter'
        }
        try:
            response = session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            issues = data.get('issues', [])
            if issues:
                print(f"   Found {len(issues)} child tickets using JQL: {jql}")
                return issues
        except requests.exceptions.RequestException as e:
            print(f"   JQL '{jql}' failed: {e}")
            continue
    print(f"   No child tickets found with any JQL pattern")
    return []

def is_epic(ticket_data):
    issue_type = ticket_data.get('fields', {}).get('issuetype', {})
    return issue_type.get('name', '').lower() == 'epic'

def extract_text_from_adf(adf):
    def _rec(node, depth=0):
        text = ""
        if isinstance(node, list):
            for n in node:
                text += _rec(n, depth)
            return text
        t = node.get('type')
        if t == 'text':
            return node.get('text', '')
        if t == 'paragraph':
            return _rec(node.get('content', []), depth) + "\n"
        if t == 'heading':
            return _rec(node.get('content', []), depth) + "\n"
        if t in ('bulletList', 'orderedList'):
            s = ""
            for item in node.get('content', []):
                s += _rec(item, depth + 1)
            return s
        if t == 'listItem':
            inner = _rec(node.get('content', []), depth).strip()
            if depth == 1:
                return "• " + inner + "\n"
            else:
                return "  " * (depth-1) + "– " + inner + "\n"
        if 'content' in node:
            return _rec(node['content'], depth)
        return ""
    return _rec(adf)

def extract_story_content(ticket_data):
    fields = ticket_data.get('fields', {})
    summary = fields.get('summary', 'No Summary')
    description = fields.get('description', '')
    if isinstance(description, dict):
        description = extract_text_from_adf(description.get('content', []))
    description = description.replace('\u200b', '').strip()
    ac_label = "Acceptance Criteria:"
    if ac_label in description:
        idx = description.index(ac_label)
        desc_part = description[:idx].rstrip()
        ac_part   = description[idx + len(ac_label):].lstrip()
    else:
        desc_part = description
        ac_part   = ""
    output = (
        f"User Story: {summary}\n"
        f"Title: {summary}\n"
        f"Description: {desc_part}\n"
        "Acceptance Criteria:\n"
        f"{ac_part}\n"
    )
    return output

def sanitize_filename(filename):
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized[:100]

def save_story(story_content, filename, folder=None):
    # Always use 'user_stories' in the project root
    if folder is None:
        # Get the absolute path to the project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
        folder = os.path.join(project_root, 'user_stories')
    os.makedirs(folder, exist_ok=True)
    safe_filename = sanitize_filename(filename)
    file_path = os.path.join(folder, f"{safe_filename}.txt")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(story_content)
        print(f"✅ Saved: {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ Error saving {file_path}: {e}")
        return None

def process_jira_ticket(jira_url, username, api_token, ticket_key):
    print(f"🔍 Fetching ticket: {ticket_key}")
    session = get_jira_session(jira_url, username, api_token)
    ticket_data = fetch_ticket(session, jira_url, ticket_key)
    if not ticket_data:
        return []
    saved_files = []
    if is_epic(ticket_data):
        print(f"📋 Detected epic: {ticket_key}")
        print(f"   Epics are containers - fetching child tickets for actual user stories...")
        children = fetch_epic_children(session, jira_url, ticket_key)
        print(f"📦 Found {len(children)} child tickets (user stories)")
        for child in children:
            child_content = extract_story_content(child)
            child_key = child.get('key', 'unknown')
            child_filename = f"{child_key}_story"
            child_file = save_story(child_content, child_filename)
            if child_file:
                saved_files.append(child_file)
    else:
        print(f"📝 Processing regular ticket: {ticket_key}")
        story_content = extract_story_content(ticket_data)
        filename = f"{ticket_key}_story"
        file_path = save_story(story_content, filename)
        if file_path:
            saved_files.append(file_path)
    return saved_files

def fetch_and_save_jira_stories():
    """
    Fetch JIRA stories for the ticket/epic specified in .env and save them as .txt files.
    Returns a list of saved file paths.
    """
    load_dotenv()
    jira_url = os.getenv('JIRA_URL')
    jira_user = os.getenv('JIRA_USER')
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    jira_ticket = os.getenv('JIRA_TICKET')
    if not all([jira_url, jira_user, jira_api_token, jira_ticket]):
        print("❌ Missing required environment variables!")
        print("Please set the following in your .env file:")
        print("  JIRA_URL=https://your-domain.atlassian.net")
        print("  JIRA_USER=your-email@domain.com")
        print("  JIRA_API_TOKEN=your-api-token")
        print("  JIRA_TICKET=PROJ-123 or PROJ-456")
        return []
    print(f"🚀 Starting JIRA story fetch for: {jira_ticket}")
    print(f"📍 JIRA URL: {jira_url}")
    print(f"👤 User: {jira_user}")
    print()
    saved_files = process_jira_ticket(jira_url, jira_user, jira_api_token, jira_ticket)
    if saved_files:
        print(f"\n🎉 Successfully saved {len(saved_files)} story files:")
        for file_path in saved_files:
            print(f"  📄 {file_path}")
        print(f"\n📁 All stories saved in: user_stories/")
    else:
        print("❌ No stories were saved. Please check your JIRA credentials and ticket key.")
    return saved_files 