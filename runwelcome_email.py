from appointmentfinder import AppointmentFinder
from logger import error, info

if __name__ == "__main__":
    try:
        finder = AppointmentFinder()
        finder.sendWelcomeEmailToNewContacts()
        info("Welcome email run complete!")
    except Exception as e:
        error(str(e))