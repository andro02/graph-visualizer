from api.api.base_visualizer import BaseVisualizer
from api.api.graph import Graph

class SimpleVisualizer(BaseVisualizer):
    """
    Implementacija Simple Visualizer-a.
    Prikazuje cvorove kao jednostavne krugove
    """

    def name(self) -> str:
        return "Simple Visualizer"

    def render(self, graph: Graph) -> str:
        """
        Generiše HTML string gde su cvorovi prikazani kao krugovi.
        """
        container_style = (
            "display: flex; "
            "flex-wrap: wrap; "
            "gap: 15px; "
            "padding: 20px; "
            "justify-content: center; " 
            "font-family: sans-serif; "
            "background-color: #fff;"
        )
        
        node_style = (
            "width: 80px; "
            "height: 80px; "
            "border-radius: 50%; " 
            "background-color: #3498db; "
            "color: white; "
            "display: flex; "
            "align-items: center; "
            "justify-content: center; "
            "text-align: center; "
            "font-size: 12px; "
            "border: 2px solid #2980b9; "
            "box-shadow: 2px 2px 5px rgba(0,0,0,0.2); "
            "overflow: hidden; "
            "padding: 5px;"
        )

        html_parts = [f'<div style="{container_style}">']

        if not hasattr(graph, 'nodes') or not graph.nodes:
            return f'<div style="{container_style}"><i>Graf je prazan.</i></div>'

        for node in graph.nodes:
            # Prikazujemo samo Labelu ili ID (bez ostalih atributa - to je poenta Simple prikaza)
            label = getattr(node, 'label', str(node.id)) or str(node.id)
            
            # Tooltip (title atribut) će prikazati ID kad se pređe mišem
            html_parts.append(
                f'<div style="{node_style}" title="ID: {node.id}">'
                f'<strong>{label}</strong>'
                f'</div>'
            )

        html_parts.append('</div>')

        if hasattr(graph, 'edges') and graph.edges:
            html_parts.append('<div style="padding: 20px; text-align: center; color: #555;">')
            html_parts.append('<h4>Struktura veza:</h4><ul style="list-style: none; padding: 0;">')
            
            for edge in graph.edges:
                s = edge.source
                t = edge.target
                html_parts.append(f'<li>{s} &mdash; {t}</li>')
            
            html_parts.append('</ul></div>')

        return "".join(html_parts)