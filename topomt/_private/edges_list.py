def connected_components_union_find(edges):
    parent = {}

    def find(x):
        # path compression
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra  # o por tamaño/rango

    # inicializa
    for u, v in edges:
        if u not in parent:
            parent[u] = u
        if v not in parent:
            parent[v] = v
        union(u, v)

    # agrupa por raíz
    comps = {}
    for x in parent:
        r = find(x)
        comps.setdefault(r, []).append(x)

    return list(comps.values())
