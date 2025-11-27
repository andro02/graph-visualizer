import csv
from datetime import datetime
import os
from typing import Dict, Any, List
from api.api.data_source import DataSourcePlugin, PluginParameter, PluginParameterType
from api.api.graph import Node, Edge, Graph

def parse_value(v: str):
        """Pokuša da konvertuje vrednost u int, float, date ili ostavi kao string."""
        v = v.strip()
        if not v:
            return None
        # 1. Pokušaj int
        try:
            return int(v)
        except ValueError:
            pass
        # 2. Pokušaj float
        try:
            return float(v)
        except ValueError:
            pass
        # 3. Pokušaj datum (YYYY-MM-DD)
        try:
            dt = datetime.strptime(v, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")  # ostavi kao string za JSON
        except ValueError:
            pass
        # 4. Ako ništa, ostavi kao string
        return v

class CSVDataSource(DataSourcePlugin):
    """
    CSV format (jedan fajl) sa automatskom detekcijom usmerenog / neusmerenog grafa.
    """

    def name(self) -> str:
        return "CSV Data Source"

    def get_parameters(self) -> List[PluginParameter]:
        return [
            PluginParameter(
                name="path",
                description="Putanja do CSV fajla",
                type=PluginParameterType.FILE
            ),
            PluginParameter(
                name="graph_name",
                description="Naziv grafa",
                type=PluginParameterType.TEXT,
                is_required=False,
                default_value="CSV Graph"
            )
        ]

    def parse(self, parameters: Dict[str, Any]) -> Graph:
        csv_path = parameters.get("path", parameters.get("csv_path"))
        graph_name = parameters.get("graph_name", "CSV Graph")

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV fajl nije pronađen: {csv_path}")

        nodes = {}
        edges_raw = []   # privremeno sve ivice

        # --- 1. ČITANJE CSV FAJLA ---
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                node_id = row["id"]
                label = row.get("label", node_id)

                # Ekstraktujemo atribute osim specijalnih kolona
                node_data = {k: parse_value(v) for k, v in row.items() if k not in ["id", "label", "target", "weight"] and v.strip() != ""}

                # Kreiranje čvora ako ne postoji
                if node_id not in nodes:
                    nodes[node_id] = Node(
                        id=node_id,
                        label=label,
                        data={"id": node_id, "label": label, **node_data}
                    )
                else:
                    nodes[node_id].data.update(node_data)

                # Obrada ivica
                target = row.get("target")
                if target and target.strip():
                    if target not in nodes:
                        nodes[target] = Node(
                            id=target,
                            label=target,
                            data={"id": target, "label": target}
                        )

                    weight = float(row.get("weight", 1) or 1)
                    edges_raw.append((node_id, target, weight))

        # --- 2. AUTOMATSKA DETEKCIJA USMEREN / NEUSMEREN ---
        edge_pairs = {(s, t) for (s, t, w) in edges_raw}

        is_undirected = True
        for (u, v) in edge_pairs:
            if (v, u) not in edge_pairs:
                is_undirected = False
                break

        # --- 3. KREIRANJE LISTE IVICA ---
        edges = []

        if is_undirected:
            # ukloni duplikate: A-B i B-A
            unique_pairs = set()
            for (s, t, w) in edges_raw:
                key = tuple(sorted([s, t]))
                if key not in unique_pairs:
                    unique_pairs.add(key)
                    edges.append(Edge(source=s, target=t, weight=w))
        else:
            # usmeren graf → uzmi sve ivice
            for (s, t, w) in edges_raw:
                edges.append(Edge(source=s, target=t, weight=w))

        # --- 4. KREIRANJE Grafa ---
        g = Graph(name=graph_name, directed=not is_undirected)

        for node in nodes.values():
            g.add_node(node)

        for edge in edges:
            g.add_edge(edge)

        return g
