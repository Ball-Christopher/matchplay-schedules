/* Exhaustive search over translation-invariant movement rules.
 *
 * Rule: after each block the bowler in (pair p, position t) moves to
 * (pair p + d[t] mod M, position pi[t]).  Positions t = 0..K-1 (bowling order
 * 1..K); position t starts on the left lane iff t is even.  Lane cycle
 * (who bowls after whom on a lane): odd positions then even positions
 * (1,3,5,..,2,4,..) -- see model.py.
 *
 * Because the rule is translation invariant, bowler (p,t) and bowler (p+delta,u)
 * meet in block b iff delta == s_t(b) - s_u(b) where s_t(b) is the total
 * shift of a bowler that started in position t.  So every statistic can be
 * kept per class (t, u, delta), each class standing for M couples.
 *
 * Score (lexicographic, smaller better), for each B = 1..BMAX:
 *   pair_spread (hard constraint: lane-pair balance), max_meet, max_follow, repeats, follow_repeats, max_ufollow,
 *   ufollow_repeats, [neg_min_meet is always 0 for rules: same-start-position
 *   bowlers never meet], exclusion (couples that can never meet, over the
 *   rule's period), side_spread, pos_spread,
 *   complexity (1000 per non-fixed point of pi, plus sum |d_t|).
 * The "universal" rule is the one matching the per-B optimum on the first
 * NFU fields (default 9 = through exclusion) for the longest prefix of B.
 *
 * Usage: rulesearch M K BMAX [NFU]  -> JSON lines on stdout.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXK 5
#define MAXM 10
#define MAXB 12
#define NF 12

static int M, K, BMAX, NFU = 9;
static int pred[MAXK];

typedef struct { int v[NF]; } Score;

static int cmp(const Score *a, const Score *b, int n) {
    for (int i = 0; i < n; i++) {
        if (a->v[i] < b->v[i]) return -1;
        if (a->v[i] > b->v[i]) return 1;
    }
    return 0;
}

static int perms[120][MAXK], nperm;
static void genperm(int *a, int k) {
    if (k == K) { memcpy(perms[nperm++], a, sizeof(int) * K); return; }
    for (int i = k; i < K; i++) {
        int t = a[k]; a[k] = a[i]; a[i] = t;
        genperm(a, k + 1);
        t = a[k]; a[k] = a[i]; a[i] = t;
    }
}

static int cabs(int x) { x = ((x % M) + M) % M; return x > M - x ? M - x : x; }

/* exclusion: number of unordered couples that never meet over the period */
static int exclusion(const int *d, const int *pi) {
    int ord = 1, x[MAXK];
    for (int t = 0; t < K; t++) x[t] = pi[t];
    for (;;) { int id = 1; for (int t = 0; t < K; t++) if (x[t] != t) id = 0;
        if (id) break; for (int t = 0; t < K; t++) x[t] = pi[x[t]]; ord++; }
    int H = M * ord;
    static char seen[MAXK][MAXK][MAXM];
    memset(seen, 0, sizeof seen);
    int s[MAXK], ty[MAXK];
    for (int t = 0; t < K; t++) { s[t] = 0; ty[t] = t; }
    for (int b = 0; b < H; b++) {
        for (int t = 0; t < K; t++) for (int u = t + 1; u < K; u++)
            seen[t][u][((s[t] - s[u]) % M + M) % M] = 1;
        for (int t = 0; t < K; t++) { s[t] = (s[t] + d[ty[t]]) % M; ty[t] = pi[ty[t]]; }
    }
    int cnt = K * M * (M - 1) / 2;   /* same start position: never */
    for (int t = 0; t < K; t++) for (int u = t + 1; u < K; u++)
        for (int dl = 0; dl < M; dl++) if (!seen[t][u][dl]) cnt += M;
    return cnt;
}

static Score best[MAXB + 1];
static int bestd[MAXB + 1][MAXK], bestpi[MAXB + 1][MAXK], nbest[MAXB + 1];

/* evaluate rule; mode 0: update best; mode 1: return prefix length of B's
 * (starting at 1) where the rule matches best[B] on the first nf fields */
