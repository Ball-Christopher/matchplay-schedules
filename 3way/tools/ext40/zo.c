// zo.c: oil-pattern versions of 30 and 36 (one round in 3 clash-free blocks, lanes exact).
// Points Z_m x C classes, lanes = T = C/3 tracks of m lane pairs, x -> x+1 rotates every track.
// The design is built in independent PARTS, each with its own pair-orbit budget, so that the
// block conditions follow from the budgets:
//  oil36 (Z_12 x 3, r = 35, blocks 17+9+9):
//    part 0 = B0 developed + 5 invariant weeks, every full orbit exactly once, antipodal (short)
//             orbits never: a Z_12-NKTS(36) leaving the antipodal 1-factor            -> block 0
//    part 1 = A0 developed + 6 invariant weeks, every orbit exactly once incl. the 3 short ones;
//             A_i meets A_(i+6) only in antipodal pairs, so A_0..5 + 3 inv and A_6..11 + 3 inv
//             are clash-free                                                         -> blocks 1, 2
//  oil30 (Z_5 x 6, 2 tracks of 5, r = 29, blocks 14+10+5):
//    Xbar = 3 mixed orbits (0,1,d1) (2,3,d2) (4,5,d3), a 1-factor.
//    part 0 = 2 base weeks + 4 invariant weeks, every orbit once except Xbar never: a Z_5-NKTS(30)
//             leaving Xbar                                                           -> block 0
//    part 1 = 3 base weeks, every orbit once except Xbar twice, with Xbar at most once in the
//             first two weeks (block 1) and once in the third (block 2)              -> blocks 1, 2
// Each part by simulated annealing (base weeks and invariant weeks together); lanes by DFS on the
// (track, lane - x) residues per class over all parts (totals floor/ceil(r/n)).
// usage: zo oil36|oil30 seed
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
static uint64_t rs;
static inline uint32_t rnd(){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)(rs>>11);}
#define MP 40
#define MT 13
int m,C,T,n,N,NP,NO,NPART;
int didx[MP][MP],pidx[12][12];
int Bp[2],Ip[2],bud[2][600];
int wk[2][4][MT][3];
int invC[2][8][4][3],invO[2][8][4][3];
int bw[2][4], bi[2][8];                 // part-1 block of each base week for the penalty (oil30), -1 = none
int xbar[3];
static inline int md(int x){x%=m;return x<0?x+m:x;}
static int oc[600],ocb[3][600],P;
static inline int cdelta(int o,int d){int b=oc[o]-bud[P][o];int a=b+d;oc[o]+=d;return abs(a)-abs(b);}
static inline int bdel(int b,int o,int d){if(b<0)return 0;int x=ocb[b][o];int be=x>1?x-1:0;x+=d;ocb[b][o]=x;int af=x>1?x-1:0;return af-be;}
static inline int cdB(int o,int d,int w){return cdelta(o,d)+bdel(bw[P][w],o,d);}
static inline int cdI(int o,int d,int k){return cdelta(o,d)+bdel(bi[P][k],o,d);}
static inline int unit(int ca,int oa,int cb,int ob){return ca<cb?C*NP+pidx[ca][cb]*m+md(ob-oa):C*NP+pidx[ca][cb]*m+md(oa-ob);}
static void orbit_units(int k,int o,int*u){int*c=invC[P][k][o],*f=invO[P][k][o];u[0]=unit(c[0],f[0],c[1],f[1]);u[1]=unit(c[0],f[0],c[2],f[2]);u[2]=unit(c[1],f[1],c[2],f[2]);}
long SA_ITERS=30000000;
// oil36b part 1: the three M orbits (missing from block 0) are met twice in part 1; legal only as
// two uses in Q0 at offsets differing by m/2 (one per half), or one invariant week in each of Y, Z.
int is30b=0,is36b=0,Mo[3],curM=0;
int mpen(){ if(!is36b||P!=1)return 0; int pen=0;
  for(int a=0;a<3;a++){int o=Mo[a],q=0,off[4],y=0,z=0;
    for(int t=0;t<n;t++){int*g=wk[1][0][t];for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(didx[g[i]][g[j]]==o&&q<4){int lo_=g[i]/m<g[j]/m?g[i]:g[j];off[q++]=lo_%m;}}
    for(int k=0;k<Ip[1];k++){int u[3];orbit_units(k,0,u);for(int j=0;j<3;j++)if(u[j]==o){if(k<4)y++;else z++;}}
    if(q==2&&md(off[0]-off[1])!=m/2)pen++;
    if(q>=1&&y+z>=1)pen+=q<y+z?q:y+z;
    if(y>=2)pen+=y-1; if(z>=2)pen+=z-1; if(q>2)pen+=q-2;}
  return pen;}
