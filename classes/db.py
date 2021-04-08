from datetime import datetime
from typing import Any, Dict, Union, List
from mysql.connector.connection import MySQLConnection
from mysql.connector.connection_cext import CMySQLConnection
import mysql.connector as msc
from os import environ

queries = {
    "selEligibleContacts" : "SELECT * FROM contacts WHERE active = 1 AND dateEligible <= CURRENT_TIMESTAMP",
    "selActiveContacts" : "SELECT * FROM contacts WHERE active = 1",
    "updateWelcomeSent" : "UPDATE contacts SET welcomeSent = 1 WHERE email IN({})",
    "selStateTimestamps": "SELECT state, updated FROM states",
    "updateStateTimestamp": "UPDATE states SET updated = '{}' WHERE state = '{}'"
}

class db:
    def __init__(self) -> None:
        self.cnx = self.__connect()
        self.cur = self.cnx.cursor(dictionary=True)

    def __connect(self) -> Union[CMySQLConnection, MySQLConnection]:
        config = {
            "host": environ.get('DBHOST'),
            "user": environ.get('DBUSER'),
            "password": environ.get('DBPWD'),
            "database": environ.get('DBNAME')
        }

        cnx = msc.connect(**config)
        cnx.autocommit = True
        return cnx

    def getEligibleContacts(self) -> List[Dict[str, Any]]:
        query = queries["selEligibleContacts"]
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data

    def getActiveContacts(self) -> List[Dict[str, Any]]:
        query = queries["selActiveContacts"]
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data

    def updateWelcomeSentStatus(self, emails: List[str]) -> None:
        query = queries["updateWelcomeSent"].format(",".join(["'{}'".format(email) for email in emails]))
        self.cur.execute(query)

    def getStateUpdatedTs(self) -> List[Dict[str, str]]:
        query = queries['selStateTimestamps']
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data

    def updateStateUpdatedTs(self, timestamp: datetime, state: str) -> None:
        query = queries['updateStateTimestamp'].format(timestamp, state)
        self.cur.execute(query)