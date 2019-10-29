import os
import sys
import csv

from  dominate import document
from dominate.tags import *
from dominate.util import raw
from datetime import date


"""
Things to make it automated:
- Convert tabs to spaces
- Make sure newlines in between --- and prev/next section
- Make sure room numbers don't have spaces
"""

filename =  'program.txt'
title_list_filenames = ['IntuitionTalkTitles.csv', 'IntuitionTalkTitles2.csv']
current_version = "V2"

# Maps student emails to titles
email_to_title = {}

email_key =  "Email Address"
title_key = "Intuition Talk Title  (Hints:  (1) use rhetoric and (2) make sure title is an accurate summary of your intended payload.   If the title is too long (e.g. > 250 characters), staff will shorten it! )"

for title_list_filename in title_list_filenames:
    with open(title_list_filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            email_address = row["Email Address"].lower()
            title = row[title_key]
            email_to_title[email_address] = title


# Should follow (time, room, tas, [list of entries])
# Entries should follow: (name, title)
tuesday_data = []
thursday_data = []
days = ['Tuesday, Oct 29', 'Thursday, Oct 31']
dates = ['29 October 2019', '31 October 2019']
days_of_week = ['Tuesday', 'Thursday']

special_people = [
    ["Katherine Touafek (School to Careers Partnership)", "David Case, Jennifer Hardy (Worcester Tech)", "Jordan Wick (MIT)"],
    ["Katherine Touafek (School to Careers Partnership)", "Yuri Petriv (Somerville HS)", "Jordan Wick (MIT)"]
]
missing_title_emails = []

# Number of <br> tags to add in between the days. It needs these so that each
# day will print onto a different page.
num_newlines = 0

def find_email(l):
    """
    finds the index of the list in which an email is contained
    """
    for index,entry in  enumerate(l):
        if '@' in entry:
            return index

with open(filename, 'r') as f:
    # Set up variables
    first_line_in_section = True
    data_to_write = False
    current_data  = tuesday_data
    current_time = '9am'
    update_time = True
    current_section = []

    for unstripped_line in f:
        line = unstripped_line.strip()
        split_line = list(filter(None, line.split(' ')))

        if line in days:
            update_time = True
            continue
        if line == '':
            first_line_in_section = True
            continue

        # New day; switch current day.
        if '==' in line:
            upate_time = True
            current_data.append((current_time, current_room, current_moderators, current_section))
            current_section = []
            current_data = thursday_data
            first_line_in_section = True
            data_to_write = False
            # current_time = '9am'
            continue

        # New time
        if '--' in line:
            update_time = True
            continue

        if first_line_in_section and line != '':
            if data_to_write:
                current_data.append((current_time, current_room, current_moderators, current_section))
                current_section = []
            # if update_time:
            current_time = split_line[0]

            print(current_time)
            update_time = False
            current_room  = split_line[1]
            print(current_room)
            current_moderators = ' '.join(split_line[2:])
            print(current_moderators)
            first_line_in_section = False
            # print("First Line:", line)

        else:
            print(split_line)
            email_index = find_email(split_line)

            first_name = split_line[0]
            last_name = split_line[1]
            email =  split_line[2]
            recitation = split_line[7]
            name = ' '.join(split_line[:email_index])
            recitation = split_line[email_index + 5]
            email = split_line[email_index]

            # name = first_name + ' ' + last_name
            if email in email_to_title:
                title = email_to_title[email]
            else:
                title = "None Submitted"
                missing_title_emails.append(email)

            current_section.append((name, title, recitation))
            data_to_write = True


    if data_to_write:
        current_data.append((current_time, current_room, current_moderators, current_section))

# print(tuesday_data)

doc = document(title="High School Conference Program")

with doc.head:
    link(rel="stylesheet", href="./style.css")

current_date = date.today().strftime("%B %d, %Y")

print(tuesday_data[-1])
print(thursday_data[0])
with doc:
    for day_num, dataset in enumerate([tuesday_data, thursday_data]):
        day_of_week = days_of_week[day_num]
        date = dates[day_num]

        # Title Page
        with div(cls="cover-page"):
            for i in range(12):
                br()
            h2("Massachusetts Institute of Technology presents", style="font-weight: normal;")
            hr(color="red", border="10px", size="5px")
            h1("6.UAT High School Conference")
            for i in range(3):
                br()
            h2(date,style="font-weight:normal;")
            hr(color="red", border="10px", size="5px")
            h2(day_of_week + " Program", style="margin-bottom: 0px; font-weight: normal;")
            h4("Last updated: " + current_date, style="margin-top: 3px; font-weight: normal;")
            for i in range(13):
                br()
            with div(cls="specialthanks", style="text-align: right; font-size: 20px"):
                em("Special thanks to: ",style="font-style: normal; font-size: 120%;")
                br()
                br()
                for person in special_people[day_num]:
                    div(person, cls="special-person")

        # Program for the day
        with div(cls="day"):
            h1(days[day_num])
            for room_data in dataset:
                time, room, tas, entries = room_data
                with div(cls="section"):
                    h3(time + " " + room + " " + tas)
                    hr(color="red")
                    # list_thing = div()
                    with div(cls="room-list") as list_thing:
                        for entry in entries:
                            name, title, recitation = entry
                            d = div(cls='entry')

                            d.add(div(raw(title), cls="title", align="left"))
                            d.add(div(name + ' [' + recitation + ']', cls='name', align="right"))
                            # l =  div(d)
                            list_thing.add(d)
            for i in range(num_newlines):
                br()


with open('test.html', 'w') as f:
    f.write(doc.render())


for email in missing_title_emails:
    print(email)
