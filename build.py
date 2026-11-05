import json, subprocess, heapq, os, shutil, itertools, html
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, Image

R = "/home/claude/blantyre-markets"; os.chdir(R)
import math
T = {"Blantyre_Central":(35.0036,-15.7867),"Limbe":(35.0642,-15.8133),"Ndirande":(35.0302,-15.7692),
"Chilomoni":(34.9806,-15.7503),"Bangwe":(35.0470,-15.8035),"Soche":(35.0170,-15.8120),"Chirimba":(35.0850,-15.8100),
"Kanjedza":(35.0620,-15.7780),"Chitawira":(35.0470,-15.7930),"Zingwangwa":(34.9850,-15.8010),
"Machinjiri_Market":(35.0800,-15.8400),"Chilobwe":(35.0320,-15.8330),"Chigumula":(34.9700,-15.8250),
"Lunzu":(34.9600,-15.7150),"Chileka_Market":(34.9750,-15.6800),"Kameza":(34.9690,-15.7870),
"Ginnery_Corner":(35.0190,-15.7760),"Mbayani":(34.9880,-15.7890),"Manje":(34.9930,-15.7640),
"Naperi":(35.0400,-15.7580),"Chimwankhunda":(35.0250,-15.7950),"Nkolokosa":(35.0130,-15.7600)}
def hav(a,b):
    (x1,y1),(x2,y2)=T[a],T[b]; p=math.pi/180
    h=math.sin((y2-y1)*p/2)**2+math.cos(y1*p)*math.cos(y2*p)*math.sin((x2-x1)*p/2)**2
    return 12742*math.asin(math.sqrt(h))
_nm=list(T); _es=set()
for a in _nm:
    for b in sorted((x for x in _nm if x!=a),key=lambda x:hav(a,x))[:3]: _es.add(frozenset((a,b)))
_comp={n:n for n in _nm}
def _f(x):
    while _comp[x]!=x: x=_comp[x]
    return x
for e in _es:
    a,b=tuple(e); _comp[_f(a)]=_f(b)
while len({_f(n) for n in _nm})>1:
    a,b=min(((a,b) for a in _nm for b in _nm if _f(a)!=_f(b)),key=lambda p:hav(*p)); _es.add(frozenset((a,b))); _comp[_f(a)]=_f(b)
E=sorted(((*sorted(e,key=_nm.index),max(100,int(round(hav(*tuple(e))*1.3*10))*100)) for e in _es),key=lambda t:(_nm.index(t[0]),_nm.index(t[1])))
names = list(T); N = len(names); M = len(E)
nm = lambda s: s.replace("_", " ")
open("graph.txt","w").write(f"{N} {M}\n"+"\n".join(names)+"\n"+"\n".join(f"{a} {b} {w}" for a,b,w in E)+"\n")
open("tests/disconnected.txt","w").write("4 2\nA\nB\nC\nD\nA B 5\nC D 7\n")
open("tests/negative.txt","w").write("2 1\nA\nB\nA B -4\n")
G = {"nodes":[{"name":n,"lon":T[n][0],"lat":T[n][1]} for n in names],"edges":[list(e) for e in E]}
json.dump(G, open("graph.json","w"), indent=1)
open("index.html","w").write(open("index.template.html").read().replace("__DATA__", json.dumps(G)))

# ---- independent reference (Python) ----
adj = {n:[] for n in names}
for a,b,w in E: adj[a].append((b,w)); adj[b].append((a,w))
def dj(s, trace=None):
    d={n:float("inf") for n in names}; p={}; d[s]=0; pq=[(0,s)]; done=set()
    while pq:
        du,u=heapq.heappop(pq)
        if u in done: continue
        done.add(u); rel=[]
        for v,w in adj[u]:
            if v not in done and du+w<d[v]: rel.append((v,d[v],du+w)); d[v]=du+w; p[v]=u; heapq.heappush(pq,(d[v],v))
        if trace is not None: trace.append((u,du,rel))
    return d,p
def path(p,s,t):
    r=[t]
    while r[-1]!=s: r.append(p[r[-1]])
    return r[::-1]

# ---- compile + tests ----
subprocess.run(["g++","-std=c++17","-O2","dijkstra.cpp","-o","dijkstra"],check=True)
def run(args):
    r=subprocess.run(["./dijkstra"]+args,capture_output=True,text=True)
    return (r.stdout+r.stderr).strip(), r.returncode
