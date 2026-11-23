/* Two-phase simulated annealing for unrestricted qualifying draws.
 *
 * Usage: anneal M K B seconds seed capM capF capU tmin [lbc1 lbc2]
 *   capM  target max meetings per couple       (phase 1)
 *   tmin  target min meetings per couple       (phase 1, 0 = none)
 *   capF  target max ordered follows per couple (phase 2)
 *   capU  target max unordered follows          (phase 2)
 *   lbc1, lbc2: lower bounds of the phase costs (stop early when reached)
 *
 * Lane-pair balance is kept as a HARD constraint (moves that would break it
 * are rejected) whenever the start is balanced; the default start (everyone
 * moves one pair right together) is.  With ANNEAL_SOFT or an unbalanced
 * initial draw it is a penalty of weight PW instead.
 * Phase 1 (who shares which pair in each block): block 1 fixed, moves swap
 * two bowlers between pairs of one block (conflict-directed) or swap two
 * whole groups between pairs.  Cost
 *   PW * pair-visit counts outside floor/ceil(B/M)   (lane-pair balance, hard)
 *   + 30 * sum max(0, meet - capM) + sum max(0, meet - 1) + sum max(0, tmin - meet).
 * Phase 2 (groups and pairs frozen): moves reorder bowlers inside a pair.  Cost
 *   5000 * excess ordered follows over capF + 200 * ordered follow repeats
 *   + 50 * excess unordered follows over capU + 20 * unordered follow repeats
 *   + 1 * left-start counts outside floor/ceil of the mean
 *   + 2 * position counts outside floor/ceil(B/K).
 * Prints {"cost1":..,"cost2":..,"draw":[[[...]]]}.  Same follow convention
 * as model.py (lane cycle 1,3,5,..,2,4,..).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define MAXN 50
#define MAXB 12
#define MAXM 10
#define MAXK 5

static int M, K, B, N;
static int capM, capF, capU, tmin;
static int pred[MAXK];
static int slot[MAXB][MAXN];
static int meet[MAXN][MAXN], fol[MAXN][MAXN];
static int vis[MAXN][MAXM], posc[MAXN][MAXK], leftc[MAXN];
static int pf, pc, sf, sc, qf, qc;
static int phase;
static int PW = 3;   /* weight of a lane-pair balance violation in phase 1 (env ANNEAL_PW) */

