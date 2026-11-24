/* Fast core of cyclic.py: find base parallel classes whose pairs hit pair-orbit keys
   at most once (exactly once by counting).  Input (stdin): V nkeys nclasses
   k_1..k_nclasses, then the V*V key table (-1 = pair never allowed), then nused and the
   keys already used (by fixed weeks).
   usage: basecls seed seconds nodelimit  < spec
   Output (stdout) on success: one line per block "c p1 p2 ..." (c = base class index). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
int V, NK, NC, KS[16], key[64][64], used[8192], freept[64];
long nodes, nodelimit; static unsigned long long rs;
static inline unsigned rnd(void){ rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)(rs >> 11); }
int stk[1024][8], stc[1024], nst;           /* completed blocks */
int rec_class(int c);
int rec_block(int c, int nfree);
/* extend current block cur[0..d-1] using candidates cand[start..] */
int ext(int c, int nfree, int d, int *cand, int nc, int start){
  int k = KS[c];
  if (d == k){
    stc[nst] = c; nst++;
    int r = rec_block(c, nfree - k);
    if (!r) nst--; return r;
  }
  for (int i = start; i < nc; i++){
    int q = cand[i]; if (!freept[q]) continue;
    int ks[8], n = 0, ok = 1, *cur = stk[nst];
    for (int t = 0; t < d && ok; t++){ int kk = key[cur[t]][q]; if (kk < 0 || used[kk]) ok = 0;
      else { for (int u = 0; u < n; u++) if (ks[u] == kk) ok = 0; ks[n++] = kk; } }
    if (!ok) continue;
    for (int t = 0; t < n; t++) used[ks[t]] = 1; freept[q] = 0; cur[d] = q;
    int r = ext(c, nfree, d + 1, cand, nc, i + 1);
    for (int t = 0; t < n; t++) used[ks[t]] = 0; freept[q] = 1;
    if (r) return 1;
    if (nodes > nodelimit) return 0;
  }
  return 0;
}
int rec_block(int c, int nfree){
  if (nfree == 0) return rec_class(c + 1);
  if (++nodes > nodelimit) return 0;
  int p = -1; for (int i = 0; i < V; i++) if (freept[i]){ p = i; break; }
  int cand[64], nc = 0;
  for (int q = p + 1; q < V; q++) if (freept[q] && key[p][q] >= 0 && !used[key[p][q]]) cand[nc++] = q;
  if (nc < KS[c] - 1) return 0;
  for (int i = nc - 1; i > 0; i--){ int j = rnd() % (i + 1); int t = cand[i]; cand[i] = cand[j]; cand[j] = t; }
  freept[p] = 0; stk[nst][0] = p;
  int r = ext(c, nfree, 1, cand, nc, 0);
  freept[p] = 1; return r;
}
int rec_class(int c){
  if (c == NC) return 1;
  int save[64]; memcpy(save, freept, sizeof save);
  for (int i = 0; i < V; i++) freept[i] = 1;
  int r = rec_block(c, V);
  memcpy(freept, save, sizeof save); return r;
}
int main(int argc, char **argv){
  rs = 0x9E3779B97F4A7C15ULL ^ (unsigned long long)atoll(argv[1]) * 1000003ULL; double secs = atof(argv[2]); nodelimit = atol(argv[3]);
  for (int i = 0; i < 10; i++) rnd();
  if (scanf("%d %d %d", &V, &NK, &NC) != 3) return 2;
  for (int c = 0; c < NC; c++) if (scanf("%d", &KS[c]) != 1) return 2;
  for (int a = 0; a < V; a++) for (int b = 0; b < V; b++) if (scanf("%d", &key[a][b]) != 1) return 2;
  int nu, init[8192]; if (scanf("%d", &nu) != 1) return 2; for (int i = 0; i < nu; i++) if (scanf("%d", &init[i]) != 1) return 2;
  clock_t t0 = clock(); long tries = 0;
  while ((double)(clock() - t0) / CLOCKS_PER_SEC < secs){
    memset(used, 0, sizeof used); for (int i = 0; i < nu; i++) used[init[i]] = 1;
    nodes = 0; nst = 0; tries++;
    if (rec_class(0)){
      for (int b = 0; b < nst; b++){ printf("%d", stc[b]); for (int t = 0; t < KS[stc[b]]; t++) printf(" %d", stk[b][t]); printf("\n"); }
      fprintf(stderr, "found after %ld tries %.1fs\n", tries, (double)(clock() - t0) / CLOCKS_PER_SEC);
      return 0;
    }
  }
  fprintf(stderr, "not found (%ld tries)\n", tries); return 1;
}
