// zn.c: resolvable 2-(3n,3,lam) designs on Z_n x {0,1,2} whose automorphism x -> x+1
// also rotates the n lane pairs (METHODS 3.3), generalising fable_search/z8.c and z9.c.
// Each round = B base weeks developed mod n (group on lane l moves to l+1) + I Z_n-invariant
// weeks (orbit of a transversal trio {(0,j),(1,u+j),(2,w+j)} on lane l0+j).
// With R=2 two designs are found together: no trio orbit shared, each round lane-exact alone
// (floor/ceil(r/n)) and the two together floor/ceil(2r/n).
// Lane counts depend only on (lane - x) per class: DFS over base lane labels and offsets.
// usage: zn n B I lam R seed      prints SOLUTION + weeks (bowler = n*class + x + 1) + BASE lines
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
static uint64_t rs;
static inline uint32_t rnd(){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)(rs>>11);}
#define MX 13
int n,B,I,lam,R,N,NP,NO;
int didx[3*MX][3*MX], bud[200];
int wk[2][2][MX][3]; int inv[2][MX][2]; int CR; long nodes,cap;
static inline int md(int x){x%=n;return x<0?x+n:x;}
static int take(int a,int b,int c){int i=didx[a][b],j=didx[a][c],k=didx[b][c];bud[i]--;bud[j]--;bud[k]--;
  if(bud[i]<0||bud[j]<0||bud[k]<0){bud[i]++;bud[j]++;bud[k]++;return 0;}return 1;}
static void give(int a,int b,int c){bud[didx[a][b]]++;bud[didx[a][c]]++;bud[didx[b][c]]++;}
int dfs(int w,int t,uint64_t used){
  if(++nodes>cap)return -1;
  if(t==n){ if(w+1<B) return dfs(w+1,0,0); return 1; }
  int p=0;while(used>>p&1)p++;
  static int cq[64][800],cr[64][800]; int d=w*MX+t; int m=0;
  for(int q=p+1;q<N;q++)if(!(used>>q&1))for(int r=q+1;r<N;r++)if(!(used>>r&1)){cq[d][m]=q;cr[d][m]=r;m++;}
  for(int i=m-1;i>0;i--){int j=rnd()%(i+1);int x=cq[d][i];cq[d][i]=cq[d][j];cq[d][j]=x;x=cr[d][i];cr[d][i]=cr[d][j];cr[d][j]=x;}
  for(int i=0;i<m;i++){int q=cq[d][i],r=cr[d][i];if(!take(p,q,r))continue;
    wk[CR][w][t][0]=p;wk[CR][w][t][1]=q;wk[CR][w][t][2]=r;
    int res=dfs(w,t+1,used|1ull<<p|1ull<<q|1ull<<r);give(p,q,r);if(res)return res;}
  return 0;
}
int canon(int a,int b,int c){int best=1<<30;
  for(int s=0;s<n;s++){int x[3]={a/n*n+(a%n+s)%n,b/n*n+(b%n+s)%n,c/n*n+(c%n+s)%n};
    for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(x[j]<x[i]){int t=x[i];x[i]=x[j];x[j]=t;}
    int code=(x[0]*64+x[1])*64+x[2];if(code<best)best=code;}return best;}
