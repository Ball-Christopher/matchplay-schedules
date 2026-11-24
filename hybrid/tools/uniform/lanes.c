/* Simulated annealing for lane pairs (C version of common.anneal_lanes).
   stdin: v n R W, then per week: cap ng k g1_1..g1_k ... (bowlers 1-based, groups of size k)
   usage: lanes seed seconds [restart_iters]
   Minimises sum over bowlers of (dev + W*(dev>0)), dev = distance of each lane count from
   [floor(R/n), ceil(R/n)].  Output: "off cost" then per week the slot list (group idx or -1). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#define MV 64
#define MW 32
#define MS 64
int v, n, R, W, cap[MW], ng[MW], gk[MW], grp[MW][40][4], slot[MW][MS], ns[MW];
int cnt[MV + 1][MS], dev[MV + 1], lo, hi, best[MW][MS], bestcost = 1 << 30, bestoff;
static unsigned long long rs;
static inline unsigned rnd(void){ rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)(rs >> 11); }
static inline double urand(void){ return (rnd() & 0xFFFFFF) / 16777216.0; }
static inline int pen(int c){ return c > hi ? c - hi : (c < lo ? lo - c : 0); }
static inline int bp(int d){ return d + W * (d > 0); }
int main(int argc, char **argv){
  rs = 0x9E3779B97F4A7C15ULL ^ (unsigned long long)atoll(argv[1]) * 2654435761ULL; for (int i = 0; i < 20; i++) rnd();
  double secs = atof(argv[2]); long rit = argc > 3 ? atol(argv[3]) : 3000000;
  if (scanf("%d %d %d %d", &v, &n, &R, &W) != 4) return 2;
  for (int w = 0; w < R; w++){
    if (scanf("%d %d %d", &cap[w], &ng[w], &gk[w]) != 3) return 2;
    for (int g = 0; g < ng[w]; g++) for (int t = 0; t < gk[w]; t++) if (scanf("%d", &grp[w][g][t]) != 1) return 2;
    ns[w] = n * cap[w];
  }
  lo = R / n; hi = (R + n - 1) / n;
  clock_t t0 = clock();
  while ((double)(clock() - t0) / CLOCKS_PER_SEC < secs && bestcost > 0){
    memset(cnt, 0, sizeof cnt);
    for (int w = 0; w < R; w++){
      for (int s = 0; s < ns[w]; s++) slot[w][s] = s < ng[w] ? s : -1;
      for (int s = ns[w] - 1; s > 0; s--){ int j = rnd() % (s + 1); int t = slot[w][s]; slot[w][s] = slot[w][j]; slot[w][j] = t; }
      for (int s = 0; s < ns[w]; s++) if (slot[w][s] >= 0) for (int t = 0; t < gk[w]; t++) cnt[grp[w][slot[w][s]][t]][s / cap[w]]++;
    }
    int cost = 0;
    for (int p = 1; p <= v; p++){ dev[p] = 0; for (int L = 0; L < n; L++) dev[p] += pen(cnt[p][L]); cost += bp(dev[p]); }
    double T = 2.0;
    for (long it = 0; it < rit && cost > 0; it++){
      int w = rnd() % R, c = cap[w], a = rnd() % ns[w], b = rnd() % ns[w];
      int La = a / c, Lb = b / c, ga = slot[w][a], gb = slot[w][b];
      if (La == Lb || (ga < 0 && gb < 0)) continue;
      int d = 0, np = 0, P[8], X[8], Y[8], DD[8];
      for (int side = 0; side < 2; side++){
        int g = side ? gb : ga, x = side ? Lb : La, y = side ? La : Lb;
        if (g < 0) continue;
        for (int t = 0; t < gk[w]; t++){
          int p = grp[w][g][t];
          int dd = dev[p] + pen(cnt[p][x] - 1) - pen(cnt[p][x]) + pen(cnt[p][y] + 1) - pen(cnt[p][y]);
          d += bp(dd) - bp(dev[p]); P[np] = p; X[np] = x; Y[np] = y; DD[np] = dd; np++;
        }
      }
      if (d <= 0 || urand() < exp(-d / T)){
        for (int i = 0; i < np; i++){ cnt[P[i]][X[i]]--; cnt[P[i]][Y[i]]++; dev[P[i]] = DD[i]; }
        slot[w][a] = gb; slot[w][b] = ga; cost += d;
        if (cost < bestcost){
          bestcost = cost; bestoff = 0; for (int p = 1; p <= v; p++) bestoff += dev[p] > 0;
          memcpy(best, slot, sizeof slot);
        }
      }
      T *= 0.9999985; if (T < 0.08) T = 0.08;
    }
  }
  printf("%d %d\n", bestoff, bestcost);
  for (int w = 0; w < R; w++){ for (int s = 0; s < ns[w]; s++) printf("%d ", best[w][s]); printf("\n"); }
  return 0;
}
