import pathlib2
import jwt
from dataclasses import dataclass
import time
import sqlite3

tid = 0
tid_update = 0

time_form = "%Y-%m-%d %H:%M:%S"

@dataclass
class moni_client:
    name: str
    collage: str = None
    id: str
    # time: str
    purpose: str = None
    type: str = None
    

def getinfo(id_token: str):
    '''用jwt从id_token中解析信息'''
    
    h = jwt.get_unverified_header(id_token)
    # print(h, type(h))

    info = jwt.decode(id_token, algorithms=h['alg'], options={"verify_signature": False})
    # print(info)
    # print(type(info))
    return info

def add_db(client: moni_client):
    "向db中增加条目"
    t = int(time.time())
    t_hour = int(t/3600)
    
    if(t_hour > tid_update):
        tid_update = t_hour
        tid = 0
    assert tid < 0x1000
    pid = int(t/3600)<<3 + tid
    tid += 1
    
    with sqlite3.connect('database.db') as conn:
        conn.execute(("CREATE TABLE IF NOT EXISTS users(ID          INT(12)       PRIMARY KEY      NOT NULL,\
                                                        Name        TEXT                        NOT NULL, \
                                                        StudentID   TEXT,\
                                                        Collage     TEXT,\
                                                        Purpose     TEXT,\
                                                        Time        INT                         NOT NULL,\
                                                        Type        TEXT,\
         )"))
        cursor = conn.cursor()
        if client.collage:
            cursor.execute("INSERT INTO users (ID, Name, StudentID, Type, Collage, Purpose, Time) VALUES (?,?,?,?,?,?)", (pid, client.name, client.id, client.type, client.collage, client.purpose, t))
        else:
            cursor.execute("INSERT INTO users (ID, Name, StudentID, Type, Purpose, Time) VALUES (?,?,?,?,?,?)", (pid, client.name, client.id, client.type, client.purpose, t))
        conn.commit()
        
def read_db():
    pass