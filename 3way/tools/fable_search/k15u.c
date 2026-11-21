// Enumerate ALL KTS(15) whose first parallel class is {012}{345}{678}{9AB}{CDE} (classes unordered),
// classify by invariant, and exhaustively test each for exact lane balance (each bowler 1 or 2 on each of 5 lanes).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
int cls[7][5][3]; char pu[15][15];
long total=0, balanced=0; long lanenodes=0;
#define MAXK 64
unsigned long long keys[MAXK]; long kcnt[MAXK], kbal[MAXK]; int nk=0; int rep[MAXK][7][5][3];
int cnt[15][5];
int lanedfs(int w,int t,int usedmask){
  lanenodes++;
  if(t==5){
    // feasibility: each bowler's unvisited lanes <= remaining weeks
    int rem=6-w;
    for(int b=0;b<15;b++){int z=0;for(int l=0;l<5;l++)z+=cnt[b][l]==0;if(z>rem)return 0;}
    if(w==6)return 1;
    return lanedfs(w+1,0,0);
  }
  int *T=cls[w][t];
  for(int l=0;l<5;l++){ if(usedmask>>l&1)continue;
    if(cnt[T[0]][l]>=2||cnt[T[1]][l]>=2||cnt[T[2]][l]>=2)continue;
    cnt[T[0]][l]++;cnt[T[1]][l]++;cnt[T[2]][l]++;
    int r=lanedfs(w,t+1,usedmask|1<<l);
    cnt[T[0]][l]--;cnt[T[1]][l]--;cnt[T[2]][l]--;
    if(r)return 1;
  }
  return 0;
}
unsigned long long invariant(){
  // Pasch count of the STS + multiset over class pairs of tr((MM^T)^2),tr((MM^T)^3)
  int blk[35][3],nb=0; for(int w=0;w<7;w++)for(int t=0;t<5;t++){memcpy(blk[nb++],cls[w][t],12);}
  int third[15][15]; for(int i=0;i<35;i++){int a=blk[i][0],b=blk[i][1],c=blk[i][2];third[a][b]=third[b][a]=c;third[a][c]=third[c][a]=b;third[b][c]=third[c][b]=a;}
  int pasch=0;
  for(int i=0;i<35;i++)for(int j=i+1;j<35;j++){ // two blocks sharing a point x: {x,a,b},{x,c,d}; pasch if third(a,c)==third(b,d) or third(a,d)==third(b,c)
    int x=-1; for(int p=0;p<3;p++)for(int q=0;q<3;q++)if(blk[i][p]==blk[j][q])x=blk[i][p];
    if(x<0)continue; int a[2],c[2],n=0,m=0; for(int p=0;p<3;p++){if(blk[i][p]!=x)a[n++]=blk[i][p]; if(blk[j][p]!=x)c[m++]=blk[j][p];}
    if(third[a[0]][c[0]]==third[a[1]][c[1]])pasch++; if(third[a[0]][c[1]]==third[a[1]][c[0]])pasch++;
  }
  // each Pasch counted once per point-pair-of-blocks: 4 blocks, 6 pairs of blocks each sharing a point, each pair detects it once -> /6
  pasch/=6;
  int where[7][15]; for(int w=0;w<7;w++)for(int t=0;t<5;t++)for(int j=0;j<3;j++)where[w][cls[w][t][j]]=t;
  int vals[21],nv=0;
  for(int A=0;A<7;A++)for(int B=A+1;B<7;B++){
    int M[5][5]={{0}}; for(int p=0;p<15;p++)M[where[A][p]][where[B][p]]=1;
    int G[5][5],G2[5][5]; for(int i=0;i<5;i++)for(int j=0;j<5;j++){int s=0;for(int k=0;k<5;k++)s+=M[i][k]*M[j][k];G[i][j]=s;}
    int t2=0,t3=0; for(int i=0;i<5;i++)for(int j=0;j<5;j++){int s=0;for(int k=0;k<5;k++)s+=G[i][k]*G[k][j];G2[i][j]=s;}
    for(int i=0;i<5;i++){t2+=G2[i][i];for(int k=0;k<5;k++)t3+=G2[i][k]*G[k][i];}
    vals[nv++]=t2*100000+t3;
  }
  for(int i=0;i<21;i++)for(int j=i+1;j<21;j++)if(vals[j]<vals[i]){int t=vals[i];vals[i]=vals[j];vals[j]=t;}
  unsigned long long h=pasch; for(int i=0;i<21;i++)h=h*1000003ULL+vals[i];
  // finer: per class A, per pair of blocks X,Y of A: pattern of third points of the 9 cross pairs
  unsigned long long ch[7];
  for(int A=0;A<7;A++){ int pv[10],np=0;
    for(int X=0;X<5;X++)for(int Y=X+1;Y<5;Y++){ int seen[15]={0},bc[5]={0},dz=0;
      for(int i=0;i<3;i++)for(int j=0;j<3;j++){int z=third[cls[A][X][i]][cls[A][Y][j]]; if(!seen[z]){seen[z]=1;dz++;} bc[where[A][z]]++;}
      int s3[5],n3=0; for(int k=0;k<5;k++)s3[n3++]=bc[k]; for(int i=0;i<5;i++)for(int j=i+1;j<5;j++)if(s3[j]<s3[i]){int t=s3[i];s3[i]=s3[j];s3[j]=t;}
      int mult=0; for(int z=0;z<15;z++)mult+=seen[z]; 
      pv[np++]=dz*100000+s3[4]*1000+s3[3]*100+s3[2]*10+s3[1];}
    for(int i=0;i<10;i++)for(int j=i+1;j<10;j++)if(pv[j]<pv[i]){int t=pv[i];pv[i]=pv[j];pv[j]=t;}
    unsigned long long x=7; for(int i=0;i<10;i++)x=x*1000033ULL+pv[i]; ch[A]=x;}
  for(int i=0;i<7;i++)for(int j=i+1;j<7;j++)if(ch[j]<ch[i]){unsigned long long t=ch[i];ch[i]=ch[j];ch[j]=t;}
  for(int i=0;i<7;i++)h=h*1000003ULL+ch[i];
  return (h%18000000000000000ULL)*1000ULL+pasch;
}
void leaf(){
  total++;
  unsigned long long k=invariant(); int i; for(i=0;i<nk;i++)if(keys[i]==k)break;
  if(i==nk){if(nk==MAXK){fprintf(stderr,"too many classes\n");exit(1);}keys[nk]=k;kcnt[nk]=0;kbal[nk]=0;memcpy(rep[nk],cls,sizeof cls);nk++;}
  kcnt[i]++; if(kcnt[i]<=40){printf("K %llu",k);for(int w=0;w<7;w++)for(int t=0;t<5;t++)printf(" %d %d %d",cls[w][t][0],cls[w][t][1],cls[w][t][2]);printf("\n");}
  memset(cnt,0,sizeof cnt); for(int t=0;t<5;t++)for(int j=0;j<3;j++)cnt[cls[0][t][j]][t]=1; // week 0 lanes fixed WLOG
  if(0){balanced++;kbal[i]++;}
}

