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
  return h*1000ULL+pasch;
}
void leaf(){
  total++;
  unsigned long long k=invariant(); int i; for(i=0;i<nk;i++)if(keys[i]==k)break;
  if(i==nk){if(nk==MAXK){fprintf(stderr,"too many classes\n");exit(1);}keys[nk]=k;kcnt[nk]=0;kbal[nk]=0;memcpy(rep[nk],cls,sizeof cls);nk++;}
  kcnt[i]++;
  memset(cnt,0,sizeof cnt); for(int t=0;t<5;t++)for(int j=0;j<3;j++)cnt[cls[0][t][j]][t]=1; // week 0 lanes fixed WLOG
  if(lanedfs(1,0,0)){balanced++;kbal[i]++;}
}
void dfs(int w,int t,int used){
  if(t==5){ if(w==6){leaf();return;} dfs(w+1,0,0); return; }
  int p=0; while(used>>p&1)p++;
  for(int q=p+1;q<15;q++){ if(used>>q&1||pu[p][q])continue;
    if(t==0){ // p==0: q must be smallest point not yet paired with 0
      int s=1; while(pu[0][s])s++; if(q!=s)break; }
    for(int r=q+1;r<15;r++){ if(used>>r&1||pu[p][r]||pu[q][r])continue;
      pu[p][q]=pu[q][p]=pu[p][r]=pu[r][p]=pu[q][r]=pu[r][q]=1;
      cls[w][t][0]=p;cls[w][t][1]=q;cls[w][t][2]=r;
      dfs(w,t+1,used|1<<p|1<<q|1<<r);
      pu[p][q]=pu[q][p]=pu[p][r]=pu[r][p]=pu[q][r]=pu[r][q]=0;
    }
  }
}
int main(){
  for(int t=0;t<5;t++){int a=3*t;cls[0][t][0]=a;cls[0][t][1]=a+1;cls[0][t][2]=a+2;pu[a][a+1]=pu[a+1][a]=pu[a][a+2]=pu[a+2][a]=pu[a+1][a+2]=pu[a+2][a+1]=1;}
  dfs(1,0,0);
  printf("KTS(15) with fixed first class: %ld (expected 1788480 = 7*15!*(2/168+2/24+1/12+2/21)/1401400)\n",total);
  printf("lane-balanced: %ld   lane DFS nodes: %ld\n",balanced,lanenodes);
  printf("invariant classes: %d\n",nk);
  for(int i=0;i<nk;i++){printf("class %d: pasch=%llu count=%ld (=> |Aut| = %.2f if single iso class) balanced=%ld\n rep:",i,keys[i]%1000,kcnt[i],6531840.0/kcnt[i],kbal[i]);
    for(int w=0;w<7;w++){for(int t=0;t<5;t++)printf(" %d,%d,%d",rep[i][w][t][0],rep[i][w][t][1],rep[i][w][t][2]);printf(" |");}printf("\n");}
}
