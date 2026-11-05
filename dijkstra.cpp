// Malawi Road Network - Dijkstra (shortest path) and Kruskal (MST)
// Build: g++ -std=c++17 -O2 dijkstra.cpp -o dijkstra
// Usage: ./dijkstra graph.txt shortest <FROM> <TO> [--trace]
//        ./dijkstra graph.txt mst
// Graph file: first line "N M", then N town names, then M lines "A B m".
#include <bits/stdc++.h>
using namespace std;

struct Edge { int to; int w; };
int N, M;
vector<string> names;
map<string,int> id;
vector<vector<Edge>> adj;
vector<array<int,3>> edges; // u, v, w

bool load(const string& file) {
    ifstream in(file);
    if (!in) { cerr << "ERROR: cannot open file " << file << "\n"; return false; }
    if (!(in >> N >> M) || N <= 0 || M < 0) { cerr << "ERROR: bad header\n"; return false; }
    names.resize(N); adj.assign(N, {});
    for (int i = 0; i < N; i++) { in >> names[i]; id[names[i]] = i; }
    for (int i = 0; i < M; i++) {
        string a, b; int w;
        if (!(in >> a >> b >> w)) { cerr << "ERROR: bad edge line " << i + 1 << "\n"; return false; }
        if (!id.count(a) || !id.count(b)) { cerr << "ERROR: unknown town in edge " << a << " " << b << "\n"; return false; }
        if (w < 0) { cerr << "ERROR: negative weight on " << a << "-" << b << " (Dijkstra needs w >= 0)\n"; return false; }
        int u = id[a], v = id[b];
        adj[u].push_back({v, w}); adj[v].push_back({u, w}); // undirected
        edges.push_back({u, v, w});
    }
    return true;
}

// Dijkstra with a min-heap: O((V+E) log V)
void dijkstra(int s, int t, bool trace) {
    const int INF = INT_MAX;
    vector<int> dist(N, INF), prev(N, -1);
    vector<bool> done(N, false);
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;
    dist[s] = 0; pq.push({0, s});
    int step = 0;
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (done[u]) continue;           // stale heap entry
        done[u] = true;
        if (trace) cout << "Step " << ++step << ": settle " << names[u] << " (dist=" << d << ")\n";
        for (auto& e : adj[u]) {
            if (done[e.to]) continue;
            if (d + e.w < dist[e.to]) {
                if (trace) cout << "    relax " << names[e.to] << ": "
                    << (dist[e.to] == INF ? string("INF") : to_string(dist[e.to])) << " -> " << d + e.w << "\n";
                dist[e.to] = d + e.w; prev[e.to] = u; pq.push({dist[e.to], e.to});
            }
        }
        if (u == t) break;               // early exit: target settled
    }
    if (dist[t] == INF) { cout << "No route from " << names[s] << " to " << names[t] << "\n"; return; }
    vector<int> path;
    for (int v = t; v != -1; v = prev[v]) path.push_back(v);
    reverse(path.begin(), path.end());
    cout << "Shortest distance " << names[s] << " -> " << names[t] << " = " << dist[t] << " m\nPath: ";
    for (size_t i = 0; i < path.size(); i++) cout << names[path[i]] << (i + 1 < path.size() ? " -> " : "\n");
}

// Union-Find for Kruskal
vector<int> par;
int find(int x) { return par[x] == x ? x : par[x] = find(par[x]); }

void kruskal() {
    auto es = edges;
    sort(es.begin(), es.end(), [](auto& a, auto& b) { return a[2] < b[2]; });
    par.resize(N); iota(par.begin(), par.end(), 0);
    int total = 0, cnt = 0;
    for (auto& e : es) {
        int a = find(e[0]), b = find(e[1]);
        if (a == b) continue;            // would create a cycle
        par[a] = b; total += e[2]; cnt++;
        cout << names[e[0]] << " - " << names[e[1]] << " (" << e[2] << " m)\n";
    }
    if (cnt != N - 1) cout << "Graph is disconnected: minimum spanning FOREST (" << cnt << " edges)\n";
    cout << "MST total = " << total << " m using " << cnt << " edges\n";
}

int main(int argc, char** argv) {
    if (argc < 3) { cerr << "Usage: " << argv[0] << " graph.txt shortest FROM TO [--trace] | mst\n"; return 1; }
    if (!load(argv[1])) return 1;
    string mode = argv[2];
    if (mode == "mst") { kruskal(); return 0; }
    if (mode == "shortest" && argc >= 5) {
        if (!id.count(argv[3]) || !id.count(argv[4])) { cerr << "ERROR: unknown town name\n"; return 2; }
        dijkstra(id[argv[3]], id[argv[4]], argc >= 6 && string(argv[5]) == "--trace");
        return 0;
    }
    cerr << "ERROR: bad arguments\n"; return 1;
}
