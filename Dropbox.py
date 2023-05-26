import requests
import urllib
import webbrowser
import socket
from socket import AF_INET, socket, SOCK_STREAM
import json
import helper

app_key = 'zt8z29pjcndwu4c'
app_secret = '1087bnlsow1f91m'
server_addr = "127.0.0.1"
server_port = 8090
redirect_uri = "http://" + server_addr + ":" + str(server_port)


class Dropbox:
    _access_token = ""
    _path = "/"
    _files = []
    _root = None
    _msg_listbox = None
    _fkop = 0

    def __init__(self, root):
        self._root = root

    def local_server(self):
        print("\n\tHandle the OAuth 2.0 server response")
        # 8090. portuan entzuten dagoen zerbitzaria sortu
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('localhost', 8090))
        server_socket.listen(1)
        print("\t\tSocket listening on port 8090")

        print("\t\tWaiting for client requests...")
        # ondorengo lerroan programa gelditzen da zerbitzariak 302 eskaera jasotzen duen arte
        client_connection, client_address = server_socket.accept()
        # nabitzailetik 302 eskaera jaso
        eskaera = client_connection.recv(1024).decode()
        print("\t\tNabigatzailetik ondorengo eskaera jaso da:")
        print(eskaera)  # zerbitzariak jasotzen duen eskaera

        # eskaeran "auth_code"-a bilatu
        lehenengo_lerroa = eskaera.split('\n')[0]
        aux_auth_code = lehenengo_lerroa.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        print("auth_code: " + auth_code)

        #########################################################################33
        http_response = "HTTP/1.1 200 OK\r\n\r\n" \
                        "<html>" \
                        "<head><title>Proba</title></head>" \
                        "<body>The authentication flow has completed. Close this window.</body>" \
                        "</html>"

        client_connection.sendall(
            str.encode(http_response))
        client_connection.close()
        server_socket.close()

        return auth_code

    def do_oauth(self):
        print('Baimena lortzen...')
        base_uri = "https://www.dropbox.com/oauth2/authorize"
        datuak = {'client_id': app_key,
                  'redirect_uri': redirect_uri,  #Dirección IP de bucle invertido
                  'response_type': 'code'}

        datuak_kodifikatuta = urllib.parse.urlencode(datuak)
        auth_uri = base_uri + '?' + datuak_kodifikatuta

        print("\n\t Web nabigatzailea irekitzen")
        webbrowser.open_new(auth_uri)  # eskera nabigatzailean zabaldu (Get metodoa modu lehenetsian erabiliko da)

        auth_code = self.local_server()

        # Exchange authorization code for access token
        print("\n\tStep 5: Exchange authorization code for refresh and access tokens")

        uri = 'https://api.dropboxapi.com/oauth2/token'
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Content-Type': 'application/x-www-form-urlencoded'}
        datuak = {'code': auth_code,
                  'grant_type': 'authorization_code',
                  'redirect_uri': redirect_uri,
                  'client_id': app_key,
                  'client_secret': app_secret}

        datuak_kodifikatuta = urllib.parse.urlencode(datuak)
        goiburuak['Content-Length'] = str(len(datuak_kodifikatuta))
        erantzuna = requests.post(uri, headers=goiburuak, data=datuak_kodifikatuta,
                                  allow_redirects=False)  # eskaera ez dugu nabigatzaileanegingo, gure programan egingo da
        status = erantzuna.status_code
        print("\t\tStatus: " + str(status))

        # This endpoint returns a JSON-encoded dictionary
        # That contains access_token -> The access token to be used to call the Dropbox API.
        #           Denbora mugatu batean erabili ahalko da (expire_in definitzen den demboran)
        # Refresh token -> this token is long-lived and won't expire automatically. It can be stored and re-used multiple times.

        edukia = erantzuna.text
        print("\t\tEdukia:")
        print("\n" + edukia)
        edukia_json = json.loads(edukia)
        access_token = edukia_json['access_token']
        print("\naccess_token: " + access_token)
        print("Autentifikazio fluxua amaitu da.")

        self._access_token = access_token
        self._root.destroy()

    def list_folder(self, msg_listbox, cursor="", edukia_json_entries=[]):
        if self._path == "/":
            self._path = ""

        if not cursor:
            print("\n/list_folder")
            uri = 'https://api.dropboxapi.com/2/files/list_folder'
            datuak = {'path': self._path, 'recursive': False}
        else:
            print("\n/list_folder/continue")
            uri = 'https://api.dropboxapi.com/2/files/list_folder/continue'
            datuak = {'cursor': cursor}

        # Call Dropbox API
        goiburuak = {'Host': 'api.dropboxapi.com', 'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        datuak_json = json.dumps(datuak)

        response = requests.post(uri, headers=goiburuak, data=datuak_json, allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        edukia = response.content
        edukia_json = json.loads(edukia)

        edukia_json_entries = edukia_json['entries']

        if edukia_json['has_more']:
            self.list_folder(msg_listbox, edukia_json['cursor'], edukia_json_entries)
        else:
            self._fkop = 0
            self._files = helper.update_listbox2(msg_listbox, self._path, edukia_json_entries)

        print('###############################################################################')
        print('FITXATEGIAK LISTAN SARTU DIRA')
        print('###############################################################################')

    def transfer_file(self, file_path, file_data):
        print("\n/upload " + file_path)

        uri = 'https://content.dropboxapi.com/2/files/upload'
        parameters = {"autorename": True,  # estaba en false
                      "mode": "add",
                      "mute": False,
                      "path": file_path,
                      "strict_conflict": False}

        json_datuak = json.dumps(parameters)
        goiburuak = {'Host': 'content.dropboxapi.com',
                     'Dropbox-API-Arg': json_datuak,
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/octet-stream'}

        response = requests.post(uri, headers=goiburuak, data=file_data, allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('###############################################################################')
            print('FITXATEGIAK TRANSFERITU DIRA')
            print('###############################################################################')

    def delete_file(self, file_path):
        print("\n/delete_file " + file_path)

        uri = 'https://api.dropboxapi.com/2/files/delete_v2'
        parameters = {"path": file_path}
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        data = json.dumps(parameters)
        response = requests.post(uri, headers=goiburuak, data=data, allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('###############################################################################')
            print('FITXATEGIA EZABATU DA')
            print('###############################################################################')

    def create_folder(self, path):
        print("\n/create_folder " + path)

        uri = 'https://api.dropboxapi.com/2/files/create_folder_v2'
        parameters = {"autorename": False,
                      "path": path}
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        data = json.dumps(parameters)
        response = requests.post(uri, headers=goiburuak, data=data, allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('###############################################################################')
            print('KARPETA SORTU DA')
            print('###############################################################################')

    #################################### ALDERDI GEHIGARRIAK ################################################
    def download(self, path):
        print("\n/download " + path)

        uri = 'https://content.dropboxapi.com/2/files/download'
        parameters = {'path': path}
        data = json.dumps(parameters)
        goiburuak = {'Host': 'content.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Dropbox-API-Arg': data}
        response = requests.post(uri, headers=goiburuak, data=data, allow_redirects=False)

        status = response.status_code
        edukia = response.content
        print("\nStatus: " + str(status) + " " + response.reason)
        print(edukia)

        if status == 200:
            with open(path.split('/')[-1], 'wb') as exp_file:
                exp_file.write(edukia)
            print('###############################################################################')
            print('DESKARGATU DA FITXATEGIA')
            print('###############################################################################')
        elif status == 409:
            print('###############################################################################')
            print('EZ DA FITXATEGIA')
            print('###############################################################################')

    def download_zip(self, path):
        print("\n/download_zip " + path)

        uri = 'https://content.dropboxapi.com/2/files/download_zip'
        parameters = {"path": path}
        data = json.dumps(parameters)
        goiburuak = {'Host': 'content.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Dropbox-API-Arg': data}
        response = requests.post(uri, headers=goiburuak, data=data, allow_redirects=False)

        status = response.status_code
        edukia = response.content
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            zip_fitxategia = open(path.split('/')[-1] + '.zip', 'wb')
            zip_fitxategia.write(edukia)
            zip_fitxategia.close()
            print('###############################################################################')
            print('KARPETAREN ZIP-A JEITSI DA')
            print('###############################################################################')

    def copy(self, fromPath, toPath):
        print("\n/copy_file from " + fromPath + " to " + toPath)

        uri = 'https://api.dropboxapi.com/2/files/copy_v2'
        parameters = {"allow_ownership_transfer": False,
                      "allow_shared_folder": False,
                      "autorename": False,
                      "from_path": fromPath,
                      "to_path": toPath}
        data = json.dumps(parameters)
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        response = requests.post(uri, headers=goiburuak, data=data, allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('###############################################################################')
            print('FITXATEGIA KOPIATU DA')
            print('###############################################################################')
        elif status == 409:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('ERRORE BAT SUERTATU DA')
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        return status

    def move(self, fromPath, toPath):
        print("\n/move_file from " + fromPath + " to " + toPath)

        uri = 'https://api.dropboxapi.com/2/files/move_v2'
        parameters = {"allow_ownership_transfer": False,
                      "allow_shared_folder": False,
                      "autorename": False,
                      "from_path": fromPath,
                      "to_path": toPath}
        data = json.dumps(parameters)
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        response = requests.post(uri, headers=goiburuak, data=data, allow_redirects=False)

        status = response.status_code
        print("\nStatus: " + str(status) + " " + response.reason)

        if status == 200:
            print('###############################################################################')
            print('FITXATEGIA MUGITU DA')
            print('###############################################################################')
        elif status == 409:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('ERRORE BAT SUERTATU DA')
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        return status

    def add_file_member(self, path, email):
        print("\n/add_file_member " + path)

        uri = 'https://api.dropboxapi.com/2/sharing/add_file_member'
        parameters = {"access_level": "viewer",
                      "add_message_as_comment": False,
                      "custom_message": "Here is my doc:",
                      "file": path,
                      "members": [
                          {
                              ".tag": "email",
                              "email": email
                          }
                      ],
                      "quiet": False}
        data = json.dumps(parameters)
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        response = requests.post(uri, headers=goiburuak, data=data, allow_redirects=False)

        status = response.status_code
        edukia = response.content
        print("\nStatus: " + str(status) + " " + response.reason)
        print(edukia)

        if status == 200:
            print('###############################################################################')
            print('PARTEKATU DA FITXATEGIA')
            print('###############################################################################')
        elif status == 400:
            print('###############################################################################')
            print('SARTUTAKO EMAILA EZ DA ZUZENA')
            print('###############################################################################')
        return status
