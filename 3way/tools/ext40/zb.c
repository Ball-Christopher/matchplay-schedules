// zb.c: lane-rotating Z_m x C design (as zm.c) with oil blocks checked at PAIR level.
// Every developed week (base week w, shift i) and every invariant week is assigned to a block;
// the annealing cost is  sum_orbits |count - lambda|  +  sum_blocks sum_pairs max(0, meetings - 1).
// Used for 36 = Z_12 x 3, where an orbit-exact split (v24's template) is impossible by parity:
// under Z_12 -> Z_2 a triple has an even number of odd-difference pairs and transversal invariant
// weeks too, but an exact cover of the full orbits needs 3*3 + 3*6 = 27 odd-difference orbits.
// usage: BLK="<m digits per base week>,...,<1 digit per invariant week>,..." zb m C B I lam seed
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
static uint64_t rs;
static inline uint32_t rnd(){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)(rs>>11);}
#define MP 40
#define MT 13
int m,C,T,n,B,I,lam,N,NP,NO,NB;
int didx[MP][MP],pidx[12][12],bud[600];
int wk[6][MT][3],invC[MT*2][4][3],invO[MT*2][4][3];
int blkW[6][MT],blkI[MT*2];
static inline int md(int x){x%=m;return x<0?x+m:x;}
static int oc[600]; static unsigned char pc[4][MP][MP];
static inline int cdelta(int o,int d){int b=oc[o]-bud[o];int a=b+d;oc[o]+=d;return abs(a)-abs(b);}
static inline int sh(int p,int i){return p/m*m+md(p%m+i);}
static inline int pdel(int b,int p,int q,int d){if(p>q){int t=p;p=q;q=t;}int x=pc[b][p][q];int be=x>1?x-1:0;x+=d;pc[b][p][q]=x;int af=x>1?x-1:0;return af-be;}
// base-week pair (p,q) of week w, all developments
static inline int bpair(int w,int p,int q,int d){int r=cdelta(didx[p][q],d);for(int i=0;i<m;i++)r+=pdel(blkW[w][i],sh(p,i),sh(q,i),d);return r;}
static inline int ipair(int k,int ca,int oa,int cb,int ob,int d){int p=ca*m+md(oa),q=cb*m+md(ob);int r=cdelta(didx[p][q],d);
  for(int j=0;j<m;j++)r+=pdel(blkI[k],sh(p,j),sh(q,j),d);return r;}
