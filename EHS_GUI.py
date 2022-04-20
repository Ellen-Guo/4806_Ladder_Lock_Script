import requests
import sys
import socket
from psygnal import Signal
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, \
    QComboBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QScrollArea, \
    QFormLayout, QAbstractItemView
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QThread, QCoreApplication, QObject

client_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
valid = False
EHS_url = 'https://www.ehss.vt.edu/programs/ROOF_access_chart_050916.php'

# 2 hatch status colors
Red = 'rgb(255, 0, 0)'
Green = 'rgb(0, 153, 0)'
# 5 Primary VT Colors
Burnt_orange = 'rgb(232, 119, 34)'
Burnt_orange_web = 'rgb(198, 70, 0)'
Chicago_maroon = 'rgb(134, 31, 65)'
Yardline_white = 'rgb(255, 255, 255)'
Hokie_stone = 'rgb(117, 120, 123)'
Black = 'rgb(0, 0, 0)'


class EHSWindow(QMainWindow):  # EHS GUI Class
    # Main Window Class Constructor
    def __init__(self):
        super().__init__()
        # self.title = "EHS Safety Application"
        self.title = "Pad & Swipe EHS Application"
        self.setWindowTitle(self.title)
        # Evoke main EHS GUI code
        self.home()
        # Evoke background lock status update thread
        self.lock_update()

    # EHS GUI main app page **** Building Selection ****
    def home(self):
        self.show_vt()  # VT Logo Qt Label Widget
        self.lock_stat()  # Lock status Qt Label Widget
        # widget objects
        self.prompt = QLabel("Select Building Name: ")  # label above the combobox
        self.button = QPushButton('OK')  # button
        self.combo = QComboBox()
        # add building names to the dropdown menu
        buildings = build_list()
        for i in buildings:
            self.combo.addItem(i)
        # ********* Setting Color ***************
        self.prompt.setStyleSheet("QLabel {color: %s; font-size: 12pt}" % Chicago_maroon)
        self.button.setStyleSheet("QPushButton {color: %s; font-size: 12pt}" % Chicago_maroon)
        self.combo.setStyleSheet("""QComboBox {
        selection-background-color: %s; 
        selection-color: %s;
        font-size: 12pt}""" % (Burnt_orange, Yardline_white))
        # ********* GUI Homepage Layout **********
        self.home_screen()

    def on_click(self):
        self.clear_home()  # Clear home screen
        widget = QWidget()
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox1 = QHBoxLayout()
        soup = query()
        # Scrollbox layout
        form_layout = QFormLayout()
        self.group_box = QGroupBox()
        self.scroll = QScrollArea()
        self.button = QPushButton('Quit')
        content = soup.find("div", {"class": "content-block"}).findAll("tr")
        building_list = build_list()
        building = self.combo.currentText()
        ind = building_list.index(building)  # get index of list
        types = hazard_type()
        hazards = []
        c = len(content[0].findAll("td"))
        for j in range(c-1):  # scrap hazard information from table on EHS website
            hazards.append(content[ind + 1].findAll("td")[j+1].getText().replace('\n', ' '))
        # Health & Safety Legend Info from bottom of table
        building_info, hazard_leg = hazard_legend()
        legend_list = []
        # Building Specific Hazards
        if building in building_info:
            legend_list.append(QLabel(building_info.get(building)))
        # Standard Hazards QLabel Creation
        for k in range(len(hazards)):
            if (hazards[k] != 'N/A') & (hazards[k] != 'No') & (hazards[k] != '\xa0'):
                if k == 0:  # Chemical Hazard
                    legend_list.append(QLabel(hazard_leg.get(types[k].split(" ")[0])))
                    if (hazards[k].split("*")[0] == " Restricted") | (hazards[k] == "Restricted"):
                        legend_list.append(QLabel('\t• ' + hazard_leg.get("Restricted Access")))
                    elif (hazards[k].split("*")[0] == " Unrestricted") | (hazards[k] == "Unrestricted"):
                        legend_list.append(QLabel('\t• ' + hazard_leg.get("Unrestricted")))
                if k == 1:  # Biological Hazard
                    legend_list.append(QLabel(hazard_leg.get("Biological")))
                if k == 2:  # Radio Frequency Hazard
                    legend_list.append(QLabel(hazard_leg.get("Radio Frequency")))
                if k == 3:  # Noise Hazard
                    legend_list.append(QLabel(hazard_leg.get(types[k].split(" ")[0])))
                    if hazards[k] == 'Siren':
                        legend_list.append(QLabel('\t• ' + hazard_leg.get(hazards[k]+'s')))
                    else:
                        legend_list.append(QLabel('\t• ' + hazard_leg.get(hazards[k])))
                if k == 4:  # Fall Hazard
                    legend_list.append(QLabel(hazard_leg.get("Fall Hazards")))
                    if hazards[k].find("&") != -1:
                        fall_haz = hazards[k].replace(' ', '').split("&")
                        for j in fall_haz:
                            legend_list.append(QLabel('\t• ' + hazard_leg.get(j)))
                    elif hazards[k].find("and") != -1:
                        fall_haz = hazards[k].replace(' ', '').split("and")
                        for j in fall_haz:
                            legend_list.append(QLabel('\t• ' + hazard_leg.get(j)))
                    elif (hazards[k].find("or") != -1) & (hazards[k].find(",") != -1):
                        fall_haz = hazards[k].replace("or ", '').split(",")
                        for j in fall_haz:
                            legend_list.append(QLabel('\t• ' + hazard_leg.get(j)))
                    elif hazards[k].find("or") != -1:
                        fall_haz = hazards[k].replace(' ', '').split("or")
                        for j in fall_haz:
                            legend_list.append(QLabel('\t• ' + hazard_leg.get(j)))
                    elif hazards[k].find(",") != -1:
                        fall_haz = hazards[k].replace(' ', '').split(",")
                        for j in fall_haz:
                            legend_list.append(QLabel('\t• ' + hazard_leg.get(j)))
                    else:
                        legend_list.append(QLabel('\t• ' + hazard_leg.get(hazards[k])))
        # QScrollArea for better viewing of legend information
        for n in legend_list:
            n.setFont(QFont('Times'))
            n.setStyleSheet("QLabel {color: %s; font-size: 12pt}" % Yardline_white)
            form_layout.addRow(n)
        self.group_box.setLayout(form_layout)
        self.scroll.setWidget(self.group_box)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(200)
        # QLabel Widgets
        self.building_name = QLabel(building + " EHS Hazard Information: ")
        self.leg = QLabel("Additional Legend Information: ")
        self.table = QTableWidget()  # QTableWidget
        # Row & Column Count for Qt Table
        self.table.setRowCount(2)
        self.table.setColumnCount(5)
        self.table.setFixedHeight(124)
        # Place parsed information into table
        for i in range(c-1):
            self.table.setItem(0, i, QTableWidgetItem(types[i]))
            self.table.setItem(1, i, QTableWidgetItem(hazards[i]))
        # delete header numbers & Fit Screen Horizontally
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # ********* Setting Color ***************
        self.building_name.setStyleSheet("QLabel {color: %s; font-size: 12pt}" % Burnt_orange_web)
        self.leg.setStyleSheet("QLabel {color: %s; font-size: 12pt}" % Burnt_orange_web)
        self.button.setStyleSheet("QPushButton {color: %s; font-size: 12pt}" % Burnt_orange_web)
        self.table.setStyleSheet("""QTableWidget {
        background-color: %s;
        color: %s; 
        font-size: 12pt}""" % (Chicago_maroon, Yardline_white))
        self.group_box.setStyleSheet("""QGroupBox {
        background-color: %s; 
        color: %s}""" % (Chicago_maroon, Yardline_white))
        # ********* GUI Info Page Layout **********
        # _________________________________
        # |         | [VT Logo] |          |
        # |_________|___________|__________|
        # |          [Building]            |
        # |______[Table Information]_______|
        # |      [Legend Information]      |
        # |[Lock][Hatch]________|__[QUIT]__|
        hbox.addStretch(2)
        hbox.addWidget(self.image_label)
        hbox.addStretch(2)
        vbox.addLayout(hbox)
        vbox.addStretch(2)
        vbox.addWidget(self.building_name)
        vbox.addWidget(self.table)
        vbox.addWidget(self.leg)
        vbox.addWidget(self.scroll)
        vbox.addStretch(2)
        hbox1.addWidget(self.c_lock_stat)
        hbox1.addWidget(self.c_lock_word)
        hbox1.addStretch(2)
        hbox1.addWidget(self.button)
        vbox.addLayout(hbox1)
        # set widget layout
        widget.setLayout(vbox)
        self.setCentralWidget(widget)
        self.button.clicked.connect(self.return_home)

    # refresher homepage
    def return_home(self):
        self.clear_click()
        # widget objects
        self.prompt = QLabel("Select Building Name: ")  # label above the combobox
        self.button = QPushButton('OK')  # button
        self.combo = QComboBox()
        # add building names to the dropdown menu
        buildings = build_list()
        for i in buildings:
            self.combo.addItem(i)
        # ********* Setting Color ***************
        self.prompt.setStyleSheet("QLabel {color: %s; font-size: 12pt}" % Chicago_maroon)
        self.button.setStyleSheet("QPushButton {color: %s; font-size: 12pt}" % Chicago_maroon)
        self.combo.setStyleSheet("""QComboBox {
        selection-background-color: %s; 
        selection-color: %s;
        font-size: 12pt}""" % (Burnt_orange, Yardline_white))
        # ********* GUI Homepage Layout **********
        self.home_screen()

    def home_screen(self):
        # instantiation
        widget = QWidget()
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox1 = QHBoxLayout()
        # ********* GUI Homepage Layout **********
        # _________________________________
        # |         | [VT Logo] |          |
        # |_________|___________|__________|
        # |          [Prompt]              |
        # |__________[ComboBox]____________|
        # |         |           |          |
        # |         |           |          |
        # |[Lock][Hatch]________|_[Button]_|
        hbox.addStretch(2)
        hbox.addWidget(self.image_label)
        hbox.addStretch(2)
        vbox.addLayout(hbox)
        vbox.addStretch(2)
        vbox.addWidget(self.prompt)
        vbox.addWidget(self.combo)
        vbox.addStretch(2)
        hbox1.addWidget(self.c_lock_stat)
        hbox1.addWidget(self.c_lock_word)
        hbox1.addStretch(2)
        hbox1.addWidget(self.button)
        vbox.addLayout(hbox1)
        # set widget layout
        widget.setLayout(vbox)
        self.setCentralWidget(widget)
        self.button.clicked.connect(self.on_click)

    # clear widgets from home layout
    def clear_home(self):
        self.button.setParent(None)
        self.prompt.setParent(None)
        self.combo.setParent(None)

    # clear widgets from Building_info page
    def clear_click(self):
        self.button.setParent(None)
        self.table.setParent(None)
        self.group_box.setParent(None)
        self.scroll.setParent(None)
        self.building_name.setParent(None)
        self.leg.setParent(None)

    # VT Logo
    def show_vt(self):
        image_path = ('VT_logo.png')
        self.image_label = QLabel()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)

    # ------------------------ LOCK STATUS FUNCTIONS --------------------------
    # lock status items **** Loading of images
    def lock_stat(self):
        locked = ('locked.png')
        unlocked = ('unlocked.png')
        self.c_lock_stat = QLabel()
        self.plock = QPixmap(locked).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.punlock = QPixmap(unlocked).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.c_lock_stat.setPixmap(self.plock)
        # lock QLabel item
        self.c_lock_word = QLabel("LOCKED")
        self.c_lock_word.setStyleSheet("QLabel {color: %s; font-weight: bold; font-size: 15pt}" % Red)

    # Instantiate background running QThread for lock update
    def lock_update(self):
        QCoreApplication.processEvents()
        self.thread = QThread()
        self.worker = LockThread()
        self.worker.moveToThread(self.thread)
        # connect signal with pad lock updating function
        self.worker.signals.update_lock.connect(self.lock_status)

    # update pad lock icon based on signal emitted | [0] lock & [1] unlock
    def lock_status(self, stat):
        if stat:
            self.c_lock_stat.setPixmap(self.punlock)
            self.c_lock_word.setText("UNLOCKED")
            self.c_lock_word.setStyleSheet("QLabel {color: %s; font-weight: bold; font-size: 15pt}" % Green)
        else:
            self.c_lock_stat.setPixmap(self.plock)
            self.c_lock_word.setText("LOCKED")
            self.c_lock_word.setStyleSheet("QLabel {color: %s; font-weight: bold; font-size: 15pt}" % Red)



