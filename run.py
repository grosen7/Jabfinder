from appointmentfinder import AppointmentFinder
from logger import error, info

if __name__ == "__main__":
    try:
        finder = AppointmentFinder()
        finder.sendWelcomeToNewContacts()
        contacts = finder.getContactsByState()
        
        for state in contacts:
            available = finder.isStateAvailable(state)

            if available:
                emails = contacts[state]
                finder.sendApptAvailableEmail(emails, state)
                
        info("Run complete!")
    except Exception as e:
        error(str(e))