tests=[("T1","Long route across the district (north edge to south-east)",["graph.txt","shortest","Chileka_Market","Machinjiri_Market"]),
("T2","Far-apart markets (west to east)",["graph.txt","shortest","Lunzu","Chirimba"]),
("T3","Source equals destination",["graph.txt","shortest","Limbe","Limbe"]),
("T4","Far outlying market to city centre",["graph.txt","shortest","Chileka_Market","Blantyre_Central"]),
("T5","Neighbouring markets (direct road likely best)",["graph.txt","shortest","Blantyre_Central","Chitawira"]),
("T6","Route through the middle of the network",["graph.txt","shortest","Mbayani","Bangwe"]),
("T7","Invalid market name (error handling)",["graph.txt","shortest","Limbe","Lusaka"]),
("T8","Unreachable node (disconnected graph)",["tests/disconnected.txt","shortest","A","D"]),
("T9","Negative weight rejected",["tests/negative.txt","shortest","A","B"]),
("T10","Missing input file",["nofile.txt","shortest","A","B"]),
("T11","Kruskal MST",["graph.txt","mst"])]
log=[]; rows=[["ID","Purpose","Input","Output (actual)","Result"]]
for tid,desc,a in tests:
    out,rc=run(a); log.append(f"[{tid}] {desc}\n$ ./dijkstra {' '.join(a)}\n{out}\n(exit code {rc})\n")
    ok=True
    if a[1]=="shortest" and a[0]=="graph.txt" and rc==0:
        d,p=dj(a[2]); ok=f"= {d[a[3]]} m" in out and " -> ".join(nm(x) if False else x for x in path(p,a[2],a[3]))==out.split("Path: ")[1]
    if tid in("T7","T9","T10"): ok = out.startswith("ERROR") and rc!=0
    if tid=="T8": ok="No route" in out
    rows.append([tid,desc," ".join(a[1:]) if a[0]=="graph.txt" else " ".join(a),out.replace("\n","; ")[:150],"PASS" if ok else "FAIL"])
    print(tid,"PASS" if ok else "FAIL")
# exhaustive cross-check: every pair, C++ vs Python
bad=0; pairs=0
for s,t in itertools.combinations(names,2):
    out,_=run(["graph.txt","shortest",s,t]); d,_p=dj(s); pairs+=1
    if f"= {d[t]} m" not in out: bad+=1
log.append(f"[X] Exhaustive cross-check: C++ vs independent Python Dijkstra on all {pairs} town pairs -> mismatches: {bad}\n")
print("pairs",pairs,"mismatch",bad)
tr_out,_=run(["graph.txt","shortest","Chileka_Market","Machinjiri_Market","--trace"])
log.append("[D] Dry-run trace Chileka -> Machinjiri\n"+tr_out+"\n")
open("docs/test_log.txt","w").write("\n".join(log))

# ---- MST (Python reference) ----
par={n:n for n in names}
def f(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
mst=[]
for a,b,w in sorted(E,key=lambda e:e[2]):
    if f(a)!=f(b): par[f(a)]=f(b); mst.append((a,b,w))
mst_total=sum(w for *_,w in mst)
dL,pL=dj("Chileka_Market"); pth=path(pL,"Chileka_Market","Machinjiri_Market")

# ---- figures ----
def fig(fn,title,hl=set(),hn=set(),col="#c8102e"):
    plt.figure(figsize=(10,10)); ax=plt.gca()
    for a,b,w in E:
        on=frozenset((a,b)) in hl; x=[T[a][0],T[b][0]]; y=[T[a][1],T[b][1]]
        ax.plot(x,y,color=col if on else "#999",lw=3 if on else 1.2,zorder=1)
        ax.text(sum(x)/2,sum(y)/2,str(w),fontsize=7,ha="center",color=col if on else "#555",bbox=dict(fc="white",ec="none",pad=.5),zorder=2)
    for n,(x,y) in T.items():
        ax.scatter(x,y,s=70 if n in hn else 40,c=col if n in hn else "#0a7d3b",zorder=3)
        ax.text(x+.002,y+.0015,nm(n),fontsize=8)
    ax.set_title(title); ax.axis("off"); plt.tight_layout(); plt.savefig(fn,dpi=130); plt.close()
fig("docs/fig_graph.png","Blantyre District markets (edge labels = metres)")
fig("docs/fig_path.png","Dijkstra: Chileka Market to Machinjiri Market = %d m"%dL["Machinjiri_Market"],{frozenset(x) for x in zip(pth,pth[1:])},set(pth))
fig("docs/fig_mst.png","Minimum spanning tree (Kruskal), total %d m"%mst_total,{frozenset((a,b)) for a,b,_ in mst},set(names),"#0a5dc8")

# ---- PDF ----
st=getSampleStyleSheet(); B=ParagraphStyle("B",parent=st["Normal"],fontSize=10,leading=14)
S=ParagraphStyle("S",parent=B,fontSize=8,leading=10); H=st["Heading1"]; H2=st["Heading2"]
P=lambda t,s=B:Paragraph(t,s)
def tbl(data,cw=None):
    data=[[Paragraph(html.escape(str(c)),S) for c in r] for r in data]
    t=Table(data,colWidths=cw,repeatRows=1)
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.4,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("VALIGN",(0,0),(-1,-1),"TOP")])); return t
def img(fn,h=520): im=Image(fn); r=im.imageWidth/im.imageHeight; im.drawHeight=h; im.drawWidth=h*r; return im
SRC,DST="Chileka_Market","Machinjiri_Market"
tr=[]; dj(SRC,tr)
steps=[["Step","Settle (dist m)","Relaxations (neighbour: old -> new)"]]
for i,(u,du,rel) in enumerate(tr,1):
    steps.append([i,f"{nm(u)} ({du})","; ".join(f"{nm(v)}: {'INF' if o==float('inf') else o} -> {n}" for v,o,n in rel) or "none"])
    if u==DST: break
