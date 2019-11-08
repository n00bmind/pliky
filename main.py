#!/usr/bin/env python3
import os, sys, time
from pathlib import Path

import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
from prompt_toolkit import HTML
from prompt_toolkit import print_formatted_text as printf

import app.prompt


def _glfw_init(width=0, height=0):
    window_name = 'pliky'

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    mode = glfw.get_video_mode(glfw.get_primary_monitor())
    if width == 0 or height == 0:
        width = mode.size.width / 2 if width == 0 else width
        height = mode.size.height / 2 if height == 0 else height

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.DECORATED, False)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    print(f'Window width: {width}, height: {height}')
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if window:
        glfw.set_window_pos(window, int((mode.size.width - width) / 2), int((mode.size.height - height) / 2))
    else:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window






class State():
    pass

def main():
    if len(sys.argv) < 2:
        print('I need a path to the project\'s root')
        return 1

    project_path = Path(sys.argv[1])
    if not os.path.isdir(project_path):
        print('Invalid path')
        return 1

    project_file = project_path / 'project.plik'
    if os.path.isfile(project_file):
        printf(HTML(f'<gray>Found project file at {project_file}</gray>'))

    # Init graphics
    imgui.create_context()
    window = _glfw_init(500, 1000)
    renderer = GlfwRenderer(window)

    __main_locals_marker = None
    def on_glfw_key(window, key, scancode, action, mods):
        renderer.keyboard_callback(window, key, scancode, action, mods)

        if action == glfw.RELEASE:
            if key in (glfw.KEY_PAUSE, glfw.KEY_SCROLL_LOCK):
                # Pretty slow I assume, but reliable
                frame = inspect.currentframe()
                while frame:
                    if '__main_locals_marker' in frame.f_locals:
                        break
                    frame = frame.f_back

                ipshell(local_ns=frame.f_locals)

    # Need to set this after creating the renderer because by default it does its own hooks
    glfw.set_key_callback(window, on_glfw_key)

    #  TODO 
    state = State()
    state.project_path = project_path
    state.project_file = project_file

    app.prompt.start(state)

    running = True
    while not glfw.window_should_close(window) and running:

        glfw.poll_events()
        renderer.process_inputs()

        # TODO Render only when any events are detected to lower CPU usage
        imgui.new_frame()

        imgui.show_test_window()

        # state.window_width, state.window_height = glfw.get_window_size(window)
        # TODO Just set the font at the beginning!
        # with imgui.font(font):
        running = app.prompt.process_next_entry(state)

        gl.glClearColor(.1, .1, .1, .1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        renderer.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    renderer.shutdown()
    glfw.terminate()



if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
