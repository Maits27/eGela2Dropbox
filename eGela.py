import os
import sys
from tkinter import messagebox as tkMessageBox
import requests
import urllib
from bs4 import BeautifulSoup
import time
import helper

class eGela:
    _login = 0
    _cookiea = ""
    _ikasgaia = ""
    _refs = []
    _root = None

    #Añadidos por mi:
    _token=""
    _uri=""

    def __init__(self, root):
        self._root = root

    def check_credentials(self, username, password, event=None):

        global LOGIN_EGIAZTAPENA
        LOGIN_EGIAZTAPENA = False
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. ESKAERA (Login inprimakia lortu 'logintoken' ateratzeko #####")
        metodoa = 'GET'
        self._uri = 'https://egela.ehu.eus/login/index.php'
        goiburua = {'Host': 'egela.ehu.eus'}
        edukia = ''

        response = requests.request(metodoa, self._uri, headers=goiburua, data=edukia,
                                    allow_redirects=False)

        html_fitxategia = response.content

        print("##### HTML-aren azterketa... #####")

        orria = BeautifulSoup(html_fitxategia, 'html.parser')
        formularioa = orria.find_all('form', {'class': 'm-t-1 ehuloginform'})[0]
        self._token = formularioa.find_all('input', {'name': 'logintoken'})[0]['value']

        print("\n-----------------------------------------------------------------------\n"
              "\nURI: " + self._uri +
              "\nEDUKIA: " + str(edukia))

        kode = str(response.status_code)
        if int(kode) // 100 == 3:
            self._uri = response.headers['Location']

        try:
            self._cookiea = response.headers['Set-Cookie'].split(";")[0]
        except Exception:
            print("Cookie-a mantentzen da")

        print("\nESKAERAREN EGOERA: " + kode + " ---> " + response.reason)

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 2. ESKAERA (Kautotzea -datu bidalketa-) #####")

        metodoa = 'POST'
        goiburua = {'Host': 'egela.ehu.eus', 'Cookie': self._cookiea,
                    'Content-Type': 'application/x-www-form-urlencoded'}
        edukia = {'logintoken': self._token, 'username': username.get(), 'password': password.get()}
        edukia_encoded = urllib.parse.urlencode(edukia)
        goiburua['Content-Length'] = str(len(edukia_encoded))

        response = requests.request(metodoa, self._uri, headers=goiburua, data=edukia,
                                    allow_redirects=False)  # berbidalketak (host, 30x kodedun erantzunak)

        if (response.headers['Location'].__eq__("https://egela.ehu.eus/login/index.php")):
            print(edukia)
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("Pasahitza ez da egokia, saiatu zaitez berriro")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            sys.exit(0)

        print("\n-----------------------------------------------------------------------\n"
              "\nURI: " + self._uri +
              "\nEDUKIA: " + str(edukia))

        kode = str(response.status_code)
        if int(kode) // 100 == 3:
            self._uri = response.headers['Location']

        try:
            self._cookiea = response.headers['Set-Cookie'].split(";")[0]
        except Exception:
            print("Cookie-a mantentzen da")

        print("\nESKAERAREN EGOERA: " + kode + " ---> " + response.reason)

        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 3. ESKAERA (berbidalketa) #####")

        metodoa = 'GET'
        goiburua = {'Host': 'egela.ehu.eus', 'Cookie': self._cookiea}
        edukia = ''

        response = requests.request(metodoa, self._uri, headers=goiburua, data=edukia,
                                    allow_redirects=False)

        print("\n-----------------------------------------------------------------------\n"
              "\nURI: " + self._uri +
              "\nEDUKIA: " + str(edukia))

        kode = str(response.status_code)
        if int(kode) // 100 == 3:
            self._uri = response.headers['Location']

        try:
            self._cookiea = response.headers['Set-Cookie'].split(";")[0]
        except Exception:
            print("Cookie-a mantentzen da")

        print("\nESKAERAREN EGOERA: " + kode + " ---> " + response.reason)

        progress = 75
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)

        print("\n##### 4. ESKAERA (eGelako orrialde nagusia) #####")

        metodoa = 'GET'
        goiburua = {'Host': 'egela.ehu.eus', 'Cookie': self._cookiea}
        edukia = ''

        response = requests.request(metodoa, self._uri, headers=goiburua, data=edukia,
                                    allow_redirects=False)

        print("\n-----------------------------------------------------------------------\n"
              "\nURI: " + self._uri +
              "\nEDUKIA: " + str(edukia))

        kode = str(response.status_code)
        if int(kode) // 100 == 3:
            self._uri = response.headers['Location']
        elif int(kode) == 200:
            LOGIN_EGIAZTAPENA = True

        try:
            self._cookiea = response.headers['Set-Cookie'].split(";")[0]
        except Exception:
            print("Cookie-a mantentzen da")

        print("\nESKAERAREN EGOERA: " + kode + " ---> " + response.reason)

        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(0.1)
        popup.destroy()

        print("\n##### LOGIN EGIAZTAPENA #####")
        if LOGIN_EGIAZTAPENA:
            print("\n\n#########################Egiaztapena ondo burutu da###########################")
            self._login = 1
            # KLASEAREN ATRIBUTUAK EGUNERATU
            self._root.destroy()

        else:
            tkMessageBox.showinfo("Alert Message", "Login incorrect!")

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 5. ESKAERA (Ikasgairen eGelako orrialdea) #####")
        metodoa = 'GET'
        goiburua = {'Host': 'egela.ehu.eus', 'Cookie': self._cookiea}
        edukia = ''

        response = requests.request(metodoa, self._uri, headers=goiburua, data=edukia,
                                    allow_redirects=False)
        orria = BeautifulSoup(response.content, 'html.parser')
        kurtso_zerrenda = orria.find_all('a', {'class': 'ehu-visible'})
        aurkitutaWS = False
        irakasgaia = "Web Sistemak"

        for kurtso in kurtso_zerrenda:
            if irakasgaia.lower() in str(kurtso).lower():
                self._ikasgaia = kurtso['href']
                aurkitutaWS = True


        print("Aurkitua WS: "+str(aurkitutaWS))
        if not aurkitutaWS:
            print("EZ DA AURKITU " + irakasgaia + " IRAKASGAIA. ")
            exit(400)

        print("\n-----------------------------------------------------------------------\n"+
              "\nURI: " + self._uri +
              "\nEGOERA: " + str(response.status_code) + " " + response.reason +
              "\nEDUKIA: " + str(edukia))



        print("\n##### HTML-aren azterketa... #####")
        metodoa = 'GET'
        goiburua = {'Host': 'egela.ehu.eus', 'Cookie': self._cookiea}
        edukia = ''

        response = requests.request(metodoa, self._ikasgaia, headers=goiburua, data=edukia,
                                    allow_redirects=False)
        print(self._ikasgaia +" !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        orria = BeautifulSoup(response.content, 'html.parser')
        link_zerrenda = orria.find_all('img', {'class': 'iconlarge activityicon'})

        progress_step = float(100.0 / len(link_zerrenda))

        print(self._ikasgaia)

        for link in link_zerrenda:
            if '/pdf' in link['src']:
                uri = link.parent['href']
                metodoa = 'GET'
                goiburua = {'Host': 'egela.ehu.eus', 'Cookie': self._cookiea}
                edukia = ''

                response = requests.request(metodoa, uri, headers=goiburua, data=edukia,
                                            allow_redirects=False)
                orria = BeautifulSoup(response.content, 'html.parser')
                a_zerrenda = orria.find_all('div', {'class': 'resourceworkaround'})

                for a in a_zerrenda:
                    pdf_file = a.find_all('a')[0]['href']
                    pdf_name = pdf_file.split('/')[-1]
                    self._refs.append({'pdf_link': pdf_file, 'pdf_name': pdf_name})

            progress += progress_step
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(0.1)

        popup.destroy()

        return self._refs

    def get_pdf(self, selection):
        print("##### PDF-a deskargatzen... #####")
        pdf_file = self._refs[selection]['pdf_link']
        pdf_name = self._refs[selection]['pdf_name']
        print("Deskargatzen ari den PDF-aren link-a:\n" + pdf_file)

        metodoa = 'GET'
        goiburua = {'Host': pdf_file.split('/')[2], 'Cookie': self._cookiea}
        edukia = ''

        response = requests.request(metodoa, pdf_file, headers=goiburua, data=edukia,
                                    allow_redirects=False)

        if not os.path.exists("pdf"):
            os.mkdir("pdf")

        file = open("./pdf/" + pdf_name, "wb")
        file.write(response.content)
        file.close()
        return pdf_name, "./pdf/"+pdf_file
