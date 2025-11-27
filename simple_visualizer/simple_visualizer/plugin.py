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

        graph_json = json.dumps({"nodes": nodes_data, "links": links_data, "directed": graph.directed})

        # --- 2. GENERISANJE HTML-a ---
        js_code = f"""
            (function() {{
                try {{
                    const data = GRAPH_DATA_PLACEHOLDER;
                    
                    // Kontejneri
                    const mainContainer = document.getElementById('simple-viz-container');
                    const birdContainer = document.getElementById('bird-view-container');
                    
                    if (!mainContainer || !birdContainer) return;

                    const mainWidth = mainContainer.clientWidth;
                    const mainHeight = mainContainer.clientHeight || 600; 
                    
                    const birdWidth = birdContainer.clientWidth;
                    const birdHeight = birdContainer.clientHeight || 200;
                    
                    // Promenljive za dinamicko skaliranje
                    let currentMinimapScale = 1;
                    let currentMinimapX = 0;
                    let currentMinimapY = 0;
                    let currentMainTransform = d3.zoomIdentity;

                    // --- 1. MAIN VIEW SETUP ---
                    d3.select("#simple-viz-container").html("");
                    const svg = d3.select("#simple-viz-container").append("svg")
                        .attr("width", "100%").attr("height", "100%")
                        .style("background", "white")
                        .attr("viewBox", `0 0 ${{mainWidth}} ${{mainHeight}}`); 

                    const g = svg.append("g");

                    // --- 2. BIRD VIEW SETUP ---
                    d3.select("#bird-view-container").html("");
                    const birdSvg = d3.select("#bird-view-container").append("svg")
                        .attr("width", "100%").attr("height", "100%")
                        .style("background", "#f5f5f5") 
                        .style("border", "1px solid #ccc");
                    
                    const birdG = birdSvg.append("g"); // Bez fiksnog transforma

                    const viewportRect = birdSvg.append("rect")
                        .attr("fill", "none").attr("stroke", "red").attr("stroke-width", 2);

                    // --- ZOOM ---
                    const zoom = d3.zoom()
                        .scaleExtent([0.1, 4])
                        .on("zoom", (event) => {{
                            currentMainTransform = event.transform;
                            g.attr("transform", event.transform);
                            updateRedRectangle();
                        }});

                    svg.call(zoom);

                    // Definicija strelice (arrowhead)
                    if (data.directed) {{
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
                    }}

                    // --- SIMULATION ---
                    const simulation = d3.forceSimulation(data.nodes)
                        .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
                        .force("charge", d3.forceManyBody().strength(-300))
                        .force("center", d3.forceCenter(mainWidth / 2, mainHeight / 2));

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
                            .attr("fill", isMinimap ? "#888" : "#e3f2fd") 
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
                                .style("pointer-events", "none"); 
                                
                            node.call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));
                        }}
                        
                        return {{ link, node }};
                    }}

                    const mainViz = drawGraph(g, false);
                    const birdViz = drawGraph(birdG, true);

                    // --- AUTO FIT MINIMAP ---
                    function autoFitMinimap() {{
                        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
                        
                        data.nodes.forEach(d => {{
                            if (d.x < minX) minX = d.x;
                            if (d.x > maxX) maxX = d.x;
                            if (d.y < minY) minY = d.y;
                            if (d.y > maxY) maxY = d.y;
                        }});

                        if (minX === Infinity) return; 

                        const graphWidth = maxX - minX + 100; // Margina
                        const graphHeight = maxY - minY + 100; 

                        const scaleX = birdWidth / graphWidth;
                        const scaleY = birdHeight / graphHeight;
                        currentMinimapScale = Math.min(scaleX, scaleY) * 0.9;

                        const graphCenterX = (minX + maxX) / 2;
                        const graphCenterY = (minY + maxY) / 2;

                        currentMinimapX = (birdWidth / 2) - (graphCenterX * currentMinimapScale);
                        currentMinimapY = (birdHeight / 2) - (graphCenterY * currentMinimapScale);

                        birdG.attr("transform", `translate(${{currentMinimapX}}, ${{currentMinimapY}}) scale(${{currentMinimapScale}})`);
                        
                        updateRedRectangle();
                    }}

                    function updateRedRectangle() {{
                        const t = currentMainTransform;
                        const worldX = -t.x / t.k;
                        const worldY = -t.y / t.k;
                        const worldW = mainWidth / t.k;
                        const worldH = mainHeight / t.k;

                        const birdX = worldX * currentMinimapScale + currentMinimapX;
                        const birdY = worldY * currentMinimapScale + currentMinimapY;
                        const birdW = worldW * currentMinimapScale;
                        const birdH = worldH * currentMinimapScale;

                        viewportRect
                            .attr("x", birdX)
                            .attr("y", birdY)
                            .attr("width", birdW)
                            .attr("height", birdH);
                    }}

                    // --- TICK ---
                    simulation.on("tick", () => {{
                        // Main View Update
                        mainViz.link
                            .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                            .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                        
                        mainViz.node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);

                        // Bird View Update
                        birdViz.link
                            .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                            .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                            
                        birdViz.node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);

                        // AUTO FIT CALL
                        autoFitMinimap();
                    }});

                    function dragstarted(event, d) {{ if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }}
                    function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
                    function dragended(event, d) {{ if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}
                    
                    // Inicijalni zoom
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
    