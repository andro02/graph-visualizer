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
            
            label_text = n.label if n.label else n.id

            nodes_data.append({
                "id": str(n.id), 
                "label": str(label_text),
                "attributes": filtered_attrs
            })

        links_data = []
        for e in graph.edges:
            s = e.source.id if hasattr(e.source, "id") else e.source
            t = e.target.id if hasattr(e.target, "id") else e.target
            links_data.append({"source": str(s), "target": str(t)})

        graph_json = json.dumps({"nodes": nodes_data, "links": links_data, "directed": graph.directed})

        # --- 2. GENERISANJE HTML-a ---
        js_logic = f"""
            (function() {{
                try {{
                    const data = GRAPH_DATA_PLACEHOLDER;
                    
                    const mainContainer = document.getElementById('block-viz-container');
                    const birdContainer = document.getElementById('bird-view-container');
                    
                    if (!mainContainer || !birdContainer) return;

                    // Dimenzije
                    const mainWidth = mainContainer.clientWidth;
                    const mainHeight = mainContainer.clientHeight || 600;
                    const birdWidth = birdContainer.clientWidth;
                    const birdHeight = birdContainer.clientHeight || 200;
                    
                    const nodeWidth = 180; 
                    const headerHeight = 30;
                    const lineHeight = 16;
                    const padding = 10;

                    // Promenljive za dinamicko skaliranje minimape (Auto-Fit)
                    let currentMinimapScale = 1;
                    let currentMinimapX = 0;
                    let currentMinimapY = 0;
                    let currentMainTransform = d3.zoomIdentity;

                    // --- 1. SETUP MAIN VIEW ---
                    d3.select("#block-viz-container").html("");
                    const svg = d3.select("#block-viz-container").append("svg")
                        .attr("width", "100%").attr("height", "100%")
                        .style("background", "#f9f9f9")
                        .attr("viewBox", `0 0 ${{mainWidth}} ${{mainHeight}}`);

                    const g = svg.append("g");

                    // --- 2. SETUP BIRD VIEW ---
                    d3.select("#bird-view-container").html("");
                    const birdSvg = d3.select("#bird-view-container").append("svg")
                        .attr("width", "100%").attr("height", "100%")
                        .style("background", "#e0e0e0")
                        .style("border", "1px solid #ccc");
                    
                    // Grupa za minimapu (na nju primenjujemo auto-fit transformacije)
                    const birdG = birdSvg.append("g");

                    const viewportRect = birdSvg.append("rect")
                        .attr("fill", "none")
                        .attr("stroke", "red")
                        .attr("stroke-width", 2);

                    // --- ZOOM BEHAVIOR ---
                    const zoom = d3.zoom()
                        .scaleExtent([0.05, 5])
                        .on("zoom", (event) => {{
                            currentMainTransform = event.transform;
                            g.attr("transform", event.transform);
                            // Kad zumiramo glavni graf, samo azuriramo crveni pravougaonik
                            updateRedRectangle();
                        }});

                    svg.call(zoom);

                    // --- SIMULATION ---
                    // Jaci charge (-1000) da se veliki grafovi lepo rasire
                    const simulation = d3.forceSimulation(data.nodes)
                        .force("link", d3.forceLink(data.links).id(d => d.id).distance(200))
                        .force("charge", d3.forceManyBody().strength(-1000))
                        .force("center", d3.forceCenter(mainWidth / 2, mainHeight / 2))
                        .force("collide", d3.forceCollide(nodeWidth / 1.2));

                    // --- DRAW ELEMENTS ---
                    function draw(container, isMinimap) {{
                        if (!isMinimap) {{
                             container.append("defs").append("marker")
                                .attr("id", "arrowhead-block")
                                .attr("viewBox", "0 -5 10 10")
                                .attr("refX", nodeWidth/2 + 10).attr("refY", 0)
                                .attr("markerWidth", 6).attr("markerHeight", 6)
                                .attr("orient", "auto")
                                .append("path").attr("d", "M0,-5L10,0L0,5").attr("fill", "#555");
                        }}

                        const isDirected = data.directed;

                        const link = container.append("g").selectAll("line")
                            .data(data.links).join("line")
                            .attr("stroke", "#555")
                            .attr("stroke-width", isMinimap ? 10 : 2) // Deblje na mapi
                            .attr("marker-end", isDirected && !isMinimap ? "url(#arrowhead-block)" : null);

                        const node = container.append("g").selectAll("g")
                            .data(data.nodes).join("g");

                        if (!isMinimap) {{
                            node.call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));
                        }}

                        // Pravougaonik
                        node.append("rect")
                            .attr("class", "node-box")
                            .attr("width", nodeWidth)
                            .attr("x", -nodeWidth/2)
                            .attr("rx", 8).attr("ry", 8)
                            .attr("fill", isMinimap ? "#999" : "white")
                            .attr("stroke", "#2c3e50").attr("stroke-width", isMinimap ? 0 : 2);

                        if (!isMinimap) {{
                            // Tekst i atributi (samo main)
                            node.append("text")
                                .text(d => d.label || d.id)
                                .attr("y", -headerHeight/2 - 10)
                                .attr("text-anchor", "middle")
                                .style("font-weight", "bold").style("font-family", "sans-serif").style("font-size", "14px").style("fill", "#2c3e50");  

                            node.append("line")
                                .attr("x1", -nodeWidth/2).attr("y1", -10).attr("x2", nodeWidth/2).attr("y2", -10)
                                .attr("stroke", "#ccc").attr("stroke-width", 2);

                            node.each(function(d) {{
                                const el = d3.select(this);
                                let yPos = 10; 
                                if (d.attributes && typeof d.attributes === 'object') {{
                                    Object.entries(d.attributes).forEach(([key, val]) => {{
                                        let valStr = String(val);
                                        if (valStr.length > 20) valStr = valStr.substring(0, 17) + "...";
                                        el.append("text").text(key + ": " + valStr).attr("y", yPos).attr("x", -nodeWidth/2 + 10)
                                            .style("font-size", "12px").style("font-family", "monospace").style("fill", "#555");
                                        yPos += lineHeight;
                                    }});
                                }}
                                const contentHeight = Math.max(50, yPos + padding);
                                const totalHeight = contentHeight + headerHeight;
                                el.select("rect.node-box").attr("height", totalHeight).attr("y", -headerHeight - 15);
                                el.select("line").attr("y1", -headerHeight + 15).attr("y2", -headerHeight + 15);
                                el.select("text").attr("y", -headerHeight);
                            }});
                        }} else {{
                            // Pojednostavljen prikaz na mapi
                            node.select("rect").attr("height", 80).attr("y", -40);
                        }}
                        return {{link, node}};
                    }}

                    const mainViz = draw(g, false);
                    const birdViz = draw(birdG, true);

                    // --- FUNKCIJA: AUTO FIT (Resava problem velikih grafova) ---
                    function autoFitMinimap() {{
                        // 1. Nadji granice (min/max) celog grafa
                        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
                        
                        data.nodes.forEach(d => {{
                            if (d.x < minX) minX = d.x;
                            if (d.x > maxX) maxX = d.x;
                            if (d.y < minY) minY = d.y;
                            if (d.y > maxY) maxY = d.y;
                        }});

                        if (minX === Infinity) return; // Nema cvorova

                        // Dodajemo marginu oko grafa da ne dodiruje ivice
                        const graphWidth = maxX - minX + nodeWidth * 4; 
                        const graphHeight = maxY - minY + 400; 

                        // 2. Izracunaj skalu tako da ceo taj prostor stane u birdContainera
                        const scaleX = birdWidth / graphWidth;
                        const scaleY = birdHeight / graphHeight;
                        
                        // Koristimo manju skalu da bi sve stalo
                        currentMinimapScale = Math.min(scaleX, scaleY);

                        // 3. Izracunaj translaciju da se centrira
                        const graphCenterX = (minX + maxX) / 2;
                        const graphCenterY = (minY + maxY) / 2;

                        currentMinimapX = (birdWidth / 2) - (graphCenterX * currentMinimapScale);
                        currentMinimapY = (birdHeight / 2) - (graphCenterY * currentMinimapScale);

                        // 4. Primeni transformaciju na celu grupu minimape
                        birdG.attr("transform", `translate(${{currentMinimapX}}, ${{currentMinimapY}}) scale(${{currentMinimapScale}})`);
                        
                        // 5. Azuriraj crveni okvir jer su se koordinate promenile
                        updateRedRectangle();
                    }}

                    function updateRedRectangle() {{
                        // Racunamo: Gde je Viewport glavnog ekrana u odnosu na svet grafa?
                        const t = currentMainTransform;
                        
                        // Inverzna transformacija: (screen - translate) / scale
                        const worldX = -t.x / t.k;
                        const worldY = -t.y / t.k;
                        const worldW = mainWidth / t.k;
                        const worldH = mainHeight / t.k;

                        // Konvertujemo te "world" koordinate u koordinate minimape
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
                        // Update pozicije u glavnom pogledu
                        mainViz.link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                            .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                        mainViz.node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);

                        // Update pozicije u minimapi
                        birdViz.link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                            .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                        birdViz.node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);

                        // KLJUCNO: Prilagodi skalu minimape u svakom frejmu
                        autoFitMinimap();
                    }});

                    function dragstarted(event, d) {{ if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }}
                    function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
                    function dragended(event, d) {{ if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}
                    
                    // Inicijalni poziv zooma
                    svg.call(zoom.transform, d3.zoomIdentity);

                }} catch (err) {{
                    console.error("Block Visualizer Error:", err);
                }}
            }})();
        """
        
        js_code = js_logic.replace("GRAPH_DATA_PLACEHOLDER", graph_json)

        return f"""
        <div id="block-viz-container" style="width:100%; height:100%; border:1px solid #ddd; background: #f9f9f9;"></div>
        <script>
            {js_code}
        </script>
        """