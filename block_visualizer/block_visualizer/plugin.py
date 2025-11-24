import json
from api.api.base_visualizer import BaseVisualizer
from api.api.graph import Graph

class BlockVisualizer(BaseVisualizer):
    def name(self) -> str:
        return "Block Visualizer"

    def render(self, graph: Graph) -> str:
        # --- 1. PRIPREMA PODATAKA ---
        nodes_data = []
        for n in graph.nodes:
            attrs = getattr(n, "data", {})
            filtered_attrs = {k: v for k, v in attrs.items() if k not in ['id', 'label']}
            
            # FIX: Ako je label prazan string, koristi ID
            label_text = n.label if n.label else n.id

            nodes_data.append({
                "id": str(n.id), 
                "label": str(label_text), # Šaljemo popunjen label ili ID
                "attributes": filtered_attrs
            })

        links_data = []
        for e in graph.edges:
            s = e.source.id if hasattr(e.source, "id") else e.source
            t = e.target.id if hasattr(e.target, "id") else e.target
            links_data.append({"source": str(s), "target": str(t)})

        graph_json = json.dumps({"nodes": nodes_data, "links": links_data})

        # --- 2. GENERISANJE HTML-a ---
        js_logic = f"""
            (function() {{
                try {{
                    const data = GRAPH_DATA_PLACEHOLDER;
                    const container = document.getElementById('block-viz-container');
                    
                    if (!container) throw new Error("Container not found");
                    
                    const width = container.clientWidth || 800;
                    const height = 600;
                    
                    const nodeWidth = 180; 
                    const headerHeight = 30;
                    const lineHeight = 18;
                    const padding = 10;

                    d3.select("#block-viz-container").html("");

                    const svg = d3.select("#block-viz-container").append("svg")
                        .attr("width", "100%")
                        .attr("height", height)
                        .style("background-color", "#f9f9f9")
                        .call(d3.zoom().on("zoom", (event) => g.attr("transform", event.transform)));

                    const g = svg.append("g");

                    const simulation = d3.forceSimulation(data.nodes)
                        .force("link", d3.forceLink(data.links).id(d => d.id).distance(250))
                        .force("charge", d3.forceManyBody().strength(-2000))
                        .force("center", d3.forceCenter(width / 2, height / 2))
                        .force("collide", d3.forceCollide(nodeWidth / 1.5));

                    svg.append("defs").append("marker")
                        .attr("id", "arrowhead-block")
                        .attr("viewBox", "0 -5 10 10")
                        .attr("refX", nodeWidth/2 + 10) 
                        .attr("refY", 0)
                        .attr("markerWidth", 6).attr("markerHeight", 6)
                        .attr("orient", "auto")
                        .append("path").attr("d", "M0,-5L10,0L0,5").attr("fill", "#555");

                    const link = g.append("g").selectAll("line")
                        .data(data.links).join("line")
                        .attr("stroke", "#555").attr("stroke-width", 2)
                        .attr("marker-end", "url(#arrowhead-block)");

                    const node = g.append("g").selectAll("g")
                        .data(data.nodes).join("g")
                        .call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));

                    node.append("rect")
                        .attr("class", "node-box")
                        .attr("width", nodeWidth)
                        .attr("x", -nodeWidth / 2)
                        .attr("rx", 8).attr("ry", 8)
                        .attr("fill", "white")
                        .attr("stroke", "#2c3e50").attr("stroke-width", 2);

                    // 2. Naslov (FIX: Prikazuje Labelu ILI ID ako je labela prazna)
                    node.append("text")
                        .text(d => d.label || d.id) 
                        .attr("y", -headerHeight/2 - 5)
                        .attr("text-anchor", "middle")
                        .style("font-weight", "bold")
                        .style("font-family", "sans-serif")
                        .style("font-size", "14px")
                        .style("fill", "#2c3e50");

                    node.append("line")
                        .attr("x1", -nodeWidth/2).attr("y1", -10)
                        .attr("x2", nodeWidth/2).attr("y2", -10)
                        .attr("stroke", "#eee").attr("stroke-width", 2);

                    node.each(function(d) {{
                        const el = d3.select(this);
                        let yPos = 10; 
                        
                        if (d.attributes && typeof d.attributes === 'object') {{
                            Object.entries(d.attributes).forEach(([key, val]) => {{
                                let valStr = String(val);
                                if (valStr.length > 20) valStr = valStr.substring(0, 17) + "...";
                                
                                let textStr = key + ": " + valStr;

                                el.append("text")
                                    .text(textStr)
                                    .attr("y", yPos)
                                    .attr("x", -nodeWidth/2 + 10)
                                    .style("font-size", "12px")
                                    .style("font-family", "monospace")
                                    .style("fill", "#555");
                                
                                yPos += lineHeight;
                            }});
                        }}

                        const contentHeight = Math.max(50, yPos + padding);
                        const totalHeight = contentHeight + headerHeight;

                        el.select("rect.node-box")
                            .attr("height", totalHeight)
                            .attr("y", -headerHeight - 10);
                    }});

                    simulation.on("tick", () => {{
                        link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                            .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                        node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
                    }});

                    function dragstarted(event, d) {{ if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }}
                    function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
                    function dragended(event, d) {{ if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}

                }} catch (err) {{
                    console.error("Block Visualizer Error:", err);
                    document.getElementById('block-viz-container').innerHTML = 
                        `<div style='color:red; padding:20px;'>Greska u renderovanju: ${{err.message}}</div>`;
                }}
            }})();
        """
        
        js_code = js_logic.replace("GRAPH_DATA_PLACEHOLDER", graph_json)

        return f"""
        <div id="block-viz-container" style="width:100%; height:600px; border:1px solid #ddd; background: #f9f9f9;"></div>
        <script>
            {js_code}
        </script>
        """