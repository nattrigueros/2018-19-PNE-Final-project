import http.server
import socketserver
import termcolor
import http.client
import json
from Seq import Seq

# Define the Server's port
PORT = 8000


# Class with our Handler. It is a called derived from BaseHTTPRequestHandler
# It means that our class inheritates all his methods and properties

class TestHandler(http.server.BaseHTTPRequestHandler):

    def extract_parameters(self, path):
        dictionary = dict ()
        if '?' in path:
            parameters = path.split('?')[1]
            parameters = parameters.split(' ')[0]
            parameters_list = parameters.split('&')
            for keyvalue in parameters_list:
                key = keyvalue.split('=')[0]
                try:
                    value = keyvalue.split('=')[1]
                    dictionary[key] = value
                except IndexError:
                    print ("IndexError in parameter")
        return dictionary


    def do_GET(self):
        json_option = False
        response_status = 200
        """This method is called whenever the client invokes the GET method
        in the HTTP protocol request"""

        termcolor.cprint(self.requestline, 'green')

        HOSTNAME = 'rest.ensembl.org'

        if self.path == '/':        #  WHAT WANTS THE SERVER
            filename = 'index.html'
            with open(filename, 'r') as f:
                contents = f.read()

        elif '/listSpecies' in self.path:
            parameters = self.extract_parameters(self.path)
            conn = http.client.HTTPConnection(HOSTNAME)
            conn.request('GET', '/info/species?content-type=application/json')

            # WAIT FOR THE SERVER RESPONSE
            r1 = conn.getresponse()

            # READ THE RESPONSE AND CLOSE THE CONNECTION
            text_json = r1.read().decode("utf-8")
            answer = json.loads(text_json)
            data_species = answer['species']

            if 'limit' in parameters:
                try:
                    limit = int(parameters['limit'])
                except:
                    limit = len(data_species)
            else:
                limit = len(data_species)

            if 'json' in parameters:
                json_option = True
                list_species = data_species[1:limit + 1]
                contents = json.dumps(list_species)

            else:
                contents = """
                            <html>
                            <body style="background-color: pink;">
                            <font face="Trebuchet MS">THIS IS THE LIST OF SPECIES
                            <ol>
                            """

                counter = 0
                for specie in data_species:
                    contents = contents + '<li>' + specie['display_name'] + '</li>'
                    counter = counter + 1
                    if (counter == limit):
                        break
                contents = contents + """
                            </ol>
                            </font>
                            </body>
                            </html>
                            """
                conn.close()

        elif '/karyotype' in self.path:
            parameters = self.extract_parameters(self.path)
            if 'specie' in parameters and parameters['specie']!='':
                specie = parameters['specie']
                try:
                    conn = http.client.HTTPConnection(HOSTNAME)
                    conn.request('GET', '/info/assembly/' +specie+ '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    chromosome_data = answer['karyotype']

                    if 'json' in parameters:
                        json_option = True
                        contents = json.dumps(chromosome_data)
                    else:
                        contents = """
                               <html>
                               <body style="background-color: pink;">
                               <font face="Trebuchet MS">This is the karyotype information of the  """ + specie + """:<ul>"""
                        for specie in chromosome_data:
                            contents = contents + '<li>' + specie + '</li>'

                        contents = contents + """
                                   </ul>
                                   </font>
                                   </body>
                                   </html>
                                   """
                except KeyError:
                    response_status = 404
                    filename = open('error.html', 'r')
                    contents = filename.read()
            else:
                response_status=404
                filename =open('error.html','r')
                contents = filename.read()

        elif '/chromosomeLength' in self.path:
            parameters = self.extract_parameters(self.path)

            if 'specie' in parameters and 'chromo' in parameters and parameters['specie']!='' and parameters['chromo']!='':
                specie = parameters['specie']
                chromosome = parameters['chromo']
                try:
                    conn = http.client.HTTPConnection(HOSTNAME)
                    conn.request('GET', '/info/assembly/' + specie + '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)

                    chromosome_specie = answer['top_level_region']

                    if 'json' in parameters:
                        json_option = True
                        chromosome_length = 0
                        for i in chromosome_specie:
                            if (i['name'] == chromosome):
                                chromosome_length = str(i['length'])
                        length_dictionary = dict()
                        length_dictionary['length'] = chromosome_length
                        contents = json.dumps(length_dictionary)

                        if chromosome_length == 0:
                            response_status = 404
                            filename = open('error.html', 'r')
                            contents = json.dumps(filename.read())
                    else:
                        contents = """
                                               <html>
                                               <body style="background-color: pink;">""" + """<font face="Trebuchet MS">This is the length of the """\
                                   + chromosome + """ chromosome of the """ + specie+ """:<ul>"""

                        chromosome_length = 0
                        for i in chromosome_specie:
                            if (i['name'] == chromosome):
                                chromosome_length = str(i['length'])



                        contents = contents + "<li>" + str(chromosome_length) + "</li>" """
                                               </ul>
                                               </body>
                                               </html>
                                               """

                        if chromosome_length == 0:
                            response_status = 404
                            filename = open('error.html', 'r')
                            contents = filename.read()

                except ValueError:
                    response_status = 404
                    filename = open('error.html', 'r')
                    contents = filename.read()
                except KeyError:
                    response_status = 404
                    filename = open('error.html', 'r')
                    contents = filename.read()

            else:
                response_status=404
                filename =open('error.html','r')
                contents = filename.read()

        elif '/geneSeq' in self.path:
            parameters = self.extract_parameters(self.path)

            if 'gene' in parameters and parameters['gene']!='':
                gene = parameters['gene']
                try:
                    conn = http.client.HTTPConnection(HOSTNAME)
                    conn.request('GET', '/homology/symbol/human/'+gene+'?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    id = answer['data'][0]['id']

                    conn.request('GET', '/sequence/id/' +id+ '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    sequence = answer['seq']

                    if 'json' in parameters:
                        json_option = True
                        seq_dictionary = dict()
                        seq_dictionary['seq'] = sequence
                        contents = json.dumps(seq_dictionary)
                    else:
                        contents = """
                                           <html>
                                           <body style="background-color: pink;">
                                           <font face="Trebuchet MS">The sequence corresponding to gene</font>
                                           """+gene+'\n'+"""<font face="Trebuchet MS">is</font>"""+'\n'+sequence+"""
                                           </body>
                                           </html>
                                           """
                except KeyError:
                    response_status = 404
                    filename = open('error.html', 'r')
                    contents = filename.read()

            else:
                response_status=404
                filename =open('error.html','r')
                contents = filename.read()

        elif '/geneInfo' in self.path:
            parameters = self.extract_parameters(self.path)
            if 'gene' in parameters and parameters['gene'] != '':
                gene = parameters['gene']
                try:
                    conn = http.client.HTTPConnection(HOSTNAME)
                    conn.request('GET', '/homology/symbol/human/' + gene + '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    id = answer['data'][0]['id']

                    conn.request('GET', '/overlap/id/' + id + '?feature=gene;content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    start = answer[0]['start']
                    end = answer[0]['end']
                    length = end - start
                    chromosome = answer[0]['seq_region_name']

                    if 'json' in parameters:
                        json_option = True
                        info_dictionary = dict()
                        info_dictionary['start']=start
                        info_dictionary['end'] = end
                        info_dictionary['length'] = length
                        info_dictionary['chromosome'] = chromosome
                        contents = json.dumps(info_dictionary)

                    else:
                        contents = """
                                                       <html>
                                                       <body style="background-color: pink;">
                                                       <font face="Trebuchet MS">The information corresponding to gene
                                                       """ + gene + '\n' + """is""" + '\n' +"<li>START: " +str(start)+ \
                               "</li>" +"<li>END: " +str(end)+ \
                               "<li>ID: " +str(id)+ \
                               "<li>LENGTH: " +str(length) + \
                               "<li>CHROMOSOME: " +chromosome \
                               + """
                                                       </font>
                                                       </body>
                                                       </html>
                                                       """
                except KeyError:
                    response_status = 404
                    filename = open('error.html', 'r')
                    contents = filename.read()
            else:
                response_status=404
                filename =open('error.html','r')
                contents = filename.read()

        elif '/geneCal' in self.path:
            parameters = self.extract_parameters(self.path)

            if 'gene' in parameters and parameters['gene'] != '':
                gene = parameters['gene']
                try:
                    conn = http.client.HTTPConnection(HOSTNAME)
                    conn.request('GET', '/homology/symbol/human/' + gene + '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    id = answer['data'][0]['id']

                    conn.request('GET', '/sequence/id/' + id + '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    sequence = answer['seq']
                    seq = Seq(sequence)
                    length = len(sequence)
                    percA = seq.perc('A')
                    percC = seq.perc('C')
                    percT = seq.perc('T')
                    percG = seq.perc('G')

                    if 'json' in parameters:
                        json_option = True
                        calc_dictionary = dict()
                        calc_dictionary['sequence']=sequence
                        calc_dictionary['percentage A'] = percA
                        calc_dictionary['percentage C'] = percC
                        calc_dictionary['percentage T'] = percG
                        calc_dictionary['percentage G'] = percG
                        calc_dictionary['length'] = length
                        contents = json.dumps(calc_dictionary)

                    else:
                        contents = """
                                                                   <html>
                                                                   <body style="background-color: pink;">
                                                                   <font face="Trebuchet MS">The sequence corresponding to gene
                                                                   """ + gene + '\n' + """is""" + '\n' + sequence +'\n'+ "and the calculations are: " +'\n'+ "<li>TOTAL LENGTH: " + str(length) + \
                               "<li>PERCENTAGE OF A BASES: " + str(percA) + "<li>PERCENTAGE OF C BASES: " + str(percC) + "<li>PERCENTAGE OF T BASES: " + str(percT) + "<li>PERCENTAGE OF G BASES: " + str(percG) +"""
                                                                   </font>
                                                                   </body>
                                                                   </html>
                                                                   """
                except KeyError:
                    response_status = 404
                    filename = open('error.html', 'r')
                    contents = filename.read()
            else:
                response_status=404
                filename =open('error.html','r')
                contents = filename.read()


        elif "/geneList" in self.path:
            parameters = self.extract_parameters(self.path)

            if ('chromo' in parameters and 'start' in parameters and 'end' in parameters) and (parameters['chromo'] != "" and parameters['start'] != "" and parameters['end'] != ""):
                chromo = parameters['chromo']
                start = parameters['start']
                end = parameters['end']
                print(chromo,end,start)

                try:
                    conn = http.client.HTTPConnection("rest.ensembl.org")
                    conn.request("GET", "/overlap/region/human/" + str(chromo) + ":" + str(start) + "-" + str(end) + "?content-type=application/json;feature=gene;feature=transcript;feature=cds;feature=exon")
                    r1 = conn.getresponse()
                    data1 = r1.read().decode("utf-8")
                    answer = json.loads(data1)
                    
                    if 'json' in parameters:
                        json_option = True
                        list = []

                        for element in answer:

                            if (element['feature_type'] == "gene"):
                                gene_dictionary = dict()
                                gene_dictionary['name'] = element['external_name']
                                gene_dictionary['start'] = element['start']
                                gene_dictionary['end'] = element['end']
                                list.append(gene_dictionary)

                        contents = json.dumps(list)

                    else:

                        contents = """
                                <html>
                                <body style= "background-color: pink;">
                                <font face="Trebuchet MS">The names of the genes located in chromosome""" + '\n' + chromo + ' from position '+ start+ ' to position ' + end + ' are: '+ """<ul>"""


                        for element in answer:

                            if (element['feature_type'] == "gene"):
                                contents = contents + "<li>" + (
                                            str(element['external_name']) + " " + str(element['start']) + " " + str(element['end'])) + "</li>"

                        contents = contents + """</ul></body></html>"""


                except ValueError:
                    json_option = False
                    response_status = 404
                    f = open("error.html", 'r')
                    contents = f.read()

                except SyntaxError:
                    json_option = False
                    response_status = 404
                    f = open("error.html", 'r')
                    contents = f.read()

                except KeyboardInterrupt:
                    json_option = False
                    response_status = 404
                    f = open("error.html", 'r')
                    contents = f.read()

                except KeyError:
                    json_option = False
                    response_status = 404
                    f = open("error.html", 'r')
                    contents = f.read()

                except NameError:
                    json_option = False
                    response_status = 404
                    f = open("error.html", 'r')
                    contents = f.read()

                except TypeError:
                    json_option = False
                    response_status = 404
                    f = open("error.html", 'r')
                    contents = f.read()

            else:
                response_status = 404
                f = open("error.html", 'r')
                contents = f.read()

        else:                                       # IF NOT RAISE AN ERROR
            response_status = 404
            filename = 'error.html'
            with open(filename, 'r') as f:
                contents = f.read()


        # Generating the response message
        self.send_response(response_status)  # -- Status line: OK!

        # Define the content-type header:
        if (json_option==True):
            self.send_header('Content-Type', 'application/json')
        else:
            self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(str.encode(contents)))

        # The header is finished
        self.end_headers()

        # Send the response message
        self.wfile.write(str.encode(contents))

        return


# ------------------------
# - Server MAIN program
# ------------------------
# -- Set the new handler
Handler = TestHandler
socketserver.TCPServer.allow_reuse_address = True

# -- Open the socket server
with socketserver.TCPServer(("", PORT), Handler) as httpd:

    print("Serving at PORT", PORT)

    # -- Main loop: Attend the client. Whenever there is a new
    # -- clint, the handler is called
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Stoped by the user")
        httpd.server_close()