static int run(const int *d, const int *pi, int mode, int nf) {
    int meet[MAXK][MAXK][MAXM], fol[MAXK][MAXK][MAXM];
    int vis[MAXK][MAXM], posc[MAXK][MAXK], left[MAXK];
    memset(meet, 0, sizeof meet); memset(fol, 0, sizeof fol);
    memset(vis, 0, sizeof vis); memset(posc, 0, sizeof posc); memset(left, 0, sizeof left);
    int s[MAXK], ty[MAXK], inv[MAXK];
    for (int t = 0; t < K; t++) { s[t] = 0; ty[t] = t; }
    int maxm = 0, rep = 0, maxf = 0, frep = 0;
    int comp = 0;
    for (int t = 0; t < K; t++) { if (pi[t] != t) comp += 1000; comp += cabs(d[t]); }
    int excl = -1;
    int prefix = 0;
    for (int b = 0; b < BMAX; b++) {
        for (int t = 0; t < K; t++) inv[ty[t]] = t;
        for (int t = 0; t < K; t++) for (int u = t + 1; u < K; u++) {
            int dl = ((s[t] - s[u]) % M + M) % M;
            int c = ++meet[t][u][dl];
            if (c > maxm) maxm = c;
            if (c > 1) rep += M;
        }
        for (int t = 0; t < K; t++) {
            int u = inv[pred[ty[t]]];
            if (u == t) continue;
            int dl = ((s[t] - s[u]) % M + M) % M;
            int c = ++fol[t][u][dl];
            if (c > maxf) maxf = c;
            if (c > 1) frep += M;
            vis[t][s[t]]++; posc[t][ty[t]]++; if (ty[t] % 2 == 0) left[t]++;
        }
        if (K == 1) { vis[0][s[0]]++; posc[0][0]++; left[0]++; }
        int B = b + 1;
        Score sc; memset(&sc, 0, sizeof sc);
        int ps = 0;
        for (int t = 0; t < K; t++) {
            int mn = 1 << 30, mx = 0;
            for (int p = 0; p < M; p++) { if (vis[t][p] < mn) mn = vis[t][p]; if (vis[t][p] > mx) mx = vis[t][p]; }
            if (mx - mn > ps) ps = mx - mn;
        }
        sc.v[0] = ps; sc.v[1] = maxm; sc.v[2] = maxf; sc.v[3] = rep; sc.v[4] = frep;
        int c6 = (mode == 0) ? cmp(&sc, &best[B], 5) : 0;
        if (mode == 0 && c6 > 0) goto advance;
        if (mode == 1 && cmp(&sc, &best[B], 5 < nf ? 5 : nf) != 0) return prefix;
        {
            /* unordered follows */
            int mu = 0, ur = 0;
            for (int t = 0; t < K; t++) for (int u = t + 1; u < K; u++)
                for (int dl = 0; dl < M; dl++) {
                    int c = fol[t][u][dl] + fol[u][t][(M - dl) % M];
                    if (c > mu) mu = c;
                    if (c > 1) ur += M * (c - 1);
                }
            /* repeats above counted +M per increment beyond 1: equals sum max(0,c-1)*M */
            int lmin = 1 << 30, lmax = 0, qs = 0;
            for (int t = 0; t < K; t++) {
                int mn = 1 << 30, mx = 0;
                for (int q = 0; q < K; q++) { if (posc[t][q] < mn) mn = posc[t][q]; if (posc[t][q] > mx) mx = posc[t][q]; }
                if (mx - mn > qs) qs = mx - mn;
                if (left[t] < lmin) lmin = left[t];
                if (left[t] > lmax) lmax = left[t];
            }
            sc.v[5] = mu; sc.v[6] = ur; sc.v[7] = 0;
            if (mode == 0 && cmp(&sc, &best[B], 8) > 0) goto advance;
            if (mode == 1 && cmp(&sc, &best[B], 8 < nf ? 8 : nf) != 0) return prefix;
            if (excl < 0) excl = exclusion(d, pi);
            sc.v[8] = excl; sc.v[9] = lmax - lmin; sc.v[10] = qs; sc.v[11] = comp;
            if (mode == 0) {
                int c = cmp(&sc, &best[B], 12);
                if (c < 0) { best[B] = sc; nbest[B] = 0;
                    memcpy(bestd[B], d, sizeof(int) * K); memcpy(bestpi[B], pi, sizeof(int) * K); }
                if (cmp(&sc, &best[B], 11) == 0) nbest[B]++;
            } else {
                if (cmp(&sc, &best[B], nf) != 0) return prefix;
                prefix = B;
            }
        }
    advance:
        for (int t = 0; t < K; t++) { s[t] = (s[t] + d[ty[t]]) % M; ty[t] = pi[ty[t]]; }
    }
    return prefix;
}

