from PyQt6 import uic

"""Poetry scripts"""

def compile_ui():
    def map_filename(fileName, py_file_name):
        return fileName, "ui_" + py_file_name
    uic.compile_ui.compileUiDir("./task_time_tracker/ui", True, map_filename)

def start():
    compile_ui()
    # Execute main script
    from .main import start as main_start
    main_start()
    

    
    