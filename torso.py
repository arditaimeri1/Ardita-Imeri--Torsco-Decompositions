import random


# ---------------------------------------------------------------
#  Grafi
# ---------------------------------------------------------------

def lexo_graf(skajet):
    """Nga lista e skajeve [(u, v), ...] ndërton dict: kulm -> set fqinjësh."""
    g = {}
    for u, v in skajet:
        g.setdefault(u, set()).add(v)
        g.setdefault(v, set()).add(u)
    return g


def _hiq_kulmin(g, k):
    """Heq kulmin k nga g (në vend) dhe lidh fqinjët e tij mes tyre.
    Kthen listën e fqinjëve; gjatësia e saj është outdegree i k."""
    fqinjet = list(g[k])
    for a in fqinjet:                   # lidh fqinjët mes tyre
        for b in fqinjet:
            if a != b:
                g[a].add(b)
    for a in fqinjet:                   # fshij k
        g[a].discard(k)
    del g[k]
    return fqinjet


# ---------------------------------------------------------------
#  Vlerësimi i një zgjidhjeje (pi, t)
# ---------------------------------------------------------------

def outdegree_list(graf, pi):
    """Eliminon kulmet sipas renditjes pi dhe kthen outdegree për çdo pozicion."""
    g = {v: set(fq) for v, fq in graf.items()}   # kopje, që graf të mos ndryshojë
    return [len(_hiq_kulmin(g, k)) for k in pi]


def gjeresia(out, t):
    """Gjerësia e torsos = maksimumi i outdegree nga pozicioni t deri në fund."""
    return max(out[t:])


def pikat_shpejt(out):
    """Lista (t, gjerësia) për çdo t, e llogaritur në një kalim nga fundi."""
    n = len(out)
    w = 0
    rez = [None] * n
    for t in range(n - 1, -1, -1):
        w = max(w, out[t])
        rez[t] = (t, w)
    return rez


def pikat(graf, pi):
    """Për çdo t jep çiftin (madhësia e torsos, gjerësia).
    Kujdes: këtu e para është madhësia n - t, jo t."""
    out = outdegree_list(graf, pi)
    n = len(pi)
    return [(n - t, gjeresia(out, t)) for t in range(n)]


# ---------------------------------------------------------------
#  Fronti Pareto dhe hypervolume
# ---------------------------------------------------------------

def fronti_pareto(pika):
    """pika = lista (t, gjeresia); minimizojmë të dyja. Kthen vetëm pikat që nuk dominohen."""
    front, best_w = [], float("inf")
    for t, w in sorted(set(pika)):
        if w < best_w:
            front.append((t, w))
            best_w = w
    return front


def hipervolumi(pika, ref):
    """Sipërfaqja e zonës që dominohet nga fronti, deri te pika referuese ref = (t_ref, w_ref)."""
    front = fronti_pareto(pika)
    hv = 0
    for i, (t, w) in enumerate(front):
        t_tjeter = front[i + 1][0] if i + 1 < len(front) else ref[0]
        hv += max(0, t_tjeter - t) * max(0, ref[1] - w)
    return hv


def vlera(graf, pi, ref):
    """Hypervolume i renditjes pi (sa më i madh, aq më mirë)."""
    return hipervolumi(pikat_shpejt(outdegree_list(graf, pi)), ref)


# ---------------------------------------------------------------
#  Ndërtimi i renditjeve (heuristika)
# ---------------------------------------------------------------

def renditja_greedy(graf):
    """Heq gjithmonë kulmin me më pak fqinjë në grafin e mbetur. Kthen renditjen pi."""
    g = {v: set(fq) for v, fq in graf.items()}
    pi = []
    while g:
        k = min(g, key=lambda v: len(g[v]))
        _hiq_kulmin(g, k)
        pi.append(k)
    return pi


