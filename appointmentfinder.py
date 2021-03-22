from os import environ
from db import db
from typing import Dict, List, Any
from requests import get
from email.message import EmailMessage
from logger import info, error
import smtplib

class AppointmentFinder():
    def __init__(self) -> None:
        self.db = db()
        self.baseReqUrl = "https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.{}.json?vaccineinfo"

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

    # pulls data from cvs api about open appointments
    def getApptDataForState(self, state: str) -> Any:
        reqUrl = self.baseReqUrl.format(state)
        headers = {'Referer': 'https://www.cvs.com/immunizations/covid-19-vaccine'}
        req = get(url=reqUrl, headers=headers)
        apptData = req.json()['responsePayloadData']
        return apptData

    # checks if there are any appointments available in a state
    def isStateAvailable(self, state: str) -> bool:
        try:
            respData = self.getApptDataForState(state)
            stateData = respData['data']
            bookingComplete = respData['isBookingCompleted']
        except Exception as e:
            stateData = False
            bookingComplete = False
            error(str(e))

        return stateData and not bookingComplete

    # sends emails about available appointments to any email
    # associated with the state
    def sendApptAvailableEmail(self, emails: List[str], state: str) -> None:
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
