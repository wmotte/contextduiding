import os
import json

def generate_data():
    data = {}
    
    # Get current directory
    root_dir = "."
    
    # Exclude list
    exclude_dirs = {'.git', '.DS_Store', 'css', 'js', 'output', 'node_modules', '.gemini'}
    exclude_files = {'index.html', 'script.js', 'style.css', 'generate_data.py', 'data.js', 'website_server.py'}

    for item in os.listdir(root_dir):
        if os.path.isdir(item) and item not in exclude_dirs and not item.startswith('.'):
            # This is likely a municipality folder
            municipality = item
            data[municipality] = {}
            
            # Walk through files in this directory
            for filename in os.listdir(os.path.join(root_dir, municipality)):
                if filename.endswith('.md'):
                    filepath = os.path.join(root_dir, municipality, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        data[municipality][filename] = content
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
                        
    # Write to data.js
    js_content = f"window.CONTEXT_DATA = {json.dumps(data, indent=2)};"
    
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Generated data.js with {len(data)} municipalities.")

if __name__ == "__main__":
    generate_data()
