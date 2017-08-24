# Introduzione e scopo del progetto
Il presente lavoro ha l'obiettivo di fare il design, implementare e testare un'applicazione 
su ambiente OSHI che permetta la configurazione automatica di indirizzi ipv6 su una topologia
relativamente semplice. A questo scopo è stata utilizzata la tecnologia [gRPC](grpc.io).
Essenzialmente è un framework multipiattaforma che permette di eseguire procedure su un server
remoto in modo scalabile e veloce. 

Nel seguito analizzeremo i passaggi che ci hanno permesso di raggiungere l'obbiettivo.

# Deploy
In questa sezione analizziamo in dettaglio i principali passaggi che hanno 
permesso l'inizializzazione dei server gRPC in ogni nodo della rete. 

Prima di tutto avevamo la necessità di comunicare al *deployer* della topologia
l'utilizzo dei server gRPC. A tale scopo è stata creata una semplice struttura
dati da inserire manualmente nell'output json della topologia in questione:

    "grpc_ipv6": {
      "path": "/path/del/server/grpc.py"
    }
    
L'unico attributo **"path"** indica il percorso del file python dove è 
implementato il server gRPC. 

In seguito abbiamo apportato delle modifiche al file python relativo al parsing 
del codice JSON generato nell'interfaccia web:

*~/workspace/Dreamer-Topology-Parser-and-Validator/topo_parser.py*:

    def parse_data(self):
        self.load_advanced()
        self.load_vertex()
        self.load_links()
        self.load_vss()
        self.create_subnet()
        self.load_grpc()  # load gRPC path 
        self.parsed = True
    ...
    def load_grpc(self):
        if self.verbose:
            print "*** Retrieve Grpc Options"
        grpc_ipv6 = self.json_data['grpc_ipv6'] if 'grpc_ipv6' in self.json_data else []
        self.path_grpc = grpc_ipv6['path']

La classe *TopoParser* viene istanziata nel file *~/workspace/Dreamer-Mininet-Extensions/mininet_deployer.py* che si occupa del 
deploy della rete creata nell'interfaccia web, ovvero dell'instaurazione dei nodi e 
dei links nell'emulatore Mininet. In particolare sono state aggiunte queste righe 
nella creazione della rete:

*mininet_deployer.py*

    if parser.path_grpc != "":
      net.grpc_path = parser.path_grpc

Come spiegato nel dettaglio a seguire, grazie a questa modifica assegnamo al campo
*grpc_path* del costruttore dell'estensione custom della classe Mininet, la stringa
contenente il path del server gRPC. 

La definizione dell'estensione della classe Mininet si trova nel file *~/workspace/Dreamer-Mininet-Extensions/mininet_extensions.py* dove sono definiti 
anche tutti i nodi personalizzati dell'ambiente OSHI. In questa classe, in
particolare nel metodo *start()*, avviene la vera e propria instaurazione dei 
server gRPC in tutti i nodi:

*mininet_extensions.py*

    if self.grpc_path != "":
        all_nodes = self.cr_oshis + self.pe_oshis + self.ce_routers
        start_server = ["python",self.grpc_path,"&"]
        print "Starting grpc servers with %s" % start_server
        for node in all_nodes: 
            node_name = node.name
            node.popen(start_server)  # with cmd (for some unsolved reason) we were not able to run python
            print "*** Starting grpc server on %s at %s" % (node_name, node.IP())

Inizialmente nell'array *all_nodes* vengono salvati i riferimenti agli 
oggetti "nodo" (da notare che abbiamo volutamente escluso i controllers in 
quato questi sarebbero i client del sistema gRPC) e salviamo in *start_server* 
il comando bash per eseguire i server. In seguito nel costrutto *foreach* 
cicliamo su tutti i nodi e in questi facciamo partire il server con il comando 
**node.popen(start_server)**. 

A questo proposito è doveroso aprire una parentesi:
il comando che viene utilizzato solitamente nei nodi mininet **node.cmd("")**,
non funzionava per il comando assegnato. Facendo diversi test ci siamo accorti 
che, per qualche motivo che ancora non ci è noto, questo comando non esegue 
applicativi python, ma tutto il resto sì. La soluzione più veloce è stata quella 
di utilizzare per l'appunto il metodo sopracitato che, ai nostri fini, era 
equivalente. 

