/* Exact Z_5-equivariant lane solve for a resolvable (40,4,1) on Z_5 x 8 classes with
   3 fixed weeks (2 base blocks each) + 2 week orbits of 5 (10 base blocks each).
   Lane pairs = 2 tracks of 5, Z_5 rotates each track.  A base block on lane (t,j) puts
   bowler (0,c) on lane (t, j-a) for each of its points (a,c).  Need every cnt[c][lane] in {1,2}.
   stdin: per design 208 ints (26 blocks x 4 points x (class,residue)); fixed blocks first.
   Prints per design: index, #solutions (capped), nodes; first solution's 26 lanes. */
#include <stdio.h>
#include <stdlib.h>
int bc[26][4], ba[26][4];
int cnt[8][10], zeros[8], rem[8];
int lane[26], sol[26];
long long nsol, nodes, cap = 1, nodecap = 2000000000LL;
int used[2]; /* lane masks for orbit weeks */
static int place(int b, int L) {
    int t = L / 5, j = L % 5, k;
    for (k = 0; k < 4; k++) {
        int c = bc[b][k], l = t * 5 + (j - ba[b][k] + 5) % 5;
        if (cnt[c][l] == 2) { while (k--) { c = bc[b][k]; l = t * 5 + (j - ba[b][k] + 5) % 5; if (--cnt[c][l] == 0) zeros[c]++; rem[c]++; } return 0; }
        if (cnt[c][l]++ == 0) zeros[c]--;
        rem[c]--;
    }
    for (k = 0; k < 4; k++) { int c = bc[b][k]; if (zeros[c] > rem[c]) { 
        for (k = 4; k--;) { c = bc[b][k]; int l = t * 5 + (j - ba[b][k] + 5) % 5; if (--cnt[c][l] == 0) zeros[c]++; rem[c]++; } return 0; } }
    return 1;
}
static void unplace(int b, int L) {
    int t = L / 5, j = L % 5, k;
    for (k = 4; k--;) { int c = bc[b][k], l = t * 5 + (j - ba[b][k] + 5) % 5; if (--cnt[c][l] == 0) zeros[c]++; rem[c]++; }
}
static void dfs(int b) {
    if (nsol >= cap || nodes > nodecap) return;
    nodes++;
    if (b == 26) { if (!nsol) for (int i = 0; i < 26; i++) sol[i] = lane[i]; nsol++; return; }
    if (b < 6) {
        int f = b / 2;
        if (b % 2 == 0) {
            for (int L = 0; L < (f == 0 ? 1 : 10); L++) { if (place(b, L)) { lane[b] = L; dfs(b + 1); unplace(b, L); } }
        } else {
            int t = 1 - lane[b - 1] / 5;
            for (int j = 0; j < (f == 0 ? 1 : 5); j++) { int L = t * 5 + j; if (place(b, L)) { lane[b] = L; dfs(b + 1); unplace(b, L); } }
        }
    } else {
        int w = (b - 6) / 10;
        for (int L = 0; L < 10; L++) if (!(used[w] >> L & 1)) {
            if (place(b, L)) { used[w] |= 1 << L; lane[b] = L; dfs(b + 1); used[w] &= ~(1 << L); unplace(b, L); }
        }
    }
}
int main(int argc, char **argv) {
    if (argc > 1) cap = atoll(argv[1]);
    if (argc > 2) nodecap = atoll(argv[2]);
    int idx = 0;
    for (;; idx++) {
        for (int b = 0; b < 26; b++) for (int k = 0; k < 4; k++) if (scanf("%d %d", &bc[b][k], &ba[b][k]) != 2) return 0;
        for (int c = 0; c < 8; c++) { zeros[c] = 10; rem[c] = 13; for (int l = 0; l < 10; l++) cnt[c][l] = 0; }
        nsol = nodes = 0; used[0] = used[1] = 0;
        dfs(0);
        printf("%d sols %lld nodes %lld%s", idx, nsol, nodes, nodes > nodecap ? " (node cap)" : "");
        if (nsol) { printf(" lanes"); for (int i = 0; i < 26; i++) printf(" %d", sol[i]); }
        printf("\n"); fflush(stdout);
    }
}
