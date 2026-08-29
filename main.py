import argparse
from cli import add_todo, list_todos, mark_done, delete_todo
from models import Todo
import os
import json

def display_todos(todos: list[Todo]):
    """Prints the todos in a readable format."""
    if not todos:
        print("✅ Todo list is empty!")
        return
    print("\n--- TODO LIST ---")
    for todo in todos:
        print(todo)
    print("-----------------\n")

def main_cli():
    """Main function to handle CLI arguments."""
    parser = argparse.ArgumentParser(description="A simple CLI Todo app.")
    subparsers = parser.add_subparsers(dest='command')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new todo.')
    add_parser.add_argument('description', type=str, help='The description of the todo.')

    # List command
    subparsers.add_parser('list', help='List all todos.')

    # Done command
    done_parser = subparsers.add_parser('done', help='Mark a todo as done.')
    done_parser.add_argument('id', type=int, help='The ID of the todo to mark done.')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a todo.')
    delete_parser.add_argument('id', type=int, help='The ID of the todo to delete.')

    args = parser.parse_args()

    if args.command == 'add':
        new_todo = add_todo(args.description)
        print(f"Successfully added todo: {new_todo}")
    elif args.command == 'list':
        todos = list_todos()
        display_todos(todos)
    elif args.command == 'done':
        todo = mark_done(args.id)
        if todo:
            print(f"Successfully marked todo {args.id} as done: {todo}")
        else:
            print(f"Error: Todo with ID {args.id} not found.")
    elif args.command == 'delete':
        if delete_todo(args.id):
            print(f"Successfully deleted todo with ID {args.id}.")
        else:
            print(f"Error: Todo with ID {args.id} not found.")
    else:
        parser.print_help()

if __name__ == '__main__':
    main_cli()