import json
from api.api.base_visualizer import BaseVisualizer
from api.api.graph import Graph

class SimpleVisualizer(BaseVisualizer):
    def name(self) -> str:
        return "Simple Visualizer"

    def render(self, graph: Graph) -> str:
        # --- 1. PRIPREMA PODATAKA ---
        nodes_data = [{"id": str(n.id), "label": str(getattr(n, "label", n.id))} for n in graph.nodes]
        
        links_data = []
        for e in graph.edges:
            s = e.source.id if hasattr(e.source, "id") else e.source
            t = e.target.id if hasattr(e.target, "id") else e.target
            links_data.append({"source": str(s), "target": str(t)})

        graph_json = json.dumps({"nodes": nodes_data, "links": links_data})

        # --- 2. GENERISANJE HTML-a ---
        js_code = f"""
            (function() {{
                try {{
                    const data = GRAPH_DATA_PLACEHOLDER;
                    
                    // Kontejneri
                    const mainContainer = document.getElementById('simple-viz-container');
                    const birdContainer = document.getElementById('bird-view-container');
                    
                    if (!mainContainer || !birdContainer) return;

                    const width = mainContainer.clientWidth;
                    const height = mainContainer.clientHeight; 
                    
                    // Skaliranje za minimapu (20% velicine)
                    const minimapScale = 0.2; 

                    // --- 1. MAIN VIEW SETUP ---
                    d3.select("#simple-viz-container").html("");
                    const svg = d3.select("#simple-viz-container").append("svg")
                        .attr("width", "100%").attr("height", height)
                        .style("background", "white")
                        .attr("viewBox", `0 0 ${{width}} ${{height}}`); // Bitno za koordinatni sistem

                    const g = svg.append("g");

                    // --- 2. BIRD VIEW SETUP ---
                    d3.select("#bird-view-container").html("");
                    const birdSvg = d3.select("#bird-view-container").append("svg")
                        .attr("width", "100%").attr("height", "100%")
                        .style("background", "#f5f5f5") // Malo tamnija pozadina da se razlikuje
                        .style("border", "1px solid #ccc");
                    
                    // FIX: Uklonjen translate, samo scale. 
                    // Posto simulacija centrira cvorove na width/2, height/2, 
                    // oni ce na minimapi biti na (width/2)*0.2, (height/2)*0.2
                    const birdG = birdSvg.append("g")
                        .attr("transform", `scale(${{minimapScale}})`);

                    const viewportRect = birdSvg.append("rect")
                        .attr("fill", "none").attr("stroke", "red").attr("stroke-width", 2);

                    // --- ZOOM ---
                    const zoom = d3.zoom()
                        .scaleExtent([0.1, 4])
                        .on("zoom", (event) => {{
                            // 1. Pomeramo glavni graf
                            g.attr("transform", event.transform);
                            
                            // 2. Azuriramo crveni pravougaonik na mapi
                            const t = event.transform;
                            
                            // Invertujemo transformaciju da dobijemo sta se vidi
                            // x na mapi = ((-t.x / t.k) * scale)
                            const mapX = (-t.x / t.k) * minimapScale;
                            const mapY = (-t.y / t.k) * minimapScale;
                            const mapW = (width / t.k) * minimapScale;
                            const mapH = (height / t.k) * minimapScale;

                            viewportRect
                                .attr("x", mapX)
                                .attr("y", mapY)
                                .attr("width", mapW)
                                .attr("height", mapH);
                        }});

                    svg.call(zoom);

                    // Definicija strelice (arrowhead)
                    
                    svg.append("defs").append("marker")
                        .attr("id", "arrow")
                        .attr("viewBox", "0 0 10 10")
                        .attr("refX", 30)      
                        .attr("refY", 5)
                        .attr("markerWidth", 6)
                        .attr("markerHeight", 6)
                        .attr("markerUnits", "strokeWidth")
                        .attr("orient", "auto")
                        .append("path")
                        .attr("d", "M 0 0 L 10 5 L 0 10 z")
                        .attr("fill", "#999");

                    // --- SIMULATION ---
                    // Centriramo simulaciju tacno u centar glavnog kontejnera
                    const simulation = d3.forceSimulation(data.nodes)
                        .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
                        .force("charge", d3.forceManyBody().strength(-300))
                        .force("center", d3.forceCenter(width / 2, height / 2));

                    // --- FUNKCIJA ZA CRTANJE ---
                    function drawGraph(containerGroup, isMinimap) {{

                        const link = containerGroup.append("g").selectAll("line")
                            .data(data.links).join("line")
                            .attr("stroke", "#999")
                            .attr("stroke-width", isMinimap ? 3 : 2)
                            .attr("marker-end", isMinimap ? null : "url(#arrow)");

                        const node = containerGroup.append("g").selectAll("g") // Grupa za krug i tekst
                            .data(data.nodes).join("g");

                        // Krug
                        node.append("circle")
                            .attr("r", isMinimap ? 6 : 20) // Velicina
                            .attr("fill", isMinimap ? "#888" : "#e3f2fd") // FIX: Plava boja na glavnom, siva na mapi
                            .attr("stroke", "#333")
                            .attr("stroke-width", isMinimap ? 0 : 2);

                        // Tekst (samo na glavnom)
                        if (!isMinimap) {{
                            node.append("text")
								.text(d => d.label || d.id)
								.attr("text-anchor", "middle")
								.attr("dy", 5)
								.style("font-family", "sans-serif")
								.style("font-size", "12px")
								.style("pointer-events", "none"); // Da ne smeta pri kliku
                                
                            node.call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));
                        }}
                        
                        return {{ link, node }};
                    }}

                    const mainViz = drawGraph(g, false);
                    const birdViz = drawGraph(birdG, true);

                    // --- TICK ---
                    simulation.on("tick", () => {{
                        // Main View Update
                        mainViz.link
                            .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                            .attr("x2", d => d.target.x).attr("y2", d => d.target.y)
                            .attr("marker-end", "url(#arrow)");
                        
                        // Kod grupa (g) koristimo translate
                        mainViz.node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);

                        // Bird View Update (Iste koordinate!)
                        birdViz.link
                            .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                            .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                            
                        birdViz.node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
                    }});

                    function dragstarted(event, d) {{ if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }}
                    function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
                    function dragended(event, d) {{ if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}
                    
                    // Inicijalizacija zooma na 0,0 (da se crveni pravougaonik pojavi odmah)
                    svg.call(zoom.transform, d3.zoomIdentity);

                }} catch (err) {{
                    console.error("Simple Visualizer Error:", err);
                }}
            }})();
        """
        
        js_code = js_code.replace("GRAPH_DATA_PLACEHOLDER", graph_json)

        return f"""
        <div id="simple-viz-container" style="width:100%; height:100%; border:1px solid #ddd; background: white;"></div>
        <script>
            {js_code}
        </script>
        """
    