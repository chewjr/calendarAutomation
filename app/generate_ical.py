from dataclasses import dataclass
from datetime import datetime, timedelta
import csv 
import logging
from icalendar import Calendar, Event

# Gets or creates a logger
logger = logging.getLogger(__name__)  

# set log level
logger.setLevel(logging.INFO)

# define file handler and set formatter
file_handler = logging.FileHandler('ical.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)

@dataclass()
class SMUEvent:
    start_time: datetime
    end_time: datetime
    end_date: datetime
    summary: str
    duration: float
    description: str
    location: str
    recurrence: dict

def generate_ical(events, username):
    cal = Calendar()
    cal.add('prodid', '-//Google Inc//Google Calendar 70.9054//EN')
    cal.add('version', '2.0')

    for e in events:
        event = Event()
        event.add('dtstart', e.start_time)
        event.add('dtend', e.end_time)
        event.add('rrule', e.recurrence)
        event.add('dtstamp', datetime.now())
        event.add('created', datetime.now())
        event.add('description', e.description)
        event.add('last-modified', datetime.now())
        event.add('location', e.location)
        event.add('status', 'CONFIRMED')
        event.add('summary', e.summary)
        cal.add_component(event)

    filename = "calendar_files/" + username + ".ics"
    f = open(filename, 'wb')
    f.write(cal.to_ical())
    f.close()
    return filename

def automate(file_data):
    rows = file_data.split("\r\n")
    # with open(file) as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    events = []
    print("=== > Picking Events from Excel ... \n\n")
    logger.info("=== > Picking Events from Excel ...")
    # for row in csv_reader:
    for r in rows:
        row = r.split(",")
        temp = []
        for ro in row:
            temp.append(ro.strip("\""))
        row = temp
        if len(row) < 15:
            continue
        # print(len(row), row)
        # inputs class schedules
        if row[6] == 'Enrolled' and row[7] == 'CLASS':
            # start time
            days = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat':5, 'Sun':6}
            start_time_str = row[8] + " " + row[11]
            start_time = datetime.strptime(start_time_str, "%d-%b-%Y %H:%M")
            for d in days.keys(): 
                if row[10] == d:
                    start_time += timedelta(days=days[d])
            end_time = start_time + timedelta(hours=3.25)
            
            # end date
            end_date_str = " ".join([row[9], " 235959"])    # recurrence requires the full day 
            end_date = datetime.strptime(end_date_str, "%d-%b-%Y %H%M%S")

            summary = row[3] + " - " + row[5] + " " + row[4]
            location = row[13]
            description = row[14]

            recurrence = {
                "FREQ": "WEEKLY",
                "UNTIL": end_date
            }

            event = SMUEvent(
                start_time=start_time,
                end_time=end_time,
                end_date=end_date,
                summary=summary,
                duration=3.25,
                description=description,
                location=location,
                recurrence=recurrence
            )
            events.append(event)

        # input exam schedules
        if row[6] == 'Enrolled' and row[7] == 'EXAM':
            start_time_str = row[8] + " " + row[11]
            start_time = datetime.strptime(start_time_str, "%d-%b-%Y %H:%M")
            end_date_str = " ".join([row[9], " 235959"])    # recurrence requires the full day 
            end_date = datetime.strptime(end_date_str, "%d-%b-%Y %H%M%S")
            duration = abs(datetime.strptime(row[11], '%H:%S')-datetime.strptime(row[12], '%H:%S')).total_seconds()/3600 
            end_time = start_time + timedelta(hours=duration)

            summary = row[3] + " - " + row[5] + " " + row[4]
            location = row[13]
            description = row[14]

            recurrence = {
                "FREQ": "WEEKLY",
                "UNTIL": end_date
            }

            event = SMUEvent(
                start_time=start_time,
                end_time=end_time,
                end_date=end_date,
                summary=summary,
                duration=duration,
                description=description,
                location=location,
                recurrence=recurrence
            )
            events.append(event)

    print("=== > Printing events information ...")
    logger.info("=== > Printing events information ...")
    print(events)
    logger.info(str(events))
    print()
    return events

def generate_calendar(file_data, username):
    logger.info("starting ical generation for " + username)
    success = False
    events = automate(file_data)
    if len(events) != 0:
        print("=== > Generating ical ...")
        logger.info("=== > Generating ical ...")
        filename = generate_ical(events, username)
        print()
        print("=== > ical generated and saved.")
        logger.info("=== > ical generated and saved. File: " + filename)
        return True, filename
    else:
        logger.warning(
            "No file generated, some issue with {user} file".format(username)
        )
    return success, "nofile"
