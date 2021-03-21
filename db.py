from typing import Any, Dict, Union, Tuple
from mysql.connector.connection import MySQLConnection
from mysql.connector.connection_cext import CMySQLConnection
import mysql.connector as msc
from os import environ

queries = {
    "selActiveContacts" : "SELECT * FROM contacts WHERE active = 1",
}

class db:
    def __init__(self) -> None:
        self.cnx = self.connect()
        self.cur = self.cnx.cursor()

    def connect(self) -> Union[CMySQLConnection, MySQLConnection]:
        config = {
            "host": environ.get('DBHOST'),
            "user": environ.get('DBUSER'),
            "password": environ.get('DBPWD'),
            "database": environ.get('DBNAME')
        }

        cnx = msc.connect(**config)
        return cnx

    def getActiveContacts(self) -> Tuple:
        query = queries["selActiveContacts"]
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data

if __name__ == "__main__":
    myDB = db()
    data = myDB.getActiveContacts()