import pandas as pd
import numpy as np
import requests
import sqlite3
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float

excelPodatci = ("./data.xls")

csvPodatci = "kvaliteta_zraka_zagreb_2025.csv"

tablicaZaCSV = []

for i in range (8):
  df = pd.read_excel(excelPodatci, sheet_name=i)

  df = df[7:]

  df.columns = ['Datum', 'Vrijeme', 'Vrijednost']

  df['Vrijednost'] = df['Vrijednost'].astype(str).str.replace(',', '.')
  df = df.replace('-', np.nan)

  df['Vrijednost'] = df['Vrijednost'].astype(float)
  df['Datum'] = pd.to_datetime(df['Datum'], dayfirst=True)

  if i == 0 or i == 1:
   postaja = "ZAGREB-1"

  elif i == 2 or i == 3:
      postaja = "ZAGREB-2"
  elif i == 4 or i == 5:
     postaja = "ZAGREB-3"
  else:
    postaja = "ZAGREB-4"

  if i % 2 == 0:
     čestica = "PM10"
  else:
    čestica = "PM2.5"

  df['Postaja'] = postaja
  df['Čestica'] = čestica

  tablicaZaCSV.append(df)

  df_final = pd.concat(tablicaZaCSV, ignore_index=True)
  df_final.to_csv("kvaliteta_zraka_zagreb_2025.csv", index=False, sep=';')

df = pd.read_csv("./kvaliteta_zraka_zagreb_2025.csv", sep=";"); 

#.............................................................
engine = create_engine('sqlite:///baza_podataka.db')

metadata = MetaData()

users = Table('mjerenja_2025', metadata,
    Column('id', Integer, primary_key=True),
    Column('postaja', String),
    Column('cestica', String),
    Column('vrijednost', Float),
    Column('datum', String),
    Column('vrijeme', String),
)

metadata.create_all(engine)

df.columns = ["datum", "vrijeme", "vrijednost", "postaja", "cestica"]
df.to_sql("mjerenja_2025", engine, if_exists="append", index=False)
print("CSV uspješno spremljen u bazu!")

sql_upit = """
SELECT 
    datum, 
    UPPER(postaja) as postaja, 
    UPPER(cestica) as cestica, 
    ROUND(AVG(vrijednost), 2) as avg, 
    ROUND(MAX(vrijednost), 2) as max
FROM mjerenja_2025
GROUP BY datum, postaja, cestica
"""

df_prosjeci_max = pd.read_sql(sql_upit, engine)
df_prosjeci_max.to_sql("mjerenja_dnevni_prosjeci_2025", engine, if_exists="replace", index=False)
print("Nova tablica 'mjerenja_dnevni_prosjeci_2025' je kreirana u bazi!")

#.............................................................
token = '6fc5181bcb70fba76fabae90f5f3ee05ce2d6c0e'
api_url = 'https://api.waqi.info/feed'

postaje_id = [
    'croatia/zagreb-1',
    'croatia/zagreb-2',
    'croatia/zagreb-3',
    'A470719'
]

svi_podaci = []

for station in postaje_id:
    url = f"{api_url}/{station}/?token={token}"
    
    response = requests.get(url)
    json_data = response.json()
    
    if json_data["status"] != "ok":
        print(f"Greška pri dohvaćanju postaje {station}")
        continue

    data = json_data["data"]


    postaja_ime = data["city"]["name"].split(",")[0].strip().upper()
    datum = data["time"]["s"].split(" ")[0]
    

    dnevno_mjerenje = data.get("forecast", {}).get("daily", {})
    iaqi_podaci = data.get("iaqi", {})

    cestice = ["pm10", "pm25"]
    
    for cestica in cestice:

        if cestica in dnevno_mjerenje:
            danasnja = next((item for item in dnevno_mjerenje[cestica] if item["day"] == datum), None)
            if danasnja:
                svi_podaci.append({
                    "datum": datum,
                    "postaja": postaja_ime,
                    "cestica": cestica.upper(),
                    "avg_danas": danasnja["avg"],
                    "max_danas": danasnja["max"],
                })
        
        elif cestica in iaqi_podaci:
            vrijednost = iaqi_podaci[cestica].get("v")
            if vrijednost is not None:
                svi_podaci.append({
                    "datum": datum,
                    "postaja": postaja_ime,
                    "cestica": cestica.upper(),
                    "avg_danas": vrijednost,
                    "max_danas": vrijednost,
                })

df_danas = pd.DataFrame(svi_podaci)
df_danas.to_sql("mjerenja_2026_api", engine, if_exists="replace", index=False)
print("Nova tablica 'mjerenja_2026_api' je kreirana u bazi!")

#.............................................................
app = Flask(__name__)

@app.route("/", methods=["GET"])
def pocetna():
    return """
    <h1>Koncentracija lebdećih čestica PM10 i PM2.5 u Zagrebu</h1>
    <h2>Dostupne putanje</h2>
    <ul>
        <li><a href="/mjerenja_sijecanj_2025">/mjerenja_sijecanj_2025</a> – vraća sva mjerenja za siječanj 2025.</li>
        <li><a href="/zagreb1_2025">/zagreb1_2025</a> – vraća sva mjerenja za postaju ZAGREB-1 u 2025.</li>
        <li><a href="/dnevni_prosjeci_2025">/dnevni_prosjeci_2025</a> – vraća dnevne prosječne vrijednosti za sve postaje i čestice u 2025.</li>
        <li><a href="/mjerenje_danas">/mjerenje_danas</a> – vraća današnja mjerenja za sve postaje iz API-ja.</li>
    </ul>
    """

@app.route("/mjerenja_sijecanj_2025", methods=["GET"])
def mjerenja_sijecanj_2025a():
    df = pd.read_sql("SELECT * FROM mjerenja_2025 WHERE datum LIKE '2025-01%'", engine)
    return jsonify(df.to_dict(orient="records"))

@app.route("/zagreb1_2025", methods=["GET"])
def mjerenja_zagreb1_2025():
    df = pd.read_sql("SELECT * FROM mjerenja_2025 WHERE postaja='ZAGREB-1'", engine)
    return jsonify(df.to_dict(orient="records"))

@app.route("/dnevni_prosjeci_2025", methods=["GET"])
def dnevni_prosjeci_2025():
    df = pd.read_sql("SELECT * FROM mjerenja_dnevni_prosjeci_2025", engine)
    return jsonify(df.to_dict(orient="records"))

@app.route("/mjerenje_danas", methods=["GET"])
def mjerenje_danas():
    return jsonify(df_danas.to_dict(orient="records"))

@app.errorhandler(404)
def stranica_ne_postoji(error):
    return """
    <h2>Stranica ne postoji (404)</h2>
    <p>Pogrešan URL.</p> 
    <li><a href="/">Početna stranica</a> – popis svih putanja</li>
    """
if __name__ == "__main__":
    app.run(debug=True)
    
