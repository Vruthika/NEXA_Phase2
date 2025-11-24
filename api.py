import json
from datetime import datetime
from pathlib import Path
import requests

# Configuration
OPENAPI_URL = "http://127.0.0.1:8000/openapi.json"
OUTPUT_FILE = Path("docs/API_Documentation.md")
MANUAL_NOTES_FILE = Path("docs/manual_notes.md")

def fetch_openapi_spec():
    """Fetch OpenAPI specification from running FastAPI server"""
    try:
        response = requests.get(OPENAPI_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching OpenAPI spec: {e}")
        print("Make sure your FastAPI server is running at http://127.0.0.1:8000")
        return None

def format_parameters(params):
    """Format parameter list"""
    if not params:
        return ""
    
    lines = ["\n**Parameters:**\n"]
    for param in params:
        required = " (required)" if param.get('required', False) else ""
        description = param.get('description', '')
        lines.append(f"- `{param['name']}` ({param['in']}){required} — {description}\n")
    return "".join(lines)

def format_request_body(request_body):
    """Format request body example"""
    if not request_body:
        return ""
    
    lines = ["\n**Request Body Example:**\n"]
    content = request_body.get('content', {})
    
    if 'application/json' in content:
        schema = content['application/json'].get('schema', {})
        example = content['application/json'].get('example')
        
        if example:
            lines.append(f"```json\n{json.dumps(example, indent=2)}\n```\n")
        else:
            lines.append("```json\n// See schema in full documentation\n```\n")
    
    return "".join(lines)

def format_responses(responses):
    """Format response codes"""
    if not responses:
        return ""
    
    lines = ["\n**Responses:**\n"]
    for code, response in responses.items():
        description = response.get('description', '')
        lines.append(f"- `{code}` — {description}\n")
    
    return "".join(lines)

def generate_markdown(data):
    """Generate markdown documentation from OpenAPI spec"""
    
    # Metadata
    title = data.get("info", {}).get("title", "API Documentation")
    version = data.get("info", {}).get("version", "1.0.0")
    description = data.get("info", {}).get("description", "API Documentation")
    
    md = []
    md.append(f"# {title}\n")
    md.append(f"**Version:** {version}\n")
    md.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md.append(f"\n---\n\n{description}\n\n---\n")
    
    # Group endpoints by tags
    paths = data.get("paths", {})
    endpoints_by_tag = {}
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                tags = details.get('tags', ['Uncategorized'])
                tag = tags[0] if tags else 'Uncategorized'
                
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                
                endpoints_by_tag[tag].append({
                    'path': path,
                    'method': method.upper(),
                    'details': details
                })
    
    # Generate documentation for each tag
    for tag, endpoints in sorted(endpoints_by_tag.items()):
        md.append(f"\n## {tag}\n")
        
        for endpoint in endpoints:
            path = endpoint['path']
            method = endpoint['method']
            details = endpoint['details']
            
            summary = details.get('summary', '')
            description = details.get('description', '')
            
            md.append(f"\n### `{method}` {path}\n")
            
            if summary:
                md.append(f"**{summary}**\n")
            
            if description:
                md.append(f"\n{description}\n")
            
            # Parameters
            params = details.get('parameters', [])
            md.append(format_parameters(params))
            
            # Request Body
            request_body = details.get('requestBody', {})
            md.append(format_request_body(request_body))
            
            # Responses
            responses = details.get('responses', {})
            md.append(format_responses(responses))
            
            md.append("\n---\n")
    
    return "".join(md)

def append_manual_notes(md_content):
    """Append manual notes if file exists"""
    if MANUAL_NOTES_FILE.exists():
        manual_notes = MANUAL_NOTES_FILE.read_text(encoding='utf-8')
        md_content += "\n\n---\n\n"
        md_content += "# Additional Documentation\n\n"
        md_content += manual_notes
    return md_content

def main():
    """Main execution"""
    print("🚀 Generating API Documentation...")
    
    # Fetch OpenAPI spec
    print("📥 Fetching OpenAPI specification...")
    openapi_data = fetch_openapi_spec()
    
    if not openapi_data:
        print("❌ Failed to fetch OpenAPI specification")
        return
    
    # Generate markdown
    print("📝 Generating markdown documentation...")
    md_content = generate_markdown(openapi_data)
    
    # Append manual notes
    if MANUAL_NOTES_FILE.exists():
        print("📎 Appending manual notes...")
        md_content = append_manual_notes(md_content)
    
    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    OUTPUT_FILE.write_text(md_content, encoding='utf-8')
    
    print(f"✅ Documentation generated successfully: {OUTPUT_FILE}")
    print(f"📊 Total size: {len(md_content)} characters")

if __name__ == "__main__":
    main()