int anneal(int p){
  P=p;int B=Bp[p],I=Ip[p];int (*W)[MT][3]=wk[p];
  for(int w=0;w<B;w++){int perm[MP];for(int i=0;i<N;i++)perm[i]=i;for(int i=N-1;i>0;i--){int j=rnd()%(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;}
    for(int t=0;t<n;t++)for(int j=0;j<3;j++)W[w][t][j]=perm[3*t+j];}
  for(int k=0;k<I;k++){int perm[12];for(int i=0;i<C;i++)perm[i]=i;for(int i=C-1;i>0;i--){int j=rnd()%(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;}
    for(int o=0;o<T;o++)for(int e=0;e<3;e++){invC[p][k][o][e]=perm[3*o+e];invO[p][k][o][e]=rnd()%m;}}
  memset(oc,0,sizeof oc);memset(ocb,0,sizeof ocb);
  for(int w=0;w<B;w++)for(int t=0;t<n;t++){int*g=W[w][t];int us[3]={didx[g[0]][g[1]],didx[g[0]][g[2]],didx[g[1]][g[2]]};
    for(int j=0;j<3;j++){oc[us[j]]++;if(bw[p][w]>=0)ocb[bw[p][w]][us[j]]++;}}
  for(int k=0;k<I;k++)for(int o=0;o<T;o++){int u[3];orbit_units(k,o,u);for(int j=0;j<3;j++){oc[u[j]]++;if(bi[p][k]>=0)ocb[bi[p][k]][u[j]]++;}}
  int cost=0;for(int o=0;o<NO;o++)cost+=abs(oc[o]-bud[p][o]);
  for(int b=0;b<3;b++)for(int o=0;o<NO;o++)if(ocb[b][o]>1)cost+=ocb[b][o]-1;
  curM=mpen();cost+=curM;
  double Tm=2.0,pinv=I?(double)I*T*3/(I*T*3+B*N):0;
  for(long it=0;it<SA_ITERS&&cost;it++){
    if((it&1023)==0){Tm*=0.995;if(Tm<0.12)Tm=0.6;}
    if((rnd()&0xffff)<65536.0*pinv){
      int k=rnd()%I,o1=rnd()%T,e1=rnd()%3,o2=-1,e2=-1,nr=3,ua[6],ub[6];
      int oldC1=invC[p][k][o1][e1],oldO1=invO[p][k][o1][e1],oldC2=0,oldO2=0;
      if(T>1&&(rnd()&1)){o2=(o1+1+rnd()%(T-1))%T;e2=rnd()%3;}
      orbit_units(k,o1,ua);if(o2>=0){orbit_units(k,o2,ua+3);nr=6;}
      if(o2>=0){oldC2=invC[p][k][o2][e2];oldO2=invO[p][k][o2][e2];invC[p][k][o1][e1]=oldC2;invO[p][k][o1][e1]=oldO2;invC[p][k][o2][e2]=oldC1;invO[p][k][o2][e2]=oldO1;}
      else invO[p][k][o1][e1]=rnd()%m;
      orbit_units(k,o1,ub);if(o2>=0)orbit_units(k,o2,ub+3);
      int d=0;for(int j=0;j<nr;j++)d+=cdI(ua[j],-1,k);for(int j=0;j<nr;j++)d+=cdI(ub[j],1,k);
      int nm=mpen();d+=nm-curM;
      if(d<=0||(rnd()&0xffff)<65536.0*exp(-d/Tm)){cost+=d;curM=nm;}
      else{for(int j=0;j<nr;j++)cdI(ub[j],-1,k);for(int j=0;j<nr;j++)cdI(ua[j],1,k);
        invC[p][k][o1][e1]=oldC1;invO[p][k][o1][e1]=oldO1;if(o2>=0){invC[p][k][o2][e2]=oldC2;invO[p][k][o2][e2]=oldO2;}}
      continue;}
    int w=rnd()%B,t1=rnd()%n,t2=rnd()%n;if(t1==t2)continue;int i=rnd()%3,j=rnd()%3;
    int*g1=W[w][t1],*g2=W[w][t2];int a=g1[i],b=g2[j];
    int a1=g1[(i+1)%3],a2=g1[(i+2)%3],b1=g2[(j+1)%3],b2=g2[(j+2)%3];
    int d=0;
    d+=cdB(didx[a][a1],-1,w);d+=cdB(didx[a][a2],-1,w);d+=cdB(didx[b][b1],-1,w);d+=cdB(didx[b][b2],-1,w);
    d+=cdB(didx[b][a1],1,w);d+=cdB(didx[b][a2],1,w);d+=cdB(didx[a][b1],1,w);d+=cdB(didx[a][b2],1,w);
    int nm=curM; if(is36b&&p==1){g1[i]=b;g2[j]=a;nm=mpen();g1[i]=a;g2[j]=b;d+=nm-curM;}
    if(d<=0||(rnd()&0xffff)<65536.0*exp(-d/Tm)){g1[i]=b;g2[j]=a;cost+=d;curM=nm;}
    else{cdB(didx[a][b2],-1,w);cdB(didx[a][b1],-1,w);cdB(didx[b][a2],-1,w);cdB(didx[b][a1],-1,w);
      cdB(didx[b][b2],1,w);cdB(didx[b][b1],1,w);cdB(didx[a][a2],1,w);cdB(didx[a][a1],1,w);}
  }
  if(getenv("SADBG"))fprintf(stderr,"part %d sa end cost %d\n",p,cost);
  return cost==0;
}
long canon(int a,int b,int c){long best=1L<<60;
  for(int s=0;s<m;s++){int x[3]={a/m*m+(a%m+s)%m,b/m*m+(b%m+s)%m,c/m*m+(c%m+s)%m};
    for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(x[j]<x[i]){int t=x[i];x[i]=x[j];x[j]=t;}
    long code=((long)x[0]*64+x[1])*64+x[2];if(code<best)best=code;}return best;}
int collect(long*codes){int k=0;
  for(int p=0;p<NPART;p++){for(int w=0;w<Bp[p];w++)for(int t=0;t<n;t++)codes[k++]=canon(wk[p][w][t][0],wk[p][w][t][1],wk[p][w][t][2]);
    for(int i=0;i<Ip[p];i++)for(int o=0;o<T;o++)codes[k++]=canon(invC[p][i][o][0]*m+invO[p][i][o][0],invC[p][i][o][1]*m+invO[p][i][o][1],invC[p][i][o][2]*m+invO[p][i][o][2]);}
  return k;}
// lanes
int cnt[12][MT],rem[12],lane[2][4][MT],il0[2][8][4];long ln,lcap;int lo,hi,RT;
static int feas(){for(int c=0;c<C;c++){int def=0;for(int i=0;i<n;i++){int x=lo-cnt[c][i];if(x>0)def+=x;}if(def>rem[c])return 0;}return 1;}
static inline int cell(int L,int y){return (L/m)*m+md(L%m-y);}
int nitems; int itp[64],itw[64],itt[64]; // item: part, base week (or -1-inv index), triple
int ldfs(int it,uint32_t*mask,int o,uint32_t tracks);
int ldfs(int it,uint32_t*mask,int o,uint32_t tracks){
  if(++ln>lcap)return -1;
  if(it==nitems)return 1;
  int p=itp[it];int st=rnd()%n;
  if(itw[it]>=0){int w=itw[it],t=itt[it];
    for(int kk=0;kk<n;kk++){int l=(st+kk)%n;if(it==0){if(kk)break;l=0;}if(mask[p*4+w]>>l&1)continue;
      int ok=1;for(int j=0;j<3;j++){int q=wk[p][w][t][j];int c=q/m,e=cell(l,q%m);cnt[c][e]++;rem[c]--;if(cnt[c][e]>hi)ok=0;}
      int res=0;if(ok&&feas()){mask[p*4+w]|=1u<<l;res=ldfs(it+1,mask,0,0);mask[p*4+w]&=~(1u<<l);}
      for(int j=0;j<3;j++){int q=wk[p][w][t][j];int c=q/m,e=cell(l,q%m);cnt[c][e]--;rem[c]++;}
      if(res){if(res==1)lane[p][w][t]=l;return res;}}
    return 0;}
  int k=-1-itw[it];
  if(o==T)return ldfs(it+1,mask,0,0);
  for(int kk=0;kk<n;kk++){int L=(st+kk)%n;int tau=L/m,l=L%m;if(tracks>>tau&1)continue;
    int*c=invC[p][k][o],*f=invO[p][k][o];int e[3];int ok=1;
    for(int j=0;j<3;j++){e[j]=tau*m+md(l-f[j]);cnt[c[j]][e[j]]++;rem[c[j]]--;if(cnt[c[j]][e[j]]>hi)ok=0;}
    int res=0;if(ok&&feas())res=ldfs(it,mask,o+1,tracks|1u<<tau);
    for(int j=0;j<3;j++){cnt[c[j]][e[j]]--;rem[c[j]]++;}
    if(res){if(res==1)il0[p][k][o]=L;return res;}}
  return 0;
}
int main(int argc,char**argv){
  if(argc<3){fprintf(stderr,"usage: zo oil36|oil30 seed\n");return 1;}
  int is36=!strncmp(argv[1],"oil36",5); is36b=!strcmp(argv[1],"oil36b"); is30b=!strcmp(argv[1],"oil30b");
  rs=strtoull(argv[2],0,10)*0x9E3779B97F4A7C15ULL+1;
  if(getenv("SAIT"))SA_ITERS=atol(getenv("SAIT"));
  if(is36){m=12;C=3;}else{m=5;C=6;}
  T=C/3;n=T*m;N=C*m;NP=m/2;NPART=2;
  int np=0;for(int a=0;a<C;a++)for(int b=a+1;b<C;b++){pidx[a][b]=pidx[b][a]=np++;}
  NO=C*NP+np*m;
  for(int p=0;p<N;p++)for(int q=0;q<N;q++){if(p==q)continue;int c=p/m,x=p%m,c2=q/m,x2=q%m;
    if(c==c2){int d=md(x2-x);if(d>NP)d=m-d;didx[p][q]=c*NP+d-1;}
    else if(c<c2)didx[p][q]=C*NP+pidx[c][c2]*m+md(x2-x);
    else didx[p][q]=C*NP+pidx[c][c2]*m+md(x-x2);}
  for(int p=0;p<2;p++){for(int w=0;w<4;w++)bw[p][w]=-1;for(int k=0;k<8;k++)bi[p][k]=-1;}
  int r=0;
  for(long tries=1;;tries++){
    if(is36b){ // blocks 16 (P0 + 4 inv) + 10 (Q_0..5 + 4 inv) + 9 (Q_6..11 + 3 inv)
      Bp[0]=1;Ip[0]=4;Bp[1]=1;Ip[1]=7;r=35;
      int dd[3];do{for(int j=0;j<3;j++)dd[j]=rnd()%m;}while(((dd[0]+dd[1]+dd[2])&1)==0); // odd number of odd deltas
      Mo[0]=C*NP+pidx[0][1]*m+dd[0];Mo[1]=C*NP+pidx[0][2]*m+dd[1];Mo[2]=C*NP+pidx[1][2]*m+dd[2];
      for(int o=0;o<NO;o++){int sh=o<C*NP&&2*(o%NP+1)==m;bud[0][o]=sh?0:1;bud[1][o]=1;}
      for(int j=0;j<3;j++){bud[0][Mo[j]]=0;bud[1][Mo[j]]=2;}
    }else if(is36){
      Bp[0]=1;Ip[0]=5;Bp[1]=1;Ip[1]=6;r=35;
      for(int o=0;o<NO;o++){int sh=o<C*NP&&2*(o%NP+1)==m;bud[0][o]=sh?0:1;bud[1][o]=1;}
    }else if(is30b){ // blocks 14 (2 base + 4 inv) + 9 (1 base + 4 inv) + 6 (1 base + 1 inv)
      Bp[0]=2;Ip[0]=4;Bp[1]=2;Ip[1]=5;r=29;bw[1][0]=0;bw[1][1]=1;for(int k=0;k<5;k++)bi[1][k]=k<4?0:1;
      for(int j=0;j<3;j++)xbar[j]=C*NP+pidx[2*j][2*j+1]*m+rnd()%m;
      for(int o=0;o<NO;o++){bud[0][o]=1;bud[1][o]=1;}
      for(int j=0;j<3;j++){bud[0][xbar[j]]=0;bud[1][xbar[j]]=2;}
    }else{
      Bp[0]=2;Ip[0]=4;Bp[1]=3;Ip[1]=0;r=29;bw[1][0]=0;bw[1][1]=0;bw[1][2]=1;
      for(int j=0;j<3;j++)xbar[j]=C*NP+pidx[2*j][2*j+1]*m+rnd()%m;
      for(int o=0;o<NO;o++){bud[0][o]=1;bud[1][o]=1;}
      for(int j=0;j<3;j++){bud[0][xbar[j]]=0;bud[1][xbar[j]]=2;}
    }
    int ok=1;
    for(int p=0;p<2&&ok;p++){int got=0;for(int a=0;a<(getenv("PTRIES")?atoi(getenv("PTRIES")):8)&&!got;a++)got=anneal(p);ok=got;}
    if(!ok){fprintf(stderr,"try %ld: a part failed\n",tries);continue;}
    long codes[200];int K=collect(codes),rep=0;for(int i=0;i<K;i++)for(int j=i+1;j<K;j++)if(codes[i]==codes[j])rep++;
    if(rep>(getenv("MAXREP")?atoi(getenv("MAXREP")):0)){fprintf(stderr,"try %ld: %d repeated trio orbits\n",tries,rep);continue;}
    if(rep)fprintf(stderr,"accepting %d repeated trio orbits\n",rep);
    nitems=0;
    for(int p=0;p<2;p++){for(int w=0;w<Bp[p];w++)for(int t=0;t<n;t++){itp[nitems]=p;itw[nitems]=w;itt[nitems]=t;nitems++;}
      for(int k=0;k<Ip[p];k++){itp[nitems]=p;itw[nitems]=-1-k;itt[nitems]=0;nitems++;}}
    lo=r/n;hi=(r+n-1)/n;int lr=0;
    for(int rep2=0;rep2<10&&lr!=1;rep2++){memset(cnt,0,sizeof cnt);for(int c=0;c<C;c++)rem[c]=r;uint32_t mask[8]={0};ln=0;lcap=3000000;lr=ldfs(0,mask,0,0);}
    fprintf(stderr,"try %ld lane result %d\n",tries,lr);
    if(lr!=1)continue;
    printf("SOLUTION\n");
    // weeks with block labels: "B<block> " prefix
    for(int p=0;p<2;p++){
      for(int w=0;w<Bp[p];w++)for(int i=0;i<m;i++){int out[MP];for(int t=0;t<n;t++){int L=lane[p][w][t];int l=(L/m)*m+(L%m+i)%m;
          for(int j=0;j<3;j++){int q=wk[p][w][t][j];out[l*3+j]=q/m*m+(q%m+i)%m+1;}}
        int blk;if(is36)blk=p==0?0:(i<m/2?1:2);else if(is30b)blk=p==0?0:(w<1?1:2);else blk=p==0?0:(w<2?1:2);
        printf("W%d ",blk);for(int k=0;k<N;k++)printf("%d ",out[k]);printf("\n");}
      for(int k=0;k<Ip[p];k++){int out[MP];for(int o=0;o<T;o++)for(int j=0;j<m;j++){int L=il0[p][k][o];int l=(L/m)*m+(L%m+j)%m;int*c=invC[p][k][o],*f=invO[p][k][o];
            for(int e=0;e<3;e++)out[l*3+e]=c[e]*m+md(f[e]+j)+1;}
        int blk;if(is36b)blk=p==0?0:(k<4?1:2);else if(is36)blk=p==0?0:(k<3?1:2);else if(is30b)blk=p==0?0:(k<4?1:2);else blk=0;
        printf("W%d ",blk);for(int q=0;q<N;q++)printf("%d ",out[q]);printf("\n");}
    }
    for(int p=0;p<2;p++){
      for(int w=0;w<Bp[p];w++){printf("BASE %d %d:",p,w);for(int t=0;t<n;t++){int*g=wk[p][w][t];printf(" {%d.%d,%d.%d,%d.%d}@%d",g[0]/m,g[0]%m,g[1]/m,g[1]%m,g[2]/m,g[2]%m,lane[p][w][t]);}printf("\n");}
      if(Ip[p]){printf("INV %d:",p);for(int i=0;i<Ip[p];i++){printf(" [");for(int o=0;o<T;o++){int*c=invC[p][i][o],*f=invO[p][i][o];printf("{%d.%d,%d.%d,%d.%d}@%d ",c[0],f[0],c[1],f[1],c[2],f[2],il0[p][i][o]);}printf("]");}printf("\n");}
    }
    return 0;
  }
}