def _min_fill(graf, ndarje=None):
    """Heq gjithmonë kulmin që shton më pak skaje të reja (fill-in).
    Barazimet zgjidhen me numrin e fqinjëve, ose me 'ndarje' (dict kulm -> numër) nëse jepet."""
    g = {v: set(fq) for v, fq in graf.items()}

    def fill(v):
        fq = list(g[v])
        mungojne = 0
        for i in range(len(fq)):
            for j in range(i + 1, len(fq)):
                if fq[j] not in g[fq[i]]:
                    mungojne += 1
        return mungojne

    def celesi(v):
        if ndarje is None:
            return (vlerat[v], len(g[v]))
        return (vlerat[v], ndarje[v])

    vlerat = {v: fill(v) for v in g}
    pi = []
    while g:
        k = min(g, key=celesi)
        fqinjet = _hiq_kulmin(g, k)
        del vlerat[k]
        pi.append(k)
        # rillogarit vetëm për kulmet që mund të kenë ndryshuar
        prekur = set(fqinjet)
        for a in fqinjet:
            prekur |= g[a]
        for v in prekur:
            vlerat[v] = fill(v)
    return pi


def renditja_min_fill(graf):
    """Min-fill me barazime të zgjidhura nga numri i fqinjëve. Kthen renditjen pi."""
    return _min_fill(graf)


def renditja_min_fill_rastesi(graf, seed):
    """Min-fill ku barazimet zgjidhen rastësisht (sipas seed). Seed i ndryshëm, renditje e ndryshme."""
    rnd = random.Random(seed)
    ndarje = {v: rnd.random() for v in graf}
    return _min_fill(graf, ndarje)


# ---------------------------------------------------------------
#  Hill climbing
# ---------------------------------------------------------------

def hill_climbing(graf, pi_fillestar, hapa, ref, seed=1):
    """Ndërron dy kulme rastësisht dhe e mban ndryshimin vetëm nëse hypervolume rritet."""
    rnd = random.Random(seed)
    pi = list(pi_fillestar)
    mire = vlera(graf, pi, ref)
    for hap in range(hapa):
        i, j = rnd.sample(range(len(pi)), 2)
        pi[i], pi[j] = pi[j], pi[i]              # ndërro dy vende
        v = vlera(graf, pi, ref)
        if v > mire:
            mire = v                             # përmirësim: e mbajmë
        else:
            pi[i], pi[j] = pi[j], pi[i]          # jo më mirë: kthejmë mbrapsht
    return pi, mire


def hill_climbing_lokal(graf, pi_fillestar, hapa, ref, dritarja=30, seed=1):
    """Ndërron kulmin në pozicionin i me një pozicion afër; pranon edhe rezultate të barabarta."""
    rnd = random.Random(seed)
    pi = list(pi_fillestar)
    n = len(pi)
    mire = vlera(graf, pi, ref)
    for hap in range(hapa):
        i = rnd.randrange(n)
        j = i + rnd.randint(1, dritarja)
        if j >= n:
            continue
        pi[i], pi[j] = pi[j], pi[i]
        v = vlera(graf, pi, ref)
        if v >= mire:                            # >= : pranojmë edhe të barabartën
            mire = v
        else:
            pi[i], pi[j] = pi[j], pi[i]
    return pi, mire


# ---------------------------------------------------------------
#  Formati i zgjidhjes
# ---------------------------------------------------------------

def eshte_permutacion(pi, n):
    """True nëse pi përmban çdo kulm nga 0 deri n-1 saktësisht një herë."""
    return sorted(pi) == list(range(n))


def vektori_vendimit(pi, t):
    """Vektori x = [p1, ..., pn, t] siç e kërkon sfida."""
    n = len(pi)
    assert eshte_permutacion(pi, n), "pi nuk është permutacion"
    assert 0 <= t <= n - 1, "t duhet të jetë në {0, ..., n-1}"
    return list(pi) + [t]

def renditja_me_peshat(graf, peshat, ndarje):
    """Heq kulmin me pikën më të vogël, ku pika = p0*d + p1*fill + p2*m:
    d = numri i fqinjëve, fill = skajet e reja që do të krijohen, m = shkalla mesatare e fqinjëve.
    peshat = (p0, p1, p2). ndarje = dict kulm -> numër, për barazimet."""
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
        return peshat[0] * d + peshat[1] * fill + peshat[2] * m

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