// simulated annealing for the base weeks: state = B partitions of the 3n points into triples,
// cost = sum over pair-orbits |count - budget|; move = swap two points between two triples of one week.
int USE_DFS=0; long SA_ITERS=20000000;
static int oc[200];
static inline int cdelta(int o,int d){int b=oc[o]-bud[o];int a=b+d;oc[o]+=d;return abs(a)-abs(b);}
int anneal(int r){
  int (*W)[MX][3]=wk[r];
  for(int w=0;w<B;w++){int perm[3*MX];for(int i=0;i<N;i++)perm[i]=i;for(int i=N-1;i>0;i--){int j=rnd()%(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;}
    for(int t=0;t<n;t++)for(int j=0;j<3;j++)W[w][t][j]=perm[3*t+j];}
  memset(oc,0,sizeof oc);
  for(int w=0;w<B;w++)for(int t=0;t<n;t++){int*g=W[w][t];oc[didx[g[0]][g[1]]]++;oc[didx[g[0]][g[2]]]++;oc[didx[g[1]][g[2]]]++;}
  int cost=0;for(int o=0;o<NO;o++)cost+=abs(oc[o]-bud[o]);
  double T=2.0;
  for(long it=0;it<SA_ITERS;it++){
    if(cost==0)return 1;
    if((it&1023)==0){T*=0.995;if(T<0.12)T=0.6;}
    int w=rnd()%B,t1=rnd()%n,t2=rnd()%n;if(t1==t2)continue;int i=rnd()%3,j=rnd()%3;
    int*g1=W[w][t1],*g2=W[w][t2];int a=g1[i],b=g2[j];
    int a1=g1[(i+1)%3],a2=g1[(i+2)%3],b1=g2[(j+1)%3],b2=g2[(j+2)%3];
    int d=0;
    d+=cdelta(didx[a][a1],-1);d+=cdelta(didx[a][a2],-1);d+=cdelta(didx[b][b1],-1);d+=cdelta(didx[b][b2],-1);
    d+=cdelta(didx[b][a1],1);d+=cdelta(didx[b][a2],1);d+=cdelta(didx[a][b1],1);d+=cdelta(didx[a][b2],1);
    if(d<=0||(rnd()&0xffff)<65536.0*exp(-d/T)){g1[i]=b;g2[j]=a;cost+=d;}
    else{cdelta(didx[a][b2],-1);cdelta(didx[a][b1],-1);cdelta(didx[b][a2],-1);cdelta(didx[b][a1],-1);
      cdelta(didx[b][b2],1);cdelta(didx[b][b1],1);cdelta(didx[a][a2],1);cdelta(didx[a][a1],1);}
  }
  if(getenv("SADBG"))fprintf(stderr,"sa end cost %d\n",cost);
  return cost==0;
}
int design(int r){ CR=r;
  for(long tries=0;;tries++){
    for(int c=0;c<3;c++)for(int d=1;d<=NP;d++)bud[c*NP+d-1]=(2*d==n)?lam/2:lam;
    for(int i=3*NP;i<NO;i++)bud[i]=lam;
    int k=0,guard=0;
    while(k<I&&guard<5000){guard++;int u=rnd()%n,v=rnd()%n;int dup=0;for(int i=0;i<k;i++)if(inv[r][i][0]==u&&inv[r][i][1]==v)dup=1;if(dup)continue;
      int a=3*NP+u,b=3*NP+n+v,c=3*NP+2*n+md(v-u);if(bud[a]<1||bud[b]<1||bud[c]<1)continue;bud[a]--;bud[b]--;bud[c]--;inv[r][k][0]=u;inv[r][k][1]=v;k++;}
    if(k<I)continue;
    int dr;
    if(USE_DFS){nodes=0;cap=lam==1?3000000:500000; dr=dfs(0,0,0);} else dr=anneal(r);
    if(tries%20==0)fprintf(stderr,"tries %ld dr %d\n",tries,dr); if(dr!=1)continue;
    // distinct trio orbits within the round
    int codes[64],m=0,ok=1;
    for(int w=0;w<B;w++)for(int t=0;t<n;t++)codes[m++]=canon(wk[r][w][t][0],wk[r][w][t][1],wk[r][w][t][2]);
    for(int i=0;i<I;i++)codes[m++]=canon(0,n+inv[r][i][0],2*n+inv[r][i][1]);
    for(int i=0;i<m;i++)for(int j=i+1;j<m;j++)if(codes[i]==codes[j])ok=0;
    if(ok){fprintf(stderr,"round %d design after %ld tries\n",r,tries+1);return 1;}
  }
}
// lanes
int cnt[2][3][MX],rem[2][3],lane[2][2][MX],l0[2][MX];long ln,lcap; int lo1,hi1,lo2,hi2,ITEMS;
static int feas(int r){
  for(int c=0;c<3;c++){int def=0;for(int i=0;i<n;i++){int x=lo1-cnt[r][c][i];if(x>0)def+=x;}if(def>rem[r][c])return 0;
    if(R==2){int d2=0;for(int i=0;i<n;i++){int x=lo2-cnt[0][c][i]-cnt[1][c][i];if(x>0)d2+=x;}if(d2>rem[0][c]+rem[1][c])return 0;}}
  return 1;}
static int over(int r,int c,int q){return cnt[r][c][q]>hi1||(R==2&&cnt[0][c][q]+cnt[1][c][q]>hi2);}
int ldfs(int it,uint32_t*mask){
  if(++ln>lcap)return -1;
  if(it==R*ITEMS)return 1;
  int r=it/ITEMS,k=it%ITEMS;int st=rnd()%n;
  if(k<B*n){int w=k/n,t=k%n;
    for(int kk=0;kk<n;kk++){int l=(st+kk)%n; if(it==0){if(kk)break;l=0;} if(mask[r*2+w]>>l&1)continue;
      int ok=1;
      for(int j=0;j<3;j++){int p=wk[r][w][t][j];int c=p/n,q=md(l-p%n);cnt[r][c][q]++;rem[r][c]--;if(over(r,c,q))ok=0;}
      int res=0;
      if(ok&&feas(r)){mask[r*2+w]|=1u<<l;res=ldfs(it+1,mask);mask[r*2+w]&=~(1u<<l);}
      for(int j=0;j<3;j++){int p=wk[r][w][t][j];int c=p/n,q=md(l-p%n);cnt[r][c][q]--;rem[r][c]++;}
      if(res){if(res==1)lane[r][w][t]=l;return res;}
    }
    return 0;}
  int i=k-B*n,u=inv[r][i][0],v=inv[r][i][1];
  for(int kk=0;kk<n;kk++){int l=(st+kk)%n;int q[3]={l,md(l-u),md(l-v)};int ok=1;
    for(int c=0;c<3;c++){cnt[r][c][q[c]]++;rem[r][c]--;if(over(r,c,q[c]))ok=0;}
    int res=0;if(ok&&feas(r))res=ldfs(it+1,mask);
    for(int c=0;c<3;c++){cnt[r][c][q[c]]--;rem[r][c]++;}
    if(res){if(res==1)l0[r][i]=l;return res;}
  }
  return 0;
}
int main(int argc,char**argv){
  if(argc<7){fprintf(stderr,"usage: zn n B I lam R seed\n");return 1;}
  n=atoi(argv[1]);B=atoi(argv[2]);I=atoi(argv[3]);lam=atoi(argv[4]);R=atoi(argv[5]);
  rs=strtoull(argv[6],0,10)*0x9E3779B97F4A7C15ULL+1;
  N=3*n;NP=n/2;NO=3*NP+3*n;ITEMS=B*n+I;
  int r1=B*n+I; lo1=r1/n;hi1=(r1+n-1)/n;lo2=2*r1/n;hi2=(2*r1+n-1)/n;
  for(int p=0;p<N;p++)for(int q=0;q<N;q++){if(p==q)continue;int c=p/n,x=p%n,c2=q/n,x2=q%n;
    if(c==c2){int d=md(x2-x);if(d>NP)d=n-d;didx[p][q]=c*NP+d-1;}
    else if(c<c2){int pi=c==0?(c2==1?0:1):2;didx[p][q]=3*NP+pi*n+md(x2-x);}
    else{int pi=c2==0?(c==1?0:1):2;didx[p][q]=3*NP+pi*n+md(x-x2);}}
  for(long tries=1;;tries++){
    if(R==1||tries==1||rnd()%4==0) design(0);
    if(R==2){design(1);
      int codes[128],m=0,ok=1;
      for(int r=0;r<2;r++){for(int w=0;w<B;w++)for(int t=0;t<n;t++)codes[m++]=canon(wk[r][w][t][0],wk[r][w][t][1],wk[r][w][t][2]);
        for(int i=0;i<I;i++)codes[m++]=canon(0,n+inv[r][i][0],2*n+inv[r][i][1]);}
      int rep=0;for(int i=0;i<m/2;i++)for(int j=m/2;j<m;j++)if(codes[i]==codes[j])rep++;
      if(rep){fprintf(stderr,"pair shares %d orbits\n",rep);continue;}
    }
    int lr=0;
    for(int rep=0;rep<10&&lr!=1;rep++){memset(cnt,0,sizeof cnt);for(int r=0;r<2;r++)for(int c=0;c<3;c++)rem[r][c]=r<R?r1:0;
      uint32_t mask[4]={0,0,0,0};ln=0;lcap=3000000;lr=ldfs(0,mask);}
    fprintf(stderr,"try %ld lane result %d\n",tries,lr);
    if(lr!=1)continue;
    printf("SOLUTION\n");
    for(int r=0;r<R;r++){
      for(int w=0;w<B;w++)for(int i=0;i<n;i++){int out[3*MX];for(int t=0;t<n;t++){int l=(lane[r][w][t]+i)%n;for(int j=0;j<3;j++){int p=wk[r][w][t][j];out[l*3+j]=p/n*n+(p%n+i)%n+1;}}for(int k=0;k<N;k++)printf("%d ",out[k]);printf("\n");}
      for(int k=0;k<I;k++){int out[3*MX];for(int j=0;j<n;j++){int l=(l0[r][k]+j)%n;out[l*3]=j+1;out[l*3+1]=n+(inv[r][k][0]+j)%n+1;out[l*3+2]=2*n+(inv[r][k][1]+j)%n+1;}for(int q=0;q<N;q++)printf("%d ",out[q]);printf("\n");}
    }
    for(int r=0;r<R;r++){
      for(int w=0;w<B;w++){printf("BASE %d %d:",r,w);for(int t=0;t<n;t++)printf(" {%c%d,%c%d,%c%d}@%d","abc"[wk[r][w][t][0]/n],wk[r][w][t][0]%n,"abc"[wk[r][w][t][1]/n],wk[r][w][t][1]%n,"abc"[wk[r][w][t][2]/n],wk[r][w][t][2]%n,lane[r][w][t]);printf("\n");}
      printf("INV %d:",r);for(int i=0;i<I;i++)printf(" (%d,%d)@%d",inv[r][i][0],inv[r][i][1],l0[r][i]);printf("\n");
    }
    return 0;
  }
}