static inline int iorb(int k,int o,int d){int*c=invC[k][o],*f=invO[k][o];return ipair(k,c[0],f[0],c[1],f[1],d)+ipair(k,c[0],f[0],c[2],f[2],d)+ipair(k,c[1],f[1],c[2],f[2],d);}
long SA_ITERS=30000000;
int anneal(){
  for(int c=0;c<C;c++)for(int d=1;d<=NP;d++)bud[c*NP+d-1]=(2*d==m)?lam/2:lam;
  for(int i=C*NP;i<NO;i++)bud[i]=lam;
  memset(oc,0,sizeof oc);memset(pc,0,sizeof pc);
  for(int w=0;w<B;w++){int perm[MP];for(int i=0;i<N;i++)perm[i]=i;for(int i=N-1;i>0;i--){int j=rnd()%(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;}
    for(int t=0;t<n;t++)for(int j=0;j<3;j++)wk[w][t][j]=perm[3*t+j];}
  for(int k=0;k<I;k++){int perm[12];for(int i=0;i<C;i++)perm[i]=i;for(int i=C-1;i>0;i--){int j=rnd()%(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;}
    for(int o=0;o<T;o++)for(int e=0;e<3;e++){invC[k][o][e]=perm[3*o+e];invO[k][o][e]=rnd()%m;}}
  int cost=0;for(int o=0;o<NO;o++)cost-=bud[o]; // start from |0-bud| = bud
  cost=0;for(int o=0;o<NO;o++)cost+=bud[o];
  for(int w=0;w<B;w++)for(int t=0;t<n;t++){int*g=wk[w][t];cost+=bpair(w,g[0],g[1],1)+bpair(w,g[0],g[2],1)+bpair(w,g[1],g[2],1);}
  for(int k=0;k<I;k++)for(int o=0;o<T;o++)cost+=iorb(k,o,1);
  double Tm=2.0,pinv=I?(double)I*T*3/(I*T*3+B*N):0; int best=cost;
  for(long it=0;it<SA_ITERS&&cost;it++){
    if((it&1023)==0){Tm*=0.995;if(Tm<0.12)Tm=0.6;}
    if((rnd()&0xffff)<65536.0*pinv){
      int k=rnd()%I,o1=rnd()%T,e1=rnd()%3,o2=-1,e2=-1;
      int oldC1=invC[k][o1][e1],oldO1=invO[k][o1][e1],oldC2=0,oldO2=0;
      if(T>1&&(rnd()&1)){o2=(o1+1+rnd()%(T-1))%T;e2=rnd()%3;}
      int d=iorb(k,o1,-1);if(o2>=0)d+=iorb(k,o2,-1);
      if(o2>=0){oldC2=invC[k][o2][e2];oldO2=invO[k][o2][e2];invC[k][o1][e1]=oldC2;invO[k][o1][e1]=oldO2;invC[k][o2][e2]=oldC1;invO[k][o2][e2]=oldO1;}
      else invO[k][o1][e1]=rnd()%m;
      d+=iorb(k,o1,1);if(o2>=0)d+=iorb(k,o2,1);
      if(d<=0||(rnd()&0xffff)<65536.0*exp(-d/Tm))cost+=d;
      else{iorb(k,o1,-1);if(o2>=0)iorb(k,o2,-1);
        invC[k][o1][e1]=oldC1;invO[k][o1][e1]=oldO1;if(o2>=0){invC[k][o2][e2]=oldC2;invO[k][o2][e2]=oldO2;}
        iorb(k,o1,1);if(o2>=0)iorb(k,o2,1);}
      continue;}
    int w=rnd()%B,t1=rnd()%n,t2=rnd()%n;if(t1==t2)continue;int i=rnd()%3,j=rnd()%3;
    int*g1=wk[w][t1],*g2=wk[w][t2];int a=g1[i],b=g2[j];
    int a1=g1[(i+1)%3],a2=g1[(i+2)%3],b1=g2[(j+1)%3],b2=g2[(j+2)%3];
    int d=bpair(w,a,a1,-1)+bpair(w,a,a2,-1)+bpair(w,b,b1,-1)+bpair(w,b,b2,-1)
         +bpair(w,b,a1,1)+bpair(w,b,a2,1)+bpair(w,a,b1,1)+bpair(w,a,b2,1);
    if(d<=0||(rnd()&0xffff)<65536.0*exp(-d/Tm)){g1[i]=b;g2[j]=a;cost+=d;}
    else{bpair(w,a,b2,-1);bpair(w,a,b1,-1);bpair(w,b,a2,-1);bpair(w,b,a1,-1);
      bpair(w,b,b2,1);bpair(w,b,b1,1);bpair(w,a,a2,1);bpair(w,a,a1,1);}
    if(cost<best)best=cost;
  }
  if(getenv("SADBG"))fprintf(stderr,"sa end cost %d (best %d)\n",cost,best);
  return cost==0;
}
long canon(int a,int b,int c){long bst=1L<<60;
  for(int s=0;s<m;s++){int x[3]={sh(a,s),sh(b,s),sh(c,s)};
    for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)if(x[j]<x[i]){int t=x[i];x[i]=x[j];x[j]=t;}
    long code=((long)x[0]*64+x[1])*64+x[2];if(code<bst)bst=code;}return bst;}
// lanes (single round)
int cnt[12][MT],rem[12],lane[6][MT],il0[MT*2][4];long ln,lcap;int lo,hi,ITEMS;
static int feas(){for(int c=0;c<C;c++){int def=0;for(int i=0;i<n;i++){int x=lo-cnt[c][i];if(x>0)def+=x;}if(def>rem[c])return 0;}return 1;}
static inline int cell(int L,int y){return (L/m)*m+md(L%m-y);}
int ldfs(int it,uint32_t*mask,int o,uint32_t tracks){
  if(++ln>lcap)return -1;
  if(it==ITEMS)return 1;
  int st=rnd()%n;
  if(it<B*n){int w=it/n,t=it%n;
    for(int kk=0;kk<n;kk++){int l=(st+kk)%n;if(it==0){if(kk)break;l=0;}if(mask[w]>>l&1)continue;
      int ok=1;for(int j=0;j<3;j++){int q=wk[w][t][j];int c=q/m,e=cell(l,q%m);cnt[c][e]++;rem[c]--;if(cnt[c][e]>hi)ok=0;}
      int res=0;if(ok&&feas()){mask[w]|=1u<<l;res=ldfs(it+1,mask,0,0);mask[w]&=~(1u<<l);}
      for(int j=0;j<3;j++){int q=wk[w][t][j];int c=q/m,e=cell(l,q%m);cnt[c][e]--;rem[c]++;}
      if(res){if(res==1)lane[w][t]=l;return res;}}
    return 0;}
  int k=it-B*n;
  if(o==T)return ldfs(it+1,mask,0,0);
  for(int kk=0;kk<n;kk++){int L=(st+kk)%n;int tau=L/m,l=L%m;if(tracks>>tau&1)continue;
    int*c=invC[k][o],*f=invO[k][o];int e[3];int ok=1;
    for(int j=0;j<3;j++){e[j]=tau*m+md(l-f[j]);cnt[c[j]][e[j]]++;rem[c[j]]--;if(cnt[c[j]][e[j]]>hi)ok=0;}
    int res=0;if(ok&&feas())res=ldfs(it,mask,o+1,tracks|1u<<tau);
    for(int j=0;j<3;j++){cnt[c[j]][e[j]]--;rem[c[j]]++;}
    if(res){if(res==1)il0[k][o]=L;return res;}}
  return 0;
}
int main(int argc,char**argv){
  if(argc<7||!getenv("BLK")){fprintf(stderr,"usage: BLK=... zb m C B I lam seed\n");return 1;}
  m=atoi(argv[1]);C=atoi(argv[2]);B=atoi(argv[3]);I=atoi(argv[4]);lam=atoi(argv[5]);
  rs=strtoull(argv[6],0,10)*0x9E3779B97F4A7C15ULL+1;
  if(getenv("SAIT"))SA_ITERS=atol(getenv("SAIT"));
  T=C/3;n=T*m;N=C*m;NP=m/2;ITEMS=B*n+I;
  int np=0;for(int a=0;a<C;a++)for(int b=a+1;b<C;b++){pidx[a][b]=pidx[b][a]=np++;}
  NO=C*NP+np*m;
  for(int p=0;p<N;p++)for(int q=0;q<N;q++){if(p==q)continue;int c=p/m,x=p%m,c2=q/m,x2=q%m;
    if(c==c2){int d=md(x2-x);if(d>NP)d=m-d;didx[p][q]=c*NP+d-1;}
    else if(c<c2)didx[p][q]=C*NP+pidx[c][c2]*m+md(x2-x);
    else didx[p][q]=C*NP+pidx[c][c2]*m+md(x-x2);}
  {char*p=getenv("BLK");NB=0;
    for(int w=0;w<B;w++){for(int i=0;i<m;i++){blkW[w][i]=p[i]-'0';if(blkW[w][i]+1>NB)NB=blkW[w][i]+1;}p+=m;if(*p==',')p++;}
    for(int k=0;k<I;k++){blkI[k]=*p-'0';p++;if(*p==',')p++;}
    fprintf(stderr,"%d blocks\n",NB);}
  int r1=B*m+I;lo=r1/n;hi=(r1+n-1)/n;
  for(long tries=1;;tries++){
    if(!anneal())continue;
    long codes[200];int K=0,rep=0;
    for(int w=0;w<B;w++)for(int t=0;t<n;t++)codes[K++]=canon(wk[w][t][0],wk[w][t][1],wk[w][t][2]);
    for(int k=0;k<I;k++)for(int o=0;o<T;o++)codes[K++]=canon(invC[k][o][0]*m+invO[k][o][0],invC[k][o][1]*m+invO[k][o][1],invC[k][o][2]*m+invO[k][o][2]);
    for(int i=0;i<K;i++)for(int j=i+1;j<K;j++)if(codes[i]==codes[j])rep++;
    if(rep){fprintf(stderr,"try %ld: %d repeated trio orbits\n",tries,rep);continue;}
    int lr=0;
    for(int r2=0;r2<10&&lr!=1;r2++){memset(cnt,0,sizeof cnt);for(int c=0;c<C;c++)rem[c]=r1;uint32_t mask[8]={0};ln=0;lcap=3000000;lr=ldfs(0,mask,0,0);}
    fprintf(stderr,"try %ld lane result %d\n",tries,lr);
    if(lr!=1)continue;
    printf("SOLUTION\n");
    for(int w=0;w<B;w++)for(int i=0;i<m;i++){int out[MP];for(int t=0;t<n;t++){int L=lane[w][t];int l=(L/m)*m+(L%m+i)%m;
        for(int j=0;j<3;j++)out[l*3+j]=sh(wk[w][t][j],i)+1;}
      printf("W%d ",blkW[w][i]);for(int k=0;k<N;k++)printf("%d ",out[k]);printf("\n");}
    for(int k=0;k<I;k++){int out[MP];for(int o=0;o<T;o++)for(int j=0;j<m;j++){int L=il0[k][o];int l=(L/m)*m+(L%m+j)%m;int*c=invC[k][o],*f=invO[k][o];
          for(int e=0;e<3;e++)out[l*3+e]=c[e]*m+md(f[e]+j)+1;}
      printf("W%d ",blkI[k]);for(int q=0;q<N;q++)printf("%d ",out[q]);printf("\n");}
    for(int w=0;w<B;w++){printf("BASE %d:",w);for(int t=0;t<n;t++){int*g=wk[w][t];printf(" {%d.%d,%d.%d,%d.%d}@%d",g[0]/m,g[0]%m,g[1]/m,g[1]%m,g[2]/m,g[2]%m,lane[w][t]);}printf("\n");}
    printf("INV:");for(int k=0;k<I;k++){printf(" [");for(int o=0;o<T;o++){int*c=invC[k][o],*f=invO[k][o];printf("{%d.%d,%d.%d,%d.%d}@%d ",c[0],f[0],c[1],f[1],c[2],f[2],il0[k][o]);}printf("]");}printf("\n");
    return 0;
  }
}