static unsigned long long rs = 88172645463325252ULL;
static inline unsigned long long xr(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double ur(void) { return (xr() >> 11) * (1.0 / 9007199254740992.0); }

static inline long cm(int m) {
    long c = 0;
    if (m > capM) c += 30L * (m - capM);
    if (m > 1) c += (m - 1);
    if (m < tmin) c += (tmin - m);
    return c;
}
static inline long cf(int f) { long c = 0; if (f > capF) c += 5000L * (f - capF); if (f > 1) c += 200L * (f - 1); return c; }
static inline long cu(int u) { long c = 0; if (u > capU) c += 50L * (u - capU); if (u > 1) c += 20L * (u - 1); return c; }
static inline long rng(int v, int lo, int hi, long w) { return v < lo ? w * (lo - v) : v > hi ? w * (v - hi) : 0; }

static long apply(int b, int p, int sg) {
    long d = 0;
    int *x = &slot[b][p * K];
    if (phase == 1) {
        for (int i = 0; i < K; i++) for (int j = i + 1; j < K; j++) {
            int a = x[i], c = x[j], m = meet[a][c];
            d += cm(m + sg) - cm(m);
            meet[a][c] = meet[c][a] = m + sg;
        }
        for (int i = 0; i < K; i++) {   /* lane-pair balance: hard, weight PW */
            int a = x[i], v = vis[a][p];
            d += rng(v + sg, pf, pc, PW) - rng(v, pf, pc, PW);
            vis[a][p] = v + sg;
        }
        return d;
    }
    for (int i = 0; i < K; i++) {
        int a = x[i], c = x[pred[i]];
        if (a != c) {
            int f = fol[a][c], g = fol[c][a];
            d += cf(f + sg) - cf(f);
            d += cu(f + g + sg) - cu(f + g);
            fol[a][c] = f + sg;
        }
        int v = posc[a][i];
        d += rng(v + sg, qf, qc, 2) - rng(v, qf, qc, 2);
        posc[a][i] = v + sg;
        if (i % 2 == 0) {
            v = leftc[a];
            d += rng(v + sg, sf, sc, 1) - rng(v, sf, sc, 1);
            leftc[a] = v + sg;
        }
    }
    return d;
}

static long rebuild(void) {
    memset(meet, 0, sizeof meet); memset(fol, 0, sizeof fol); memset(vis, 0, sizeof vis);
    memset(posc, 0, sizeof posc); memset(leftc, 0, sizeof leftc);
    long c = 0;
    for (int b = 0; b < B; b++) for (int p = 0; p < M; p++) apply(b, p, 1);
    if (phase == 1) {
        for (int a = 0; a < N; a++) for (int b = a + 1; b < N; b++) c += cm(meet[a][b]);
        for (int a = 0; a < N; a++) for (int p = 0; p < M; p++) c += rng(vis[a][p], pf, pc, PW);
        return c;
    }
    for (int a = 0; a < N; a++) for (int b = a + 1; b < N; b++) c += cu(fol[a][b] + fol[b][a]);
    for (int a = 0; a < N; a++) for (int b = 0; b < N; b++) if (a != b) c += cf(fol[a][b]);
    for (int a = 0; a < N; a++) {
        for (int q = 0; q < K; q++) c += rng(posc[a][q], qf, qc, 2);
        c += rng(leftc[a], sf, sc, 1);
    }
    return c;
}

static int bestslot[MAXB][MAXN];
static int hard;   /* 1: lane-pair balance kept as a hard constraint in phase 1 */
static inline int okmove(int a, int from, int to) { return vis[a][to] + 1 <= pc && vis[a][from] - 1 >= pf; }

/* does pair p of block b contain a costly couple (phase 1)? */
static int hot(int b, int p) {
    int *x = &slot[b][p * K];
    for (int i = 0; i < K; i++) for (int j = i + 1; j < K; j++) if (meet[x[i]][x[j]] > 1) return 1;
    return 0;
}

static long anneal(double secs, long lbc, double Tst, double Tend) {
    long cost = rebuild(), bestc = cost;
    memcpy(bestslot, slot, sizeof slot);
    if (cost <= lbc) return cost;
    clock_t t0 = clock();
    long chunk = 200000, it = 0;
    long round_len = phase == 1 ? 4000000 : 1000000;
    double T = Tst;
    int b0 = phase == 1 ? 1 : 0;
    if (B - b0 <= 0) return cost;
    for (;;) {
        if (it % chunk == 0 && (double)(clock() - t0) / CLOCKS_PER_SEC > secs) break;
        long r = it % round_len;
        if (r == 0 && it > 0) {   /* restart round from best */
            memcpy(slot, bestslot, sizeof slot);
            cost = rebuild();
        }
        T = Tst * pow(Tend / Tst, (double)r / round_len);
        it++;
        int b = b0 + xr() % (B - b0);
        long d;
        if (phase == 1 && M > 1 && B - b0 >= 2 && xr() % 3 == 0) {
            /* double swap: bowler a (pair p in block b, pair q in block b2) and
             * bowler c (pair q in b, pair p in b2) exchange seats in both
             * blocks.  Every bowler keeps the same multiset of pairs, so
             * lane-pair balance is preserved (needed when B >= M). */
            int b2 = b0 + xr() % (B - b0);
            if (b2 == b) continue;
            int s1 = xr() % N, a = slot[b][s1], p = s1 / K;
            int s2 = 0; while (slot[b2][s2] != a) s2++;
            int q = s2 / K;
            if (p == q) continue;
            int cand[MAXK], nc = 0, cs1[MAXK];
            for (int i = 0; i < K; i++) {
                int c = slot[b][q * K + i];
                for (int j = 0; j < K; j++) if (slot[b2][p * K + j] == c) { cand[nc] = q * K + i; cs1[nc++] = p * K + j; }
            }
            if (!nc) continue;
            int k = xr() % nc, t1 = cand[k], t2 = cs1[k];
            d = apply(b, p, -1) + apply(b, q, -1) + apply(b2, p, -1) + apply(b2, q, -1);
            int t = slot[b][s1]; slot[b][s1] = slot[b][t1]; slot[b][t1] = t;
            t = slot[b2][s2]; slot[b2][s2] = slot[b2][t2]; slot[b2][t2] = t;
            d += apply(b, p, 1) + apply(b, q, 1) + apply(b2, p, 1) + apply(b2, q, 1);
            if (d <= 0 || ur() < exp(-d / T)) {
                cost += d;
                if (cost < bestc) { bestc = cost; memcpy(bestslot, slot, sizeof slot); if (bestc <= lbc) break; }
            } else {
                apply(b, p, -1); apply(b, q, -1); apply(b2, p, -1); apply(b2, q, -1);
                t = slot[b][s1]; slot[b][s1] = slot[b][t1]; slot[b][t1] = t;
                t = slot[b2][s2]; slot[b2][s2] = slot[b2][t2]; slot[b2][t2] = t;
                apply(b, p, 1); apply(b, q, 1); apply(b2, p, 1); apply(b2, q, 1);
            }
        } else if (phase == 1 && M > 1 && xr() % 4 == 0) {
            int p1 = xr() % M, p2 = xr() % M;
            if (p1 == p2) continue;
            if (hard) {
                int ok = 1;
                for (int q = 0; q < K && ok; q++)
                    ok = okmove(slot[b][p1 * K + q], p1, p2) && okmove(slot[b][p2 * K + q], p2, p1);
                if (!ok) continue;
            }
            d = apply(b, p1, -1) + apply(b, p2, -1);
            for (int q = 0; q < K; q++) { int t = slot[b][p1 * K + q]; slot[b][p1 * K + q] = slot[b][p2 * K + q]; slot[b][p2 * K + q] = t; }
            d += apply(b, p1, 1) + apply(b, p2, 1);
            if (d <= 0 || ur() < exp(-d / T)) {
                cost += d;
                if (cost < bestc) { bestc = cost; memcpy(bestslot, slot, sizeof slot); if (bestc <= lbc) break; }
            } else {
                apply(b, p1, -1); apply(b, p2, -1);
                for (int q = 0; q < K; q++) { int t = slot[b][p1 * K + q]; slot[b][p1 * K + q] = slot[b][p2 * K + q]; slot[b][p2 * K + q] = t; }
                apply(b, p1, 1); apply(b, p2, 1);
            }
        } else if (phase == 1) {
            int s1 = xr() % N;
            for (int tries = 0; tries < 4 && !hot(b, s1 / K); tries++) s1 = xr() % N;
            int s2 = xr() % N;
            int p1 = s1 / K, p2 = s2 / K;
            if (p1 == p2) continue;
            if (hard && !(okmove(slot[b][s1], p1, p2) && okmove(slot[b][s2], p2, p1))) continue;
            d = apply(b, p1, -1) + apply(b, p2, -1);
            int t = slot[b][s1]; slot[b][s1] = slot[b][s2]; slot[b][s2] = t;
            d += apply(b, p1, 1) + apply(b, p2, 1);
            if (d <= 0 || ur() < exp(-d / T)) {
                cost += d;
                if (cost < bestc) { bestc = cost; memcpy(bestslot, slot, sizeof slot); if (bestc <= lbc) break; }
            } else {
                apply(b, p1, -1); apply(b, p2, -1);
                t = slot[b][s1]; slot[b][s1] = slot[b][s2]; slot[b][s2] = t;
                apply(b, p1, 1); apply(b, p2, 1);
            }
        } else {
            int p1 = xr() % M, p2;
            int grp = 0;   /* groups and their pairs are frozen in phase 2 */
            if (grp) { p2 = xr() % M; if (p2 == p1) continue; }
            else p2 = p1;
            int i = xr() % K, j = xr() % K;
            if (!grp && i == j) continue;
            d = apply(b, p1, -1); if (grp) d += apply(b, p2, -1);
            if (grp) for (int q = 0; q < K; q++) { int t = slot[b][p1 * K + q]; slot[b][p1 * K + q] = slot[b][p2 * K + q]; slot[b][p2 * K + q] = t; }
            else { int t = slot[b][p1 * K + i]; slot[b][p1 * K + i] = slot[b][p1 * K + j]; slot[b][p1 * K + j] = t; }
            d += apply(b, p1, 1); if (grp) d += apply(b, p2, 1);
            if (d <= 0 || ur() < exp(-d / T)) {
                cost += d;
                if (cost < bestc) { bestc = cost; memcpy(bestslot, slot, sizeof slot); if (bestc <= lbc) break; }
            } else {
                apply(b, p1, -1); if (grp) apply(b, p2, -1);
                if (grp) for (int q = 0; q < K; q++) { int t = slot[b][p1 * K + q]; slot[b][p1 * K + q] = slot[b][p2 * K + q]; slot[b][p2 * K + q] = t; }
                else { int t = slot[b][p1 * K + i]; slot[b][p1 * K + i] = slot[b][p1 * K + j]; slot[b][p1 * K + j] = t; }
                apply(b, p1, 1); if (grp) apply(b, p2, 1);
            }
        }
    }
    memcpy(slot, bestslot, sizeof slot);
    if (getenv("ANNEAL_DEBUG")) fprintf(stderr, "phase %d iters %ld best %ld\n", phase, it, bestc);
    return bestc;
}

int main(int argc, char **argv) {
    if (argc < 10) { fprintf(stderr, "usage: anneal M K B secs seed capM capF capU tmin [lbc1 lbc2] [init.txt]\n"); return 1; }
    M = atoi(argv[1]); K = atoi(argv[2]); B = atoi(argv[3]);
    double secs = atof(argv[4]);
    rs ^= (unsigned long long)atoll(argv[5]) * 0x9E3779B97F4A7C15ULL; xr(); xr();
    capM = atoi(argv[6]); capF = atoi(argv[7]); capU = atoi(argv[8]); tmin = atoi(argv[9]);
    long lbc1 = argc > 10 ? atol(argv[10]) : 0, lbc2 = argc > 11 ? atol(argv[11]) : 0;
    N = M * K;
    if (getenv("ANNEAL_PW")) PW = atoi(getenv("ANNEAL_PW"));
    double T1s = getenv("ANNEAL_T") ? atof(getenv("ANNEAL_T")) : 2.0;
    int cyc[MAXK], n = 0;
    for (int t = 0; t < K; t += 2) cyc[n++] = t;
    for (int t = 1; t < K; t += 2) cyc[n++] = t;
    for (int i = 0; i < K; i++) pred[cyc[i]] = cyc[(i + K - 1) % K];
    pf = B / M; pc = (B + M - 1) / M;
    qf = B / K; qc = (B + K - 1) / K;
    int lnum = B * ((K + 1) / 2);
    sf = lnum / K; sc = (lnum + K - 1) / K;

    int have_init = 0;
    if (argc > 12) {  /* initial draw: B*N integers, block-major, slot order */
        FILE *f = fopen(argv[12], "r");
        if (f) { have_init = 1; for (int b = 0; b < B; b++) for (int i = 0; i < N; i++) if (fscanf(f, "%d", &slot[b][i]) != 1) have_init = 0; fclose(f); }
    }
    if (!have_init) {
        if (getenv("ANNEAL_SOFT"))
            for (int b = 0; b < B; b++) {
                for (int i = 0; i < N; i++) slot[b][i] = i;
                if (b > 0) for (int i = N - 1; i > 0; i--) { int j = xr() % (i + 1); int t = slot[b][i]; slot[b][i] = slot[b][j]; slot[b][j] = t; }
            }
        else   /* everybody moves one pair right together: balanced for any B */
            for (int b = 0; b < B; b++)
                for (int p = 0; p < M; p++) for (int q = 0; q < K; q++)
                    slot[b][((p + b) % M) * K + q] = p * K + q;
    }
    phase = 1;
    rebuild();
    hard = !getenv("ANNEAL_SOFT");
    for (int a = 0; a < N && hard; a++) for (int p = 0; p < M; p++)
        if (vis[a][p] < pf || vis[a][p] > pc) { hard = 0; break; }
    long c1 = anneal(secs * 0.75, lbc1, T1s, 0.05);
    if (K == 2) {  /* follows are fixed by the meetings when K = 2 */
        lbc2 = 0;
        for (int a = 0; a < N; a++) for (int b = a + 1; b < N; b++) {
            int m = meet[a][b];
            lbc2 += 2 * cf(m) + cu(2 * m);
        }
    }
    phase = 2;
    long c2 = anneal(secs * 0.25, lbc2, 300.0, 0.3);
    printf("{\"cost1\":%ld,\"cost2\":%ld,\"draw\":[", c1, c2);
    for (int b = 0; b < B; b++) {
        printf("%s[", b ? "," : "");
        for (int p = 0; p < M; p++) {
            printf("%s[", p ? "," : "");
            for (int q = 0; q < K; q++) printf("%s%d", q ? "," : "", slot[b][p * K + q]);
            printf("]");
        }
        printf("]");
    }
    printf("]}\n");
    return 0;
}
