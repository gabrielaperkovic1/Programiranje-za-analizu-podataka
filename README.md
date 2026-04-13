# Analiza zagađenosti zraka lebdećim česticama u gradu Zagrebu
_Ovaj projekt obrađuje podatke o česticama PM10 i PM2.5 u Zagrebu. Sustav povlači podatke iz Excel datoteka i vanjskog API-ja, sprema ih u bazu te nudi REST API za pregled i skriptu za vizualizaciju._

**Funkcionalnosti sustava** 

- Obrada i čišćenje podataka iz data.xls datoteke.

- Pohrana podataka u lokalnu SQLite bazu podataka (baza_podataka.db).

- Integracija s AQI API servisom za dohvat trenutnih mjerenja.

- REST API server za pristup podacima u JSON formatu.

- Automatizirana izrada grafova s prikazom trendova po godišnjim dobima.


## **Upute za pokretanje** 

****1.** Instalirati potrebne biblioteke:**

_pip install pandas flask sqlalchemy requests matplotlib seaborn xlrd_

Pri izradi projekta korišten je Python verzija 3.14.0.
___
****2.** Pokrenuti main.py**

Skripta će generirati pročišćeni CSV i bazu podataka te podići lokalni poslužitelj.

Podacima se pristupa putem preglednika na adresi: http://127.0.0.1:5000

____
**3. Generiranje grafova**

Za generaciju svih grafova potrebno je pokrenuti grafovi.py. 

Nakon pokretajna svi grafovi će se spremiti u obliku slika u folder programa. 

___
**Struktura datoteka**

main.py: Glavni program za obradu podataka i pokretanje API-ja.

grafovi.py: Skripta za vizualizaciju i generiranje grafova.

data.xls: Izvorna datoteka s mjerenjima.

baza_podataka.db: SQLite baza (generira se automatski).


kvaliteta_zraka_zagreb_2025.csv: Pročišćeni podatci mjerenja.
____

**Dostupne API rute**

/mjerenja_sijecanj_2025: Sva mjerenja za siječanj 2025.

/zagreb1_2025: Svi podaci za mjernu postaju ZAGREB-1.

/dnevni_prosjeci_2025: Dnevni prosjeci svih postaja.

/mjerenje_danas: Trenutni podaci s API-ja.


Projekt izrađen u sklopu kolegija Programiranje za analizu podataka (PZAP).