int main(int argc, char **argv) {
    M = atoi(argv[1]); K = atoi(argv[2]); BMAX = atoi(argv[3]);
    if (argc > 4) NFU = atoi(argv[4]);
    /* lane cycle: positions 0,2,4,..,1,3,.. (0-based) */
    int cyc[MAXK], n = 0;
    for (int t = 0; t < K; t += 2) cyc[n++] = t;
    for (int t = 1; t < K; t += 2) cyc[n++] = t;
    for (int i = 0; i < K; i++) pred[cyc[i]] = cyc[(i + K - 1) % K];
    int a[MAXK]; for (int i = 0; i < K; i++) a[i] = i;
    genperm(a, 0);
    for (int B = 0; B <= MAXB; B++) for (int i = 0; i < NF; i++) best[B].v[i] = 1 << 30;
    long total = 1; for (int t = 0; t < K; t++) total *= M;
    int d[MAXK];
    for (int pass = 0; pass < 2; pass++) {
        /* pass 1: find the rule optimal (fields 0..10, i.e. all but complexity)
         * for the longest prefix of B; tie-break complexity */
        int bestpre = -1, bpcomp = 1 << 30, bpd[MAXK], bppi[MAXK];
        for (int ip = 0; ip < nperm; ip++)
            for (long code = 0; code < total; code++) {
                long c = code;
                for (int t = 0; t < K; t++) { d[t] = c % M; c /= M; }
                if (pass == 0) run(d, perms[ip], 0, 0);
                else {
                    int pre = run(d, perms[ip], 1, NFU);
                    int comp = 0;
                    for (int t = 0; t < K; t++) { if (perms[ip][t] != t) comp += 1000; comp += cabs(d[t]); }
                    if (pre > bestpre || (pre == bestpre && comp < bpcomp)) {
                        bestpre = pre; bpcomp = comp;
                        memcpy(bpd, d, sizeof(int) * K); memcpy(bppi, perms[ip], sizeof(int) * K);
                    }
                }
            }
        if (pass == 0) {
            for (int B = 1; B <= BMAX; B++) {
                printf("{\"kind\":\"best\",\"M\":%d,\"K\":%d,\"B\":%d,\"score\":[", M, K, B);
                for (int i = 0; i < NF; i++) printf("%d%s", best[B].v[i], i < NF - 1 ? "," : "");
                printf("],\"n_optimal\":%d,\"d\":[", nbest[B]);
                for (int t = 0; t < K; t++) printf("%d%s", bestd[B][t], t < K - 1 ? "," : "");
                printf("],\"pi\":[");
                for (int t = 0; t < K; t++) printf("%d%s", bestpi[B][t], t < K - 1 ? "," : "");
                printf("]}\n");
            }
        } else {
            printf("{\"kind\":\"universal\",\"M\":%d,\"K\":%d,\"prefix\":%d,\"d\":[", M, K, bestpre);
            for (int t = 0; t < K; t++) printf("%d%s", bpd[t], t < K - 1 ? "," : "");
            printf("],\"pi\":[");
            for (int t = 0; t < K; t++) printf("%d%s", bppi[t], t < K - 1 ? "," : "");
            printf("]}\n");
        }
        fflush(stdout);
    }
    return 0;
}
