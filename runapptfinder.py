from classes.appointmentfinder import AppointmentFinder
from classes.logger import error, info

if __name__ == "__main__":
    try:
        finder = AppointmentFinder()
        contacts = finder.getContactsByState()
        
        for state in contacts:
            available = finder.checkStateAvailability(state)

            if available:
                emails = contacts[state]
                finder.sendApptAvailableEmailCvs(emails, state)
                
        info("Appointment finder run complete!")
    except Exception as e:
        error(str(e))