/* Independent search: 15 lane-balanced words (len 6 over 5 lanes), cells exactly 3,
   pairwise agreement <= AMAX, invariant under a given (sigma,tau) in S6 x S5.
   usage: sym AMAX type(-1=trivial group, 0..18) [nodelimit] [mode]
     mode 0: full search for 15 words (exact cells)
     mode k>0: sanity (a): find any k pairwise-compatible words, cells <=3 (trivial group only)
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define NW 1800
#define MAXO 1800
#define BW ((MAXO+63)/64)
typedef uint64_t bs[BW];

static int W[NW][6], nw = 0;
static int AMAX;
static int sig[6], tau[5];
static int norb, osize[MAXO], owords[MAXO][5], ocnt[MAXO][30];
static bs compat[MAXO], over[30][4], cellm[30], sizeover[16];
static long long nodes = 0, nodelimit = 0;
static int nsol = 0, chosen[16], nch = 0;
static int nb; /* bitset words in use */

static int code(const int *w) { int c = 0; for (int i = 0; i < 6; i++) c = c * 5 + w[i]; return c; }
static int idx[15625];
static int agree(int a, int b) { int s = 0; for (int i = 0; i < 6; i++) s += W[a][i] == W[b][i]; return s; }
static void act(const int *w, int *o) { for (int i = 0; i < 6; i++) o[sig[i]] = tau[w[i]]; }

static void gen(void) {
    memset(idx, -1, sizeof idx);
    for (int c = 0; c < 15625; c++) {
        int w[6], x = c, cnt[5] = {0};
        for (int i = 5; i >= 0; i--) { w[i] = x % 5; x /= 5; }
        for (int i = 0; i < 6; i++) cnt[w[i]]++;
        int ok = 1; for (int l = 0; l < 5; l++) if (cnt[l] < 1 || cnt[l] > 2) ok = 0;
        if (!ok) continue;
        memcpy(W[nw], w, sizeof w); idx[c] = nw++;
    }
}

/* types: list of (p,a,b) */
static int TP[19], TA[19], TB[19], NT = 0;
static void types(void) {
    int P[3] = {2, 3, 5};
    for (int k = 0; k < 3; k++) { int p = P[k];
        for (int a = 0; a * p <= 6; a++) for (int b = 0; b * p <= 5; b++) {
            if (!a && !b) continue;
            TP[NT] = p; TA[NT] = a; TB[NT] = b; NT++; } }
}
static void setperm(int *perm, int n, int p, int c) {
    for (int i = 0; i < n; i++) perm[i] = i;
    for (int j = 0; j < c; j++) for (int i = 0; i < p; i++) perm[j * p + i] = j * p + (i + 1) % p;
}

static void bset(uint64_t *b, int i) { b[i >> 6] |= 1ULL << (i & 63); }

static void report(void) {
    nsol++;
    if (nsol <= 3) {
        printf("SOLUTION %d:", nsol);
        for (int k = 0; k < nch; k++) for (int j = 0; j < osize[chosen[k]]; j++) {
            int w = owords[chosen[k]][j]; printf(" ");
            for (int i = 0; i < 6; i++) printf("%c", 'A' + W[w][i]); }
        printf("\n");
        /* verify independently */
        int ws[15], n = 0, cnt[30] = {0}, ok = 1;
        for (int k = 0; k < nch; k++) for (int j = 0; j < osize[chosen[k]]; j++) ws[n++] = owords[chosen[k]][j];
        if (n != 15) ok = 0;
        for (int a = 0; a < n; a++) { for (int i = 0; i < 6; i++) cnt[i * 5 + W[ws[a]][i]]++;
            for (int b = a + 1; b < n; b++) if (agree(ws[a], ws[b]) > AMAX || ws[a] == ws[b]) ok = 0; }
        for (int c = 0; c < 30; c++) if (cnt[c] != 3) ok = 0;
        printf("  verified: %s\n", ok ? "OK" : "FAIL");
    }
}

