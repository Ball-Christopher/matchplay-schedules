/* Exact Z_5-equivariant lane solve, decomposed by track.
   Design: Z_5 x 8 classes, 3 fixed weeks (2 base blocks each, blocks 0..5), 2 week orbits of 5
   (10 base blocks each, blocks 6..15 and 16..25).  Lane pairs = 2 tracks of 5 rotated by Z_5.
   A base block on lane (t,j) puts bowler (0,c) on (t, j-a) for each of its points (a,c).
   Step 1: choose which blocks go on track 0 (5 of 10 per orbit week, one of the two per fixed week);
           every class must then visit track 0 between 5 and 8 times.
   Step 2: the two tracks are independent; each is a small DFS over offsets (cells in {1,2}).
   A track problem is keyed by (subset S1, subset S2, fixed choice); track 1 is the complement key.
   stdin: per design 208 ints (26 blocks x 4 points x (class,residue)).  argv[1]=max solutions to print (default 1).
   Exhaustive: "sols 0" is a proof that no Z_5-equivariant 2-track lane assignment exists for that design. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int bc[26][4], ba[26][4];
int cnt[8][5], zeros[8], rem[8];
int items[13], off[13], usedj[2];
long long nodes;
static int place(int b, int j) {
    int k;
    for (k = 0; k < 4; k++) {
        int c = bc[b][k], l = (j - ba[b][k] + 5) % 5;
        if (cnt[c][l] == 2) goto undo;
        if (cnt[c][l]++ == 0) zeros[c]--;
        rem[c]--;
    }
    for (int q = 0; q < 4; q++) if (zeros[bc[b][q]] > rem[bc[b][q]]) goto undo;
    return 1;
undo:
    while (k--) { int c = bc[b][k], l = (j - ba[b][k] + 5) % 5; if (--cnt[c][l] == 0) zeros[c]++; rem[c]++; }
    return 0;
}
static void unplace(int b, int j) {
    for (int k = 4; k--;) { int c = bc[b][k], l = (j - ba[b][k] + 5) % 5; if (--cnt[c][l] == 0) zeros[c]++; rem[c]++; }
}
static int dfs(int i) {
    nodes++;
    if (i == 13) return 1;
    int b = items[i];
    if (i < 3) {
        for (int j = 0; j < (i == 0 ? 1 : 5); j++) if (place(b, j)) { off[i] = j; if (dfs(i + 1)) return 1; unplace(b, j); }
    } else {
        int w = (i - 3) / 5;
        for (int j = 0; j < 5; j++) if (!(usedj[w] >> j & 1) && place(b, j)) {
            usedj[w] |= 1 << j; off[i] = j;
            if (dfs(i + 1)) return 1;
            usedj[w] &= ~(1 << j); unplace(b, j);
        }
    }
    return 0;
}
int sub[252], nsub;
static signed char memo[252][252][8];
static int nc[26][8];
static int setup(int s1, int s2, int f) { /* returns 0 if count condition fails */
    int n = 0, tot[8] = {0};
    for (int w = 0; w < 3; w++) items[n++] = 2 * w + (f >> w & 1);
    for (int g = 0; g < 10; g++) if (sub[s1] >> g & 1) items[n++] = 6 + g;
    for (int g = 0; g < 10; g++) if (sub[s2] >> g & 1) items[n++] = 16 + g;
    for (int i = 0; i < 13; i++) for (int c = 0; c < 8; c++) tot[c] += nc[items[i]][c];
    for (int c = 0; c < 8; c++) { if (tot[c] < 5 || tot[c] > 8) return 0; rem[c] = tot[c]; zeros[c] = 5; }
    memset(cnt, 0, sizeof cnt); usedj[0] = usedj[1] = 0;
    return 1;
}
static int solve(int s1, int s2, int f) {
    if (memo[s1][s2][f] >= 0) return memo[s1][s2][f];
    int r = setup(s1, s2, f) ? dfs(0) : 0;
    return memo[s1][s2][f] = r;
}
int main(int argc, char **argv) {
    int cap = argc > 1 ? atoi(argv[1]) : 1;
    for (int m = 0; m < 1024; m++) if (__builtin_popcount(m) == 5) sub[nsub++] = m;
    int comp[252];
    for (int i = 0; i < 252; i++) for (int k = 0; k < 252; k++) if (sub[k] == (1023 ^ sub[i])) comp[i] = k;
    for (int idx = 0;; idx++) {
        for (int b = 0; b < 26; b++) for (int k = 0; k < 4; k++) if (scanf("%d %d", &bc[b][k], &ba[b][k]) != 2) return 0;
        memset(nc, 0, sizeof nc);
        for (int b = 0; b < 26; b++) for (int k = 0; k < 4; k++) nc[b][bc[b][k]]++;
        memset(memo, -1, sizeof memo); nodes = 0;
        long long nsol = 0, ncand = 0;
        for (int f = 0; f < 4 && nsol < cap; f++) /* fixed week 0: block 0 on track 0 (track swap) */
            for (int s1 = 0; s1 < 252 && nsol < cap; s1++)
                for (int s2 = 0; s2 < 252 && nsol < cap; s2++) {
                    int ff = f << 1;
                    if (!setup(s1, s2, ff)) continue;
                    ncand++;
                    if (!solve(s1, s2, ff)) continue;
                    if (!solve(comp[s1], comp[s2], 7 ^ ff)) continue;
                    nsol++;
                    int lane[26];
                    setup(s1, s2, ff); dfs(0);
                    for (int i = 0; i < 13; i++) lane[items[i]] = off[i];
                    setup(comp[s1], comp[s2], 7 ^ ff); dfs(0);
                    for (int i = 0; i < 13; i++) lane[items[i]] = 5 + off[i];
                    printf("%d SOL lanes", idx); for (int i = 0; i < 26; i++) printf(" %d", lane[i]); printf("\n");
                }
        printf("%d sols %lld cands %lld nodes %lld\n", idx, nsol, ncand, nodes); fflush(stdout);
    }
}
