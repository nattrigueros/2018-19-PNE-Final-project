# THIS IS THE SERVER FOR MY FINAL PROJECT: Natalia Trigueros Alegre #

import http.server
import socketserver
import termcolor
import http.client
import json
from Seq import Seq

# Define the Server's port
PORT = 8000

class TestHandler(http.server.BaseHTTPRequestHandler):

    # The purpose of this function is to extract the parameters from the url, and create a dictionary with them, which we would use posteriorly

    def extract_parameters(self, path):
        dictionary = dict ()
        if '?' in path:           # We extract the parameters from the path and create our dictionary
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

    # This method is called whenever the client invokes the GET method in the HTTP protocol request

    def do_GET(self):
        json_option = False
        response_status = 200

        termcolor.cprint(self.requestline, 'green')

        HOSTNAME = 'rest.ensembl.org'  # This will be the data base we will be using

        if self.path == '/':        # When the user enters '/' the main page ( Index ) is going to pop up
            filename = 'index.html'
            with open(filename, 'r') as f:
                contents = f.read()

# LET'S DEAL WITH THE FIRST ENDPOINT: /listSpecies
        elif '/listSpecies' in self.path:
            parameters = self.extract_parameters(self.path)    # Let's get our parameter 'limit' from our  function
            conn = http.client.HTTPConnection(HOSTNAME)
            conn.request('GET', '/info/species?content-type=application/json')

            # Wait for the server's response, decode the information received
            r1 = conn.getresponse()

            text_json = r1.read().decode("utf-8")
            answer = json.loads(text_json)
            data_species = answer['species']  # Let's create a list with all the available species in the data base

            if 'limit' in parameters:   # In case we have a limit we are going to get that number of species
                try:
                    limit = int(parameters['limit'])
                except:
                    limit = len(data_species)   # In the case the number is not a valid integer we get the entire list
            else:  # In case there is no limit specified: limit= or /listSpecies
                limit = len(data_species)

            if 'json' in parameters:   # If the json option is chosen return the information in a json format
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
                for specie in data_species:   # We iterate over all the the list of species
                    contents = contents + '<li>' + specie['display_name'] + '</li>'
                    counter = counter + 1
                    if (counter == limit):  # We stop iterating whenever the number of the species equals the limit set
                        break
                contents = contents + """
                            </ol>
                            </font>
                            </body>
                            </html>
                            """
                conn.close()

