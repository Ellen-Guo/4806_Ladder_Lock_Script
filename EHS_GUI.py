import requests
import sys
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, \
    QComboBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView

EHS_url = 'https://www.ehss.vt.edu/programs/ROOF_access_chart_050916.php'


class EHSWindow(QMainWindow):  # EHS GUI Class

    # class constructor
    def __init__(self):
        super().__init__()
        self.title = "EHS Safety Application"
        self.setWindowTitle(self.title)
        self.home()

    # EHS GUI main app page **** Building Selection ****
    def home(self):
        # instantiation
        widget = QWidget()
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        # widget objects
        self.prompt = QLabel("Which building's health and safety information do you want?")  # label above the combobox
        self.button = QPushButton('OK')  # button
        self.combo = QComboBox()
        # add building names to the dropdown menu
        buildings = build_list()
        for i in buildings:
            self.combo.addItem(i)
        # ********* GUI Homepage Layout **********
        # _________________________________
        # |         |           |          |
        # |_________|___________|__________|
        # |          [Prompt]              |
        # |__________[ComboBox]____________|
        # |         |           |          |
        # |         |           |          |
        # |_________|___________|_[Button]_|
        vbox.addStretch(2)
        vbox.addWidget(self.prompt)
        vbox.addWidget(self.combo)
        vbox.addStretch(2)
        hbox.addStretch(2)
        hbox.addWidget(self.button)
        vbox.addLayout(hbox)
        # set widget layout
        widget.setLayout(vbox)
        self.setCentralWidget(widget)
        self.button.clicked.connect(self.on_click)

    def on_click(self):
        self.clear()
        widget = QWidget()
        vbox = QVBoxLayout()
        soup = query()
        content = soup.find("div", {"class": "content-block"}).findAll("tr")
        building_list = build_list()
        building = self.combo.currentText()
        ind = building_list.index(building)  # get index of list
        types = hazard_type()
        hazards = []
        c = len(content[0].findAll("td"))
        for j in range(c-1):  # scrap hazard information from table on EHS website
            hazards.append(content[ind + 1].findAll("td")[j+1].getText().replace('\n', ' '))
        self.building_name = QLabel(building + " EHS Hazard Information: ")  # QLabel Widget
        self.table = QTableWidget()  # QTableWidget
        # Row & Column Count for Qt Table
        self.table.setRowCount(2)
        self.table.setColumnCount(5)
        # Place parsed information into table
        for i in range(c-1):
            self.table.setItem(0, i, QTableWidgetItem(types[i]))
            self.table.setItem(1, i, QTableWidgetItem(hazards[i]))
        # delete header numbers & Fit Screen Horizontally
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # ********* GUI Info Page Layout **********
        # _________________________________
        # |         |           |          |
        # |_________|___________|__________|
        # |          [Building]            |
        # |_________[Information]__________|
        # |         |           |          |
        # |_________|___________|__________|
        vbox.addStretch(2)
        vbox.addWidget(self.building_name)
        vbox.addWidget(self.table)
        vbox.addStretch(2)
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

    # clear widgets from layout
    def clear(self):
        self.button.setParent(None)
        self.prompt.setParent(None)
        self.combo.setParent(None)


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


# Parse hazard types as show on table
def hazard_type():
    soup = query()
    content = soup.find("div", {"class": "content-block"}).findAll("tr")
    c = len(content[0].findAll("td"))
    types = []
    for i in range(c-1):
        types.append(content[0].findAll("td")[i+1].getText().replace('\n', ' '))
    return types


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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
