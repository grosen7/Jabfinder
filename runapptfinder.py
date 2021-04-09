from classes.appointmentfinder import AppointmentFinder
from classes.logger import error, info

if __name__ == "__main__":
    try:
        finder = AppointmentFinder()
        contacts = finder.getContactsByState()
        statesUpdated = finder.getUpdatedTsByState()
        
        for state in contacts:
            cvsData = finder.getApptDataForStateCvs(state)
            aptsAvailable = finder.openStateApts(cvsData)
            parsedTs = finder.parseCvsTs(cvsData)
            tsIsOld = True

            if state in statesUpdated:
                curTs = statesUpdated[state]
                tsIsOld = parsedTs > curTs

                if tsIsOld:
                    finder.updateStateTs(state, parsedTs)
                    statesUpdated[state] = parsedTs
                    info("{} appointment data timestamp updated to {}".format(state.upper(), parsedTs))

            if tsIsOld and aptsAvailable:
                emails = contacts[state]
                finder.sendApptAvailableEmailCvs(emails, state)
                
        info("Appointment finder run complete!")
    except Exception as e:
        error(str(e))