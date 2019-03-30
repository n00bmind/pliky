#!/usr/bin/env python3
import os, sys
import json
import subprocess
from pathlib import Path
from prompt_toolkit import prompt, print_formatted_text, HTML, PromptSession
from prompt_toolkit import print_formatted_text as printf
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import CompleteStyle


commands_list = [
    '#add',
    '#quit'
]


def parse_directive(text, project_path, entries_dict):
    running = True
    reload_entries = False

    args = text.split()
    cmd = args[0]
    if cmd == '#quit':
        running = False
    elif cmd == '#add':
        if len(args) < 3:
            print('Syntax: #add [alias] [path]')
        else:
            # FIXME Ensure relative path is given!
            path = project_path / args[2] #os.path.join(project_path, args[2])
            if not path.exists(): #os.path.exists(path):
                print(f'Invalid path {path}')
            else:
                entries_dict[args[1]] = args[2]
                reload_entries = True

    return running, reload_entries



def execute_entry(path):
    if not path:
        print('Unknown entry')
        return

    printf(HTML(f'<gray>> {path}</gray>'))
    try:
        # TODO Handle paths with spaces
        prefix = 'start ' if os.name == 'nt' else 'open '
        retcode = subprocess.run(prefix + str(path), shell=True)
    except OSError as e:
        print(f'Execution failed: {e}')




if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('I need a path to the project\'s root')
        exit(1)
    project_path = Path(sys.argv[1])
    project_file = project_path / 'project.plik'
    print(repr(project_file))
    if not os.path.isdir(project_path):
        print('Invalid path')
        exit(1)

    entries_dict = {}
    try:
        with open(project_file, 'rt') as f:
            entries_dict = json.load(f)
    except FileNotFoundError:
        pass

    if not isinstance(entries_dict, dict):
        print('Corrupted project file!')
        exit(1)


    completions = commands_list + list(entries_dict.keys())
    completer = WordCompleter(completions, WORD=True)
    session = PromptSession()

    running = True
    while(running):
        # TODO Auto-complete paths in #add
        # TODO Show path next to alias in auto-complete options?
        text = session.prompt(HTML('<b><white>:: </white></b>'), vi_mode=True, completer=completer, complete_while_typing=False)
        if text.startswith('#'):
            running, reload_entries = parse_directive(text, project_path, entries_dict)
            if reload_entries:
                completions = commands_list + list(entries_dict.keys())
                completer.words = completions

                with open(project_file, 'wt') as f:
                    json.dump(entries_dict, f, indent=4)

        elif text in ['q', 'quit']:
            running = False
        elif text:
            execute_entry(project_path / entries_dict.get(text))
