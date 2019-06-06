import socketserver
import http.server
import http.client
import json

IP = "127.0.0.1"
PORT = 8000

principio_activo  = "&search=active_ingredient:"
proveedor ='&search=openfda.manufacturer_name:'

class loader_FDA():
    url_fda = "api.fda.gov"
    load_fda = "/drug/label.json"
    company_fda = "/drug/label.json?search=openfda.manufacturer_name:%s"
    drug_fda = "/drug/label.json?limit=%s"

    def get_label(self, limit):
        connection = http.client.HTTPSConnection(self.url_fda)
        connection.request("GET", self.load_fda + "?limit=" + limit)
        fda_response = connection.getresponse()
        print (fda_response.status, fda_response.reason)
        data = fda_response.read()
        data = data.decode("utf8")
        event = data
        return event

    def search_drug(self, drug):
        connection = http.client.HTTPSConnection(self.url_fda)
        connection.request("GET", self.load_fda + '?search=patient.drug.medicinalproduct='+ drug +'&limit=10')
        fda_response = connection.getresponse()
        print (fda_response.status, fda_response.reason)
        data = fda_response.read()
        data = data.decode("utf8")
        event = data
        return event

    def search_company(self, comp):
        connection = http.client.HTTPSConnection(self.url_fda)
        connection.request("GET", self.company_fda + '?search=companynumb:'+ comp +'&limit=10')
        fda_response = connection.getresponse()
        print (fda_response.status, fda_response.reason)
        data = fda_response.read()
        data = data.decode("utf8")
        event = data
        return event

class OpenFDAParser():

    def get_drugs(self,limit):
        client = loader_FDA()
        data1 = client.get_event(limit)
        med_list = []
        events = json.loads(data1)
        results = events["results"]
        for i in results:
            patient = i["patient"]
            drug = patient["drug"]
            med_prod = drug[0]["medicinalproduct"]
            med_list.append(med_prod)
        return med_list

    def get_COMPANIES(self,drug):
        client = loader_FDA()
        event = client.search_drug(drug)
        companies_list = []
        info = json.loads(event)
        results = info["results"]
        for event in results:
            companies_list += [event ['companynumb']]
        return companies_list

    def get_COMPANIES_list(self,limit):
        client = loader_FDA()
        event = client.get_event(limit)
        companies_list = []
        info = json.loads(event)
        results = info["results"]
        for event in results:
            companies_list += [event ['companynumb']]
        return companies_list

    def get_company_search(self,drug):
        client = loader_FDA()
        event = client.search_company(drug)
        drugs_list = []
        info = json.loads(event)
        results = info["results"]
        for event in results:
            drugs_list += [event["patient"]["drug"][0]["medicinalproduct"]]
        return drugs_list

    def get_warnings(self,limit):
        client = loader_FDA()
        event = client.get_event(limit)
        warning_list = []
        info = json.loads(event)
        results = info['results']
        for event in results:
            warning_list += [number['warnings']]
        return warning_list

class open_HTML():
    def main_page(self):
        html = '''
        <html>
            <head>
                <link rel="shortcut icon" href="https://pandeoro.net/462-thickbox_default/logo-cruz-roja-adhesivo-.jpg">
                <title>Mediline Laura Garcia Perrin</title>
                </form>
            </head>
            <body bgcolor=#CEE3F6>
                <h1>Mediline por Laura Garcia Perrin</h1>
                <form method="get" action="listDrugs">
                    <input type="submit" value = "Lista de medicamentos: Enviar para abrir FDA">
                    </input>
                    Limit: <input type="text" name = "limit" size="5">
                    </input>
                </form>
                <form method="get" action="listCompanies">
                    <input type="submit" value= "Lista de proveedores: Enviar para abrir FDA">
                    </input>
                    Limit: <input type="text" name = "limit" size="5">
                    </input>
                </form>
                <h5>Introduzca el nombre del medicamento que desea buscar:</h5>
                <form method="get" action = "searchDrug">
                    <input type="text" name = "drug">
                    </input>
                    <input type="submit" value = "Send drug to OpenFDA">
                    </input>
                </form>
                <h5>Introduzca el proveedor que desea buscar:</h5>
                <form method="get" action="searchCompany">
                    <input type="text" name= "company">
                    </input>
                    <input type="submit" value = "Send company to OpenFDA">
                    </input>

				</form>
				<form method="get" action="listGender">
					<input type = "submit" value= "Lista por genero: Enviar para abrir FDA">
					</input>
					Limit: <input type= "text" name = "limit" size ="5">
					</input>
				</form>
            </body>
        </html>
        '''
        return html

    def second_page(self,items):
        med_list = items
        html2 = """
		<html>
        	<head>
                <link rel="shortcut icon" href="https://pbs.twimg.com/profile_images/701113332183371776/57JHEzt7.jpg">
				<title>OpenFDA Cool App</title>
			</head>
        	<body bgcolor=#CEE3F6>
				<ol>
		"""
        for drug in med_list:
            html2 += "<li>"+drug+"</li>"
        html2 += """
				</ol>
            </body>
		</html>
		"""
        return html2

    def get_error_page(self):
        html3 = """
        <html>
            <head>
                <body>
                   <h1>Error 404</h1>
                <body>
            </head>
                <body>
                    Page not found
                </body>
            </html>
        """
        return html3

class testHTTPRequestHandler (http.server.BaseHTTPRequestHandler):
    def execute(self,html):
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(html, "utf8"))

    def do_GET (self):

        if self.path == '/':
            self.send_response(200)
            HTML = open_HTML()
            html = HTML.main_page()
            self.execute(html)

        elif '/listDrugs' in self.path:
            self.send_response(200)
            HTML = open_HTML()
            parser = OpenFDAParser()
            limit = self.path.split("=")[-1]
            items=parser.get_drugs(limit)
            html = HTML.get_second_page(items)
            self.execute(html)

        elif "searchDrug?drug=" in self.path:
            self.send_response(200)
            HTML = open_HTML()
            parser = OpenFDAParser()
            drug = self.path.split("=")[-1]
            items= parser.get_COMPANIES(drug)
            html = HTML.get_second_page(items)
            self.execute(html)

        elif '/listCompanies' in self.path:
            self.send_response(200)
            HTML = open_HTML()
            parser = OpenFDAParser()
            limit = self.path.split("=")[-1]
            items = parser.get_COMPANIES_list(limit)
            html = HTML.get_second_page(items)
            self.execute(html)

        elif "searchCompany?company=" in self.path:
            self.send_response(200)
            HTML = open_HTML()
            parser = OpenFDAParser()
            drug = self.path.split("=")[-1]
            items = parser.get_company_search(drug)
            html = HTML.get_second_page(items)
            self.execute(html)

        elif "/listWarning" in self.path:
            self.send_response(200)
            HTML = open_HTML()
            parser = OpenFDAParser()
            limit = self.path.split("=")[-1]
            items = parser.get_warnings(limit)
            html = HTML.get_second_page(items)
            self.execute(html)

        elif "/redirect" in self.path:
            self.send_response(302)
            self.send_header('Location', 'http://localhost:8000/')
            self.end_headers()

        else:
            self.send_response(404)
            HTML = OpenFDAHTML()
            html=HTML.get_error_page()
            self.execute(html)

        return

Handler = testHTTPRequestHandler
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer((IP, PORT), Handler)

print("Conexion en puerto:", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
        print('Ha habido algún error de teclado o por parte del usuario. Por favor, vuélvalo a intentar.')
httpd.server_close()