# All signals must inherit from QObject class
class Communicate(QObject):
    update_lock = Signal(bool)

# Lock Update Thread Worker class
class LockThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self)
        self.signals = Communicate()
        self.start()

    # Infinite lock status background checking loop
    def run(self):
        curr_lock_status = False
        while True:
            message = client_server.recv(1024).decode()
            if len(message) != 0:
                # Lock status update signal
                if curr_lock_status != bool(int(message)):
                    curr_lock_status = bool(int(message))
                    self.signals.update_lock.emit(curr_lock_status)


# query EHS website for content
def query():
    r = requests.get(url=EHS_url)
    return BeautifulSoup(r.content, 'html.parser')


# scrap website content and gather all the building names
def build_list():
    soup = query()
    content = soup.find("div", {"class": "content-block"}).findAll("tr")  # obtain rows of the hazard table
    r = len(content)
    building_name = []
    for i in range(r-1):
        building_name.append(content[i+1].find("td").getText())  # Scrap all the building names into a list
    return building_name


# Parse hazard types as show on table header
def hazard_type():
    soup = query()
    content = soup.find("div", {"class": "content-block"}).findAll("tr")
    c = len(content[0].findAll("td"))
    types = []
    for i in range(c-1):
        types.append(content[0].findAll("td")[i+1].getText().replace('\n', ' '))
    return types


