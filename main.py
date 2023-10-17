import requests as rq
from dataclasses import dataclass
from bs4 import BeautifulSoup
import json


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

    try:
        with open('senaste_listan.json', 'r') as json_file:
            existing_data = [RowData(**row_data) for row_data in json.load(json_file)]
    except FileNotFoundError:
        pass

    new_data = [data for data in data_list if data not in existing_data]

    if new_data:
        print("Ny data:")
        for data in new_data:
            print(data)

    save_to_json(data_list)


def save_to_json(data_list):
    with open('senaste_listan.json', 'w') as json_file:
        json.dump([vars(data) for data in data_list], json_file, indent=4)


if __name__ == '__main__':
    main()

