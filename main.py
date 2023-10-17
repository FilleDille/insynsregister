import requests as rq
from dataclasses import dataclass
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import smtplib
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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

    table_html = '<table border="1"><thead><tr><th>Pub. Date</th><th>Emittent</th><th>Person Ledande Ställning</th>' \
                 '<th>Befattning</th><th>Närstående</th><th>Karaktär</th><th>Instrumentnamn</th><th>Instrumenttyp</th>' \
                 '<th>ISIN</th><th>Transaktionsdatum</th><th>Volym</th><th>Volymsenhet</th><th>Pris</th><th>Valuta</th>' \
                 '<th>Status</th><th>Detaljer</th></tr></thead><tbody>'

    for data in new_data:
        table_html += '<tr>'
        table_html += f'<td>{data.pub_date}</td>'
        table_html += f'<td>{data.emittent}</td>'
        table_html += f'<td>{data.person_ledande_stallning}</td>'
        table_html += f'<td>{data.befattning}</td>'
        table_html += f'<td>{data.narstaende}</td>'
        table_html += f'<td>{data.karaktar}</td>'
        table_html += f'<td>{data.instrumentnamn}</td>'
        table_html += f'<td>{data.instrumenttyp}</td>'
        table_html += f'<td>{data.isin}</td>'
        table_html += f'<td>{data.transaktionsdatum}</td>'
        table_html += f'<td>{data.volym}</td>'
        table_html += f'<td>{data.volymsenhet}</td>'
        table_html += f'<td>{data.pris}</td>'
        table_html += f'<td>{data.valuta}</td>'
        table_html += f'<td>{data.status}</td>'
        table_html += f'<td>{data.detaljer}</td>'
        table_html += '</tr>'

    table_html += '</tbody></table>'

    html_content = f'''
        <html>
            <body>
                <p>Följande har skett:</p>
                {table_html}
            </body>
        </html>
    '''

    subject = 'Ändringar i insynsregistret för Cereno Scientific'  # Set the subject here

    message = MIMEMultipart()
    message['Subject'] = subject
    message.attach(MIMEText(html_content, 'html'))

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(email, app_pw)
        s.sendmail(email, [email, cc], message.as_string())  # Convert the message to a string here
        s.quit()

    except Exception as e:
        print(e)



if __name__ == '__main__':
    main()

