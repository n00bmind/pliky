import os, json
import subprocess

from prompt_toolkit import prompt, HTML, PromptSession
from prompt_toolkit import print_formatted_text as printf
from prompt_toolkit.completion import Completer, WordCompleter, PathCompleter
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.document import Document


commands_list = [
    '#add',
    '#quit'
]


class CustomCompleter(Completer):
    def __init__(self, completions, meta_dict, project_root):
        self.words = WordCompleter(completions, meta_dict=meta_dict, WORD=True, ignore_case=True)
        # TODO Rewrite using the one in prompt-toolkit/completion/filesystem.py as ref, but include '/' at the end of dir completions
        self.paths = PathCompleter(get_paths=(lambda: [str(project_root)]))

    def _split_args(self, text):
        args = text.split()
        cur_arg_index = len(args) - 1 if args and len(args) else 0

        if text and text[-1] == ' ':
            cur_arg_index += 1

        return args, cur_arg_index

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        args, cur_arg_index = self._split_args(text)
        cmd = args[0] if args else ''

        is_directive = text and text[0] == '#'
        needs_args = is_directive and cmd != '#quit'
        if not needs_args and cur_arg_index > 0:
            return

        completer = self.words
        # For now support paths only in second arg for #add
        # FIXME Support spaces in paths!
        is_path_arg = args and cmd == '#add' and cur_arg_index == 2
        if is_path_arg:
            completer = self.paths
            # TODO Generalize for any argument position
            cur_text = args[2] if len(args) == 3 else ''
            cur_pos = len(args[2]) if len(args) == 3 else 0
            document = Document(text=cur_text, cursor_position=cur_pos, selection=document.selection)

        yield from completer.get_completions(document, complete_event)



def parse_directive(text, project_path, entries_dict):
    running = True
    entries_dirty = False

    args = text.split()
    cmd = args[0]
    if cmd == '#quit':
        running = False
    elif cmd == '#add':
        if len(args) < 3:
            print('Syntax: #add [alias] [path]')
        else:
            # TODO Ensure relative path is given!
            path = project_path / args[2] #os.path.join(project_path, args[2])
            if not path.exists(): #os.path.exists(path):
                print(f'Invalid path {path}')
            else:
                entries_dict[args[1]] = args[2]
                entries_dirty = True

    return running, entries_dirty



def execute_entry(path):
    if not path:
        print('Unknown entry')
        return

    printf(HTML(f'<gray>> {path}</gray>'))

    is_file = not os.path.isdir(path)
    dir_name = os.path.dirname(path)
    try:
        if is_file:
            cwd = os.getcwd()
            os.chdir(dir_name)

        # TODO Handle paths with spaces
        prefix = 'start ' if os.name == 'nt' else 'open '
        retcode = subprocess.run(prefix + str(path), shell=True)

        if is_file:
            os.chdir(cwd)

    except OSError as e:
        print(f'Execution failed: {e}')



def build_completions_func(entries_dict):
    def func():
        return commands_list + list(entries_dict.keys())

    return func



def start(state):
    state.entries_dict = {}
    try:
        with open(state.project_file, 'rt') as f:
            state.entries_dict = json.load(f)
    except FileNotFoundError:
        pass

    if not isinstance(state.entries_dict, dict):
        print('Corrupted project file!')
        return 1

    completions_func = build_completions_func(state.entries_dict)
    state.completer = CustomCompleter(completions_func, state.entries_dict, state.project_path)
    state.session = PromptSession()



def process_next_entry(state):
    # TODO Auto-complete paths in #add
    # TODO Key bindings?
    # TODO Complete while typing
    # TODO Async?
    running = True
    text = state.session.prompt(HTML('<b><white>:: </white></b>'), vi_mode=False, completer=state.completer, complete_while_typing=False)
            # complete_style=CompleteStyle.COLUMN)
    if text.startswith('#'):
        running, entries_dirty = parse_directive(text, state.project_path, state.entries_dict)
        if entries_dirty:
            with open(state.project_file, 'wt') as f:
                json.dump(state.entries_dict, f, indent=4)

    elif text in ['q', 'quit']:
        running = False
    elif text:
        execute_entry(state.project_path / state.entries_dict.get(text))

    return running
