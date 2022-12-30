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
        if(task.id):
            query = "UPDATE task SET title=?, description= ?, complete= ? WHERE id = ?"
            params.append(task.id)
        else:
            query = "INSERT INTO task(title, description, complete) VALUES (?, ? ,?)"
        self.con.execute(query, params)

    def get_task(self, id, fetchAll=True):
        res = self.con.execute("SELECT * FROM task t WHERE t.id = ?", [id])
        row = res.fetchone()
        steps = self.get_steps(id) if fetchAll else None
        events = self.get_task_events(id) if fetchAll else None
        return task_row_mapper(row, steps, events)

    def get_all_tasks(self, filter: str = None, fetchAll = False) -> list[Task]:
        query = "SELECT * FROM task t WHERE 1=1 "
        params = []
        if(filter):
            query += "AND t.title LIKE ? "
            params.append('%' + filter + '%')
        query += "ORDER BY creation_date DESC "
        res = self.con.execute(query, params)
        rows = res.fetchall()
        return list(map(lambda r: task_row_mapper(r), rows))

    def get_step(self, id):
        res = self.con.execute("SELECT * FROM step s WHERE s.id = ?", [id])
        return step_row_mapper(res.fetchone())

    def get_task_event(self, id):
        res = self.con.execute(
            "SELECT * FROM task_event te where te.id= ? ", [id])
        return task_event_row_mapper(res.fetchone())

    def get_steps(self, task_id=None):
        query = "SELECT * FROM step s WHERE 1=1 "
        params = []
        if(task_id):
            query += "AND s.id = ? "
            params.append(task_id)
        rows = self.con.execute(query, params).fetchall()
        return list(map(lambda r: step_row_mapper(r), rows))

    def get_task_events(self, task_id=None):
        query = "SELECT * FROM task_event te WHERE 1=1 "
        params = []
        if(task_id):
            query += "AND te.task_id = ? "
            params.append(task_id)
        rows = self.con.execute(query, params).fetchall()
        return list(map(lambda r: task_event_row_mapper(r), rows))