static int stopflag = 0;
static void rec(const uint64_t *cand, int *cnt, int nwds, int target, int exact) {
    if (stopflag) return;
    nodes++;
    if (nodelimit && nodes > nodelimit) { stopflag = 2; return; }
    if (nwds == target) { if (exact) { report(); if (nsol >= 1) stopflag = 1; } else { nsol++; stopflag = 1; } return; }
    uint64_t c2[BW];
    memcpy(c2, cand, nb * 8);
    if (exact) {
        int best = -1, bc = 1 << 30;
        for (int c = 0; c < 30; c++) if (cnt[c] < 3) {
            int k = 0; for (int i = 0; i < nb; i++) k += __builtin_popcountll(c2[i] & cellm[c][i]);
            if (k < bc) { bc = k; best = c; if (!k) return; }
        }
        for (int i = 0; i < nb; i++) {
            uint64_t m = c2[i] & cellm[best][i];
            while (m) {
                int b = __builtin_ctzll(m); m &= m - 1; int o = i * 64 + b;
                c2[i] &= ~(1ULL << b);
                uint64_t nc[BW]; int ncnt[30];
                memcpy(ncnt, cnt, sizeof ncnt);
                for (int c = 0; c < 30; c++) ncnt[c] += ocnt[o][c];
                int nn = nwds + osize[o];
                for (int j = 0; j < nb; j++) {
                    uint64_t v = c2[j] & compat[o][j] & ~sizeover[15 - nn][j];
                    for (int c = 0; c < 30; c++) if (ocnt[o][c]) v &= ~over[c][3 - ncnt[c]][j];
                    nc[j] = v;
                }
                /* need full re-filter of over for all cells: cells not touched by o unchanged, fine */
                chosen[nch++] = o;
                rec(nc, ncnt, nn, target, exact);
                nch--;
                if (stopflag) return;
            }
        }
    } else {
        /* sanity: pick any candidate in increasing order */
        for (int i = 0; i < nb; i++) {
            uint64_t m = c2[i];
            while (m) {
                int b = __builtin_ctzll(m); m &= m - 1; int o = i * 64 + b;
                c2[i] &= ~(1ULL << b);
                uint64_t nc[BW]; int ncnt[30]; memcpy(ncnt, cnt, sizeof ncnt);
                for (int c = 0; c < 30; c++) ncnt[c] += ocnt[o][c];
                for (int j = 0; j < nb; j++) {
                    uint64_t v = c2[j] & compat[o][j];
                    for (int c = 0; c < 30; c++) if (ocnt[o][c]) v &= ~over[c][3 - ncnt[c]][j];
                    nc[j] = v; }
                rec(nc, ncnt, nwds + osize[o], target, exact);
                if (stopflag) return;
            }
        }
    }
}

int main(int argc, char **argv) {
    AMAX = atoi(argv[1]); int t = atoi(argv[2]);
    if (argc > 3) nodelimit = atoll(argv[3]);
    int mode = argc > 4 ? atoi(argv[4]) : 0;
    gen(); types();
    if (t == -2) { printf("words=%d types=%d\n", nw, NT);
        for (int i = 0; i < NT; i++) printf("type %2d: p=%d a=%d b=%d\n", i, TP[i], TA[i], TB[i]); return 0; }
    if (t < 0) { for (int i = 0; i < 6; i++) sig[i] = i; for (int i = 0; i < 5; i++) tau[i] = i; }
    else { setperm(sig, 6, TP[t], TA[t]); setperm(tau, 5, TP[t], TB[t]); }
    /* orbits */
    static int seen[NW]; memset(seen, 0, sizeof seen);
    int clashing = 0, overfull = 0, rawo = 0;
    norb = 0;
    for (int s = 0; s < nw; s++) if (!seen[s]) {
        int ow[6], n = 0, cur = s;
        do { ow[n++] = cur; seen[cur] = 1; int nx[6]; act(W[cur], nx); cur = idx[code(nx)]; } while (cur != s);
        rawo++;
        int bad = 0; for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) if (agree(ow[a], ow[b]) > AMAX) bad = 1;
        if (bad) { clashing++; continue; }
        int cc[30] = {0}; for (int a = 0; a < n; a++) for (int i = 0; i < 6; i++) cc[i * 5 + W[ow[a]][i]]++;
        int of = 0; for (int c = 0; c < 30; c++) if (cc[c] > 3) of = 1;
        if (of) { overfull++; continue; }
        osize[norb] = n; memcpy(owords[norb], ow, n * sizeof(int)); memcpy(ocnt[norb], cc, sizeof cc); norb++;
    }
    nb = (norb + 63) / 64;
    memset(compat, 0, sizeof compat); memset(over, 0, sizeof over); memset(cellm, 0, sizeof cellm); memset(sizeover, 0, sizeof sizeover);
    for (int a = 0; a < norb; a++) {
        for (int b = 0; b < norb; b++) if (a != b) {
            int ok = 1;
            for (int i = 0; i < osize[a] && ok; i++) for (int j = 0; j < osize[b]; j++) if (agree(owords[a][i], owords[b][j]) > AMAX) { ok = 0; break; }
            if (ok) bset(compat[a], b);
        }
        for (int c = 0; c < 30; c++) {
            if (ocnt[a][c]) bset(cellm[c], a);
            /* over[c][r]: orbits with count in c > r (r = remaining room 0..3) */
            for (int r = 0; r < 4; r++) if (ocnt[a][c] > r) bset(over[c][r], a);
        }
        for (int r = 0; r <= 15; r++) if (osize[a] > r) bset(sizeover[r], a);
    }
    int cnt[30] = {0}; uint64_t cand[BW]; memset(cand, 0, sizeof cand);
    for (int a = 0; a < norb; a++) bset(cand, a);
    clock_t t0 = clock();
    if (mode == 0) rec(cand, cnt, 0, 15, 1); else rec(cand, cnt, 0, mode, 0);
    double el = (double)(clock() - t0) / CLOCKS_PER_SEC;
    if (t >= 0) printf("type %2d p=%d a=%d b=%d", t, TP[t], TA[t], TB[t]); else printf("trivial group");
    printf(" AMAX=%d mode=%d | orbits=%d clashing=%d overfull=%d usable=%d | nodes=%lld | %s | %.2fs\n",
        AMAX, mode, rawo, clashing, overfull, norb, nodes,
        stopflag == 2 ? "NODE LIMIT (inconclusive)" : (nsol ? "FOUND" : "NONE (exhaustive)"), el);
    return 0;
}
