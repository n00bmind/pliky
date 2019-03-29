#!/usr/bin/env python3
from prompt_toolkit import prompt, print_formatted_text, HTML, PromptSession



if __name__ == '__main__':
    session = PromptSession()

    running = True
    while(running):
        text = session.prompt(HTML('<b><ansiwhite>::</ansiwhite></b>'))
        if text in ['q', 'quit']:
            running = False
        else:
            print(f'{text}')
