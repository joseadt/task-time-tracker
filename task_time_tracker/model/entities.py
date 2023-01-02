from datetime import datetime, timedelta
from typing import Optional

event_start = 1
event_stop = 0


class TaskEvent:

    def __init__(self, id= None, task_id = None, event = None, date=None):
        self.id = id
        self.task_id = task_id
        self.event = event
        self.date = date if date else datetime.now()
        
    def get_date(self):
        self.date


class Step:

    def __init__(self, id, task_id, title, complete=False):
        self.id = id,
        self.task_id = task_id
        self.title = title
        self.complete = complete


class Task:

    def __init__(self, id= None,
                 title: str = None,
                 description: Optional[str] = None,
                 complete=False,
                 steps: list[Step]=[],
                 events: list[TaskEvent]=[],
                 creation_date = datetime.now()):
        self.id: int = id
        self.title: str = title
        self.description : str = description
        self.complete: bool = complete
        self.steps: list[Step] = steps
        self.events: list[TaskEvent]  = events if events else []
        self.events.sort(key= lambda x: x.date)
        self.creation_date: datetime = creation_date

    def add_step(self, step):
        self.steps.append(step)

    def add_event(self, event):
        self.events.append(event)
        
    def calculate_time(self) -> str:
        total_delta = timedelta()
        events = self.events.copy() if self.events else []
        events.sort(key= lambda x: x.date)
        start_date = None
        for event in events:
            if event.event == event_start and start_date == None:
                start_date = event.date
            else:
                total_delta = total_delta + (event.date - start_date)
                start_date = None
        
        if start_date != None:
            total_delta = total_delta + (datetime.now() - start_date)
        return str(total_delta).split(".")[0]
    
