// zm.c: resolvable 2-(Cm,3,lam) designs on Z_m x C classes (C = 3T) with lane pairs
// arranged as T tracks of m; x -> x+1 rotates every track (lane (tau,l) -> (tau,l+1)).
// Needed for 30 = Z_5 x 6 (2 tracks of 5 lanes): Z_10 x 3 is impossible for lam = 2 by parity
// (in a triple the number of odd-difference pairs is even; invariant weeks are transversal, hence
// even too; but each class needs an odd number (2+2+1) of odd pure differences).
// Each round = B base weeks developed mod m + I invariant weeks (T transversal orbits on a
// partition of the classes into triples, orbit k on track tau_k with lane offset l0).
// Base weeks by simulated annealing on pair-orbit counts; lanes by DFS on (track, lane - x) per class.
// usage: zm m C B I lam R seed
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
static uint64_t rs;
static inline uint32_t rnd(){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)(rs>>11);}
#define MP 40
#define MT 13
int m,C,T,n,B,I,lam,R,N,NP,NO;
int didx[MP][MP],bud[600],pidx[12][12];
int wk[2][6][MT][3];           // [round][base week][triple][3]
int ic[2][MT][4][3], io[2][MT][4][2]; // invariant week: orbit k: classes ic, offsets (u,w)
static inline int md(int x){x%=m;return x<0?x+m:x;}
static int oc[600];
static inline int cdelta(int o,int d){int b=oc[o]-bud[o];int a=b+d;oc[o]+=d;return abs(a)-abs(b);}
long SA_ITERS=20000000; int JOINT=1;
int anneal(int r){
  int (*W)[MT][3]=wk[r];
  for(int w=0;w<B;w++){int perm[MP];for(int i=0;i<N;i++)perm[i]=i;for(int i=N-1;i>0;i--){int j=rnd()%(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;}
    for(int t=0;t<n;t++)for(int j=0;j<3;j++)W[w][t][j]=perm[3*t+j];}
  memset(oc,0,sizeof oc);
  for(int w=0;w<B;w++)for(int t=0;t<n;t++){int*g=W[w][t];oc[didx[g[0]][g[1]]]++;oc[didx[g[0]][g[2]]]++;oc[didx[g[1]][g[2]]]++;}
  int cost=0;for(int o=0;o<NO;o++)cost+=abs(oc[o]-bud[o]);
  double Tm=2.0;
  for(long it=0;it<SA_ITERS;it++){
    if(cost==0)return 1;
    if((it&1023)==0){Tm*=0.995;if(Tm<0.12)Tm=0.6;}
    int w=rnd()%B,t1=rnd()%n,t2=rnd()%n;if(t1==t2)continue;int i=rnd()%3,j=rnd()%3;
    int*g1=W[w][t1],*g2=W[w][t2];int a=g1[i],b=g2[j];
    int a1=g1[(i+1)%3],a2=g1[(i+2)%3],b1=g2[(j+1)%3],b2=g2[(j+2)%3];
    int d=0;
    d+=cdelta(didx[a][a1],-1);d+=cdelta(didx[a][a2],-1);d+=cdelta(didx[b][b1],-1);d+=cdelta(didx[b][b2],-1);
    d+=cdelta(didx[b][a1],1);d+=cdelta(didx[b][a2],1);d+=cdelta(didx[a][b1],1);d+=cdelta(didx[a][b2],1);
    if(d<=0||(rnd()&0xffff)<65536.0*exp(-d/Tm)){g1[i]=b;g2[j]=a;cost+=d;}
    else{cdelta(didx[a][b2],-1);cdelta(didx[a][b1],-1);cdelta(didx[b][a2],-1);cdelta(didx[b][a1],-1);
      cdelta(didx[b][b2],1);cdelta(didx[b][b1],1);cdelta(didx[a][a2],1);cdelta(didx[a][a1],1);}
  }
  if(getenv("SADBG"))fprintf(stderr,"sa end cost %d\n",cost);
  return 0;
}

// joint annealing: base weeks AND invariant weeks (entries (class, offset), T orbits per week)
int invC[MT*2][4][3], invO[MT*2][4][3];
static inline int unit(int ca,int oa,int cb,int ob){return ca<cb?C*NP+pidx[ca][cb]*m+md(ob-oa):C*NP+pidx[ca][cb]*m+md(oa-ob);}
static int orbit_units(int k,int o,int*u){int*c=invC[k][o],*f=invO[k][o];u[0]=unit(c[0],f[0],c[1],f[1]);u[1]=unit(c[0],f[0],c[2],f[2]);u[2]=unit(c[1],f[1],c[2],f[2]);return 3;}

// oil blocks (env BLK): spec per base week then per invariant week, comma separated:
// "b" = whole development in block b, "b/c" = developed weeks 0..m/2-1 in block b, m/2..m-1 in block c.
// Penalty: for every block and pair-orbit, max(0, pairs-meetings-per-pair - 1). A short orbit (2d = m)
// used once in a whole development meets each of its pairs twice, so it weighs 2 there.
int NBLK=0, bw[12][2], bi[MT*2]; int ocb[4][600];
static inline int isshort(int o){return o<C*NP&&2*(o%NP+1)==m;}
static inline int bdel(int b,int o,int d){int x=ocb[b][o];int before=x>1?x-1:0;x+=d;ocb[b][o]=x;int after=x>1?x-1:0;return after-before;}
static inline int cdB(int o,int d,int w){int r=cdelta(o,d);if(NBLK){
  if(bw[w][1]<0)r+=bdel(bw[w][0],o,isshort(o)?2*d:d); else {r+=bdel(bw[w][0],o,d);r+=bdel(bw[w][1],o,d);}}return r;}
static inline int cdI(int o,int d,int k){int r=cdelta(o,d);if(NBLK)r+=bdel(bi[k],o,d);return r;}
int anneal2(int r){
  int (*W)[MT][3]=wk[r];
  for(int c=0;c<C;c++)for(int d=1;d<=NP;d++)bud[c*NP+d-1]=(2*d==m)?lam/2:lam;
  for(int i=C*NP;i<NO;i++)bud[i]=lam;
  for(int w=0;w<B;w++){int perm[MP];for(int i=0;i<N;i++)perm[i]=i;for(int i=N-1;i>0;i--){int j=rnd()%(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;}
    for(int t=0;t<n;t++)for(int j=0;j<3;j++)W[w][t][j]=perm[3*t+j];}
  for(int k=0;k<I;k++){int perm[12];for(int i=0;i<C;i++)perm[i]=i;for(int i=C-1;i>0;i--){int j=rnd()%(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;}
    for(int o=0;o<T;o++)for(int e=0;e<3;e++){invC[k][o][e]=perm[3*o+e];invO[k][o][e]=rnd()%m;}}
  memset(oc,0,sizeof oc);
  for(int w=0;w<B;w++)for(int t=0;t<n;t++){int*g=W[w][t];oc[didx[g[0]][g[1]]]++;oc[didx[g[0]][g[2]]]++;oc[didx[g[1]][g[2]]]++;}
  for(int k=0;k<I;k++)for(int o=0;o<T;o++){int u[3];orbit_units(k,o,u);for(int j=0;j<3;j++)oc[u[j]]++;}
  int cost=0;for(int o=0;o<NO;o++)cost+=abs(oc[o]-bud[o]);
  if(NBLK){memset(ocb,0,sizeof ocb);
    for(int w=0;w<B;w++)for(int t=0;t<n;t++){int*g=W[w][t];int us[3]={didx[g[0]][g[1]],didx[g[0]][g[2]],didx[g[1]][g[2]]};
      for(int j=0;j<3;j++){if(bw[w][1]<0)ocb[bw[w][0]][us[j]]+=isshort(us[j])?2:1;else{ocb[bw[w][0]][us[j]]++;ocb[bw[w][1]][us[j]]++;}}}
    for(int k=0;k<I;k++)for(int o=0;o<T;o++){int u[3];orbit_units(k,o,u);for(int j=0;j<3;j++)ocb[bi[k]][u[j]]++;}
    for(int b=0;b<NBLK;b++)for(int o=0;o<NO;o++)if(ocb[b][o]>1)cost+=ocb[b][o]-1;}
  double Tm=2.0; double pinv=I?(double)I*T*3/(I*T*3+B*N):0;
  for(long it=0;it<SA_ITERS;it++){
    if(cost==0)break;
    if((it&1023)==0){Tm*=0.995;if(Tm<0.12)Tm=0.6;}
    if((rnd()&0xffff)<65536.0*pinv){
      int k=rnd()%I; int rmv[6],add[6],nr=0;
      int o1=rnd()%T,e1=rnd()%3; int save[2][2][3][2];
      for(int o=0;o<T;o++)for(int e=0;e<3;e++){save[0][0][0][0]=0;}
      int oc1[3],oc2[3];int o2=-1,e2=-1;int oldC1=invC[k][o1][e1],oldO1=invO[k][o1][e1],oldC2=0,oldO2=0;
      int ua[6],ub[6];
      if(T>1&&(rnd()&1)){o2=(o1+1+rnd()%(T-1))%T;e2=rnd()%3;}
      orbit_units(k,o1,ua);nr=3;if(o2>=0)orbit_units(k,o2,ua+3),nr=6;
      if(o2>=0){oldC2=invC[k][o2][e2];oldO2=invO[k][o2][e2];invC[k][o1][e1]=oldC2;invO[k][o1][e1]=oldO2;invC[k][o2][e2]=oldC1;invO[k][o2][e2]=oldO1;}
      else invO[k][o1][e1]=rnd()%m;
      orbit_units(k,o1,ub);if(o2>=0)orbit_units(k,o2,ub+3);
      int d=0;for(int j=0;j<nr;j++)d+=cdI(ua[j],-1,k);for(int j=0;j<nr;j++)d+=cdI(ub[j],1,k);
      if(d<=0||(rnd()&0xffff)<65536.0*exp(-d/Tm)){cost+=d;}
      else{for(int j=0;j<nr;j++)cdI(ub[j],-1,k);for(int j=0;j<nr;j++)cdI(ua[j],1,k);
        invC[k][o1][e1]=oldC1;invO[k][o1][e1]=oldO1;if(o2>=0){invC[k][o2][e2]=oldC2;invO[k][o2][e2]=oldO2;}}
      (void)rmv;(void)add;(void)oc1;(void)oc2;
      continue;}
    int w=rnd()%B,t1=rnd()%n,t2=rnd()%n;if(t1==t2)continue;int i=rnd()%3,j=rnd()%3;
    int*g1=W[w][t1],*g2=W[w][t2];int a=g1[i],b=g2[j];
    int a1=g1[(i+1)%3],a2=g1[(i+2)%3],b1=g2[(j+1)%3],b2=g2[(j+2)%3];
    int d=0;
    d+=cdB(didx[a][a1],-1,w);d+=cdB(didx[a][a2],-1,w);d+=cdB(didx[b][b1],-1,w);d+=cdB(didx[b][b2],-1,w);
    d+=cdB(didx[b][a1],1,w);d+=cdB(didx[b][a2],1,w);d+=cdB(didx[a][b1],1,w);d+=cdB(didx[a][b2],1,w);
    if(d<=0||(rnd()&0xffff)<65536.0*exp(-d/Tm)){g1[i]=b;g2[j]=a;cost+=d;}
    else{cdB(didx[a][b2],-1,w);cdB(didx[a][b1],-1,w);cdB(didx[b][a2],-1,w);cdB(didx[b][a1],-1,w);
      cdB(didx[b][b2],1,w);cdB(didx[b][b1],1,w);cdB(didx[a][a2],1,w);cdB(didx[a][a1],1,w);}
  }
  if(getenv("SADBG"))fprintf(stderr,"sa2 end cost %d\n",cost);
  if(cost)return 0;
  // convert invariants to (sorted classes, u, w)
  for(int k=0;k<I;k++)for(int o=0;o<T;o++){int idx[3]={0,1,2};
    for(int a=0;a<3;a++)for(int b=a+1;b<3;b++)if(invC[k][o][idx[b]]<invC[k][o][idx[a]]){int t=idx[a];idx[a]=idx[b];idx[b]=t;}
    for(int e=0;e<3;e++)ic[r][k][o][e]=invC[k][o][idx[e]];
    io[r][k][o][0]=md(invO[k][o][idx[1]]-invO[k][o][idx[0]]);io[r][k][o][1]=md(invO[k][o][idx[2]]-invO[k][o][idx[0]]);}
  return 1;
}
long canon(int a,int b,int c){long best=1L<<60;
  for(int s=0;s<m;s++){int x[3]={a/m*m+(a%m+s)%m,b/m*m+(b%m+s)%m,c/m*m+(c%m+s)%m};
    for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(x[j]<x[i]){int t=x[i];x[i]=x[j];x[j]=t;}
    long code=((long)x[0]*64+x[1])*64+x[2];if(code<best)best=code;}return best;}
int collect(int r,long*codes){int k=0;
  for(int w=0;w<B;w++)for(int t=0;t<n;t++)codes[k++]=canon(wk[r][w][t][0],wk[r][w][t][1],wk[r][w][t][2]);
  for(int i=0;i<I;i++)for(int o=0;o<T;o++)codes[k++]=canon(ic[r][i][o][0]*m,ic[r][i][o][1]*m+io[r][i][o][0],ic[r][i][o][2]*m+io[r][i][o][1]);
  return k;}
void design(int r){
  for(long tries=0;;tries++){
    for(int c=0;c<C;c++)for(int d=1;d<=NP;d++)bud[c*NP+d-1]=(2*d==m)?lam/2:lam;
    for(int i=C*NP;i<NO;i++)bud[i]=lam;
    int k=0,guard=0;
    if(JOINT){int dr=anneal2(r);if(tries%20==0)fprintf(stderr,"round %d tries %ld\n",r,tries);if(!dr)continue;goto check;}
    while(k<I&&guard<5000){guard++;
      int perm[12];for(int i=0;i<C;i++)perm[i]=i;for(int i=C-1;i>0;i--){int j=rnd()%(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;}
      int ok=1,used[12][3];
      for(int o=0;o<T&&ok;o++){int c[3]={perm[3*o],perm[3*o+1],perm[3*o+2]};
        for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(c[j]<c[i]){int t=c[i];c[i]=c[j];c[j]=t;}
        int u=rnd()%m,w=rnd()%m;int a=C*NP+pidx[c[0]][c[1]]*m+u,b=C*NP+pidx[c[0]][c[2]]*m+w,e=C*NP+pidx[c[1]][c[2]]*m+md(w-u);
        if(bud[a]<1||bud[b]<1||bud[e]<1){ok=0;break;}
        bud[a]--;bud[b]--;bud[e]--;used[o][0]=a;used[o][1]=b;used[o][2]=e;
        for(int j=0;j<3;j++)ic[r][k][o][j]=c[j];io[r][k][o][0]=u;io[r][k][o][1]=w;}
      if(!ok){for(int o2=0;o2<T;o2++){if(o2>=T)break;} // roll back what was taken
        // recompute budgets from scratch for accepted weeks
        for(int c=0;c<C;c++)for(int d=1;d<=NP;d++)bud[c*NP+d-1]=(2*d==m)?lam/2:lam;
        for(int i=C*NP;i<NO;i++)bud[i]=lam;
        for(int i=0;i<k;i++)for(int o=0;o<T;o++){int*c=ic[r][i][o];int u=io[r][i][o][0],w=io[r][i][o][1];
          bud[C*NP+pidx[c[0]][c[1]]*m+u]--;bud[C*NP+pidx[c[0]][c[2]]*m+w]--;bud[C*NP+pidx[c[1]][c[2]]*m+md(w-u)]--;}
        continue;}
      k++;}
    if(k<I)continue;
    int dr=anneal(r);
    if(tries%20==0)fprintf(stderr,"round %d tries %ld\n",r,tries);
    if(!dr)continue;
    check:;
    long codes[200];int K=collect(r,codes),ok=1;
    for(int i=0;i<K;i++)for(int j=i+1;j<K;j++)if(codes[i]==codes[j])ok=0;
    if(ok){fprintf(stderr,"round %d design after %ld tries\n",r,tries+1);return;}
  }
}
// lanes: cell index tau*m + rho
int cnt[2][12][MT],rem[2][12],lane[2][6][MT],itr[2][MT],il0[2][MT][4];long ln,lcap;int lo1,hi1,lo2,hi2,ITEMS;
static int feas(int r){
  for(int c=0;c<C;c++){int def=0;for(int i=0;i<n;i++){int x=lo1-cnt[r][c][i];if(x>0)def+=x;}if(def>rem[r][c])return 0;
    if(R==2){int d2=0;for(int i=0;i<n;i++){int x=lo2-cnt[0][c][i]-cnt[1][c][i];if(x>0)d2+=x;}if(d2>rem[0][c]+rem[1][c])return 0;}}
  return 1;}
static int over(int r,int c,int q){return cnt[r][c][q]>hi1||(R==2&&cnt[0][c][q]+cnt[1][c][q]>hi2);}
static inline int cell(int l,int y){return (l/m)*m+md(l%m-y);}
int ldfs(int it,uint32_t*mask){
  if(++ln>lcap)return -1;
  if(it==R*ITEMS)return 1;
  int r=it/ITEMS,k=it%ITEMS;int st=rnd()%n;
  if(k<B*n){int w=k/n,t=k%n;
    for(int kk=0;kk<n;kk++){int l=(st+kk)%n; if(it==0){if(kk)break;l=0;} if(mask[r*6+w]>>l&1)continue;
      int ok=1;
      for(int j=0;j<3;j++){int p=wk[r][w][t][j];int c=p/m,q=cell(l,p%m);cnt[r][c][q]++;rem[r][c]--;if(over(r,c,q))ok=0;}
      int res=0;
      if(ok&&feas(r)){mask[r*6+w]|=1u<<l;res=ldfs(it+1,mask);mask[r*6+w]&=~(1u<<l);}
      for(int j=0;j<3;j++){int p=wk[r][w][t][j];int c=p/m,q=cell(l,p%m);cnt[r][c][q]--;rem[r][c]++;}
      if(res){if(res==1)lane[r][w][t]=l;return res;}
    }
    return 0;}
  // invariant week: choose a track permutation (T! <= 24, enumerate by random tries) and offsets per orbit
  int i=k-B*n;
  // enumerate track assignment as permutation index and offsets: do nested search over orbits
  return -2; // handled by ldfs_inv
}
int ldfs_inv(int it,uint32_t*mask,int o,uint32_t tracks);
int ldfs2(int it,uint32_t*mask){
  if(++ln>lcap)return -1;
  if(it==R*ITEMS)return 1;
  int k=it%ITEMS;
  if(k<B*n){ // reuse base-week branch of ldfs but recursing into ldfs2
    int r=it/ITEMS;int w=k/n,t=k%n;int st=rnd()%n;
    for(int kk=0;kk<n;kk++){int l=(st+kk)%n; if(it==0){if(kk)break;l=0;} if(mask[r*6+w]>>l&1)continue;
      int ok=1;
      for(int j=0;j<3;j++){int p=wk[r][w][t][j];int c=p/m,q=cell(l,p%m);cnt[r][c][q]++;rem[r][c]--;if(over(r,c,q))ok=0;}
      int res=0;
      if(ok&&feas(r)){mask[r*6+w]|=1u<<l;res=ldfs2(it+1,mask);mask[r*6+w]&=~(1u<<l);}
      for(int j=0;j<3;j++){int p=wk[r][w][t][j];int c=p/m,q=cell(l,p%m);cnt[r][c][q]--;rem[r][c]++;}
      if(res){if(res==1)lane[r][w][t]=l;return res;}
    }
    return 0;}
  return ldfs_inv(it,mask,0,0);
}
int ldfs_inv(int it,uint32_t*mask,int o,uint32_t tracks){
  int r=it/ITEMS,i=it%ITEMS-B*n;
  if(o==T)return ldfs2(it+1,mask);
  int st=rnd()%n;
  for(int kk=0;kk<n;kk++){int L=(st+kk)%n;int tau=L/m,l=L%m;if(tracks>>tau&1)continue;
    int*c=ic[r][i][o];int q[3]={tau*m+l,tau*m+md(l-io[r][i][o][0]),tau*m+md(l-io[r][i][o][1])};int ok=1;
    for(int j=0;j<3;j++){cnt[r][c[j]][q[j]]++;rem[r][c[j]]--;if(over(r,c[j],q[j]))ok=0;}
    int res=0;if(ok&&feas(r)){res=ldfs_inv(it,mask,o+1,tracks|1u<<tau);}
    for(int j=0;j<3;j++){cnt[r][c[j]][q[j]]--;rem[r][c[j]]++;}
    if(res){if(res==1)il0[r][i][o]=L;return res;}
  }
  return 0;
}
int main(int argc,char**argv){
  if(argc<8){fprintf(stderr,"usage: zm m C B I lam R seed\n");return 1;}
  m=atoi(argv[1]);C=atoi(argv[2]);B=atoi(argv[3]);I=atoi(argv[4]);lam=atoi(argv[5]);R=atoi(argv[6]);
  if(getenv("NOJOINT"))JOINT=0;
  if(getenv("BLK")){char*p=getenv("BLK");int idx=0;
    while(*p){int b1=strtol(p,&p,10),b2=-1;if(*p=='/'){p++;b2=strtol(p,&p,10);}
      if(idx<atoi(argv[3])){bw[idx][0]=b1;bw[idx][1]=b2;}else bi[idx-atoi(argv[3])]=b1;
      if(b1+1>NBLK)NBLK=b1+1;if(b2+1>NBLK)NBLK=b2+1;idx++;if(*p==',')p++;}
    fprintf(stderr,"%d blocks, %d specs\n",NBLK,idx);}
  if(getenv("SAIT"))SA_ITERS=atol(getenv("SAIT"));
  rs=strtoull(argv[7],0,10)*0x9E3779B97F4A7C15ULL+1;
  T=C/3;n=T*m;N=C*m;NP=m/2;ITEMS=B*n+I;
  int np=0;for(int a=0;a<C;a++)for(int b=a+1;b<C;b++){pidx[a][b]=pidx[b][a]=np++;}
  NO=C*NP+np*m;
  int r1=B*m+I; lo1=r1/n;hi1=(r1+n-1)/n;lo2=2*r1/n;hi2=(2*r1+n-1)/n;
  // per class contributions: each base week has every point once -> B*m per class per... per class c: m points x (B*m weeks) ... rem counts cells
  for(int p=0;p<N;p++)for(int q=0;q<N;q++){if(p==q)continue;int c=p/m,x=p%m,c2=q/m,x2=q%m;
    if(c==c2){int d=md(x2-x);if(d>NP)d=m-d;didx[p][q]=c*NP+d-1;}
    else if(c<c2)didx[p][q]=C*NP+pidx[c][c2]*m+md(x2-x);
    else didx[p][q]=C*NP+pidx[c][c2]*m+md(x-x2);}
  for(long tries=1;;tries++){
    if(R==1||tries==1||rnd()%4==0)design(0);
    if(R==2){design(1);
      long c0[200],c1[200];int K=collect(0,c0);collect(1,c1);int rep=0;
      for(int i=0;i<K;i++)for(int j=0;j<K;j++)if(c0[i]==c1[j])rep++;
      if(rep){fprintf(stderr,"pair shares %d orbits\n",rep);continue;}}
    int lr=0;
    for(int rep=0;rep<10&&lr!=1;rep++){memset(cnt,0,sizeof cnt);
      // contributions per class per round: B weeks*m developed * (m points per class) / m cells-> each class gets B*m*... count = r1 per bowler-residue sum
      for(int r=0;r<2;r++)for(int c=0;c<C;c++)rem[r][c]=r<R?r1:0;
      uint32_t mask[12]={0};ln=0;lcap=3000000;lr=ldfs2(0,mask);}
    fprintf(stderr,"try %ld lane result %d\n",tries,lr);
    if(lr!=1)continue;
    printf("SOLUTION\n");
    for(int r=0;r<R;r++){
      for(int w=0;w<B;w++)for(int i=0;i<m;i++){int out[MP];for(int t=0;t<n;t++){int L=lane[r][w][t];int l=(L/m)*m+(L%m+i)%m;
          for(int j=0;j<3;j++){int p=wk[r][w][t][j];out[l*3+j]=p/m*m+(p%m+i)%m+1;}}for(int k=0;k<N;k++)printf("%d ",out[k]);printf("\n");}
      for(int k=0;k<I;k++){int out[MP];for(int o=0;o<T;o++)for(int j=0;j<m;j++){int L=il0[r][k][o];int l=(L/m)*m+(L%m+j)%m;int*c=ic[r][k][o];
          out[l*3]=c[0]*m+j+1;out[l*3+1]=c[1]*m+(io[r][k][o][0]+j)%m+1;out[l*3+2]=c[2]*m+(io[r][k][o][1]+j)%m+1;}
        for(int q=0;q<N;q++)printf("%d ",out[q]);printf("\n");}
    }
    for(int r=0;r<R;r++){
      for(int w=0;w<B;w++){printf("BASE %d %d:",r,w);for(int t=0;t<n;t++){int*g=wk[r][w][t];printf(" {%d.%d,%d.%d,%d.%d}@%d",g[0]/m,g[0]%m,g[1]/m,g[1]%m,g[2]/m,g[2]%m,lane[r][w][t]);}printf("\n");}
      printf("INV %d:",r);for(int i=0;i<I;i++){printf(" [");for(int o=0;o<T;o++){int*c=ic[r][i][o];printf("{%d.0,%d.%d,%d.%d}@%d ",c[0],c[1],io[r][i][o][0],c[2],io[r][i][o][1],il0[r][i][o]);}printf("]");}printf("\n");
    }
    return 0;
  }
}
