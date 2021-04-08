from os import environ
from classes.db import db
from typing import Dict, List, Any
from requests import get
from email.message import EmailMessage
from classes.logger import info, error
from datetime import datetime
import smtplib

baseURLs = {
    "CVS": "https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.{}.json?vaccineinfo"
}

class AppointmentFinder():
    def __init__(self) -> None:
        self.db = db()
        self.statesUpdated = self.getUpdatedTsByState()

    # pulls contacts data from db and sorts contacts by state
    def getContactsByState(self) -> Dict[str, List[str]]:
        contactsByState = {}
        # get eligible contacts only
        contacts = self.db.getEligibleContacts()

        for row in contacts:
            state = row['state']
            email = row['email']

            if state in contactsByState:
                contactsByState[state].append(email)
            else:
                contactsByState[state] = [email]

        return contactsByState

    def getUpdatedTsByState(self) -> Dict[str, datetime]:
        statesUpdated = {}
        times = self.db.getStateUpdatedTs()

        for row in times:
            state = row['state']
            updated = row['updated']
            statesUpdated[state] = updated

        return statesUpdated

    # pulls data from cvs api about open appointments
    def getApptDataForStateCvs(self, state: str) -> Any:
        reqUrl = baseURLs["CVS"].format(state)
        headers = {'Referer': 'https://www.cvs.com/immunizations/covid-19-vaccine'}
        req = get(url=reqUrl, headers=headers)
        apptData = req.json()['responsePayloadData']
        return apptData

    # checks if there are any open appointments in a state
    def openStateApts(self, respData: Dict[str, Any]) -> bool:
        stateData = respData['data']
        bookingComplete = respData['isBookingCompleted']
        return stateData and not bookingComplete

    # checks if there are available apts in a state
    # and if the state ts has been refreshed
    # updates ts if it has been refreshed
    def checkStateAvailability(self, state: str) -> bool:
        apts = False
        tsOld = False
        
        try:
            respData = self.getApptDataForStateCvs(state)
            apts = self.openStateApts(respData)
            respTs = respData['currentTime']
            parsedTs = self.parseTs(respTs)
            tsOld = self.isStateUpdatedTsOld(state, parsedTs)
            if tsOld: self.updateStateTs(state, parsedTs)
        except Exception as e:
            error(str(e))

        return apts and tsOld

    # parses ts from cvs data
    def parseTs(self, ts: str) -> datetime:
        parsed = datetime(1, 1, 1)

        if 'T' in ts:
            splitTs = ts.split('T')

            if len(splitTs) >= 2:
                tsStr = '{} {}'.format(splitTs[0], splitTs[1])
                parsed = datetime.strptime(tsStr, '%Y-%m-%d %H:%M:%S.%f')

        return parsed
                


    # checks if the appointment data has been refreshed
    def isStateUpdatedTsOld(self, state: str, respTs: datetime) -> bool:
        tsOld = False

        if state in self.statesUpdated:
            curTs = self.statesUpdated[state]
            tsOld = respTs > curTs

        return tsOld

    def updateStateTs(self, state: str, ts: datetime) -> None:
        self.db.updateStateUpdatedTs(ts, state)

        if state in self.statesUpdated:
            self.statesUpdated[state] = ts

    # sends emails about available appointments to any email
    # associated with the state
    def sendApptAvailableEmailCvs(self, emails: List[str], state: str) -> None:
        subject = "Available Appointment"
        msg = ("There are CVS Covid vaccine appointments available in {}! "
                "Click {} to book your appointment now."
                .format(state.upper(), environ.get('CVSAPPTLINK')))

        self.sendEmails(emails, msg, subject)

    # construct and send email
    def sendEmails(self, receiverEmails: List[str], msg: str, subject: str) -> None:
        smtpServer = "smtp.gmail.com"
        senderEmail = environ.get('SENDEREMAIL')
        password = environ.get('EMAILPWD')

        if senderEmail and password:
            with smtplib.SMTP_SSL(smtpServer, 465) as server:
                server.login(senderEmail, password)

                for email in receiverEmails:
                    try:
                        emailMsg = EmailMessage()
                        emailMsg.set_content(msg)
                        emailMsg['Subject'] = subject
                        emailMsg['From'] = senderEmail
                        emailMsg['To'] = email
                        server.send_message(emailMsg)
                        info("{} Email sent to {}".format(subject, email))
                    except Exception as e:
                        # log error
                        error(str(e))
        else:
            raise Exception("Missing sender email and/or password")
    
    # sends welcome emails to new users
    def sendWelcomeEmailToNewContacts(self) -> None:
        newUsers = self.getNewContacts()
        
        if newUsers:
            msg = ("Thank you for signing up with Jabfinder! If there is a CVS Covid "
                    "vaccine appointment in your state you will get a notification from this "
                    "address alerting you about the appointment.")
            
            self.sendEmails(newUsers, msg, "Welcome")
            # update welcome sent email status
            self.db.updateWelcomeSentStatus(newUsers)
        
    
    # finds users who haven't had welcome emails sent
    def getNewContacts(self) -> List[str]:
        newUsers = []
        activeEmails = self.db.getActiveContacts()

        for row in activeEmails:
            welcomeSent = row['welcomeSent']
        
            if not welcomeSent:
                newUsers.append(row['email'])
        
        return newUsers