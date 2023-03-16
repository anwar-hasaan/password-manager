import sqlite3
from datetime import datetime


class Database():
    def __init__(self, db_name=None):
        self.db_name = db_name
        self.table_name = None
        self.connection = None
        self.cursor = None
    
    #create connections
    def open_connection(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
        except:
            return False

    #create a table name if not already exists
    def check_or_create_table(self, table_name=None):
        if table_name:
            self.open_connection()
            self.cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    updated_at TEXT)''')
            self.table_name = table_name
            self.connection.close()
            return True

        return False
    
    #get all data with the table_name
    def get_all_data(self):
        if self.table_name:
            self.open_connection()
            self.cursor.execute(f'SELECT * FROM {self.table_name}')
            data = self.cursor.fetchall()
            self.connection.close()
            return data

        return False
    
    #get a single data with the given id
    def get(self, id=None):
        if id:
            self.open_connection()
            self.cursor.execute(f'SELECT * FROM {self.table_name} WHERE rowid={id}')
            data = self.cursor.fetchone()
            self.connection.close()
            return data
            
        return False

    #add data
    def add(self, url=None, username=None, password=None):
        try:
            updated_at = f'{datetime.now()}'[:-7]
            self.open_connection()

            self.cursor.execute(f'''INSERT INTO {self.table_name} 
            (url, username, password, updated_at) 
            VALUES (?, ?, ?, ?)''', (url, username, password, updated_at))

            id = self.cursor.lastrowid
            self.connection.commit()
            self.connection.close()
            return id

        except Exception as e:
            self.connection.close()
            return False
    #update 
    def update(self, id, url, username, password):
        if id and url and username and password:
            try:
                self.open_connection()
                updated_at = f'{datetime.now()}'[:-7]

                self.cursor.execute(
                    f'''UPDATE {self.table_name} SET url=?, username=?, password=?, updated_at=? WHERE id=?''',
                    (url, username, password, updated_at, id)
                )
                self.connection.commit()
                self.connection.close()
                return True
            except:
                return False
        return False

    def delete_item(self, id=None):
        try:
            if id:
                self.open_connection()
                self.cursor.execute(
                    f'DELETE FROM {self.table_name} WHERE id={id}'
                )
                self.connection.commit()
                self.connection.close()
                return True
            return False
        except:
            return False

    def search(self, q):
        if q:
            self.open_connection()
            self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE url LIKE ? OR username LIKE ?", (f'%{q}%', f'%{q}%'))
            data = self.cursor.fetchall()
            self.connection.close()
            return data
        else:
            return []
