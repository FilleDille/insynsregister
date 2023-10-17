import requests as rq
from dataclasses import dataclass
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import smtplib
import os
import sys


load_dotenv()
if sys.platform == "darwin":
    current_subdir: str = os.getenv('MAC')
else:
    current_subdir: str = os.getenv('LINUX')


@dataclass
class RowData:
    pub_date: str
    emittent: str
    person_ledande_stallning: str
    befattning: str
    narstaende: str
    karaktar: str
    instrumentnamn: str
    instrumenttyp: str
    isin: str
    transaktionsdatum: str
    volym: int
    volymsenhet: str
    pris: float
    valuta: str
    status: str
    detaljer: str


def main():
    url = 'https://marknadssok.fi.se/Publiceringsklient/sv-SE/Search/Search?SearchFunctionType=Insyn&Utgivare=Cereno+Scientific&PersonILedandeSt%C3%A4llningNamn=&Transaktionsdatum.From=&Transaktionsdatum.To=&Publiceringsdatum.From=&Publiceringsdatum.To=&button=search&Page=1'
    response_raw = rq.get(url)
    html = response_raw.text

    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('table.table tbody tr')

    data_list = []

    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 16:
            pub_date, emittent, person_ledande_stallning, befattning, narstaende, karaktar, \
                instrumentnamn, instrumenttyp, isin, transaktionsdatum, volym, volymsenhet, \
                pris, valuta, status, detaljer = [col.text.strip() for col in columns]

            data = RowData(pub_date, emittent, person_ledande_stallning, befattning.replace('\xa0', ' '), narstaende, karaktar,
                           instrumentnamn, instrumenttyp, isin, transaktionsdatum, volym.replace('\xa0', ' '), volymsenhet, pris, valuta,
                           status, detaljer)

            data_list.append(data)

    existing_data = []
    current_dir: str = os.path.expanduser('~') + current_subdir

    try:
        with open(current_dir + 'senaste_listan.json', 'r') as json_file:
            existing_data = [RowData(**row_data) for row_data in json.load(json_file)]
    except FileNotFoundError:
        pass

    new_data = [data for data in data_list if data not in existing_data]

    if new_data:
        send_email(new_data)

    with open(current_dir + 'senaste_listan.json', 'w') as json_file:
        json.dump([vars(data) for data in data_list], json_file, indent=4)


def send_email(new_data):
    email: str = os.getenv('EMAIL')
    cc: str = os.getenv('CC')
    app_pw: str = os.getenv('APP_PW')

    message = ('Subject: Ändringar i insynsregistret för Cereno Scientific\n\nFöljande har skett: {}'
               .format(new_data).encode('utf-8'))

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(email, app_pw)
        s.sendmail(email, [email, cc], message)
        s.quit()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()

