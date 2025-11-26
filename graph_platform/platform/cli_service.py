from api.api.graph import Graph, Node, Edge

class CLIService:
    def execute_command(self, graph: Graph, command_str: str):
        """
        Parsira komandu i izvsava je nad grafom.
        graph nam treba da bismo pozvali filter/search servise ako je potrebno.
        """
        # print(command_str)
        parts = command_str.strip().split()
        if not parts:
            return {"Error": "Empty command", "graph": graph}


        action = parts[0].lower() # create, edit, delete, filter, search, clear

        try:
            if action == "create":
                return self._handle_create(graph, parts[1:])
            elif action == "edit":
                return self._handle_edit(graph, parts[1:])
            elif action == "delete":
                return self._handle_delete(graph, parts[1:])
            elif action == "filter":
                # Ocekujemo format: filter 'Age>30'
                # Spajamo sve posle 'filter' u jedan string i sklanjamo navodnike
                query = " ".join(parts[1:]).strip("'\"")
                return self._handle_filter(graph, query)
            elif action == "search":
                query = " ".join(parts[1:]).strip("'\"")
                return self._handle_search(graph, query)
            elif action == "clear":
                graph.nodes = []
                graph.edges = []
                return graph
            else:
                return graph
        except Exception as e:
            return graph

    def _handle_create(self, graph, args):
        entity_type = args[0].lower() # node, edge
        params = self._parse_args(args[1:])

        if entity_type == "node":
            node_id = params.get("id")
            if not node_id: raise ValueError("Missing --id")
            
            # Provera da li postoji
            if any(n.id == node_id for n in graph.nodes):
                raise ValueError(f"Node {node_id} already exists.")

            new_node = Node(id=node_id, data=params.get("properties", {}))
            graph.add_node(new_node) # Pretpostavljamo da ova metoda postoji u graph.py
            return graph

        elif entity_type == "edge":
            edge_id = params.get("id") # Opciono ako Edge ima ID
            
            # Kod edges, source i target su obicno pozicioni argumenti na kraju komande
            # create edge --prop... 1 2
            # Moramo izvuci source i target iz args koji nisu --flags
            plain_args = [a for a in args[1:] if not a.startswith("--") and "=" not in a]
            
            if len(plain_args) < 2:
                raise ValueError("Source and Target IDs required for edge.")
            
            source_id, target_id = plain_args[-2], plain_args[-1]
            
            # Provera da li cvorovi postoje
            if not any(n.id == source_id for n in graph.nodes) or not any(n.id == target_id for n in graph.nodes):
                raise ValueError("Source or Target node does not exist.")

            new_edge = Edge(source=source_id, target=target_id, data=params.get("properties", {}))
            graph.add_edge(new_edge)
            return graph

    def _handle_edit(self, graph, args):
        entity_type = args[0].lower()
        params = self._parse_args(args[1:])
        target_id = params.get("id")

        if entity_type == "node":
            node = next((n for n in graph.nodes if str(n.id) == target_id), None)
            if not node: raise ValueError("Node not found.")
            
            # Azuriranje propertija
            new_props = params.get("properties", {})
            node.data.update(new_props)
            return graph
            
        elif entity_type == "edge":
            # Za edge je teze naci "taj jedan" ako nemaju ID, 
            # ali recimo da editujemo na osnovu source/target ako su prosledjeni
            pass 
        
        return graph

    def _handle_delete(self, graph, args):
        entity_type = args[0].lower()
        
        if entity_type == "node":
            params = self._parse_args(args[1:])
            node_id = params.get("id")
            
            # 1. Provera da li je povezan (Constraint iz zadatka)
            is_connected = any(str(e.source) == node_id or str(e.target) == node_id for e in graph.edges)
            if is_connected:
                raise ValueError(f"Cannot delete node {node_id}: It has connected edges. Delete edges first.")

            # 2. Brisanje
            initial_len = len(graph.nodes)
            graph.nodes = [n for n in graph.nodes if str(n.id) != node_id]
            
            if len(graph.nodes) == initial_len:
                return graph
            return graph

        elif entity_type == "edge":
            # Trazimo source i target u argumentima
            plain_args = [a for a in args[1:] if not a.startswith("--")]
            if len(plain_args) < 2: return graph
            s, t = plain_args[0], plain_args[1]
            
            graph.edges = [e for e in graph.edges if not (str(e.source) == s and str(e.target) == t)]
            return graph

    def _handle_filter(self, graph, query):
        # Parsiranje query stringa 'Age>30' u atribute, operator, value
        # Ovo je jednostavan parser, moze se nadograditi regexom
        operators = [">=", "<=", "!=", "=", ">", "<", "contains"]
        attr, op, val = None, None, None
        
        for o in operators:
            if o in query:
                parts = query.split(o)
                attr = parts[0].strip()
                op = o
                val = parts[1].strip()
                break
        
        if attr and op and val:
            graph.apply_filter(attr, op, val)
            return graph
        return graph

    def _handle_search(self, graph, query):
        # create node ... Name=Tom -> search 'Name=Tom' -> ili samo 'Tom'
        # Ako je format 'Name=Tom', parsiramo, ako je samo tekst, trazimo svuda
        graph.apply_search(query)
        return graph

    def _parse_args(self, args_list):
        """Pomocna funkcija za --id=1 --property Name=Alice"""
        res = {"properties": {}}
        for arg in args_list:
            if arg.startswith("--id="):
                res["id"] = arg.split("=", 1)[1]
            elif arg.startswith("--property"):
                # format: --property key=value
                # ocekuje se da sledeci deo u listi bude key=value ako ima razmaka, 
                # ali ovde pojednostavljujemo: pretpostavljamo da je --property Key=Value jedan string ili su spojeni
                pass 
            elif "=" in arg and not arg.startswith("--"):
                # Pretpostavljamo da je properti ako ima = (npr Name=Alice)
                k, v = arg.split("=", 1)
                res["properties"][k] = v
        return res