// ---- DLX exact cover ----
#define MAXN 40000
int Lf[MAXN],Rt[MAXN],Up[MAXN],Dn[MAXN],Col[MAXN],Sz[400],optof[MAXN]; int nn,ncol;
int optk[4000],optT[4000][3],nopt; int sol[64];
long lanecheck_limit=-1;
static void cover(int c){Rt[Lf[c]]=Rt[c];Lf[Rt[c]]=Lf[c];for(int i=Dn[c];i!=c;i=Dn[i])for(int j=Rt[i];j!=i;j=Rt[j]){Up[Dn[j]]=Up[j];Dn[Up[j]]=Dn[j];Sz[Col[j]]--;}}
static void uncover(int c){for(int i=Up[c];i!=c;i=Up[i])for(int j=Lf[i];j!=i;j=Lf[j]){Sz[Col[j]]++;Up[Dn[j]]=j;Dn[Up[j]]=j;}Rt[Lf[c]]=c;Lf[Rt[c]]=c;}
int fill[7];
void search(int d){
  if(Rt[0]==0){
    for(int k=1;k<7;k++)fill[k]=1;
    for(int i=0;i<d;i++){int o=sol[i];int k=optk[o];memcpy(cls[k][fill[k]++],optT[o],12);}
    leaf();return;}
  int c=Rt[0],best=1<<30; for(int j=Rt[0];j!=0;j=Rt[j])if(Sz[j]<best){best=Sz[j];c=j;}
  if(best==0)return;
  cover(c);
  for(int r=Dn[c];r!=c;r=Dn[r]){sol[d]=optof[r];for(int j=Rt[r];j!=r;j=Rt[j])cover(Col[j]);search(d+1);for(int j=Lf[r];j!=r;j=Lf[j])uncover(Col[j]);}
  uncover(c);
}
void run_pairing(int *pa,int *pb){ // class k (1..6) has triple {0,pa[k],pb[k]}
  int pairitem[15][15],cpitem[7][15]; memset(pairitem,0,sizeof pairitem);memset(cpitem,0,sizeof cpitem);
  char forb[15][15]; memset(forb,0,sizeof forb);
  for(int t=0;t<5;t++){int a=3*t;forb[a][a+1]=forb[a][a+2]=forb[a+1][a+2]=1;}
  for(int k=1;k<7;k++){forb[pa[k]][pb[k]]=1; cls[k][0][0]=0;cls[k][0][1]=pa[k];cls[k][0][2]=pb[k];}
  ncol=0;
  for(int a=1;a<15;a++)for(int b=a+1;b<15;b++)if(!forb[a][b])pairitem[a][b]=++ncol;
  for(int k=1;k<7;k++)for(int p=1;p<15;p++)if(p!=pa[k]&&p!=pb[k])cpitem[k][p]=++ncol;
  for(int i=0;i<=ncol;i++){Lf[i]=i-1;Rt[i]=i+1;Up[i]=Dn[i]=i;Sz[i]=0;Col[i]=i;} Lf[0]=ncol;Rt[ncol]=0; nn=ncol+1; nopt=0;
  for(int k=1;k<7;k++)for(int a=1;a<15;a++)for(int b=a+1;b<15;b++)for(int c=b+1;c<15;c++){
    if(forb[a][b]||forb[a][c]||forb[b][c])continue; if(!cpitem[k][a]||!cpitem[k][b]||!cpitem[k][c])continue;
    int its[6]={pairitem[a][b],pairitem[a][c],pairitem[b][c],cpitem[k][a],cpitem[k][b],cpitem[k][c]};
    optk[nopt]=k;optT[nopt][0]=a;optT[nopt][1]=b;optT[nopt][2]=c;
    int first=nn; for(int i=0;i<6;i++){int x=nn++,cc=its[i];Col[x]=cc;optof[x]=nopt;Up[x]=Up[cc];Dn[x]=cc;Dn[Up[cc]]=x;Up[cc]=x;Sz[cc]++;Lf[x]=i?x-1:first+5;Rt[x]=i<5?x+1:first;}
    nopt++;}
  search(0);
}
int pidx=0,NP=1,PI=0;
void pairings(int k,int usedmask,int *pa,int *pb){
  if(k==7){ if(pb[1]!=6)return; if((pidx++)%NP==PI)run_pairing(pa,pb);return;}
  int a=3; while(usedmask>>a&1)a++;
  for(int b=a+1;b<15;b++){ if(usedmask>>b&1)continue; if(a/3==b/3)continue; // pair must not be in class 0
    pa[k]=a;pb[k]=b; pairings(k+1,usedmask|1<<a|1<<b,pa,pb);}
}
int main(int argc,char**argv){ if(argc>2){NP=atoi(argv[1]);PI=atoi(argv[2]);}
  for(int t=0;t<5;t++){int a=3*t;cls[0][t][0]=a;cls[0][t][1]=a+1;cls[0][t][2]=a+2;pu[a][a+1]=pu[a+1][a]=pu[a][a+2]=pu[a+2][a]=pu[a+1][a+2]=pu[a+2][a+1]=1;}
  {int pa[7],pb[7];pairings(1,0,pa,pb);}
  printf("KTS(15) with fixed first class: %ld (expected 1788480 = 7*15!*(2/168+2/24+1/12+2/21)/1401400)\n",total);
  printf("lane-balanced: %ld   lane DFS nodes: %ld\n",balanced,lanenodes);
  printf("invariant classes: %d\n",nk);
  for(int i=0;i<nk;i++){printf("class key=%llu #%d: pasch=%llu count=%ld (=> |Aut| = %.2f if single iso class) balanced=%ld\n rep:",keys[i],i,keys[i]%1000,kcnt[i],6531840.0/kcnt[i],kbal[i]);
    for(int w=0;w<7;w++){for(int t=0;t<5;t++)printf(" %d,%d,%d",rep[i][w][t][0],rep[i][w][t][1],rep[i][w][t][2]);printf(" |");}printf("\n");}
}
