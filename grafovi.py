import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import seaborn as sns
from sqlalchemy import create_engine
from datetime import datetime


baza = sqlite3.connect('baza_podataka.db')
df = pd.read_sql_query("SELECT * FROM mjerenja_dnevni_prosjeci_2025", baza)

df['datum'] = pd.to_datetime(df['datum'])
df = df.sort_values('datum')

postaje = ['ZAGREB-1', 'ZAGREB-2', 'ZAGREB-3', 'ZAGREB-4']
cestice = ['PM10', 'PM2.5']


for cestica in cestice:
    for postaja in postaje:
        datum_proljece = '2025-03-21'  
        datum_ljeto = '2025-06-21'
        datum_jesen = '2025-09-21'
        datum_zima = '2025-12-21'

        podaci = df[(df['postaja'] == postaja) & (df['cestica'] == cestica)]

        plt.figure(figsize=(20, 5))


        plt.plot(podaci['datum'], podaci['avg'], label=postaja)

        plt.axvline(x=pd.to_datetime(datum_proljece), color='green', linestyle='--', linewidth=2, label='Početak proljeća')
        plt.axvline(x=pd.to_datetime(datum_ljeto), color='orange', linestyle='--', linewidth=2, label='Početak ljeta')
        plt.axvline(x=pd.to_datetime(datum_jesen), color='brown', linestyle='--', linewidth=2, label='Početak jeseni')
        plt.axvline(x=pd.to_datetime(datum_zima), color='blue', linestyle='--', linewidth=2, label='Početak zime')

        plt.title(f'Kvaliteta zraka u 2025: {postaja} {cestica}')
        plt.ylabel('Vrijednost (ug/m3)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        ime_slike = f'{postaja}_{cestica}.png'
        plt.savefig(ime_slike)
        print(f"Spremljen {ime_slike}")

#.............................................................
danas = datetime.now()
datum_2025 = danas.replace(year=2025).strftime('%Y-%m-%d')

df_danas = pd.read_sql_query("SELECT * FROM mjerenja_2026_api", baza)
df_danas['cestica'] = df_danas['cestica'].replace('PM25', 'PM2.5')

upit_2025 = f"""
    SELECT postaja, cestica, avg as avg_2025 
    FROM mjerenja_dnevni_prosjeci_2025 
    WHERE datum LIKE '{datum_2025}%'
"""

df_2025 = pd.read_sql_query(upit_2025, baza)

tablica = pd.merge(df_danas, df_2025, on=['postaja', 'cestica'])

podaci_pm10 = tablica[tablica['cestica'] == 'PM10']

plt.figure()
pm10 = range(len(podaci_pm10))

plt.bar(pm10, podaci_pm10['avg_2025'], label='2025.', color='gray', alpha=0.6)
plt.bar(pm10, podaci_pm10['avg_danas'], label='2026.', color='blue', alpha=0.6)

plt.xticks(pm10, podaci_pm10['postaja'])
plt.title("Usporedba PM10")
plt.legend()
ime_slike = "USPOREDBA DANAS I 2025_PM10.png"
plt.savefig(ime_slike)
print(f"Spremljen {ime_slike}")



podaci_pm25 = tablica[tablica['cestica'] == 'PM2.5']

plt.figure()
pm25 = range(len(podaci_pm25))

plt.bar(pm25, podaci_pm25['avg_2025'], label='2025.', color='gray', alpha=0.6)
plt.bar(pm25, podaci_pm25['avg_danas'], label='2026.', color='red', alpha=0.6)
plt.xticks(pm25, podaci_pm25['postaja'])
plt.title("Usporedba PM2.5")
plt.legend()
ime_slike = "USPOREDBA DANAS I 2025_PM25.png"
plt.savefig(ime_slike)
print(f"Spremljen {ime_slike}")
