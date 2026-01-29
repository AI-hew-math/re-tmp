import os
import re

def update_mermaid_graph():
    exp_dir = "experiments"
    status_file = "STATUS.md"
    
    if not os.path.exists(exp_dir):
        return

    relationships = []
    
    # Scan all README.md files in experiments/
    for root, dirs, files in os.walk(exp_dir):
        if "README.md" in files:
            path = os.path.join(root, "README.md")
            with open(path, 'r') as f:
                content = f.read()
                
                # Extract ID and Parent from frontmatter
                exp_id = re.search(r"^id:\s*(.+)$", content, re.MULTILINE)
                parent_id = re.search(r"^parent:\s*(.+)$", content, re.MULTILINE)
                
                if exp_id and parent_id:
                    eid = exp_id.group(1).strip()
                    pid = parent_id.group(1).strip()
                    relationships.append(f"    {pid} --> {eid}")

    if not relationships:
        return

    # Read current STATUS.md
    with open(status_file, 'r') as f:
        lines = f.readlines()

    new_lines = []
    in_graph = False
    graph_updated = False
    
    for line in lines:
        if "```mermaid" in line:
            in_graph = True
            new_lines.append(line)
            new_lines.append("graph TD\n")
            for rel in sorted(set(relationships)):
                new_lines.append(rel + "\n")
            continue
        
        if in_graph:
            if "```" in line:
                in_graph = False
                new_lines.append(line)
            continue
        
        new_lines.append(line)

    with open(status_file, 'w') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    update_mermaid_graph()
