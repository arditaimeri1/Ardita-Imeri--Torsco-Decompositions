# ---------------------------------------------------------------
# Grafi
# ---------------------------------------------------------------

def lexo_graf(skajet):
    """Nga lista e skajeve ndërton grafikun: kulm -> fqinjët."""
    g = {}
    for u, v in skajet:
        g.setdefault(u, set()).add(v)
        g.setdefault(v, set()).add(u)
    return g


def _hiq_kulmin(g, k):
    """Heq kulmin k dhe lidh fqinjët e tij mes tyre."""
    fqinjet = list(g[k])

    for a in fqinjet:
        for b in fqinjet:
            if a != b:
                g[a].add(b)

    for a in fqinjet:
        g[a].discard(k)

    del g[k]
    return fqinjet


# ---------------------------------------------------------------
# Vlerësimi i një zgjidhjeje
# ---------------------------------------------------------------

def outdegree_list(graf, pi):
    """Kthen outdegree për çdo pozicion të renditjes."""
    g = {v: set(fq) for v, fq in graf.items()}
    return [len(_hiq_kulmin(g, k)) for k in pi]


def gjeresia(out, t):
    """Kthen gjerësinë nga pozicioni t deri në fund."""
    return max(out[t:])


def pikat_shpejt(out):
    """Llogarit pikat (t, gjerësia) në një kalim."""
    n = len(out)
    w = 0
    rez = [None] * n

    for t in range(n - 1, -1, -1):
        w = max(w, out[t])
        rez[t] = (t, w)

    return rez


def pikat(graf, pi):
    """Kthen çiftet (madhësia e torsos, gjerësia)."""
    out = outdegree_list(graf, pi)
    n = len(pi)
    return [(n - t, gjeresia(out, t)) for t in range(n)]


# ---------------------------------------------------------------
# Fronti Pareto dhe Hypervolume
# ---------------------------------------------------------------

def fronti_pareto(pika):
    """Kthen pikat që nuk dominohen."""
    front, best_w = [], float("inf")

    for t, w in sorted(set(pika)):
        if w < best_w:
            front.append((t, w))
            best_w = w

    return front


def hipervolumi(pika, ref):
    """Llogarit Hypervolume deri te pika referuese."""
    front = fronti_pareto(pika)
    hv = 0

    for i, (t, w) in enumerate(front):
        t_tjeter = front[i + 1][0] if i + 1 < len(front) else ref[0]
        hv += max(0, t_tjeter - t) * max(0, ref[1] - w)

    return hv


def vlera(graf, pi, ref):
    """Llogarit Hypervolume për renditjen pi."""
    return hipervolumi(
        pikat_shpejt(outdegree_list(graf, pi)),
        ref
    )


# ---------------------------------------------------------------
# Formati i zgjidhjes
# ---------------------------------------------------------------

def eshte_permutacion(pi, n):
    """Kontrollon nëse pi përmban çdo kulm saktësisht një herë."""
    return sorted(pi) == list(range(n))


def vektori_vendimit(pi, t):
    """Krijon vektorin x = [p1, ..., pn, t]."""
    n = len(pi)

    assert eshte_permutacion(pi, n), "pi nuk është permutacion"
    assert 0 <= t <= n - 1, "t duhet të jetë në {0, ..., n-1}"

    return list(pi) + [t]


# ---------------------------------------------------------------
# Ndërtimi i renditjes me pesha
# ---------------------------------------------------------------

def renditja_me_peshat(graf, peshat, ndarje):
    """Ndërton renditjen duke kombinuar shkallën, fill-in dhe fqinjët."""

    g = {v: set(fq) for v, fq in graf.items()}

    def pika(v):
        fq = list(g[v])
        d = len(fq)

        fill = 0
        for i in range(d):
            for j in range(i + 1, d):
                if fq[j] not in g[fq[i]]:
                    fill += 1

        m = sum(len(g[u]) for u in fq) / d if d else 0.0

        return (
            peshat[0] * d
            + peshat[1] * fill
            + peshat[2] * m
        )

    piket = {v: pika(v) for v in g}
    pi = []

    while g:
        k = min(g, key=lambda v: (piket[v], ndarje[v]))

        fqinjet = _hiq_kulmin(g, k)
        del piket[k]
        pi.append(k)

        prekur = set(fqinjet)

        for a in fqinjet:
            prekur |= g[a]

        for v in prekur:
            piket[v] = pika(v)

    return pi