# Do this (Windows + VS Code)
1. Open this folder in VS Code (File > Open Folder), open a terminal (Ctrl+`).
2. Install compiler once: winget install BrechtSanders.WinLibs.POSIX.UCRT  (then restart VS Code), check: g++ --version
3. Compile & run:
   g++ -std=c++17 -O2 dijkstra.cpp -o dijkstra.exe
   .\dijkstra.exe graph.txt shortest Chileka_Market Machinjiri_Market --trace   (expect 29700 m)
   .\dijkstra.exe graph.txt mst   (expect total 63500 m, 21 edges)
   Error tests: .\dijkstra.exe graph.txt shortest Limbe Lusaka | .\dijkstra.exe tests\disconnected.txt shortest A D | .\dijkstra.exe tests\negative.txt shortest A B
4. Open index.html in your browser to try the demo.
5. GitHub: create repo "blantyre-markets", upload ALL files (index.html must be at the top level), Settings > Pages > branch main, / (root).
6. Hand-draw docs/fig_graph.png on paper, photograph it, add to the PDF with your names. Put PDF in a shared Drive folder (View access) and email the link + GitHub + demo links before 12 Nov 2026.
7. IMPORTANT: distances are modelled (straight-line x 1.3 between nearest markets). For top marks, check a few key links in Google Maps and tell me the real distances so I regenerate the files.

# Understand it
- Vertices = markets, edges = road links, weight = metres (undirected, two-way roads). Adjacency list suits a sparse graph (46 edges, 22 vertices).
- Dijkstra: dist[] = INF (0 at source); repeatedly settle the smallest unsettled vertex, relax its edges (dist[u]+w < dist[v] => update, prev[v]=u); rebuild path via prev[]. Needs w >= 0. O((V+E) log V) with a heap.
- MST: V-1 = 21 edges connecting all markets with least total length (63500 m). Exists because graph is connected. Kruskal: sort edges, add unless it makes a cycle (Union-Find), O(E log E), good for sparse graphs. Prim: grow from one vertex, O(E log V), good for dense graphs.
- MST minimises total network length; Dijkstra minimises distance between two chosen markets.