# Obtain hazard legend information below the table
def hazard_legend():
    soup = query()
    star_legend = []
    star_dic = {}
    stars = soup.find("div", {"class": "content-block"}).findAll("p")
    # Special building hazards indicated with stars
    for i in [-3, -2, -1]:
        star_legend.append(stars[i].getText())
    star_dic["Seitz Hall-upper roof (108)"] = star_legend[0]
    star_dic["Litton-Reaves Hall (118)"] = star_legend[1]
    star_dic["Randolph Hall (133)"] = star_legend[2]
    h4_legend = {}
    tags = soup.find("div", {"class": "content-block"}).findAll(["h4", "h4" and "ul" and "li"])
    # General Building Hazards Listed
    for i in range(len(tags)):
        text = tags[i].getText().replace('   ', ' ')
        if (i == 6) | (i == 7):  # Noise Hazard Parse
            parser_text = text.split("(")
            parser_text[0] = parser_text[0][1:len(parser_text[0])-1]
            text = text[1:-1]
        elif (i == 9) | (i == 12) | (i == 13) | (i == 16) | (i == 23):  # Fall Hazard Parse
            parser_text = text.split(" -")
        else:
            parser_text = text.split(":")
        if text.find("\n"):
            text = text.split("\n")[0]
        h4_legend[parser_text[0]] = text
    return star_dic, h4_legend


# Return last updated information of website
def date():
    soup = query()
    last_update_date = soup.find("div", {"class": "content-block"}).find("caption").getText(). \
        replace('\r\n                    ', '')  # obtain caption element; remove extra space in the caption element tag
    return last_update_date


def main():
    app = QApplication(sys.argv)
    win = EHSWindow()  # window object
    win.showFullScreen()  # Display GUI Full screen
    sys.exit(app.exec_())  # exit


# main code block
if __name__ == '__main__':
    # Command Line Initalization & Socket Connection
    if len(sys.argv) == 3:
        if (sys.argv[1] == '-sip'):
            server_ip = sys.argv[2]
            # TCP Socket Connection
            try:
                client_server.connect((server_ip, 1234))
            except socket.gaierror:
                print('Error: Invalid host name or port # [Program Termination]')
                sys.exit()
            except ConnectionRefusedError:
                print('Error: Unable to Connect [Program Termination]')
                sys.exit()
            except ValueError:
                print('Error: Expecting a value for port number [Program Termination]')
                sys.exit()
            print('Connected to Server....')
            main()  # main EHS GUI Qt Widget Fucntion
        else:
            print('Error: Invalid Entries')
            sys.exit()
    else:
            print('Error: Invalid Entries')
            sys.exit()