A questo punto, una volta effettuato il deploy della topologia, tutti i nodi 
hanno il proprio server gRPC avviato, il cui funzionamento verrà esposto nella
sezione seguente.

# gRPC

Il motivo per cui usiamo gRPC è molto semplice: estendere le funzionalità di openflow tramite la tecnologia rpc.
Una soluzione alternativa sarebbe stata quella di usare le RESTapi ma in termini di prestazioni gRPC risulta nettamente superiore.

Al momento del deploy della rete ogni nodo, ad esclusione del controller, apre un socket sulla porta scelta per far comunicare server e client grpc (si è scelta la porta 50001). Precisamente il controller svolgerà la funzione di client mentre tutti gli altri nodi avranno la funzione di server. Questo perchè il controller vuole effettuare delle operazioni sui nodi che gestisce normalmente tramite openflow estendendo così le sue funzionalità con una tecnologia altrettanto prestazionale.

Un ulteriore vantaggio riscontrato è la semplicità del codice.
gRPC infatti, oltre ad avere una documentazione molto dettagliata, permette con facilità di realizzare un servizio utilizzando il linguaggio di programmazione che si desidera con poche righe e molto intuitivamente. La nostrà scelta è ricaduta su python. Vediamone i dettagli:

1) Si parte da un file con estensione .proto (qui si utilizza il linguaggio proto3). In questo andranno esplicitati sia i metodi di richiesta e risposta tra server e client sia i parametri che si vogliono controllare durante la comunicazione. Nel nostro caso, dato che abbiamo la necessità di configurare indirizzi ipv6 e le rotte sui nodi, si controlleranno i parametri **ipv6, subnet, interface** per ipv6 e **r_subnets, routes, r_devs** per le rotte. Il campo **mode** verrà utilizzato dal client e dal server per scegliere il tipo di servizio da utilizzare, o meglio scegliere se settare: indirizzi ipv6, rotte ipv6, indirizzi e rotte ipv6.

*ipset.proto*

    ...
	message Request {
	  repeated string ipv6 = 1;
	  string subnet = 2;
	  repeated string iface = 3;
	  repeated string r_subnets = 4;
	  repeated string routes = 5;
	  repeated string r_devs = 6;
	  int32 mode = 7;
	}

	message Reply {
	  string message = 1;
	}
    ...

Successivamente il file viene compilato con gli appositi tool che python mette a disposizione, nel caso specifico:
    
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ipset.proto

Da qui vengono generati 2 file: **ipset_pb2.py** e **ipset_pb2_grpc.py** che contengono le classi e le funzioni necessarie per il passo successivo.

2) Ora dobbiamo creare il client ed il server utilizzando le 2 librerie generate al passo precendente.

*client.py*

    def run(remote_ipv4,ipv6,subnet,iface,r_subnets,routes,r_devs,mode):
        ok = False
        while not ok:
            try:
                channel = grpc.insecure_channel(remote_ipv4+":50001")
                stub = ipset_pb2_grpc.IpSetStub(channel)
                response = stub.Set(ipset_pb2.Request(ipv6=ipv6,subnet=subnet,iface=iface,
                                                      r_subnets=r_subnets, routes=routes, r_devs=r_devs,
                                                      mode=mode))
            except grpc._channel._Rendezvous as e:
                print e
                time.sleep(1)
                print "Retrying..."
            else:
                print "Server at {} says: {}".format(remote_ipv4,response.message)
                ok = True

Questo è la funzione chiave presente nel client. Volendo comunicare con i server ha bisogno dei loro indirizzi ipv4 e la porta scelta per la comunicazione gRPC. Da qui, se la richiesta va a buon fine, viene ricevuta una risposta di avvenuta comunicazione con l'ulteriore conferma che l'operazione che si voleva svolgere è andata a buon fine.

