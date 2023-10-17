import pathlib2
import jwt
from dataclasses import dataclass
import time
import sqlite3

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
    
    
    with sqlite3.connect('database.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users( ID          INTEGER       PRIMARY KEY     AUTOINCREMENT     NOT NULL,\
                                                        Name        TEXT                        NOT NULL, \
                                                        StudentID   CHAR(12),\
                                                        Collage     TEXT,\
                                                        Purpose     TEXT,\
                                                        Time        TIMESTAMP                   NOT NULL    DEFAULT (datetime(CURRENT_TIMESTAMP,'localtime')),\
                                                        Type        TEXT\
         )")
        cursor = conn.cursor()
        if client.collage:
            cursor.execute("INSERT INTO users (Name, StudentID, Type, Collage, Purpose) VALUES (?,?,?,?,?)", (client.name, client.id, client.type, client.collage, client.purpose))
        else:
            cursor.execute("INSERT INTO users (Name, StudentID, Type, Purpose) VALUES (?,?,?,?,?)", (client.name, client.id, client.type, client.purpose))
        conn.commit()
        
def read_db():
    pass