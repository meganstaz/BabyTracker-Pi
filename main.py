import kivy
kivy.require('1.10.0')
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout

# Provide setup for Google Forms
import GoogleForms
import time
from time import strftime
from timeit import default_timer as timer
from datetime import timedelta
import pickle

form_url = "https://docs.google.com/forms/d/e/1FAIpQLSc4z-fmhAI9UfJziiv-Bh7yjx1jOFLOxJw77vbFdh5Cd61rjA/formResponse"
entryid_action = 'entry.1403445275'
entryid_local_time = 'entry.1513979551'
backup_csv = '/home/pi/logs/hunter_logs.csv'
debug_user = True

class pop(BoxLayout):

    def close_popup_post_request(self, instance):
        params = GoogleForms.params_builder(entry_ids=(entryid_action, entryid_local_time),
                                            entry_contents=(self.but.text, strftime("%I:%M %p", time.localtime())))
        GoogleForms.post_google_form(form_url, params, backup_csv, debug_user)
        self.main_pop.dismiss()

    def open_popup_post_request(self, entry_content):
        params = GoogleForms.params_builder(entry_ids=(entryid_action, entryid_local_time),
                                            entry_contents=(entry_content, strftime("%I:%M %p", time.localtime())))
        GoogleForms.post_google_form(form_url, params, backup_csv, debug_user)

    def close_popup(self, instance):
        self.info_popup.dismiss()

    def show_it(self, indicator):

        self.box = FloatLayout()

        self.lab = Label(text="Feeding " + indicator + " In Progress", font_size=15, pos_hint = {'x':0,'y':.35})

        self.timer_label = Label(text="", font_size=18, pos_hint = {'x':0, 'y':.05})

        self.but = Button(text="Complete " + indicator, size_hint = (1,.2), pos_hint = {'x':0,'y':0})

        self.box.add_widget(self.lab)

        self.box.add_widget(self.timer_label)

        self.box.add_widget(self.but)

        self.main_pop = Popup(title=indicator + " Feeding", content=self.box,
                              size_hint=(None, None), size=(450, 300), auto_dismiss=False, title_size=15)

        self.but.bind(on_release=self.close_popup_post_request)

        self.open_time = str(timer())  # The time that it was opened. Stays persistent

        Clock.schedule_interval(self.elapsed_time, 0.1)


        self.main_pop.open()

    def elapsed_time(self, *args):
        open_time = float(self.open_time)
        now_time = timer()
        elapsed_time = round((now_time - open_time), 1)
        elapsed_time = int(elapsed_time)
        formatted_time = str(timedelta(seconds=elapsed_time))
        self.timer_label.text = formatted_time



    def get_the_time(self, indicator, target, pickle_file_name):
        if debug_user is False:
            target.text = indicator + " at " + strftime("%I:%M %p", time.localtime())
            pickle_it = target.text
            output = open(pickle_file_name, 'wb')
            pickle.dump(pickle_it, output)
            output.close()

    def load_history(self, pickle_file_name, target):
        try:
            pkl_file = open(pickle_file_name, 'rb')
            loaded_history = pickle.load(pkl_file)
            target.text = loaded_history
        except:
            self.text = ""

    def tally_count(self, target, pickle_file_name, tallybool=True):
        if debug_user is False:
            try:
                pkl_file = open(pickle_file_name, 'rb')
                current_count = pickle.load(pkl_file)
            except:
                current_count = "0"
                output_e = open(pickle_file_name, 'wb')
                pickle.dump(current_count, output_e)
                output_e.close()
            current_count = int(current_count)
            newCount = str(current_count + 1)
            if tallybool is True:
                target.text = newCount
                output = open(pickle_file_name, 'wb')
                pickle.dump(newCount, output)
                output.close()
            else:
                target.text = str(current_count)
                return False
    pass


class PopApp(App):
    time = StringProperty()
    start_time = StringProperty()
    elapsed_meta = StringProperty()
    meta_markup_bool = BooleanProperty()

    def update(self, *args):
        self.time = strftime("%I:%M:%S %p", time.localtime())

    def reset_meta_start(self, *args):
        self.start_time = str(timer())
        self.meta_medium = timedelta(hours=2, minutes=30)
        self.meta_high = timedelta(hours=3)
        self.meta_markup_bool = False

    def track_elapsed_meta(self, *args):
        open_time = float(self.start_time)
        now_time = timer()
        elapsed_time = round((now_time - open_time), 1)
        elapsed_time = int(elapsed_time)
        formatted_time = timedelta(seconds=elapsed_time)
        meta_medium = self.meta_medium
        meta_high = self.meta_high
        if formatted_time < meta_medium:
            self.elapsed_meta = "(" + str(formatted_time) + ")"

        elif meta_medium <= formatted_time < meta_high:
            formatted_meta = "[color=ff9933](" + (str(formatted_time)) + ")[/color]"
            self.elapsed_meta = formatted_meta
            self.meta_markup_bool = True

        else:
            formatted_meta = "[color=ff0000](" + (str(formatted_time)) + ")[/color]"
            self.elapsed_meta = formatted_meta
            self.meta_markup_bool = True

    def build(self):
        self.reset_meta_start()
        Clock.schedule_interval(self.update, 0.1)
        Clock.schedule_interval(self.track_elapsed_meta, 1)

        return pop()

PopApp().run()



