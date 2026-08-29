from models import Todo
from storage import load_todos, save_todos
from typing import List, Optional

# Global state management for ID generation
next_id = 1

def get_next_id(todos: List[Todo]) -> int:
    """Determines the next available ID."""
    if not todos:
        return 1
    # Find the max ID and add 1
    return max(t.id for t in todos) + 1

def add_todo(description: str) -> Todo:
    """Adds a new todo and saves it."""
    todos = load_todos()
    new_id = get_next_id(todos)
    new_todo = Todo(id=new_id, description=description)
    todos.append(new_todo)
    save_todos(todos)
    return new_todo

def list_todos() -> List[Todo]:
    """Loads and returns all todos."""
    return load_todos()

def mark_done(todo_id: int) -> Optional[Todo]:
    """Marks a specific todo as done and saves the state."""
    todos = load_todos()
    for todo in todos:
        if todo.id == todo_id:
            todo.done = True
            save_todos(todos)
            return todo
    return None

def delete_todo(todo_id: int) -> bool:
    """Deletes a todo by ID and saves the state."""
    todos = load_todos()
    initial_count = len(todos)
    
    # Filter out the todo with the matching ID
    new_todos = [t for t in todos if t.id != todo_id]
    
    if len(new_todos) < initial_count:
        save_todos(new_todos)
        return True
    return False