import sys
import optparse
import logging, traceback

from PyQt5.QtWidgets import QApplication
from youtube_dl.compat import compat_get_terminal_size

columns = compat_get_terminal_size().columns # you could call this 'hipity hopity this is now my property'
max_width = columns if columns else 80
max_help_position = 80
fmt = optparse.IndentedHelpFormatter(width=max_width, max_help_position=max_help_position)

kw = {
    'formatter': fmt,
    'usage': '%prog [OPTIONS]',
    'conflict_handler': 'resolve'
}

parser = optparse.OptionParser(**kw)
parser.add_option('-h', '--help',
                  action='help',
                  help='Print this help message and exit')
parser.add_option('-u', '--username',
                  type=str,
                  help='Email for Tassomai',
                  default='')
parser.add_option('-p', '--password',
                  type=str,
                  help='Tassomai Password',
                  default='')
parser.add_option('--no-stats',
                  action='store_true',
                  help='Do not show the stats when finished.',
                  default=False)
parser.add_option('--close',
                  action='store_true',
                  help='Close when finished.',
                  default=False)
parser.add_option('--max-quizes',
                  metavar='NUMBER',
                  type=int,
                  help='Maximum number of quizes to do',
                  default=1000)
parser.add_option('--start',
                  action='store_true',
                  help='Automatically start the automation',
                  default=False)
parser.add_option('--gui-frameless',
                  action='store_true',
                  help='Make the GUI hidden but still runs in the background.',
                  default=False)
parser.add_option('--frameless',
                  action='store_true',
                  help='Start Chrome frameless (you will not see the window, but will still run in the background)',
                  default=False)
parser.add_option('--no-daily',
                  action='store_true',
                  help='Do not finish when daily goal is complete.',
                  default=False)
parser.add_option('--bonus',
                  action='store_true',
                  help='Finish when bonus goal is complete.',
                  default=False)

(options, args) = parser.parse_args()

if __name__ == '__main__':
    try:
        from gui import Window

        app = QApplication(sys.argv)

        win = Window(show_stats=not options.no_stats, close=options.close)

        if options.frameless:
            win.ui.framelessFirefox.setChecked(True)
        if not options.gui_frameless:
            win.show()
        if options.username != '':
            win.ui.emailTassomai.setText(options.username)
        if options.password != '':
            win.ui.passwordTassomai.setText(options.password)
        if options.no_daily:
            win.ui.dailyGoal.setChecked(False)
        if options.bonus:
            win.ui.bonusGoal.setChecked(True)

        win.ui.maxQuizes.setValue(abs(options.max_quizes))

        if options.start:
            win.ui.startButton.click()

        sys.exit(app.exec())
    except Exception as e:
        if not traceback.format_exc().__contains__('SystemExit'):
            logging.error(traceback.format_exc())