# LET'S DEAL WITH THE SECOND ENDPOINT: /karyotype
        elif '/karyotype' in self.path:
            parameters = self.extract_parameters(self.path)  # Let's get our parameter 'specie'
            if 'specie' in parameters and parameters['specie']!='':  # In the case that a specie has a value assigned
                specie = parameters['specie']
                try:
                    conn = http.client.HTTPConnection(HOSTNAME)
                    conn.request('GET', '/info/assembly/' +specie+ '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    chromosome_data = answer['karyotype']   # Let's extract our chromosome data from the response

                    if 'json' in parameters:  # In the case the json option is chosen
                        json_option = True
                        contents = json.dumps(chromosome_data)  # Return the data in a json format
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
                except KeyError:  # In the case the introduced specie is not a valid one
                    response_status = 404
                    filename = open('error.html', 'r')
                    contents = filename.read()
            else:  # In the case specie is not defined
                response_status=404
                filename =open('error.html','r')
                contents = filename.read()

# LET'S DEAL WITH THE THIRD ENDPOINT: /chromosomeLength
        elif '/chromosomeLength' in self.path:
            parameters = self.extract_parameters(self.path)  # Let's extract our parameters chromosome and specie

            if 'specie' in parameters and 'chromo' in parameters and parameters['specie']!='' and parameters['chromo']!='': # In the case both chromosome and specie have an assigned value
                specie = parameters['specie']
                chromosome = parameters['chromo']
                try:
                    conn = http.client.HTTPConnection(HOSTNAME)
                    conn.request('GET', '/info/assembly/' + specie + '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)

                    chromosome_specie = answer['top_level_region']   # Let's get the chromosome information about the given specie

                    if 'json' in parameters:  # In the case the user wants a json format
                        json_option = True
                        chromosome_length = 0
                        for i in chromosome_specie:  # Let's get the length of the chromosome of the chosen specie
                            if (i['name'] == chromosome):
                                chromosome_length = str(i['length'])
                        length_dictionary = dict()
                        length_dictionary['length'] = chromosome_length  # We now have the length value stored in the variable
                        contents = json.dumps(length_dictionary)  # Return the information in a json format

                        if chromosome_length == 0:  # In the case the length is 0, which means the specie has no such chromosome, the error page should pop up
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

            else:  # In case one of the parameters is absent or in blank
                response_status=404
                filename =open('error.html','r')
                contents = filename.read()


# LET'S DEAL WITH THE FOURTH ENDPOINT: /geneSeq
        elif '/geneSeq' in self.path:
            parameters = self.extract_parameters(self.path)   # Let's get the parameter 'gene'

            if 'gene' in parameters and parameters['gene']!='':  # In the case value for 'gene' is present, not in blank
                gene = parameters['gene']
                try:
                    conn = http.client.HTTPConnection(HOSTNAME)
                    conn.request('GET', '/homology/symbol/human/'+gene+'?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    id = answer['data'][0]['id']   # Let's get the necessary ID for asking for the data

                    conn.request('GET', '/sequence/id/' +id+ '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    sequence = answer['seq']   # Define sequence

                    if 'json' in parameters:   # In the case the json option is chosen
                        json_option = True
                        seq_dictionary = dict()
                        seq_dictionary['seq'] = sequence
                        contents = json.dumps(seq_dictionary)  # Return sequence in a json format
                    else: # Return a page with the correspondent sequence to the introduced gene, no json format
                        contents = """
                                           <html>
                                           <body style="background-color: pink;">
                                           <font face="Trebuchet MS">The sequence corresponding to gene</font>
                                           """+gene+'\n'+"""<font face="Trebuchet MS">is</font>"""+'\n'+sequence+"""
                                           </body>
                                           </html>
                                           """
                except KeyError:  # In the case not such gene exists
                    response_status = 404
                    filename = open('error.html', 'r')
                    contents = filename.read()

            else:  # In the case no 'gene' parameter appears or it is in blank
                response_status=404
                filename =open('error.html','r')
                contents = filename.read()

# LET'S DEAL WITH THE FIFTH ENDPOINT: /geneInfo
        elif '/geneInfo' in self.path:
            parameters = self.extract_parameters(self.path)  # Let's get the parameter 'gene'
            if 'gene' in parameters and parameters['gene'] != '':  # In the case value for 'gene' is present, not blank
                gene = parameters['gene']
                try:
                    conn = http.client.HTTPConnection(HOSTNAME)
                    conn.request('GET', '/homology/symbol/human/' + gene + '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    id = answer['data'][0]['id']  # Let's get the necessary ID for asking for the data

                    conn.request('GET', '/overlap/id/' + id + '?feature=gene;content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE AND CLOSE THE CONNECTION
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    start = answer[0]['start']   # Define start
                    end = answer[0]['end']   # Define end
                    length = end - start   # Define length
                    chromosome = answer[0]['seq_region_name'] # Define chromosome

                    if 'json' in parameters:  # In the case the json option is chosen
                        json_option = True
                        info_dictionary = dict()
                        info_dictionary['start']=start
                        info_dictionary['end'] = end
                        info_dictionary['length'] = length
                        info_dictionary['chromosome'] = chromosome
                        contents = json.dumps(info_dictionary)   # Return the information in a json format

                    else:   # If no json is requested, return a page with the information
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
                except KeyError: # In case no such gene exists
                    response_status = 404
                    filename = open('error.html', 'r')
                    contents = filename.read()

            else: # In the case no 'gene' parameter appears or it is in blank
                response_status=404
                filename =open('error.html','r')
                contents = filename.read()

# LET'S DEAL WITH THE SIXTH ENDPOINT: /geneCalc

        elif '/geneCalc' in self.path:
            parameters = self.extract_parameters(self.path)  # Let's extract the parameter 'gene'

            if 'gene' in parameters and parameters['gene'] != '': # In the case value for 'gene' is present, not blank
                gene = parameters['gene']
                try:
                    conn = http.client.HTTPConnection(HOSTNAME)
                    conn.request('GET', '/homology/symbol/human/' + gene + '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    id = answer['data'][0]['id']   # Let's get the necessary ID for asking for the data

                    conn.request('GET', '/sequence/id/' + id + '?content-type=application/json')

                    # WAIT FOR THE SERVER RESPONSE
                    r1 = conn.getresponse()

                    # READ THE RESPONSE
                    text_json = r1.read().decode("utf-8")
                    answer = json.loads(text_json)
                    sequence = answer['seq']  # Define sequence
                    seq = Seq(sequence)  # Use the function Seq to create the sequence
                    length = len(sequence)  # Get the length of the sequence
                    percA = seq.perc('A')   # Get all the percentages from the bases A, C, T, G
                    percC = seq.perc('C')
                    percT = seq.perc('T')
                    percG = seq.perc('G')

                    if 'json' in parameters:  # In the case json format is asked
                        json_option = True
                        calc_dictionary = dict()
                        calc_dictionary['sequence']=sequence
                        calc_dictionary['percentage A'] = percA
                        calc_dictionary['percentage C'] = percC
                        calc_dictionary['percentage T'] = percG
                        calc_dictionary['percentage G'] = percG
                        calc_dictionary['length'] = length
                        contents = json.dumps(calc_dictionary)  # Return the information in a json format

                    else:  # In the case no json format is asked, return a page with the information
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
                except KeyError: # In the case the introduced 'gene' is not a valid one
                    response_status = 404
                    filename = open('error.html', 'r')
                    contents = filename.read()
            else:  # In the case no 'gene' parameter appears or it is in blank
                response_status=404
                filename =open('error.html','r')
                contents = filename.read()

        # LET'S DEAL WITH THE SEVENTH ENDPOINT: /geneList
        elif "/geneList" in self.path:
            parameters = self.extract_parameters(self.path)  # Get the parameters from our function

            # In the case 'chromo', 'start', 'end' parameters are present and there are not in blank
            if ('chromo' in parameters and 'start' in parameters and 'end' in parameters) and (parameters['chromo'] != "" and parameters['start'] != "" and parameters['end'] != ""):
                chromo = parameters['chromo']  # Define chromo
                start = parameters['start']   # Define start
                end = parameters['end']   # Define end

                try:
                    conn = http.client.HTTPConnection("rest.ensembl.org")
                    conn.request("GET", "/overlap/region/human/" + str(chromo) + ":" + str(start) + "-" + str(end) + "?content-type=application/json;feature=gene;feature=transcript;feature=cds;feature=exon")
                    r1 = conn.getresponse()
                    data1 = r1.read().decode("utf-8")
                    answer = json.loads(data1)
                    
                    if 'json' in parameters:  # In the case json format is requested
                        json_option = True
                        list = []  # Create a list

                        for element in answer:

                            if (element['feature_type'] == "gene"):
                                gene_dictionary = dict()
                                gene_dictionary['name'] = element['external_name']
                                gene_dictionary['start'] = element['start']
                                gene_dictionary['end'] = element['end']
                                list.append(gene_dictionary)   # Create a dictionary with the requested information

                        contents = json.dumps(list)  # And return it in a json format

                    else:  # If no json is requested
                    # Return a page with the requested information
                        contents = """
                                <html>
                                <body style= "background-color: pink;">
                                <font face="Trebuchet MS">The names of the genes located in chromosome""" + '\n' + chromo + ' from position '+ start+ ' to position ' + end + ' are: '+ """<ul>"""

                        for element in answer:  # Let's iterate over all the available genes in that chromosome

                            if (element['feature_type'] == "gene"):
                                contents = contents + "<li>" + (
                                            str(element['external_name']) + " " + str(element['start']) + " " + str(element['end'])) + "</li>"

                        contents = contents + """</ul></body></html>"""  # And send the gene, the start and the end


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

            else:  # In case one of the parameters is in blank or is not present
                response_status = 404
                f = open("error.html", 'r')
                contents = f.read()

        else:  # In case we introduce an invalid ENDPOINT
            response_status = 404
            filename = 'error.html'
            with open(filename, 'r') as f:
                contents = f.read()


        # Generating the response message
        self.send_response(response_status)

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

# Server MAIN program

# Set the new handler
Handler = TestHandler
socketserver.TCPServer.allow_reuse_address = True

# Open the socket server
with socketserver.TCPServer(("", PORT), Handler) as httpd:

    print("Serving at PORT", PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Stoped by the user")
        httpd.server_close()