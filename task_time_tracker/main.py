import sys

from PyQt6 import QtWidgets, uic

from .model.entities import Step, Task, TaskEvent
from .model.repository import TaskRepository


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main.ui', self)
        self.show()
        self.task = EditableTask(self)
        self.taskSearchEdit: QtWidgets.QLineEdit
        self.taskSaveButton: QtWidgets.QPushButton
        self.taskSearchEdit.textEdited.connect(self.search_tasks)
        self.taskSaveButton.clicked.connect(self.save_task)
        self.taskList.itemClicked.connect(self.task_item_clicked)
        with TaskRepository() as repo:
            self._load_tasks(repo)
    
    def task_item_clicked(self, task_item):
        if(isinstance(task_item, TaskListItem)):
            with TaskRepository() as repo:
                task = repo.get_task(task_item.id, False)
                self.task.set_data(task)
    
    def search_tasks(self):
        with TaskRepository() as repo:
            self.taskList.clear()
            self._load_tasks(repo, self.taskSearchEdit.text())
        
    def save_task(self):
        with TaskRepository() as repo:
            repo.save_task(self.task.transform())
            self.taskList: QtWidgets.QListWidget
            self.taskList.clear()
            self._load_tasks(repo)
            self.task.clear()
            
    def _load_tasks(self, repo: TaskRepository, filter: str = None):
        for task in repo.get_all_tasks(filter):
                self.taskList.addItem(TaskListItem(self.taskList, task.id, task.title, task.complete))


class EditableTask(Task):
    
    def __init__(self, ui: Ui, task = Task()):
        super().__init__(task.id, task.title, task.description, task.complete, task.steps, task.events, task.creation_date)
        self.titleField: QtWidgets.QLineEdit = ui.taskTitleEdit
        self.descField: QtWidgets.QTextEdit = ui.taskDescEdit
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
        super().__init__(taskList)
        self.setText(text)
        self.id = id
        f = self.font()
        f.setStrikeOut(complete)
        self.setFont(f)

def start():
    app = QtWidgets.QApplication(sys.argv)
    with open('styles.qss', 'r') as file:
        styles = file.read()
        app.setStyleSheet(styles)
    window = Ui()
    app.exec()
    

if __name__ == '__main__':
    start()
