// lambda = 1 design on Z_10 x 4 classes (point p = 10*a + i): one base week developed
// mod 10, NT transversal invariant weeks, one half week (pairing {01|23}, covering the
// antipodal orbits).  Invariant weeks are drawn at random (mixed orbits distinct); the
// base week is then an exact cover of the remaining 60 pair orbits by a partition of
// the 40 points, found by randomised DFS with a node limit and restarts.
// Prints designs as lines "D b c | tr... | base(40)" for zsym's lane stage (LOAD mode).
// Usage: dfs40 seed ndesigns [nodelimit]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define M 10
#define V 40
#define H 5
static unsigned long long s=88172645463325252ULL;
static inline unsigned long long rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
int pairI[4][4]; int NO;
static int orb(int p,int q){int a=p/M,i=p%M,b=q/M,j=q%M;if(a>b){int t=a;a=b;b=t;t=i;i=j;j=t;}
  if(a!=b)return pairI[a][b]*M+((j-i+M)%M);int d=(j-i+M)%M;if(d>M-d)d=M-d;return 6*M+a*H+(d-1);}
static int isshort(int p,int q){return p/M==q/M && ((p-q+M)%M)==H;}
int PSI=0; int SIG[4]={1,2,3,0}, MU=3, TAU=0, PORD=4; static int psi(int p){return M*SIG[p/M]+(MU*(p%M)+TAU)%M;}
int used[128]; int inuse[V]; int blk[V]; int nb; long nodes, NL; int perm[V];
static int place(int*B,int*pts,int*orbs,int*np,int*no){ // add B and its psi-images; check
  int imgs[4][4];int ni=0;int cur[4];memcpy(cur,B,16);
  for(int k=0;k<(PSI?PORD:1);k++){int dup=0;
    for(int j=0;j<ni;j++){int same=1;for(int x=0;x<4&&same;x++){int f=0;for(int y=0;y<4;y++)if(imgs[j][y]==cur[x])f=1;if(!f)same=0;}if(same)dup=1;}
    if(!dup){memcpy(imgs[ni++],cur,16);}
    for(int x=0;x<4;x++)cur[x]=psi(cur[x]);}
  *np=0;*no=0;
  for(int j=0;j<ni;j++){for(int x=0;x<4;x++){int p=imgs[j][x];if(inuse[p])goto bad;
      for(int k=0;k<*np;k++)if(pts[k]==p)goto bad; pts[(*np)++]=p;}
    for(int x=0;x<4;x++)for(int y=x+1;y<4;y++){int a=imgs[j][x],b=imgs[j][y];if(isshort(a,b))goto bad;int o=orb(a,b);if(used[o])goto bad;
      for(int k=0;k<*no;k++)if(orbs[k]==o)goto bad; orbs[(*no)++]=o;}}
  for(int k=0;k<*np;k++)inuse[pts[k]]=1;for(int k=0;k<*no;k++)used[orbs[k]]=1;
  for(int j=0;j<ni;j++){memcpy(&blk[4*nb],imgs[j],16);nb++;}
  return ni;
 bad: return 0;}
static void unplace(int*pts,int np,int*orbs,int no,int ni){for(int k=0;k<np;k++)inuse[pts[k]]=0;for(int k=0;k<no;k++)used[orbs[k]]=0;nb-=ni;}
static int dfs(void){
  if(++nodes>NL)return 0;
  int p=-1;for(int i=0;i<V;i++)if(!inuse[i]){p=i;break;}
  if(p<0)return 1;
  inuse[p]=1;
  for(int qi=0;qi<V;qi++){int q=perm[qi];if(inuse[q]||isshort(p,q))continue;int o1=orb(p,q);if(used[o1])continue;
    for(int ri=qi+1;ri<V;ri++){int r=perm[ri];if(inuse[r]||isshort(p,r)||isshort(q,r))continue;int o2=orb(p,r),o3=orb(q,r);
      if(used[o2]||used[o3]||o2==o3||o1==o2||o1==o3)continue;
      for(int ti=ri+1;ti<V;ti++){int t=perm[ti];if(inuse[t])continue;
        inuse[p]=0;int B[4]={p,q,r,t},pts[16],orbs[24],np,no;int ni=place(B,pts,orbs,&np,&no);
        if(ni){if(dfs())return 1;unplace(pts,np,orbs,no,ni);}
        inuse[p]=1;
        if(nodes>NL)break;}
      if(nodes>NL)break;}
    if(nodes>NL)break;}
  inuse[p]=0;return 0;}
