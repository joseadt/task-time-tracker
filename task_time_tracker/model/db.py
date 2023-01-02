import sqlite3

from .entities import *

db_name = "task.db"


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    con.row_factory = sqlite3.Row
    return con


def init_database():
    con = connect()
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS task(
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            title varchar(50) NOT NULL,
            description varchar(250),
            complete BOOLEAN NOT NULL,
            creation_date timestamp
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS step (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(50) NOT NULL,
            complete BOOLEAN NOT NULL,
            task_id INTEGER,
            CONSTRAINT step_fk_task FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS task_event(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event INTEGER NOT NULL,
            date timestamp NOT NULL,
            task_id INTEGER,
            CONSTRAINT task_event_fk_task FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE
        );
    ''')
    con.commit()
    con.close()


def task_row_mapper(row, steps: list = None, events: list = None):
    return Task(id=row['id'],
                title=row['title'], 
                complete=row['complete'], 
                description=row['description'], 
                steps=steps, events=events,
                creation_date=row['creation_date'])


def step_row_mapper(row):
    return Step(row['id'], row['task_id'], row['title'], row['complete'])


def task_event_row_mapper(row):
    return TaskEvent(row['id'], row['task_id'], row['event'], row['date'])