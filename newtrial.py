from calendar import timegm
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from selenium.webdriver.common import keys
from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup
import os
from email.message import EmailMessage
import ssl
import smtplib
import json

MINUTES_TO_WAIT = 6
EMAIL_SENDER = "ae19b101@smail.iitm.ac.in"
EMAIL_PASSWORD = "<passcode>"

with open("course_list.json") as json_file:
    JSON_CONTENT = json.load(json_file)
COURSE_EMAILS = {course: content[0] for course, content in JSON_CONTENT.items()}
COURSE_NAME = {course: content[1] for course, content in JSON_CONTENT.items()}
COURSE_VANACY = {course: 0 for course in list(COURSE_EMAILS.keys())}

options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
wd = webdriver.Firefox(executable_path=r'E:\geckodriver-v0.32.0-win32\geckodriver.exe', options=options)

def login(user_name, password):
    wd.get("https://workflow.iitm.ac.in/student/")
    postcode_field = wd.find_element(By.ID, "txtUserName")
    postcode_field.send_keys(user_name)
    postcode_field = wd.find_element(By.ID, "txtPassword")
    postcode_field.send_keys(password)
    wd.find_element(By.ID, "Login").click()


def switch_tab(tab_name):
    wd.find_element(By.ID, tab_name).click()


def switch_iframe(frame_name):
    wd.switch_to.frame(frame_name)


def get_table(table_id):
    # print(wd.find_elements(By.XPATH, f'//*[@id="{table_id}"]/tbody/tr'))
    return wd.find_elements(By.ID, table_id)


def send_message(courses):
    print(courses)
    for course_id, vacancy in courses:
        em = EmailMessage()
        em["From"] = EMAIL_SENDER
        em["To"] = COURSE_EMAILS[course_id]
        em["Subject"] = f"Course vacancy for {COURSE_NAME[course_id]}"
        body = f"There are {vacancy} vacancies available for {course_id}: {COURSE_NAME[course_id]}"
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.sendmail(
                EMAIL_SENDER, COURSE_EMAILS[course_id].split(","), em.as_string()
            )
            print("EMAIL SENT")
            print()


login("ae19b101", "<password>")
time.sleep(2)
while True:
    try:
        wd.refresh()
        print("Looking for Vacancy...")
        switch_tab("ctl00_AddDropCoursesLink")
        time.sleep(2)
        switch_tab("btnViewAvailablityElec")

        switch_iframe("ifElectiveCourses")

        l = get_table("basketCourses")
        message_to_send = []
        course_lists = {}
        for row in l:
            r_content = row.text.split()
            course_id = r_content[0]
            vacancy = r_content[-1]
            course_lists[course_id] = vacancy

        for course_id in COURSE_VANACY.keys():
            if course_id in list(course_lists.keys()):
                if COURSE_VANACY[course_id] != course_lists[course_id]:
                    COURSE_VANACY[course_id] = course_lists[course_id]
                    message_to_send.append([course_id, course_lists[course_id]])
            else:
                COURSE_VANACY[course_id] = 0
        print(COURSE_VANACY)

        if len(message_to_send) != 0:
            # print(message_to_send)
            send_message(message_to_send)
        # switch back to the main window
        wd.switch_to.default_content()

        switch_tab("ctl00_MainContent_btnViewElectiveCourse")

        print("WAITING....")
        print()
        time.sleep(MINUTES_TO_WAIT * 60)

    except:
        print("Crashed and restaring the BROWSER..")
        print("")
        # clear cookies
        wd.delete_all_cookies()

        # close the previous web driver
        wd.quit()

        # create a new instance of the web driver
        wd = webdriver.Firefox(executable_path=r'E:\geckodriver-v0.32.0-win32\geckodriver.exe', options=options)

        login("ae19b101", "?nU3E%&t")

        with open("course_list.json") as json_file:
            JSON_CONTENT = json.load(json_file)
        COURSE_EMAILS = {course: content[0] for course, content in JSON_CONTENT.items()}
        COURSE_NAME = {course: content[1] for course, content in JSON_CONTENT.items()}
        COURSE_VANACY = {course: 0 for course in list(COURSE_EMAILS.keys())}

        time.sleep(10)
