import requests
import urllib
import webbrowser
import socket
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
    _fkop=0

    def __init__(self, root):
        self._root = root

    def local_server(self):
        print("\n\tStep 4: Handle the OAuth 2.0 server response")
        # https://developers.google.com/identity/protocols/oauth2/native-app#handlingresponse
        # 8090. portuan dagoen zerbitzaria sartu
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 8090))
        server_socket.listen(1)
        print("\t\tSocket listening on port 8090")

        print("\t\tWaiting for client requests...")
        # ondorengo lerroan programa gelditzen da zerbitzariak 302 eskaera jasotzen duen arte
        client_connection, client_address = server_socket.accept()

        # nabitzailetik 302 eskaera jaso
        eskaera = client_connection.recv(1024).decode()
        print("\t\tNabigatzailetik ondorengo eskaera jaso da:")
        print("\n" + eskaera)
        # eskaeran "auth_code"-a bilatu
        lehenengo_lerroa = eskaera.split('\n')[0] # eskaera.decode("utf8").split('\n')[0]
        aux_auth_code = lehenengo_lerroa.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        print("auth_code: " + auth_code)

        ############################################################################################
        http_response = "HTTP/1.1 200 OK\r\n\r\n" \
                        "<html>" \
                        "<head><title>Proba</title></head>" \
                        "<body>The authentication flow has completed. Close this window.</body>" \
                        "</html>"
        # erabiltzaileari erantzun bat bueltatu

        client_connection.sendall(str.encode(http_response))  # client_connection.sendall(http_response.encode(encoding="utf8"))
        client_connection.close()
        server_socket.close()

        ############################################################################################

        return auth_code

    def do_oauth(self): #TODO AQUI HAY ALGO MAL
        print("\nObtaining OAuth  access tokens")
        # Authorization
        print("\tStep 2: Send a request to Dropbox's OAuth 2.0 server")
        base_uri = 'https://www.dropbox.com/oauth2/authorize'
        goiburuak = {'Host': 'www.dropbox.com'}
        datuak = {'response_type': 'code',
                  'client_id': app_key,
                  'redirect_uri': redirect_uri,
                  'scope': 'files.content.read'} #NO LO PONE
        datuak_kodifikatuta = urllib.parse.urlencode(datuak)
        step2_uri = base_uri + '?' + datuak_kodifikatuta
        print("\t" + step2_uri)
        webbrowser.open_new(step2_uri)

        ###############################################################################################################

        print("\n\tStep 3: DropBox prompts user for consent")

        auth_code = self.local_server()

        ###############################################################################################################
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
        erantzuna = requests.post(uri, headers=goiburuak, data=datuak, allow_redirects=False) #TODO SE ME HABIA OLVIDADO EL GOIBURU
        status = erantzuna.status_code
        print(status)
        # Google responds to this request by returning a JSON object
        # that contains a short-lived access token and a refresh token.

        edukia = erantzuna.text #TODO EN VEZ DE CONTENT
        print("\nEdukia\n")
        print(edukia)
        edukia_json = json.loads(edukia)
        access_token = edukia_json['access_token']
        print("\nAccess token: " + access_token)

        self._access_token = access_token
        self._root.destroy()

    def list_folder(self, msg_listbox, cursor="", edukia_json_entries=[]):
        if self._path == "/": #TODO HE PUESTO ESTO EN VEZ DE LO DE ABAJO
            self._path = ""

        if not cursor:
            #TODO self._path = ""
            print("\n/list_folder")
            uri = 'https://api.dropboxapi.com/2/files/list_folder'
            datuak = {'path': self._path, 'recursive': False}
            # sartu kodea hemen
            #TODO EN DATOS HACE FALTA ???? "include_mounted_folders": True, "include_non_downloadable_files": True
        else:
            print("\n/list_folder/continue")
            uri = 'https://api.dropboxapi.com/2/files/list_folder/continue'
            datuak = {'cursor': cursor}
            # sartu kodea hemen

        # Call Dropbox API
        goiburuak = {'Host': 'api.dropboxapi.com', 'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        datuak_json = json.dumps(datuak)

        response = requests.post(uri, headers=goiburuak, data=datuak_json, allow_redirects=False)

        status = response.status_code
        print("\nStatus: "+str(status)+" "+response.reason)

        edukia = response.content
        edukia_json = json.loads(edukia)
        print('###############################################################################')
        print('\n FITXATEGIAK LISTAN SARTUKO DIRA')
        print('###############################################################################')

        edukia_json_entries = edukia_json['entries']
        #for entry in edukia_json['entries']:
         #   edukia_json_entries.append(entry)
          #  self._fkop = self._fkop+1
            #print(str(self._fkop) + '. Fitxategia ------>  ' + entry['name'])

        if edukia_json['has_more']:
            # sartu kodea hemen
            self.list_folder(msg_listbox, edukia_json['cursor'], edukia_json_entries)
        else:
            # sartu kodea hemen
            print("######################### NO MORE FILES ######################### ")
            print("DAUDEN FITXATEGI KOPURUA: " + str(self._fkop))
            self._fkop=0
            self._files = helper.update_listbox2(msg_listbox, self._path, edukia_json_entries)

    def transfer_file(self, file_path, file_data):
        print("\n/upload " + file_path)
        # sartu kodea hemen
        uri = 'https://content.dropboxapi.com/2/files/upload'
        parameters = {"autorename": False,
                    "mode": "add",
                    "mute": False,
                    "path": file_path,
                    "strict_conflict": False}
        json_datuak = json.dumps(parameters)
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Dropbox-API-Arg': json_datuak,
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/octet-stream'}

        response = requests.post(uri, headers=goiburuak, data=file_data, allow_redirects=False)

        status = response.status_code
        edukia = response.content
        print("\nStatus: " + str(status) + " " + response.reason)
        if status == 200:
            print('###############################################################################')
            print('\n FITXATEGIAK TRANSFERITU DIRA')
            print('###############################################################################')



    def delete_file(self, file_path):
        print("\n/delete_file " + file_path)
        # sartu kodea hemen
        uri = 'https://api.dropboxapi.com/2/files/delete_v2'
        parameters = {"path": file_path}
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        data = json.dumps(parameters)
        response = requests.post(uri, headers=goiburuak, data=data, allow_redirects=False)

        status = response.status_code
        edukia = response.content
        print("\nStatus: " + str(status) + " " + response.reason)
        if status == 200:
            print('###############################################################################')
            print('\n FITXATEGIA EZABATU DA')
            print('###############################################################################')



    def create_folder(self, path):
        print("\n/create_folder " + path)
        # TODO sartu kodea hemen
        uri = 'https://api.dropboxapi.com/2/files/create_folder_v2'
        parameters = {"autorename": False,
                      "path": path}
        goiburuak = {'Host': 'api.dropboxapi.com',
                     'Authorization': 'Bearer ' + self._access_token,
                     'Content-Type': 'application/json'}
        data = json.dumps(parameters)
        response = requests.post(uri, headers=goiburuak, data=data, allow_redirects=False)

        status = response.status_code
        edukia = response.content
        print("\nStatus: " + str(status) + " " + response.reason)
        if status == 200:
            print('###############################################################################')
            print('\n KARPETA SORTU DA')
            print('###############################################################################')

