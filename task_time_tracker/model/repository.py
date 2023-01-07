from typing import Optional

from .db import *


class TaskRepository(object):     

    def __enter__(self):
        self.con = connect()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if(exception_type):
            self.con.rollback()
        else:
            self.con.commit()
        self.close()

    def open(self):
        self.con = connect()

    def close(self):
        self.con.commit()
        self.con.close()

    def save_task(self, task: Task):
        params = [task.title, task.description, task.complete]
        query = None
        update = task.id != None
        if(update):
            query = "UPDATE task SET title=?, description= ?, complete= ? WHERE id = ?"
            params.append(task.id)
        else:
            query = "INSERT INTO task(title, description, complete) VALUES (?, ? ,?)"
        res = self.con.execute(query, params)
        if(not update):
            task.id = res.lastrowid
        return task
        

    def get_task(self, id, fetchAll=True):
        res = self.con.execute("""SELECT id, title, description, complete, creation_date FROM task t WHERE t.id = ?""", [id])
        row = res.fetchone()
        steps = self.get_steps(id) if fetchAll else []
        events = self.get_task_events(id) if fetchAll else []
        return task_row_mapper(row, steps, events)

    def get_all_tasks(self, filter: Optional[str] = None, fetchAll = False) -> list[Task]:
        query = """SELECT id, title, description, complete, creation_date FROM task t WHERE 1=1 """
        params = []
        if(filter):
            query += "AND t.title LIKE ? "
            params.append('%' + filter + '%')
        query += "ORDER BY creation_date DESC "
        res = self.con.execute(query, params)
        rows = res.fetchall()
        result = list(map(lambda r: task_row_mapper(r), rows))
        if fetchAll:
            for task in result:
                task.events = self.get_task_events(task.id)
                task.steps = self.get_steps(task.id)
        
        return result

    def get_step(self, id):
        res = self.con.execute("SELECT id, title, complete, task_id FROM step s WHERE s.id = ?", [id])
        return step_row_mapper(res.fetchone())

    def get_task_event(self, id):
        res = self.con.execute(
            """SELECT id, event, date, task_id FROM task_event te where te.id= ? """, [id])
        return task_event_row_mapper(res.fetchone())

    def get_steps(self, task_id=None):
        query = "SELECT id, title, complete, task_id FROM step s WHERE 1=1 "
        params = []
        if(task_id):
            query += "AND s.id = ? "
            params.append(task_id)
        rows = self.con.execute(query, params).fetchall()
        return list(map(lambda r: step_row_mapper(r), rows))
    
    def add_task_event(self, event: TaskEvent) -> TaskEvent:
        query = "INSERT INTO task_event(event, task_id, date) VALUES(?,?,?) "
        params = [event.event, event.task_id, event.date]
        res = self.con.execute(query, params)
        event.id = res.lastrowid
        return event

    def get_task_events(self, task_id: Optional[int]=None):
        query = """SELECT id, event, date, task_id FROM task_event te WHERE 1=1 """
        params = []
        if(task_id):
            query += "AND te.task_id = ? "
            params.append(task_id)
        rows = self.con.execute(query, params).fetchall()
        return list(map(lambda r: task_event_row_mapper(r), rows))
    
    def delete_task(self, id: int):
        query = "DELETE FROM task WHERE id = ?"
        self.con.execute(query, [id])
