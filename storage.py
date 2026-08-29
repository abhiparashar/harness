import json
import os
from typing import List
from models import Todo
from dataclasses import asdict # FIX: Import asdict

FILE_PATH = 'todos.json'

def load_todos() -> List[Todo]:
    """Loads todos from the JSON file."""
    if not os.path.exists(FILE_PATH):
        return []
    
    try:
        with open(FILE_PATH, 'r') as f:
            data = json.load(f)
            return [Todo(**d) for d in data]
    except json.JSONDecodeError:
        print("Warning: Could not decode todos.json. Starting with an empty list.")
        return []
    except Exception as e:
        print(f"An error occurred loading todos: {e}")
        return []

def save_todos(todos: List[Todo]):
    """Saves todos to the JSON file."""
    data = [asdict(todo) for todo in todos]
    try:
        with open(FILE_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"An error occurred saving todos: {e}")