import json
from api.api.base_visualizer import BaseVisualizer
from api.api.graph import Graph

class SimpleVisualizer(BaseVisualizer):
    def name(self) -> str:
        return "Simple Visualizer"

    def render(self, graph: Graph) -> str:
        # 1. Priprema podataka za JS
        nodes_data = [{"id": n.id, "label": getattr(n, "label", n.id)} for n in graph.nodes]
        
        # Pazimo da source i target budu ID-jevi
        links_data = []
        for e in graph.edges:
            s = e.source.id if hasattr(e.source, "id") else e.source
            t = e.target.id if hasattr(e.target, "id") else e.target
            links_data.append({"source": s, "target": t})

        # Serijalizujemo u JSON string da bi ga ubacili u JS
        graph_json = json.dumps({"nodes": nodes_data, "links": links_data})

        # 2. Generisanje HTML-a i Skripte
        # Koristimo D3.js sa CDN-a
        html = f"""
        <div id="simple-viz-container" style="width:100%; height:600px; border:1px solid #ddd; background: white;"></div>
        <script>
            (function() {{
                const data = {graph_json};
                const width = document.getElementById('simple-viz-container').clientWidth;
                const height = 600;

                // Čišćenje prethodnog sadržaja
                d3.select("#simple-viz-container").html("");

                const svg = d3.select("#simple-viz-container")
                    .append("svg")
                    .attr("width", width)
                    .attr("height", height)
                    .call(d3.zoom().on("zoom", (event) => {{
                        g.attr("transform", event.transform);
                    }}));

                const g = svg.append("g");

                const simulation = d3.forceSimulation(data.nodes)
                    .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-300))
                    .force("center", d3.forceCenter(width / 2, height / 2));

                // Iscrtavanje veza (linije)
                const link = g.append("g")
                    .selectAll("line")
                    .data(data.links)
                    .join("line")
                    .attr("stroke", "#999")
                    .attr("stroke-width", 2);

                // Iscrtavanje čvorova (krugovi)
                const node = g.append("g")
                    .selectAll("g")
                    .data(data.nodes)
                    .join("g")
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));

                node.append("circle")
                    .attr("r", 20)
                    .attr("fill", "white")
                    .attr("stroke", "#333")
                    .attr("stroke-width", 2);

                node.append("text")
                    .text(d => d.label || d.id)
                    .attr("text-anchor", "middle")
                    .attr("dy", 5)
                    .style("font-family", "sans-serif")
                    .style("font-size", "12px")
                    .style("pointer-events", "none"); // Da ne smeta pri kliku

                simulation.on("tick", () => {{
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);

                    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
                }});

                function dragstarted(event, d) {{
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }}

                function dragged(event, d) {{
                    d.fx = event.x;
                    d.fy = event.y;
                }}

                function dragended(event, d) {{
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }}
            }})();
        </script>
        """
        return html