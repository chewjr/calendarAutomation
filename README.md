# calendarAutomation

Currently, there is no automated way for you to download your calendar using SMU BOSS. It only provides you an excel sheet of your bidded classes and you have to manually input them into a calendar of your choice. 

I have created a script that automatically generates an ICS file of your classes and exams. This file can then be imported into your calendar of your choice and be displayed appropriately. 

The main part of the logic lies in the generate_ical function in the generate_ical file. Currently, it is developed to be used with a telegram bot. 