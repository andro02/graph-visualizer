from api.api.base_visualizer import BaseVisualizer
from api.api.graph import Graph

class BlockVisualizer(BaseVisualizer):
    """
    Implementacija Block Visualizer-a.
    Prikazuje cvorove kao HTML blokove.
    """

    def render(self, graph: Graph) -> str:
        """
        Generise HTML string gde je svaki svor predstavljen kao vizuelni blok.
        """
        # Container koristi Flexbox da bi "lepio" blokove jedan do drugog
        container_style = (
            "display: flex; "
            "flex-wrap: wrap; "
            "gap: 20px; "
            "padding: 20px; "
            "font-family: Arial, sans-serif; "
            "background-color: #f9f9f9;"
        )
        
        # Stil za pojedinačni blok
        node_style = (
            "border: 2px solid #34495e; "
            "border-radius: 8px; "
            "padding: 15px; "
            "width: 300px; "
            "background-color: #ffffff; "
            "box-shadow: 2px 2px 5px rgba(0,0,0,0.1);"
        )

        header_style = "margin-top: 0; color: #2980b9; border-bottom: 1px solid #eee; padding-bottom: 5px;"
        list_style = "list-style-type: none; padding: 0; margin: 10px 0 0 0;"
        item_style = "font-size: 14px; color: #555; margin-bottom: 4px;"

        # --- GENERISANJE HTML-a ---
        html_parts = [f'<div class="graph-container" style="{container_style}">']

        # Provera da li je graf prazan
        if not hasattr(graph, 'nodes') or not graph.nodes:
            return '<div style="padding:20px;"><i>Graf je prazan.</i></div>'

        # renderovanje cvorova
        for node in graph.nodes:
            # Naslov je labela ili ID ako labela fali
            title = getattr(node, 'label', node.id) or node.id
            
            # Pocetak bloka
            html_parts.append(f'<div class="node-block" style="{node_style}">')
            html_parts.append(f'<h3 style="{header_style}">{title}</h3>')
            html_parts.append(f'<small style="color: #999;">ID: {node.id}</small>')
            
            # Prikaz atributa iz 'data' dict
            html_parts.append(f'<ul style="{list_style}">')
            
            # Proveravamo da li node ima 'data' (za atribute)
            node_data = getattr(node, 'data', {})
            if node_data:
                for key, value in node_data.items():
                    if key not in ['id', 'label']: #vec u naslovu
                        html_parts.append(f'<li style="{item_style}"><strong>{key}:</strong> {value}</li>')
            else:
                html_parts.append(f'<li style="{item_style}"><i>Nema atributa</i></li>')
            
            html_parts.append('</ul>')
            html_parts.append('</div>') #kraj bloka

        html_parts.append('</div>') #kraj kontejnera

        # renderovanje garna
        if hasattr(graph, 'edges') and graph.edges:
            html_parts.append('<div style="padding: 20px; border-top: 1px solid #ccc;">')
            html_parts.append('<h4>Veze (Relacije):</h4><ul>')
            
            for edge in graph.edges:
                src = edge.source
                dst = edge.target
                html_parts.append(f'<li>{src} &rarr; {dst}</li>')
            
            html_parts.append('</ul></div>')

        return "".join(html_parts)