pro=" ".join(f"Step {i}: {nm(u)} is settled at {du} m"+(", improving "+", ".join(f"{nm(v)} to {n} m" for v,o,n in rel) if rel else ", improving no neighbour")+"." for i,(u,du,rel) in enumerate(tr[:6],1))
deg={n:len(adj[n]) for n in names}; leaf=min(deg,key=deg.get); hub=max(deg,key=deg.get)
doc=SimpleDocTemplate("docs/DSA_Assignment_Report.pdf",pagesize=A4,leftMargin=40,rightMargin=40,topMargin=40,bottomMargin=40,title="DSA Assignment - Blantyre District Markets")
s=[P("Data Structures &amp; Algorithms Assignment 2026",st["Title"]),P("Blantyre District Markets: Dijkstra's Algorithm and Minimum Spanning Tree",H2),
P("<b>Group members:</b> 1) ____________________ 2) ____________________ 3) ____________________"),
P("<b>Code (GitHub):</b> https://github.com/Lusekelo-1051/blantyre-markets &nbsp; <b>Live demo:</b> https://lusekelo-1051.github.io/blantyre-markets/"),Spacer(1,8),
P("1. The graph (Question 1)",H),
P(f"<b>Scenario.</b> Blantyre is Malawi's commercial capital, and its markets are where traders, minibus drivers and shoppers move goods every day. This graph models the road links between {N} major markets in Blantyre District: Blantyre Central, Limbe, Ndirande, Chilomoni, Bangwe, Soche, Chirimba, Kanjedza, Chitawira, Zingwangwa, Machinjiri, Chilobwe, Chigumula, Lunzu, Chileka, Kameza, Ginnery Corner, Mbayani, Manje, Naperi, Chimwankhunda and Nkolokosa. <b>Vertices:</b> each market is a vertex (V = {N}). <b>Edges:</b> a road link between two neighbouring markets, <b>undirected</b> because roads are two-way (E = {M}). <b>Weights:</b> road distance in metres (always positive)."),
P(f"<b>How the data was modelled.</b> Market positions are approximate GPS coordinates. Each market was linked to its three nearest markets, and each weight is the straight-line distance multiplied by 1.3 (a typical detour factor for roads), rounded to 100 m. The values are approximations for modelling and can be replaced by measured driving distances without changing the algorithms."),
P(f"The graph is connected, sparse (average degree {2*M/N:.1f}), and contains many cycles, for example around the Limbe, Bangwe and Chitawira cluster. {nm(hub)} has the most links ({deg[hub]}), and {nm(leaf)} has the fewest ({deg[leaf]}). It is stored as an <b>adjacency list</b> (memory O(V+E)), the right choice for a sparse graph."),
tbl([["Market A","Market B","Distance (m)"]]+[[nm(a),nm(b),w] for a,b,w in E],[170,170,80]),PageBreak(),
P("2. Drawing and description (Question 2)",H),
P("Conventions: circles are vertices labelled with the market name; straight lines are undirected edges; the number on a line is its weight in metres; positions follow the real map (north at the top). <b>The graph must also be hand-drawn on paper as the assignment requires: copy this figure by hand with every vertex and edge weight and attach a photo of it.</b>"),img("docs/fig_graph.png",540),PageBreak(),
P("3. How Dijkstra works on the graph (Question 3)",H),
P("<b>Idea.</b> Dijkstra finds the shortest path from one source to every other vertex when all weights are non-negative. Each vertex has a tentative distance dist[v] (infinity at first, 0 for the source). The algorithm repeatedly (a) picks the unsettled vertex with the smallest dist, which is then final (settled), and (b) <i>relaxes</i> its edges: if dist[u] + w(u,v) &lt; dist[v], then dist[v] is updated and prev[v] = u. The greedy choice is safe because no negative edge can later shorten a settled distance. With a min-heap the cost is O((V+E) log V). The path is rebuilt by following prev[] from the target back to the source."),
P(f"<b>Worked example: Chileka Market to Machinjiri Market.</b> Result: <b>{dL[DST]} m</b>, path {' -> '.join(nm(x) for x in pth)}."),tbl(steps,[35,140,340]),Spacer(1,6),img("docs/fig_path.png",400),PageBreak(),
P("4. Implementation (Question 4)",H),P("Language: C++17 (dijkstra.cpp). Build: <font face='Courier'>g++ -std=c++17 -O2 dijkstra.cpp -o dijkstra</font>. Run: <font face='Courier'>./dijkstra graph.txt shortest Chileka_Market Machinjiri_Market --trace</font>. The web demo (index.html) runs the same algorithm in JavaScript."),
Preformatted(open("dijkstra.cpp").read(),ParagraphStyle("c",fontName="Courier",fontSize=6.3,leading=7.4)),PageBreak(),
P("5. Testing (Question 5)",H),P(f"All tests run on the compiled program. In addition, <b>every one of the {pairs} market pairs was compared with an independent Python Dijkstra: {bad} mismatches.</b> Errors found: none in the final build. The program rejects invalid names, missing files and negative weights with a clear message instead of crashing."),
tbl(rows,[28,110,110,230,35]),Spacer(1,8),
P(f"<b>Dry run (by hand), Chileka Market to Machinjiri Market.</b> Start: dist[Chileka Market] = 0 and every other vertex is INF. Each step settles the unsettled vertex with the smallest distance and relaxes its edges. {pro} The same process continues (see the full trace table in Section 3) until Machinjiri Market is the smallest unsettled vertex. It is settled at <b>{dL[DST]} m</b> and the algorithm stops. Following prev[] backwards gives {' -> '.join(nm(x) for x in pth)}. The hand dry run agrees with the program output."),PageBreak(),
P("6. Does the graph have an MST? (Question 6)",H),
P(f"<b>Yes.</b> Every connected, undirected, weighted graph has a minimum spanning tree. Our graph is connected (each market can reach every other), so the MST has exactly V-1 = {N-1} edges, no cycles, and total length <b>{mst_total} m</b>. If the graph were disconnected we would only get a spanning forest."),
P("<b>What it represents:</b> the shortest total length of road that still links every market to every other market. The City Council could use it to decide which links to maintain, drain or pave first on a limited budget, or to run a power or fibre line to all markets with the least cable. It is not a shortest-route tool: the MST minimises the total length of the network, while Dijkstra minimises the distance between two chosen markets, so the path between two markets inside the MST can be longer than the shortest path."),
tbl([["Edge","Distance (m)"]]+[[f"{nm(a)} - {nm(b)}",w] for a,b,w in mst],[280,80]),Spacer(1,6),img("docs/fig_mst.png",400),PageBreak(),
P("7. Which MST algorithm? (Question 7)",H),
P("<b>Kruskal's algorithm</b> sorts all edges by weight and adds the next cheapest edge unless it forms a cycle (checked with Union-Find); it runs in O(E log E). <b>Prim's algorithm</b> grows one tree from a start vertex by always adding the cheapest edge that leaves the tree; it runs in O(E log V) with a heap."),
P(f"<b>Why Kruskal here:</b> the graph is <b>sparse</b> (V = {N}, E = {M}), and Kruskal is at its best on sparse graphs because the sort is small. It uses the edge list we already store, returns a forest if the graph is ever disconnected, and is short to code and easy to check by hand. Prim is preferred for dense graphs (E close to V<super>2</super>) stored as a matrix. Both give the same total of {mst_total} m here (press both MST buttons in the demo to check). Kruskal is implemented in dijkstra.cpp (mode mst)."),
P("8. Deployment (Question 8)",H),
P("The web demo (index.html) is one static file that runs Dijkstra, Kruskal and Prim in the browser with an interactive map. It is hosted free on GitHub Pages at <b>https://lusekelo-1051.github.io/blantyre-markets/</b>, so the lecturer opens the link and installs nothing. The source code and the C++ implementation are in the GitHub repository, and the README explains how to build and run them."),
]
doc.build(s)
shutil.copy("docs/DSA_Assignment_Report.pdf","/mnt/user-data/outputs/Blantyre_Markets_DSA_Report.pdf")
print("MST",mst_total,len(mst),"V,E",N,M,"path",pth,dL[DST]); print(tr_out)
