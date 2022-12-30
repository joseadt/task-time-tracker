import sys

from PyQt6 import QtCore, QtGui, QtWidgets, uic

from .model.entities import Step, Task, TaskEvent
from .model.repository import TaskRepository
from .ui.ui_main import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.task = EditableTask(self.ui)
        self.ui.taskSearchEdit.setPlaceholderText("Search task")
        self.ui.taskSearchEdit.textEdited.connect(self.search_tasks)
        self.ui.taskSaveButton.clicked.connect(self.save_task)
        self.ui.taskList.itemClicked.connect(self.task_item_clicked)
        self.ui.addTaskButton.clicked.connect(self.add_task)
        with TaskRepository() as repo:
            self._load_tasks(repo)
            item = self.ui.taskList.item(0)
            if item:
                self.task.set_data(repo.get_task(item.id))
    
    def task_item_clicked(self, task_item):
        if(isinstance(task_item, TaskListItem)):
            with TaskRepository() as repo:
                task = repo.get_task(task_item.id, False)
                self.task.set_data(task)
    
    def search_tasks(self):
        with TaskRepository() as repo:
            self.ui.taskList.clear()
            self._load_tasks(repo, self.ui.taskSearchEdit.text())
        
    def save_task(self):
        with TaskRepository() as repo:
            id = repo.save_task(self.task.transform())
            self.task.id = id
            self.ui.taskList.clear()
            self._load_tasks(repo)
            
    def _load_tasks(self, repo: TaskRepository, filter: str = None):
        for task in repo.get_all_tasks(filter):
                self.ui.taskList.addItem(TaskListItem(self.ui.taskList, task.id, task.title, task.complete))
    
    def add_task(self):
        with TaskRepository() as repo:
            task = Task(title= "New task", description="")
            id= repo.save_task(task)
            task.id = id
            self.task.set_data(task)
            self.ui.taskList.clear()
            self._load_tasks(repo)

class EditableTask(Task):
    
    def __init__(self, ui: Ui_MainWindow, task = Task()):
        super().__init__(task.id, task.title, task.description, task.complete, task.steps, task.events, task.creation_date)
        self.titleField= ui.taskTitleEdit
        self.titleField.setPlaceholderText("Task title...")
        self.descField = ui.taskDescEdit
        self.descField.setPlaceholderText("Description...")
        self.taskCompleteField: QtWidgets.QRadioButton =  ui.taskComplete
        
    def transform(self) -> Task:
        self.title = self.titleField.text()
        self.description = self.descField.toPlainText()
        self.complete = self.taskCompleteField.isChecked()
        return self

    def clear(self):
        self.titleField.clear()
        self.descField.clear()
        self.taskCompleteField.setChecked(False)
        
    def set_data(self, task: Task): 
        super().__init__(task.id, task.title, task.description, task.complete, task.steps, task.events, task.creation_date)
        self.titleField.setText(task.title)
        self.descField.setText(task.description)
        self.taskCompleteField.setChecked(task.complete)
        
    
        
        
        
class TaskListItem(QtWidgets.QListWidgetItem):
    
    def __init__(self, taskList: QtWidgets.QListWidget, id: int, text, complete = False):
        super().__init__(text, taskList)
        self.id = id
        f = self.font()
        f.setStrikeOut(complete)
        self.setFont(f)

def start():
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QDir.addSearchPath("icons", "./assets")
    with open('styles.qss', 'r') as file:
        styles = file.read()
        app.setStyleSheet(styles)
    window = MainWindow()
    window.show()
    app.exec()
    

if __name__ == '__main__':
    start()