static const int PAIRING[3][4]={{0,1,2,3},{0,2,1,3},{0,3,1,2}};
static int cmp4(const void*a,const void*b){return memcmp(a,b,16);}
static void sort4(int*q){for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)if(q[j]<q[i]){int z=q[i];q[i]=q[j];q[j]=z;}}
static void halfset(int pr,int b,int c,int out[][4]){const int*P=PAIRING[pr];int hv[2]={b,c};int n=0;
  for(int sd=0;sd<2;sd++){int x=P[2*sd],y=P[2*sd+1];for(int t=0;t<H;t++){int q[4]={M*x+t,M*x+t+H,M*y+(hv[sd]+t)%M,M*y+(hv[sd]+t+H)%M};sort4(q);memcpy(out[n++],q,16);}}
  qsort(out,M,16,cmp4);}
static void trset(int*c,int out[][4]){for(int k=0;k<M;k++){int q[4];for(int a=0;a<4;a++)q[a]=M*a+(c[a]+k)%M;sort4(q);memcpy(out[k],q,16);}qsort(out,M,16,cmp4);}
static void imgset(int in[][4],int out[][4]){for(int k=0;k<M;k++){for(int x=0;x<4;x++)out[k][x]=psi(in[k][x]);sort4(out[k]);}qsort(out,M,16,cmp4);}
static void markset(int S[][4],int*u){int t[128]={0};for(int k=0;k<M;k++)for(int x=0;x<4;x++)for(int y=x+1;y<4;y++)t[orb(S[k][x],S[k][y])]=1;for(int o=0;o<128;o++)u[o]+=t[o];}
int main(int argc,char**argv){
  s^=atoll(argv[1])*0x9E3779B97F4A7C15ULL;for(int i=0;i<10;i++)rnd();
  int nd=atoi(argv[2]); NL=argc>3?atol(argv[3]):2000000;
  if(argc>5){PSI=1;for(int a=0;a<4;a++)SIG[a]=argv[4][a]-'0';MU=atoi(argv[5]); if(argc>6)TAU=atoi(argv[6]);
    // order of psi
    PORD=1;for(;;){int ok=1;for(int p=0;p<V&&ok;p++){int q=p;for(int k=0;k<PORD;k++)q=psi(q);if(q!=p)ok=0;}if(ok)break;PORD++;}}
  {int k=0;for(int a=0;a<4;a++)for(int b=a+1;b<4;b++)pairI[a][b]=k++;}NO=6*M+4*H;
  // invariant half weeks
  int hp[64][3],nh=0;
  for(int pr=0;pr<3;pr++)for(int b=0;b<H;b++)for(int c=0;c<H;c++){int A[M][4],B[M][4];halfset(pr,b,c,A);if(PSI){imgset(A,B);if(memcmp(A,B,sizeof A))continue;}
    hp[nh][0]=pr;hp[nh][1]=b;hp[nh][2]=c;nh++;}
  // transversal pairs invariant as a set
  static int tp[200000][2][4];int ntp=0;
  for(int z1=0;z1<1000;z1++)for(int z2=z1+1;z2<1000;z2++){int c1[4]={0,z1%10,z1/10%10,z1/100},c2[4]={0,z2%10,z2/10%10,z2/100};
    if(PSI){int A[M][4],B[M][4],A2[M][4],I1[M][4],I2[M][4];trset(c1,A);trset(c2,A2);imgset(A,I1);imgset(A2,I2);
      int ok=(!memcmp(I1,A,sizeof A)&&!memcmp(I2,A2,sizeof A))||(!memcmp(I1,A2,sizeof A)&&!memcmp(I2,A,sizeof A));(void)B;if(!ok)continue;}
    else if(rnd()%2000)continue;
    if(ntp<200000){memcpy(tp[ntp][0],c1,16);memcpy(tp[ntp][1],c2,16);ntp++;}}
  fprintf(stderr,"psi=%d sig=%d%d%d%d mu=%d ord=%d: %d half weeks, %d transversal pairs\n",PSI,SIG[0],SIG[1],SIG[2],SIG[3],MU,PORD,nh,ntp);
  int found=0;long tries=0,exh=0,lim=0;
  long total=(long)nh*ntp;
  for(long cfg=0;found<nd;cfg++){
    if(PSI && cfg>=total)break;
    long pick=PSI?cfg:(long)(rnd()%total);
    int hi=pick/ntp,ti=pick%ntp;tries++;
    memset(used,0,sizeof used);memset(inuse,0,sizeof inuse);nb=0;nodes=0;
    int U[128];memset(U,0,sizeof U);int A[M][4];halfset(hp[hi][0],hp[hi][1],hp[hi][2],A);markset(A,U);
    trset(tp[ti][0],A);markset(A,U);trset(tp[ti][1],A);markset(A,U);
    int ok=1;for(int o=0;o<NO;o++){if(U[o]>1)ok=0;used[o]=U[o]?1:0;}
    if(!ok)continue;
    for(int i=0;i<V;i++)perm[i]=i;for(int i=V-1;i>0;i--){int j=rnd()%(i+1);int t=perm[i];perm[i]=perm[j];perm[j]=t;}
    int res=dfs(); if(res==0){if(nodes>NL)lim++;else exh++;}
    if(getenv("VERB"))fprintf(stderr,"cfg %ld nodes %ld %s\n",cfg,nodes,res?"FOUND":(nodes>NL?"limit":"exhausted"));
    if(res){found++;
      // relabel classes so the half pairing is {01|23}
      const int*P=PAIRING[hp[hi][0]];int rl[4];rl[P[0]]=0;rl[P[1]]=1;rl[P[2]]=2;rl[P[3]]=3;
      int Bk[V];for(int i=0;i<V;i++)Bk[i]=M*rl[blk[i]/M]+blk[i]%M;
      int Hs[M][4];halfset(hp[hi][0],hp[hi][1],hp[hi][2],Hs);for(int k=0;k<M;k++){for(int x=0;x<4;x++)Hs[k][x]=M*rl[Hs[k][x]/M]+Hs[k][x]%M;sort4(Hs[k]);}qsort(Hs,M,16,cmp4);
      int hb0=-1,hb1=-1;for(int b=0;b<H;b++)for(int c=0;c<H;c++){int Q[M][4];halfset(0,b,c,Q);if(!memcmp(Q,Hs,sizeof Q)){hb0=b;hb1=c;}}
      printf("BASE |");for(int i=0;i<V;i++)printf(" %d",Bk[i]);
      printf("\nTR");for(int f=0;f<2;f++){int c[4];for(int a=0;a<4;a++)c[rl[a]]=tp[ti][f][a];int c0=c[0];for(int a=0;a<4;a++)c[a]=(c[a]-c0+M)%M;printf(" %d,%d,%d,%d",c[0],c[1],c[2],c[3]);}
      printf("\nHALF %d,%d\n",hb0,hb1);fflush(stdout);
      fprintf(stderr,"found %d after %ld cfgs\n",found,tries);}
  }
  fprintf(stderr,"done: %ld cfgs tried, %ld exhausted, %ld hit node limit, %d found\n",tries,exh,lim,found);
  return 0;}
