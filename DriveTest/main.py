import logging

from DriveTest.Orchestrator import Orchestrator
from DriveTest.Utility import Logger
from DriveTest.Utility import Alarm
from DriveTest.DriveTestCandidate import DriveTestCandidate
import time
from DriveTest.Utility import FileManager


from tkinter import *
from tkinter import ttk
import tkinter as tk
import threading
import sys
from tkinter import messagebox


blls = []
class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **options):
        super().__init__(master, **options)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


class AutocompleteEntry(EntryWithPlaceholder):
        """
        Subclass of Entry that features autocompletion.

        To enable autocompletion use set_completion_list(list) to define
        a list of possible strings to hit.
        To cycle through hits use down and up arrow keys.
        """
        def set_completion_list(self, completion_list):
            self._completion_list = sorted(completion_list, key=str.lower)  # Work with a sorted list
            self._hits = []
            self._hit_index = 0
            self.position = 0
            self.bind('<KeyRelease>', self.handle_keyrelease)

        def autocomplete(self, delta=0):
            """autocomplete the Entry, delta may be 0/1/-1 to cycle through possible hits"""
            if delta:  # need to delete selection otherwise we would fix the current position
                self.delete(self.position, END)
            else:  # set position to end so selection starts where textentry ended
                self.position = len(self.get())
            # collect hits
            _hits = []
            for element in self._completion_list:
                if element.lower().startswith(self.get().lower()):  # Match case-insensitively
                    _hits.append(element)
            # if we have a new hit list, keep this in mind
            if _hits != self._hits:
                self._hit_index = 0
                self._hits = _hits
            # only allow cycling if we are in a known hit list
            if _hits == self._hits and self._hits:
                self._hit_index = (self._hit_index + delta) % len(self._hits)
            # now finally perform the auto completion
            if self._hits:
                self.delete(0, END)
                self.insert(0, self._hits[self._hit_index])
                self.select_range(self.position, END)

        def handle_keyrelease(self, event):
            """event handler for the keyrelease event on this widget"""
            if event.keysym == "BackSpace":
                self.delete(self.index(INSERT), END)
                self.position = self.index(END)
            if event.keysym == "Left":
                if self.position < self.index(END):  # delete the selection
                    self.delete(self.position, END)
                else:
                    self.position = self.position - 1  # delete one character
                    self.delete(self.position, END)
            if event.keysym == "Right":
                self.position = self.index(END)  # go to end (no selection)
            if event.keysym == "Down":
                self.autocomplete(1)  # cycle to next hit
            if event.keysym == "Up":
                self.autocomplete(-1)  # cycle to previous hit
            if len(event.keysym) == 1 or event.keysym in locations:
                self.autocomplete()

