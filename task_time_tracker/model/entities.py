from datetime import datetime

event_start = 1
event_stop = 0


class TaskEvent:

    def __init__(self, id, task_id, event, date=datetime.now()):
        self.id = id
        self.task_id = task_id
        self.event = event
        self.date = date


class Step:

    def __init__(self, id, task_id, title, complete=False):
        self.id = id,
        self.task_id = task_id
        self.title = title
        self.complete = complete


class Task:

    def __init__(self, id= None, title = None, description = None, complete=False, steps=[], events=[], creation_date = datetime.now()):
        self.id = id
        self.title = title
        self.description = description
        self.complete = complete
        self.steps = steps
        self.events = events
        self.creation_date = creation_date

    def add_step(self, step):
        self.steps.append(step)

    def add_event(self, event):
        self.events.append(event)
