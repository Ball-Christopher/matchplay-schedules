/* Simulated annealing for uniformly resolvable designs (couples meet exactly once).
   usage: urd v seed seconds k1,k2,...,kR [fixedfile]
   k_i = group size of week i (v divisible by k_i).  Weeks listed in fixedfile
   (one per line, the roster 0..v-1 in groups order, space separated) replace the
   first weeks and are never moved.  Prints the weeks (0-based, groups in order)
   when cost 0 is reached; exit 1 on timeout.
   Cost = sum over couples of max(0, meetings-1) (= number of unmet couples). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#define MV 64
#define MR 64
int v, R, K[MR], perm[MR][MV], pos[MR][MV], meet[MV][MV], nfix;
static unsigned long long rs;
static inline unsigned rnd(void){ rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)(rs >> 11); }
static inline double urand(void){ return (rnd() & 0xffffff) / 16777216.0; }
int cost(void){ int c = 0; for (int a = 0; a < v; a++) for (int b = a+1; b < v; b++) if (meet[a][b] > 1) c += meet[a][b]-1; return c; }
void addweek(int w, int s){ int k = K[w]; for (int g = 0; g < v; g += k) for (int i = 0; i < k; i++) for (int j = i+1; j < k; j++){
  int a = perm[w][g+i], b = perm[w][g+j]; meet[a][b] += s; meet[b][a] += s; } }
int main(int argc, char **argv){
  v = atoi(argv[1]); rs = 88172645463325252ULL ^ (unsigned long long)atoll(argv[2]) * 2654435761ULL; double secs = atof(argv[3]);
  char *s = argv[4]; R = 0; while (*s){ K[R++] = atoi(s); while (*s && *s != ',') s++; if (*s) s++; }
  for (int i = 0; i < 20; i++) rnd();
  for (int w = 0; w < R; w++){ for (int i = 0; i < v; i++) perm[w][i] = i; for (int i = v-1; i > 0; i--){ int j = rnd() % (i+1); int t = perm[w][i]; perm[w][i] = perm[w][j]; perm[w][j] = t; } }
  nfix = 0;
  if (argc > 5){ FILE *f = fopen(argv[5], "r"); int x, i = 0; while (fscanf(f, "%d", &x) == 1){ perm[i / v][i % v] = x; i++; } fclose(f); nfix = i / v; }
  for (int w = 0; w < R; w++){ for (int i = 0; i < v; i++) pos[w][perm[w][i]] = i; addweek(w, 1); }
  int c = cost(), best = c; double T = 2.0; long it = 0; clock_t t0 = clock();
  long since = 0;
  while (c > 0){
    if ((++it & 0xfffff) == 0){ if ((double)(clock()-t0)/CLOCKS_PER_SEC > secs) break; }
    int w = nfix + rnd() % (R - nfix), k = K[w];
    int i = rnd() % v, j = rnd() % v; if (i / k == j / k) continue;
    int p = perm[w][i], q = perm[w][j], gi = i / k * k, gj = j / k * k, d = 0;
    for (int t = 0; t < k; t++){ int x = perm[w][gi+t]; if (x == p) continue;
      d -= meet[p][x] > 1; d += meet[q][x] > 0; }
    for (int t = 0; t < k; t++){ int x = perm[w][gj+t]; if (x == q) continue;
      d -= meet[q][x] > 1; d += meet[p][x] > 0; }
    if (d <= 0 || urand() < exp(-d / T)){
      for (int t = 0; t < k; t++){ int x = perm[w][gi+t]; if (x == p) continue; meet[p][x]--; meet[x][p]--; meet[q][x]++; meet[x][q]++; }
      for (int t = 0; t < k; t++){ int x = perm[w][gj+t]; if (x == q) continue; meet[q][x]--; meet[x][q]--; meet[p][x]++; meet[x][p]++; }
      perm[w][i] = q; perm[w][j] = p; c += d;
      if (c < best){ best = c; since = 0; }
    }
    if (++since > 4000000){ since = 0; best = c; T = 2.0; }   /* reheat */
    T *= 0.9999995; if (T < 0.25) T = 0.25;
  }
  if (c > 0){ fprintf(stderr, "timeout cost %d best %d it %ld\n", c, best, it); return 1; }
  for (int w = 0; w < R; w++){ for (int i = 0; i < v; i++) printf("%d ", perm[w][i]); printf("\n"); }
  fprintf(stderr, "solved it %ld %.1fs\n", it, (double)(clock()-t0)/CLOCKS_PER_SEC);
  return 0;
}