class AutocompleteCombobox(ttk.Combobox):

    base_list = []

    def set_completion_list(self, completion_list):
        """Use our completion list as our drop down selection menu, arrows move through menu."""
        self._completion_list = sorted(completion_list, key=str.lower)  # Work with a sorted list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list  # Setup our popup menu
        AutocompleteCombobox.base_list = self._completion_list

    def show_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)  # Work with a sorted list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
        """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.delete(self.position, END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):  # Match case insensitively
                _hits.append(element)
        self.show_completion_list(_hits)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
        if self._hits:
            self.delete(0, END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.delete(self.index(INSERT), END)
            self.position = self.index(END)
            if len(self.get()) == 0:
                self.show_completion_list(AutocompleteCombobox.base_list)
        if event.keysym == "Left":
            if self.position < self.index(END):  # delete the selection
                self.delete(self.position, END)
            else:
                self.position = self.position - 1  # delete one character
                self.delete(self.position, END)
            if len(self.get()) == 0:
                self.show_completion_list(AutocompleteCombobox.base_list)
        if event.keysym == "Right":
            self.position = self.index(END)  # go to end (no selection)
        if len(event.keysym) == 1:
            self.autocomplete()
        # No need for up/down, we'll jump to the popup
        # list at the position of the autocompletion


class scraping_thread(threading.Thread):
    def __init__(self, candidate, driver_type, blls_queue):
        threading.Thread.__init__(self)
        self.candidate = candidate
        self.blls_queue = blls_queue
        self.driver_type = driver_type
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def run(self):
        self.orchestrator = Orchestrator(self.driver_type)
        self.blls_queue.append(self.orchestrator)

        print("start booking process")
        self.booking()
        print("end booking process")

    def booking(self):
        try:

            process_done = self.orchestrator.booking_road_test(self.candidate)
            #process_done = self.bll.continous_google_search(self.candidate.location)
            if process_done:
                TkinterWindowApp.business_logger.info("for one user we can select one date:")
                TkinterWindowApp.business_logger.info("test center:{}   licence number:{}    licence expiry:{}   "
                                                      "test class:{}   driver type:{}".format(self.candidate.location, self.candidate.licence_number,
                                                                             self.candidate.licence_expiry,
                                                                             self.candidate.road_test_class, self.candidate.driver_type))
                Alarm.play(FileManager.resource_path("src/alarm"))
        except BaseException as be:
            log_description = be
            TkinterWindowApp.technical_logger.error(log_description)

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True

class TkinterWindowApp:
    Logger.setup_logger('Technical', 'Technical_log', logging.DEBUG)
    Logger.setup_logger('Business', 'Business_log', logging.INFO)
    business_logger = logging.getLogger('Business')
    technical_logger = logging.getLogger("Technical")


    def __init__(self):
        self.root = Tk()
        self.root.geometry("310x380")
        # Same size will be defined in variable for center screen in Tk_Width and Tk_height
        Tk_Width = 310
        Tk_Height = 380
        self.threads = []
        self.close_all_clicked = False


        # calculate coordination of screen and window form
        x_Left = int(self.root.winfo_screenwidth() / 2 - Tk_Width / 2)
        y_Top = int(self.root.winfo_screenheight() / 2 - Tk_Height / 2)

        # Write following format for center screen
        self.root.geometry("+{}+{}".format(x_Left, y_Top))
        self.root.title("Candidate Information")
        self.root.resizable(width=False, height=False)
        self.params = FileManager.get_csv_params(FileManager.resource_path("src/locations"), ";")

    def func():
        while True:
            print('thread running')

    def validate_licence_number(self, licence):
        if len(licence) == 15:
            return True
        return False

    def validate_licence_expiry(self, expire):
        if len(expire) == 8:
            return True
        return False

    def validate_interval(self, interval):
        if len(interval) > 0 and interval != "Interval Days":
            return True
        return False

    def validate_test_location(self, location):
        if location == "Select Test Center" or location is None:
            return False
        return True

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):

            self.terminate_all_driver()
            self.root.destroy()
            sys.exit(0)

    def kill_all_threads(self):
        self.threads = [thread for thread in self.threads if thread.is_alive()]
        print("alive threads :", len(self.threads))
        for t in self.threads:
            t.kill()

    def terminate_all_driver(self):
        # PROCNAME = "chromedriver-v88.exe"  # or chromedriver or IEDriverServer
        # for proc in psutil.process_iter():
        #     # check whether the process name matches
        #     if proc.name() == PROCNAME:
        #         proc.kill()
        # start progress bar
        self.kill_all_threads()
        popup = None

        blls_len = len(blls)

        if blls_len > 0:
            print("blls at the first:",blls_len)
            time.sleep(5)
            popup = tk.Toplevel()
            popup.title = "closing progress bar"
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            w = popup.winfo_width()
            h = popup.winfo_height()
            popup.attributes("-topmost", True)
            popup.geometry("%dx%d+%d+%d" % (w + 310, h + 60, x + 100, y + 100))

            tk.Label(popup, text="Please waite, browsers being closed").grid(row=0, column=0)
            progress = 0
            max_value = 100
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(popup, variable=progress_var, maximum=max_value, length=300)
            progress_bar.grid(row=1, column=0)  # .pack(fill=tk.X, expand=1, side=tk.BOTTOM)
            popup.pack_slaves()
            progress_step = float(max_value / (2*blls_len))

            print("progress_step ", progress_step)
            print("progress (blls) ",progress)
        while len(blls) > 0:
            popup.update()
            bll = blls.pop(0)
            #print("blls after pop:", len(blls))
            driver = bll.road_test.scraper.driver if hasattr(bll.road_test.scraper, "driver") else None
            while driver is None:
                #print("driver is {} but slepp 5 sec".format(driver))
                time.sleep(5)
            if driver is not None:
                #print("driver", driver)
                driver.quit()
                #print("quit driver after pop")
            progress += progress_step
            progress_var.set(progress)
            #print("progress_step ", progress_step)
            #print("progress (blls) ", progress)
            popup.update()

        #print("quitting all drivers")

        self.close_all_clicked = True

        self.threads = [thread for thread in self.threads if thread.is_alive()]
        print("alive threads :", len(self.threads))
        threads_len = len(self.threads)
        if threads_len > 0:
            progress_step2 = float(max_value / (2*threads_len))
        while len(self.threads) > 0:
            popup.update()
            self.threads = [thread for thread in self.threads if thread.is_alive()]
            diff = (threads_len - len(self.threads))
            #print("diff :", diff)
            threads_len = len(self.threads)
            progress += diff * progress_step2
            progress_var.set(progress)
            #print("progress_step ", progress_step2)
            #print("progress (threads) ", progress)
            popup.update()
        if popup is not None:
            popup.update()
            time.sleep(1)
            progress_var.set(max_value)
            popup.update()
            time.sleep(1)
            popup.destroy()
        self.close_all_clicked = False
        print("number of alive threads: ", len(self.threads))

    def call_booking(self):
        self.threads = [thread for thread in self.threads if thread.is_alive()]
        if self.close_all_clicked and len(self.threads) > 0:
            messagebox.showwarning("Waiting", "Please wait to close all open threads (booking process)")
            print("number of alive threads: ", len(self.threads))
        else:
            self.close_all_clicked = False
            is_test_location_valid = self.validate_test_location(self.test_location.get())
            is_licence_expiry_valid = self.validate_licence_expiry(self.licence_expiry.get())
            is_licence_number_valid= self.validate_licence_number(self.licence_number.get())
            is_interval_days_valid = self.validate_interval(self.interval_day.get())
            try:
                if is_test_location_valid and is_licence_expiry_valid and is_licence_number_valid and is_interval_days_valid:

                    candidate = DriveTestCandidate()
                    candidate.licence_number = self.licence_number.get()
                    candidate.licence_expiry = self.licence_expiry.get()
                    candidate.location = self.test_location.get()
                    candidate.interval_day = int(self.interval_day.get())
                    candidate.road_test_class = self.road_test_class.get()
                    if self.action_type.get() == "New":
                        candidate.driver_type = "NEW_TEST"
                    else:
                        candidate.driver_type = "RESCHEDULE"

                    confirm = messagebox.askquestion("Confirmation",
                                           "Are you sure to booking with these information:\n\n{}{}{}{}".format(
                                               ("\nTest Center : "+candidate.location),
                                               ("\nLicence Number : "+str(candidate.licence_number)),
                                               ("\nLicence Expiry : "+ str(candidate.licence_expiry)),
                                               ("\nInterval Days : "+ str(candidate.interval_day))))
                    if confirm == "yes":
                        print("call booking thread")
                        thread = scraping_thread(candidate=candidate, driver_type= self.driver_type.get(), blls_queue=blls)
                        self.threads.append(thread)
                        thread.start()
                        print("all alive threads:", len(self.threads))
                        time.sleep(5)
                else:
                    messagebox.showwarning("Validation", "Please fill in all required fields\n with valid data: \n{}{}{}{}".format( ("\nTest Center" if not is_test_location_valid else ""),
                                                                                                         ("\nLicence Number" if not is_licence_number_valid else ""),
                                                                                                             ("\nLicence Expiry" if not is_licence_expiry_valid else ""),
                                                                                                             ("\nInterval Days" if not is_interval_days_valid else "")))
            except BaseException as be:
                log_description = be
                TkinterWindowApp.technical_logger.error(log_description)

    def main(self):

        frame = Frame(self.root)
        frame.pack()
        self.test_location = AutocompleteCombobox(frame)
        self.test_location.set_completion_list(self.params)
        self.test_location.set('Select Test Center')
        self.test_location.pack(padx=10, pady=10)

        # register a validation command
        self.licence_number = AutocompleteEntry(frame, placeholder="Licence Number", width=23, relief='sunken')
        self.licence_number.pack(padx=10, pady=10)

        self.licence_expiry = AutocompleteEntry(frame, placeholder="Licence Expiry Date", width=23, relief='sunken')
        self.licence_expiry.pack(padx=5, pady=5)

        self.interval_day = EntryWithPlaceholder(frame, placeholder="Interval Days", width=23, relief='sunken')
        self.interval_day.pack(padx=5, pady=5)

        self.driver_type = ttk.Combobox(frame, state="readonly", values=("Chrome", "Opera", "Firefox", "Edge", "Edge_Legacy"))
        self.driver_type.set("Chrome")
        self.driver_type.pack(padx=10, pady=10)

        leftframe = Frame(frame)
        leftframe.pack(side=LEFT)

        rightframe = Frame(frame)
        rightframe.pack(side=RIGHT)

        self.road_test_class = StringVar(None, "G")
        RBttn_G = Radiobutton(leftframe, text="  G", variable=self.road_test_class,
        value = 'G', justify = 'left')
        RBttn_G.pack(padx=5, pady=5)
        RBttn_G2 = Radiobutton(leftframe, text="G2", variable=self.road_test_class,
        value = 'G2', justify = 'left')
        RBttn_G2.pack(padx=5, pady=5)

        self.action_type = StringVar(None, "New")
        rbttn_new = Radiobutton(rightframe, text="New", variable=self.action_type,
        value = 'New', justify = 'right')
        rbttn_new.pack(padx=5, pady=5)
        rbttn_reschedule = Radiobutton(rightframe, text="Reschedule", variable=self.action_type,
        value = 'Reschedule', justify = 'right')
        rbttn_reschedule.pack(padx=5, pady=5)



        btn_right_frame = Frame(self.root)
        btn_right_frame.pack(side=RIGHT)

        btn_left_frame = Frame(self.root)
        btn_left_frame.pack(side=LEFT)

        button = Button(btn_left_frame, text="Booking", command=self.call_booking, width=15)
        button.pack(padx=5, pady=30)

        button = Button(btn_right_frame, text="Close All", command=self.terminate_all_driver, width=15)
        button.pack(padx=5, pady=30)

    def run(self):

        self.main()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()




