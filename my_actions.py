##################################################################################
#  You can add your actions in this file or create any other file in this folder #
##################################################################################

from rasa_sdk import Action
from rasa_sdk.events import SlotSet, ReminderScheduled, ConversationPaused, ConversationResumed, FollowupAction, Restarted, ReminderScheduled
from datetime import datetime as dt
from datetime import timedelta
import json
import requests


#class MyAction(Action):

#    def name(self):
#        return 'action_my_action'

#    def run(self, dispatcher, tracker, domain):
        # do something.
#        return []

class BreathPattern(Action):
    def name(self):
        return 'action_breath_pattern'

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("breath_pattern","true"),SlotSet("breath_anxious","true")]

class BreathPatternAnxious(Action):
    def name(self):
        return 'action_breath_pattern_anxious'

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("breath_anxious","true")]

class SetImpact(Action):
    def name(self):
        return 'action_set_impact'

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("impact","true")]

class SetInsight(Action):
    def name(self):
        return 'action_set_insight'

    def run(self, dispatcher, tracker, domain):
        if tracker.get_slot("insight") is None:
            return [SlotSet("insight","continue")]

class SetInsight(Action):
    def name(self):
        return 'action_set_insight_signup'

    def run(self, dispatcher, tracker, domain):
        if tracker.get_slot("insight") is None:
            return [SlotSet("insight","live")]

class SetFilledContact(Action):
    def name(self):
        return 'action_set_filled_contact'

    def run(self, dispatcher, tracker, domain):
        email = tracker.get_slot("email")
        phone = tracker.get_slot("phone-number")
        if email or phone:
            return [SlotSet("filled_contact",True)]
        else:
            return [SlotSet("filled_contact",False)]
        return []

class ProcessScholarship(Action):
    def name(self):
        return 'action_scholarship'

    def run(self, dispatcher, tracker, domain):
        if int(tracker.get_slot("amount-of-money")) >= 100 or tracker.get_slot("installment") == "true" or tracker.get_slot("installment") == "True":
            #dispatcher.utter_message(text="Thank you. Great news! We will be able to offer you a scholarship.")
            return [SlotSet("financial_plan","scholarship")]
        else:
            return [SlotSet("financial_plan","review")]

        return []

class ProcessIntroForm(Action):
    def name(self):
        return 'action_process_intro'

    def run(self, dispatcher, tracker, domain):
        if tracker.get_slot("handle_different") == True:
            return [SlotSet("process_intro","different")]
        elif tracker.get_slot("call") == True:
            return [SlotSet("process_intro","call")]
        else:
            return [SlotSet("process_intro","happy")]
        return []

class ShowCourses(Action):
    def __init__(self):
        self.api_key=""
        self.base_url = "https://livs.artofliving.org/csapi/courses"

    def name(self):
        return 'action_show_courses'

    def run(self, dispatcher, tracker, domain):
        user_date = tracker.get_slot("time")
        if user_date is None:
            return []
        try:
            user_date_object = dt.strptime(user_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        except ValueError:
            user_date_object = dt.now() + timedelta(days=1)
        user_date_string = user_date_object.strftime("%Y-%m-%d")
        to_date_object = user_date_object + timedelta(days=15)
        to_date_string = to_date_object.strftime("%Y-%m-%d")
        country = "uk"
        queryString={"type":"userlocation","country":country,"start_date_from":user_date_string,"start_date_to":to_date_string}

        headers = {'Accept': 'application/json', 'user-key': self.api_key}
        r =requests.get(self.base_url,params=queryString, headers=headers)
        data=r.json()

        #course_title = "SKY Breath Meditation"
        course_title = "Meditation and Breath Workshop"
        course_image = "http://chatbot.artofliving.org:8080/course-card.jpg"
        course_button = "Details"

        #construct the carousel
        carousel = {}
        carousel["type"] = "template"
        carousel["payload"] = {}
        carousel["payload"]["template_type"] = "generic"
        carousel["payload"]["elements"] = []

        i = 0
        for course in data["courses"]:
            i += 1
            if i == 4:
                break
            a_course = {}
            course_start_date_object = dt.strptime(course["start_date"], "%Y-%m-%d %H:%M:%S")
            course_start_month = course_start_date_object.strftime("%B")
            course_end_date_object = dt.strptime(course["end_date"], "%Y-%m-%d %H:%M:%S")
            course_end_month = course_end_date_object.strftime("%B")
            if course_start_month == course_end_month:
                course_start_date_string = course_start_date_object.strftime("%-d")
                course_end_date_string = course_end_date_object.strftime("%-d")
                a_course["title"] = course_start_month + " " + course_start_date_string + "-" + course_end_date_string
            else:
                course_start_date_string = course_start_date_object.strftime("%B %-d")
                course_end_date_string = course_end_date_object.strftime("%B %-d")
                a_course["title"] = course_start_date_string + " - " + ourse_end_date_string
            for teacher in course["teachers"]:
                course_teacher = teacher
                break
            if course_teacher is not None:
                a_course["subtitle"] = course_teacher
            a_course["image_url"] = course_image
            a_course["buttons"] = []
            button = {}
            button["title"] = course_button
            if course["link"].startswith('http'):
                button["url"] = course["link"]
            else:
                button["url"] = "http://" + course["link"]
            button["type"] = "web_url"
            a_course["buttons"].append(button)

            carousel["payload"]["elements"].append(a_course)

        dispatcher.utter_message(attachment=carousel)

        result = json.dumps(carousel)
        #print(json.dumps(carousel, indent=4, sort_keys=True))

        # printing result as a string
        #print ("final string = ", result)


        return []