*server.py*
    
    ...
	class GiveMe(ipset_pb2_grpc.IpSetServicer):

		def Set(self, request, context):
			if request.mode == MODE_ADDR:
				set_addrs(request.ipv6, request.subnet, request.iface)
				return ipset_pb2.Reply(message='I have set {} on subnet /{} and interface {}'
											.format(request.ipv6,request.subnet,request.iface))

			elif request.mode == MODE_ROUTES:
				set_routes(request.r_subnets, request.routes, request.r_devs)
				return ipset_pb2.Reply(message='I have set the routes')

			elif request.mode == MODE_ADDR_ROUTES:
				set_addrs(request.ipv6, request.subnet, request.iface)
				set_routes(request.r_subnets, request.routes, request.r_devs)
				return ipset_pb2.Reply(message='I have set {} on subnet /{} and interface {} and set the routes'
											.format(request.ipv6,request.subnet,request.iface))

			else:
				return ipset_pb2.Reply(message="Unrecognized mode")


	def set_addrs(ipv6, subnet, iface):
		for i in range(len(ipv6)):
			print "Command: sudo ip -6 addr add "+ipv6[i]+"/"+subnet+" dev "+iface[i]
			os.system("sudo ip -6 addr add "+ipv6[i]+"/"+subnet+" dev "+iface[i])

	def set_routes(r_subnets, routes, r_devs):
		os.system('sudo sysctl -w net.ipv6.conf.all.forwarding=1')
		for i in range(len(r_subnets)):
			print "Command: sudo ip -6 r add "+r_subnets[i]+" via "+routes[i]+" dev "+r_devs[i]
			os.system("sudo ip -6 r add "+r_subnet[i]+" via "+routes[i]+" dev "+r_devs[i])

	def serve():
		server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
		ipset_pb2_grpc.add_IpSetServicer_to_server(GiveMe(), server)
		server.add_insecure_port('[::]:50001')
		server.start()
    ...

Il server è un tantino più complicato, ma nulla se si pensa che con poche righe abbiamo fatto svolgere una comunicazione molto efficente e, volendo, scalabile ad ogni servizio ci venga in mente.
Viene aperto un socket sulla porta 50001 in attesa di richieste provenienti dal client. Se si riceve una richiesta si controlla la variabile **mode** per interpretare quali operazioni è necessario svolgere, ossia: assegnazione di indirizzi ipv6, assegnazione di rotte o entrambe.
Vengono a questo punto lanciate le funzioni **set_addrs()** e/o **set_routes** in accordo con la variabile **mode** e successivamente recuperate le variabili spedite tramite richiesta grpc dal client. A questo punto si possono eseguire i comandi:

    ...
    os.system("sudo ip -6 addr add "+ipv6[i]+"/"+subnet+" dev "+iface[i])
    ...
    ...
    os.system("sudo ip -6 r add "+r_subnet[i]+" via "+routes[i]+" dev "+r_devs[i])
    ...

Viene poi inviata, tramite il metodo **Reply()**, la risposta al mittente dell'avvenuta configurazione richiesta.


# DEMO

In questa sezione descriviamo brevemente il procedimento per testare il lavoro esposto sopra.

- Una volta eseguita la macchina virtuale OSHI (in particolare abbiamo usato la versione 8),
    avviare lo script **GO** sul desktop. Il sistema procederà ad avviare il server e 
    l'interfaccia web del framework OSHI.
- Bisogna creare un nuovo progetto e utilizzare la topologia d'esempio chiamata *example_network_3cr_2pe_2ce*
- Adesso è necessario apportare una modifica al codice json che descrive la topogia:
    1. Selezionare *edit* nel menu a tendina;
    2. Accedere al codice json;
    3. Aggiungere l'oggetto json come proposto sopra;
    4. Salvare.
- Lanciare un *deployment* della topologia.
- Eseguire un terminale e accedere al controllore attraverso ssh, la password è **root**:
    
        ssh root@10.255.248.1 
        
- Avviare il client gRPC:
        
        cd /root/ipv6-oshi-grpc/grpc
        python client.py
        
- Se tutto è andato bene per ogni nodo della rete si dovrebbero ricevere dei messaggi di 
    avvenuta configurazione
- Eseguire lo script contenuto nel repository per configurare ipv6 sul controllore:

        ./ctrl_ipv6_conf.sh
        
- Eseguire dei ping di prova che verifichino il corretto funzionamento della rete ipv6:

        ping6 $node_ip
        
        



