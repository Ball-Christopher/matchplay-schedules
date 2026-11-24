/* Independent check, word form. A bowler's draw is a word of 6 lane labels (0-4),
   one label twice and the others once (lane balance). Couples meet at most CAP times
   <=> two words agree in at most CAP positions. Each week has 3 bowlers per lane <=>
   each (position, label) cell is used by exactly 3 words. Find 15 such words.
   Symmetry used: weeks and lane labels can be permuted, so one word is 001234.
   Search: exact cover with capacity 3, branching on the cell with fewest candidates. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXW 2000
#define NB 32
typedef struct{uint64_t b[NB];} set;
int nw=0, word[MAXW][6], CAP; set compat[MAXW], incell[6][5];
long long nodes=0, sols=0; int stopfirst, chosen[15];
static int popc(const set*s){int c=0;for(int i=0;i<NB;i++)c+=__builtin_popcountll(s->b[i]);return c;}
static int pc_and(const set*a,const set*b){int c=0;for(int i=0;i<NB;i++)c+=__builtin_popcountll(a->b[i]&b->b[i]);return c;}
void dfs(set cand,int need[6][5],int k){
  nodes++;
  if(k==15){sols++; if(stopfirst){for(int i=0;i<15;i++){for(int j=0;j<6;j++)printf("%d",word[chosen[i]][j]);printf("\n");}exit(0);} return;}
  /* every remaining word uses every label at least once, so each label still needs >= 15-k slots */
  for(int t=0;t<5;t++){int ns=0;for(int c=0;c<6;c++)ns+=need[c][t]; if(ns<15-k) return;}
  /* pick cell with smallest spare = candidates - need */
  int bc=-1,bs=-1,best=1<<30;
  for(int c=0;c<6;c++)for(int s=0;s<5;s++) if(need[c][s]>0){
    int avail=pc_and(&cand,&incell[c][s]); int spare=avail-need[c][s];
    if(spare<0) return;
    if(spare<best){best=spare;bc=c;bs=s;}
  }
  set opts; for(int i=0;i<NB;i++)opts.b[i]=cand.b[i]&incell[bc][bs].b[i];
  for(int i=0;i<NB;i++) while(opts.b[i]){
    int x=i*64+__builtin_ctzll(opts.b[i]); opts.b[i]&=opts.b[i]-1;
    set nc; for(int j=0;j<NB;j++) nc.b[j]=cand.b[j]&compat[x].b[j];
    int ok=1;
    for(int c=0;c<6;c++){ need[c][word[x][c]]--; if(need[c][word[x][c]]==0) for(int j=0;j<NB;j++) nc.b[j]&=~incell[c][word[x][c]].b[j]; }
    chosen[k]=x; dfs(nc,need,k+1);
    for(int c=0;c<6;c++) need[c][word[x][c]]++;
    cand.b[x/64]&=~(1ULL<<(x%64)); /* branch "x not used" */
    (void)ok;
  }
}
int main(int argc,char**argv){
  CAP=atoi(argv[1]); stopfirst=argc>2;
  int w[6];
  for(int code=0;code<15625;code++){int t=code,cnt[5]={0};for(int j=0;j<6;j++){w[j]=t%5;t/=5;cnt[w[j]]++;}
    int ok=1,two=0;for(int s=0;s<5;s++){if(cnt[s]==0||cnt[s]>2)ok=0;if(cnt[s]==2)two++;} if(!ok||two!=1)continue;
    memcpy(word[nw++],w,sizeof w);}
  int seed=-1;
  for(int i=0;i<nw;i++){ if(word[i][0]==0&&word[i][1]==0&&word[i][2]==1&&word[i][3]==2&&word[i][4]==3&&word[i][5]==4) seed=i;
    for(int c=0;c<6;c++) incell[c][word[i][c]].b[i/64]|=1ULL<<(i%64);
    for(int j=0;j<nw;j++){int a=0;for(int c=0;c<6;c++)a+=word[i][c]==word[j][c]; if(i!=j&&a<=CAP) compat[i].b[j/64]|=1ULL<<(j%64);}}
  int need[6][5]; for(int c=0;c<6;c++)for(int s=0;s<5;s++)need[c][s]=3;
  for(int c=0;c<6;c++) need[c][word[seed][c]]--;
  chosen[0]=seed;
  set cand=compat[seed];
  dfs(cand,need,1);
  printf("words %d; cap %d: solutions %lld, nodes %lld\n",nw,CAP,sols,nodes);
}
