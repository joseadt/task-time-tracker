import sys
from typing import Optional, Tuple

from PyQt6 import QtCore, QtWidgets

from .model.entities import Step, Task, TaskEvent, event_start, event_stop
from .model.repository import TaskRepository
from .ui.ui_main import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.task = EditableTask(self.ui, self.save_task)
        self.ui.taskSearchEdit.setPlaceholderText("Search task")
        self.ui.taskSearchEdit.textEdited.connect(self.search_tasks)
        self.ui.taskList.itemClicked.connect(self.task_item_clicked)
        self.ui.addTaskButton.clicked.connect(self.add_task)
        with TaskRepository() as repo:
            self._load_tasks(repo)
            item = self.ui.taskList.item(0)
            if item:
                self.ui.taskList.setCurrentItem(item)
                self.task.set_data(repo.get_task(item.id))
    
    def task_item_clicked(self, task_item):
        if(isinstance(task_item, TaskListItem)):
            with TaskRepository() as repo:
                task = repo.get_task(task_item.id)
                self.task.set_data(task)
    
    def search_tasks(self):
        with TaskRepository() as repo:
            self._load_tasks(repo, self.ui.taskSearchEdit.text())
        
    def save_task(self, task = None):
        task = task if task != None else self.task
        with TaskRepository() as repo:
            task = repo.save_task(task)
            self.task.set_data(task)
            self._load_tasks(repo)
            
    def _load_tasks(self, repo: TaskRepository, filter: Optional[str] = None):
        self.ui.taskList.clear()
        for task in repo.get_all_tasks(filter):
                self.ui.taskList.addItem(TaskListItem(self.ui.taskList, task.id, task.title, task.complete))
    
    def add_task(self):
        self.save_task(Task(title= "New task", description=""))
        
        
class EditableTask(Task):
    
    total_time_spent_prefix = "Total Time spent: "
    start_button_text = "Start task"
    stop_button_text = "Stop task"
    
    def __init__(self, ui: Ui_MainWindow, onEdit = None, task = Task()):
        super().__init__(task.id, task.title, task.description, task.complete, task.steps, task.events, task.creation_date)
        self.titleField= ui.taskTitleEdit
        self.descField = ui.taskDescEdit
        self.titleField.setPlaceholderText("Task title...")
        self.descField.setPlaceholderText("Description...")
        self.totalTimeSpentLabel = ui.totalTimeSpentLabel
        self.eventButton = ui.startStopTaskButton
        self.eventButton.clicked.connect(self.startStopTask)
        
        self._set_time()
        self.update_time_timer = QtCore.QTimer()
        self.update_time_timer.setInterval(1000)
        self.update_time_timer.timeout.connect(self._set_time)
        self.update_time_timer.start()
        
        self.taskCompleteField =  ui.taskComplete
        self.taskCompleteField.clicked.connect(self.update_task)
        
        self.debounce = QtCore.QTimer()
        self.debounce.setInterval(500)
        self.debounce.setSingleShot(True)
        self.debounce.timeout.connect(self.update_task)
        self.descField.textChanged.connect(self.debounce.start)
        self.titleField.textChanged.connect(self.debounce.start)
        self.reloadTask = onEdit
        
    def _set_time(self):
        self.totalTimeSpentLabel.setText(EditableTask.total_time_spent_prefix + self.calculate_time())
        
    def update_task(self):
        def check_eq(new, old) -> Tuple[any, bool]:
            return [new, new != old]
        
        [self.title, changed_title] = check_eq(self.titleField.text(), self.title)
        [self.description, changed_desc] = check_eq(self.descField.toPlainText(), self.description)
        [self.complete, changed_complete] = check_eq(self.taskCompleteField.isChecked(), self.complete)  
        
        if (changed_title or changed_desc or changed_complete) and self.reloadTask:
            self.reloadTask()

    def clear(self):
        self.titleField.clear()
        self.descField.clear()
        self.taskCompleteField.setChecked(False)
        
    def set_data(self, task: Task): 
        super(EditableTask, self).__init__(task.id, task.title, task.description, task.complete, task.steps, task.events, task.creation_date)
        self._set_time()
        self.titleField.setText(task.title)
        self.descField.setText(task.description)
        self.taskCompleteField.setChecked(task.complete)
        self.eventButton.setText(EditableTask.stop_button_text if len(self.events) and self.events[-1:][0].event == event_start else EditableTask.start_button_text)
        
    def startStopTask(self):
        next_event = event_stop if len(self.events) and self.events[-1:][0].event == event_start else event_start
        event = TaskEvent(event=next_event,task_id= self.id)
        with TaskRepository() as repo:
            event = repo.add_task_event(event)
            self.events.append(event)
            self.eventButton.setText(EditableTask.stop_button_text if next_event == event_start else EditableTask.start_button_text)
        
        
class TaskListItem(QtWidgets.QListWidgetItem):
    
    def __init__(self, taskList: QtWidgets.QListWidget, id: int, text, complete = False):
        super().__init__('> ' + text, taskList)
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
