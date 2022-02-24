import requests
import numpy as np
from bs4 import BeautifulSoup

EHS_url = 'https://www.ehss.vt.edu/programs/ROOF_access_chart_050916.php'

def main():
    r = requests.get(url=EHS_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    last_update_date = soup.find("div", {"class": "content-block"}).find("caption").getText(). \
        replace('\r\n                    ', '')  # obtain caption element; remove extra space in the caption element tag
    print(last_update_date)
    content = soup.find("div", {"class": "content-block"}).findAll("tr")  # obtain rows of the hazard table
    r = len(content)
    columns = content[0].findAll("td")
    c = len(columns)
    table_content = np.zeros((r, c))
    for i in range(r):
        for j in range(c):
            labels = content[i].findAll("td")[j].getText().replace('\n', ' ')
            table_content[i, j] = labels
            print("hello")
    # print(labels)
    # print("hello")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
