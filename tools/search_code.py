import os    # built-in — file system operations, like java.io.File
import re    # built-in — regex, like java.util.regex.Pattern

def search_code(directory, pattern):
    matches = []
    for root, dirs, files in os.walk(directory):  # recursively walks every subfolder, like a tree traversal
        for file in files:
            if file.endswith('.py'):               # filter only Python files
                path = os.path.join(root, file)   # builds full path like root + "/" + file
                with open(path, 'r') as f:
                    for i, line in enumerate(f, 1):        # loop lines with line numbers starting at 1
                        if re.search(pattern, line):       # regex match — like Pattern.matcher in Java
                            matches.append({               # add match to list
                                "file": path,
                                "line": i,
                                "content": line.strip()    # strip removes whitespace from both ends
                            })
    return matches
