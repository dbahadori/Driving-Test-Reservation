from DriveTest import main
from kivy import Config

from DriveTest.Utility import Alarm, FileManager
from DriveTest.WebScraper import WebScraper

Config.set('graphics', 'multisamples', '0')


#if __name__ == '__main__':
#    main.ConsoleApp.main(__name__)

if __name__ == '__main__':
    main.TkinterWindowApp().run()
