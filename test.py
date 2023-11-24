from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

file_path = prompt("Enter file path: ", completer=PathCompleter())
print("You entered:", file_path)
