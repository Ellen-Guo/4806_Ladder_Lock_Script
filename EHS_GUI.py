import requests
import numpy as np
import sys
from bs4 import BeautifulSoup
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QScrollArea, QFormLayout, QGroupBox, \
    QVBoxLayout, QLabel, QCheckBox, QButtonGroup

EHS_url = 'https://www.ehss.vt.edu/programs/ROOF_access_chart_050916.php'


class EHSWindow(QMainWindow):  # EHS GUI Class

    def __init__(self):
        super().__init__()
        self.title = "EHS Safety Application"
        self.setWindowTitle(self.title)

        widget = QWidget()

        form_layout = QFormLayout()
        group_box = QGroupBox()

        label_list = []
        buildings = scrape()

        for i in range(len(buildings)):
            label_list.append(QCheckBox(buildings[i]))
            form_layout.addRow(label_list[i])

        group_box.setLayout(form_layout)
        scroll = QScrollArea()
        scroll.setWidget(group_box)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(400)

        layout = QVBoxLayout()
        layout.addWidget(scroll)

        widget.setLayout(layout)
        self.setCentralWidget(widget)


def scrape():
    r = requests.get(url=EHS_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    last_update_date = soup.find("div", {"class": "content-block"}).find("caption").getText(). \
        replace('\r\n                    ', '')  # obtain caption element; remove extra space in the caption element tag
    print(last_update_date)
    content = soup.find("div", {"class": "content-block"}).findAll("tr")  # obtain rows of the hazard table
    r = len(content)
    columns = content[0].findAll("td")
    building_name = []
    for i in range(r-1):
        building_name.append(content[i+1].find("td").getText())  # Scrap all the building names into a list
    print("hello")
    # for i in range(r):
    #     for j in range(c):
    #         labels = content[i].findAll("td")[j].getText().replace('\n', ' ')
    #         table_content[i, j] = labels
    #         print("hello")
    # print(labels)
    # print("hello")
    return building_name


def main():
    app = QApplication(sys.argv)
    win = EHSWindow()  # window object
    win.showFullScreen()  # Display GUI Full screen
    sys.exit(app.exec_())  # exit


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
