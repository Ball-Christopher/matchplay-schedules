// Lane-rotating 4-way designs on Z_m x 4 classes (point p = m*a + i, class a, i in Z_m).
// The automorphism i -> i+1 also moves every group up one lane pair (mod m).
// Weeks: NB base weeks developed mod m (m weeks each), NT transversal invariant
// weeks (block {(a, c_a)} developed mod m), NH "half" invariant weeks (m even,
// H = m/2): blocks {(x,t),(x,t+H),(y,b+t),(y,b+t+H)} and {(z,t),(z,t+H),(u,c+t),(u,c+t+H)},
// t = 0..H-1, class pairing cycling {01|23},{02|13},{03|12}. Half weeks cover the
// short (antipodal) pair orbits once each; base weeks would cover them twice.
// Stage 1: anneal pair-orbit counts to lambda (optionally with oil-block penalty:
//   base orbit w is block w, half week h joins block h, transversals form the last block).
// Stage 2: anneal lane perms of base weeks, offsets of transversal weeks and lane
//   perms of half weeks to exact per-bowler lane counts.
// Usage: zsym m NB NT NH lambda oil seed [maxdesigns]
// Output (stdout): one line per week, 4m point ids in lane order; then "BLOCKS ..." line.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
static unsigned long long s = 88172645463325252ULL;
static inline unsigned long long rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
static inline double urand(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
int TABU, TEN, DEEP; int LTRY=40; long LIT=400000; int m, NB, NT, NH, LAM, OIL, V, H, NO, NBLK;
int base[4][64]; int tr[16][4]; int hb[8][2];
int cnt[256]; int cw[8][256]; long cost;
int pairI[4][4];
static const int PAIRING[3][4] = {{0,1,2,3},{0,2,1,3},{0,3,1,2}};
static int orb(int p, int q, int *wt, int isbase){
  int a=p/m,i=p%m,b=q/m,j=q%m;
  if(a>b){int t=a;a=b;b=t;t=i;i=j;j=t;}
  *wt=1;
  if(a!=b) return pairI[a][b]*m + ((j-i+m)%m);
  int d=(j-i+m)%m; if(d>m-d) d=m-d;
  if(isbase && 2*d==m) *wt=2;
  return 6*m + a*(m/2) + (d-1);
}
static inline long fo(int c){return labs((long)c-LAM);}
static inline long fw(int c){return c>1? c-1:0;}
static void addp(int p,int q,int blk,int sg,int isbase){
  int wt; int o=orb(p,q,&wt,isbase);
  cost -= fo(cnt[o]); cnt[o]+=sg*wt; cost += fo(cnt[o]);
  if(OIL){cost -= 3*fw(cw[blk][o]); cw[blk][o]+=sg*wt; cost += 3*fw(cw[blk][o]);}
}
static void blockpairs(int *pts,int blk,int sg,int isbase){
  for(int x=0;x<4;x++)for(int y=x+1;y<4;y++)addp(pts[x],pts[y],blk,sg,isbase);
}
static void trweek(int f,int sg){int pts[4];for(int a=0;a<4;a++)pts[a]=m*a+tr[f][a];blockpairs(pts,NB,sg,0);}
static int halfblk(int h){return (OIL && NH==NB)? h : NB;}
static void halfweek(int h,int sg){
  const int*P=PAIRING[h%3];
  // one representative block per half-orbit; pairs inside: antipodal (weight 1) + 4 mixed
  for(int side=0;side<2;side++){int x=P[2*side],y=P[2*side+1],b=hb[h][side];
    int pts[4]={m*x+0,m*x+H,m*y+b,m*y+b+H};
    // the orbit of this block (H blocks) covers each pair in each of these orbits once
    blockpairs(pts,halfblk(h),sg,0);
    // blockpairs counted the mixed orbits d and d+H once each (2 of the 4 pairs hit each
    // orbit once per H translates -> once per pair). Fine: pairs (x0,yb),(xH,y b+H) are the
    // same orbit; correct for the double count:
    addp(pts[0],pts[2],halfblk(h),-sg,0); addp(pts[0],pts[3],halfblk(h),-sg,0);
  }
}
static void build(void){
  memset(cnt,0,sizeof cnt);memset(cw,0,sizeof cw);cost=0;
  for(int o=0;o<NO;o++)cost+=fo(0);
  for(int w=0;w<NB;w++)for(int b=0;b<m;b++)blockpairs(&base[w][4*b],w,1,1);
  for(int f=0;f<NT;f++)trweek(f,1);
  for(int h=0;h<NH;h++)halfweek(h,1);
}
// ---------- lanes ----------
int pi[4][16], rf[16], hl[8][16];
int lc[64][16];
static int lo_, hi_;
static long lanecost(void){
  int hr[4][16];memset(hr,0,sizeof hr);
  for(int w=0;w<NB;w++)for(int b=0;b<m;b++)for(int x=0;x<4;x++){int p=base[w][4*b+x];hr[p/m][(pi[w][b]-p%m+m)%m]++;}
  for(int f=0;f<NT;f++)for(int a=0;a<4;a++)hr[a][(rf[f]-tr[f][a]+m)%m]++;
  long c=0;
  if(!NH){for(int a=0;a<4;a++)for(int d=0;d<m;d++){int v=hr[a][d];if(v<lo_)c+=lo_-v;if(v>hi_)c+=v-hi_;}return c;}
  for(int p=0;p<V;p++)for(int L=0;L<m;L++)lc[p][L]=hr[p/m][(L-p%m+m)%m];
  for(int h=0;h<NH;h++){const int*P=PAIRING[h%3];
    for(int side=0;side<2;side++){int x=P[2*side],y=P[2*side+1],b=hb[h][side];
      for(int t=0;t<H;t++){int L=hl[h][side*H+t];
        lc[m*x+t][L]++;lc[m*x+t+H][L]++;lc[m*y+(b+t)%m][L]++;lc[m*y+(b+t+H)%m][L]++;}}}
  for(int p=0;p<V;p++)for(int L=0;L<m;L++){int v=lc[p][L];if(v<lo_)c+=lo_-v;if(v>hi_)c+=v-hi_;}
  return c;
}
static void shuf(int*a,int n){for(int i=0;i<n;i++)a[i]=i;for(int i=n-1;i>0;i--){int j=rnd()%(i+1);int t=a[i];a[i]=a[j];a[j]=t;}}
static int lanes(long iters){
  for(int w=0;w<NB;w++)shuf(pi[w],m);
  for(int f=0;f<NT;f++)rf[f]=rnd()%m;
  for(int h=0;h<NH;h++)shuf(hl[h],m);
  long c=lanecost();double T=2.0;
  for(long it=0;it<iters&&c>0;it++){
    if((it&1023)==0)T=2.0*pow(0.02,(double)it/iters);
    int kind=rnd()%(NB+NT+NH);
    if(kind<NB){int w=kind,x=rnd()%m,y=rnd()%m;if(x==y)continue;int t=pi[w][x];pi[w][x]=pi[w][y];pi[w][y]=t;
      long n=lanecost();if(n<=c||urand()<exp(-(n-c)/T))c=n;else{t=pi[w][x];pi[w][x]=pi[w][y];pi[w][y]=t;}}
    else if(kind<NB+NT){int f=kind-NB,old=rf[f];rf[f]=rnd()%m;long n=lanecost();if(n<=c||urand()<exp(-(n-c)/T))c=n;else rf[f]=old;}
    else{int h=kind-NB-NT,x=rnd()%m,y=rnd()%m;if(x==y)continue;int t=hl[h][x];hl[h][x]=hl[h][y];hl[h][y]=t;
      long n=lanecost();if(n<=c||urand()<exp(-(n-c)/T))c=n;else{t=hl[h][x];hl[h][x]=hl[h][y];hl[h][y]=t;}}
  }
  return (int)c;
}

static int mvK[4096],mv1[4096],mv2[4096],mv3[4096];int NMV;
static void genmoves(void){NMV=0;
  for(int w=0;w<NB;w++)for(int x=0;x<V;x++)for(int y=x+1;y<V;y++)if(x/4!=y/4){mvK[NMV]=0;mv1[NMV]=w;mv2[NMV]=x;mv3[NMV]=y;NMV++;}
  for(int f=0;f<NT;f++)for(int a=1;a<4;a++)for(int v=0;v<m;v++){mvK[NMV]=1;mv1[NMV]=f;mv2[NMV]=a;mv3[NMV]=v;NMV++;}
  for(int h=0;h<NH;h++)for(int sd=0;sd<2;sd++)for(int v=0;v<H;v++){mvK[NMV]=2;mv1[NMV]=h;mv2[NMV]=sd;mv3[NMV]=v;NMV++;}}
static void doswap(int w,int x,int y){int bx=x/4,by=y/4;
  blockpairs(&base[w][4*bx],w,-1,1);blockpairs(&base[w][4*by],w,-1,1);
  int t=base[w][x];base[w][x]=base[w][y];base[w][y]=t;
  blockpairs(&base[w][4*bx],w,1,1);blockpairs(&base[w][4*by],w,1,1);}
// apply move i; returns undo value (old) or -1 if no-op
static int applymv(int i){int k=mvK[i];
  if(k==0){doswap(mv1[i],mv2[i],mv3[i]);return 0;}
  if(k==1){int f=mv1[i],a=mv2[i],old=tr[f][a];if(old==mv3[i])return -1;trweek(f,-1);tr[f][a]=mv3[i];trweek(f,1);return old;}
  {int h=mv1[i],sd=mv2[i],old=hb[h][sd];if(old==mv3[i])return -1;halfweek(h,-1);hb[h][sd]=mv3[i];halfweek(h,1);return old;}}
static void undomv(int i,int old){int k=mvK[i];if(old<0)return;
  if(k==0){doswap(mv1[i],mv2[i],mv3[i]);return;}
  if(k==1){int f=mv1[i],a=mv2[i];trweek(f,-1);tr[f][a]=old;trweek(f,1);return;}
  {int h=mv1[i],sd=mv2[i];halfweek(h,-1);hb[h][sd]=old;halfweek(h,1);}}
// descent over single and pairs of moves; returns when no improving 1- or 2-move exists
static void deep(void){
  for(;;){ long c0=cost; int imp=0;
    int order[4096];for(int i=0;i<NMV;i++)order[i]=i;for(int i=NMV-1;i>0;i--){int j=rnd()%(i+1);int t=order[i];order[i]=order[j];order[j]=t;}
    for(int ii=0;ii<NMV&&!imp;ii++){int i=order[ii];int o1=applymv(i);if(o1==-1)continue;
      if(cost<c0){imp=1;break;}
      if(cost<=c0+12) for(int jj=0;jj<NMV;jj++){int j=order[jj];int o2=applymv(j);if(o2==-1)continue;
        if(cost<c0){imp=1;break;} undomv(j,o2);}
      if(imp)break; undomv(i,o1);}
    if(!imp)return; if(cost==0)return; }}

// ---- PHI mode: class map phi = (0)(1 2 3) ties base week w+1 = phi(base week w),
// transversal weeks in phi-orbits of 3 (first 3*NT3) or phi-fixed (0,c,c,c), half week h+1 = phi(half h).
int PHI=0, NT3=0; static const int phiC[4]={0,2,3,1};
static int Pp(int p){return m*phiC[p/m]+p%m;}
int htab[8][8][2];
static void halfset(int h,int b,int c,int out[][4]){const int*P=PAIRING[h%3];int hbv[2]={b,c};int n=0;
  for(int side=0;side<2;side++){int x=P[2*side],y=P[2*side+1],bb=hbv[side];
    for(int t=0;t<H;t++){int q[4]={m*x+t,m*x+t+H,m*y+(bb+t)%m,m*y+(bb+t+H)%m};
      for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)if(q[j]<q[i]){int z=q[i];q[i]=q[j];q[j]=z;}
      memcpy(out[n++],q,sizeof q);}}}
static int cmp4(const void*a,const void*b){return memcmp(a,b,16);}
static void mkhtab(int h){ // htab[b][c] for half h -> params of half h+1 equal to phi(half h)
  for(int b=0;b<H;b++)for(int c=0;c<H;c++){int A[16][4];halfset(h,b,c,A);
    for(int k=0;k<m;k++){for(int i=0;i<4;i++)A[k][i]=Pp(A[k][i]);for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)if(A[k][j]<A[k][i]){int z=A[k][i];A[k][i]=A[k][j];A[k][j]=z;}}
    qsort(A,m,16,cmp4);int found=0;
    for(int b2=0;b2<H&&!found;b2++)for(int c2=0;c2<H&&!found;c2++){int B[16][4];halfset(h+1,b2,c2,B);qsort(B,m,16,cmp4);
      if(!memcmp(A,B,sizeof(int)*4*m)){htab[b*H+c][h][0]=b2;htab[b*H+c][h][1]=c2;found=1;}}
    if(!found){fprintf(stderr,"htab fail\n");exit(3);}}}
static void phitr(int*src,int*dst){for(int a=0;a<4;a++)dst[phiC[a]]=src[a];}
static void derive_tr(int f){ if(f<3*NT3){int j=f/3*3;phitr(tr[j],tr[j+1]);phitr(tr[j+1],tr[j+2]);} }
static void derive_hb(void){for(int h=0;h+1<NH;h++){int b=hb[h][0],c=hb[h][1];hb[h+1][0]=htab[b*H+c][h][0];hb[h+1][1]=htab[b*H+c][h][1];}}
static void trgroup(int f,int sg){ if(f<3*NT3){int j=f/3*3;trweek(j,sg);trweek(j+1,sg);trweek(j+2,sg);} else trweek(f,sg);}
int main(int argc,char**argv){
  if(argc<8){fprintf(stderr,"usage: zsym m NB NT NH lambda oil seed [maxdesigns] [iters]\n");return 2;}
  m=atoi(argv[1]);NB=atoi(argv[2]);NT=atoi(argv[3]);NH=atoi(argv[4]);LAM=atoi(argv[5]);OIL=atoi(argv[6]);
  s^=(unsigned long long)atoll(argv[7])*0x9E3779B97F4A7C15ULL; for(int i=0;i<10;i++)rnd();
  int maxd=argc>8?atoi(argv[8]):1000000; long iters=argc>9?atol(argv[9]):20000000; double T0=argc>10?atof(argv[10]):1.5, TF=argc>11?atof(argv[11]):0.03; TABU=argc>12?atoi(argv[12]):0; TEN=argc>13?atoi(argv[13]):15; DEEP=argc>14?atoi(argv[14]):0;
  V=4*m;H=m/2;NO=6*m+4*(m/2);NBLK=NB+1;
  {int k=0;for(int a=0;a<4;a++)for(int b=a+1;b<4;b++)pairI[a][b]=k++;}
  int r=NB*m+NT+NH; lo_=r/m; hi_=(r+m-1)/m;
  if(m%2==1 && NH){fprintf(stderr,"NH needs even m\n");return 2;}
  if(m%2==1){NO=6*m+4*((m-1)/2);}
  if(getenv("LTRY"))LTRY=atoi(getenv("LTRY")); if(getenv("LIT"))LIT=atol(getenv("LIT"));
  if(getenv("PHI")){PHI=1;NT3=atoi(getenv("PHI"));if(NB!=3){fprintf(stderr,"PHI needs NB=3\n");return 2;} if(NH){for(int h=0;h+1<NH;h++)mkhtab(h);} }
  fprintf(stderr,"m=%d NB=%d NT=%d NH=%d lam=%d oil=%d weeks=%d lanes %d..%d orbits=%d\n",m,NB,NT,NH,LAM,OIL,r,lo_,hi_,NO);
  for(int att=0;att<maxd;att++){
    for(int w=0;w<NB;w++){int t[64];shuf(t,V);memcpy(base[w],t,sizeof(int)*V);}
    for(int f=0;f<NT;f++){tr[f][0]=0;for(int a=1;a<4;a++)tr[f][a]=rnd()%m;}
    for(int h=0;h<NH;h++){hb[h][0]=rnd()%H;hb[h][1]=rnd()%H;}
    if(PHI){for(int w=1;w<NB;w++)for(int i=0;i<V;i++)base[w][i]=Pp(base[w-1][i]);
      for(int f=0;f<NT;f++){if(f<3*NT3){if(f%3==0)derive_tr(f);}else{int c=rnd()%m;tr[f][1]=tr[f][2]=tr[f][3]=c;}}
      derive_hb();}
    build();double T=T0;long best=cost;
    if(TABU){ // tabu search: best non-tabu move each step
      static int tabu[4][64][16]; memset(tabu,0,sizeof tabu); static int ttr[16][4][16]; memset(ttr,0,sizeof ttr);
      static int thb[8][2][8]; memset(thb,0,sizeof thb);
      for(long it=1;it<=iters&&cost>0;it++){
        long bd=1L<<40;int nb=0;int bk=-1,b1=0,b2=0,b3=0;
        for(int w=0;w<NB;w++)for(int x=0;x<V;x++)for(int y=x+1;y<V;y++){int bx=x/4,by=y/4;if(bx==by)continue;
          long c0=cost;
          blockpairs(&base[w][4*bx],w,-1,1);blockpairs(&base[w][4*by],w,-1,1);
          int t=base[w][x];base[w][x]=base[w][y];base[w][y]=t;
          blockpairs(&base[w][4*bx],w,1,1);blockpairs(&base[w][4*by],w,1,1);
          long d=cost-c0;
          blockpairs(&base[w][4*bx],w,-1,1);blockpairs(&base[w][4*by],w,-1,1);
          t=base[w][x];base[w][x]=base[w][y];base[w][y]=t;
          blockpairs(&base[w][4*bx],w,1,1);blockpairs(&base[w][4*by],w,1,1);
          int ist=(tabu[w][base[w][x]][by]>it)||(tabu[w][base[w][y]][bx]>it);
          if(ist && c0+d>=best)continue;
          if(d<bd){bd=d;nb=1;bk=0;b1=w;b2=x;b3=y;}else if(d==bd && rnd()%(++nb)==0){bk=0;b1=w;b2=x;b3=y;}}
        for(int f=0;f<NT;f++)for(int a=1;a<4;a++)for(int v=0;v<m;v++){if(v==tr[f][a])continue;
          long c0=cost;int old=tr[f][a];trweek(f,-1);tr[f][a]=v;trweek(f,1);long d=cost-c0;trweek(f,-1);tr[f][a]=old;trweek(f,1);
          if(ttr[f][a][v]>it && c0+d>=best)continue;
          if(d<bd){bd=d;nb=1;bk=1;b1=f;b2=a;b3=v;}else if(d==bd && rnd()%(++nb)==0){bk=1;b1=f;b2=a;b3=v;}}
        for(int h=0;h<NH;h++)for(int sd=0;sd<2;sd++)for(int v=0;v<H;v++){if(v==hb[h][sd])continue;
          long c0=cost;int old=hb[h][sd];halfweek(h,-1);hb[h][sd]=v;halfweek(h,1);long d=cost-c0;halfweek(h,-1);hb[h][sd]=old;halfweek(h,1);
          if(thb[h][sd][v]>it && c0+d>=best)continue;
          if(d<bd){bd=d;nb=1;bk=2;b1=h;b2=sd;b3=v;}else if(d==bd && rnd()%(++nb)==0){bk=2;b1=h;b2=sd;b3=v;}}
        int ten=TEN+rnd()%(TEN/2+1);
        if(bk==0){int w=b1,x=b2,y=b3,bx=x/4,by=y/4;
          tabu[w][base[w][x]][bx]=it+ten;tabu[w][base[w][y]][by]=it+ten;
          blockpairs(&base[w][4*bx],w,-1,1);blockpairs(&base[w][4*by],w,-1,1);
          int t=base[w][x];base[w][x]=base[w][y];base[w][y]=t;
          blockpairs(&base[w][4*bx],w,1,1);blockpairs(&base[w][4*by],w,1,1);}
        else if(bk==1){ttr[b1][b2][tr[b1][b2]]=it+ten;trweek(b1,-1);tr[b1][b2]=b3;trweek(b1,1);}
        else if(bk==2){thb[b1][b2][hb[b1][b2]]=it+ten;halfweek(b1,-1);hb[b1][b2]=b3;halfweek(b1,1);}
        if(cost<best){best=cost;}
        if((it%20000)==0)fprintf(stderr,"  it %ld cost %ld best %ld\n",it,cost,best);
      }
    } else
    for(long it=0;it<iters&&cost>0;it++){
      if((it&4095)==0)T=T0*pow(TF/T0,(double)it/iters);
      long c0=cost;unsigned long long rr=rnd()%64;
      if(PHI){
        if(rr<2 && NT){int f=rnd()%NT;if(f<3*NT3)f=f/3*3;int sv[4];memcpy(sv,tr[f],16);trgroup(f,-1);
          if(f<3*NT3){tr[f][1+rnd()%3]=rnd()%m;derive_tr(f);}else{int c=rnd()%m;tr[f][1]=tr[f][2]=tr[f][3]=c;}
          trgroup(f,1);
          if(!(cost<=c0||urand()<exp(-(cost-c0)/T))){trgroup(f,-1);memcpy(tr[f],sv,16);derive_tr(f);trgroup(f,1);}}
        else if(rr<3 && NH){int sd=rnd()%2,old=hb[0][sd];for(int h=0;h<NH;h++)halfweek(h,-1);hb[0][sd]=rnd()%H;derive_hb();for(int h=0;h<NH;h++)halfweek(h,1);
          if(!(cost<=c0||urand()<exp(-(cost-c0)/T))){for(int h=0;h<NH;h++)halfweek(h,-1);hb[0][sd]=old;derive_hb();for(int h=0;h<NH;h++)halfweek(h,1);}}
        else{int x=rnd()%V,y=rnd()%V;if(x/4==y/4)continue;for(int w=0;w<NB;w++)doswap(w,x,y);
          if(!(cost<=c0||urand()<exp(-(cost-c0)/T)))for(int w=0;w<NB;w++)doswap(w,x,y);}
      } else
      if(rr<2 && NT){int f=rnd()%NT,a=1+rnd()%3,old=tr[f][a];trweek(f,-1);tr[f][a]=rnd()%m;trweek(f,1);
        if(!(cost<=c0||urand()<exp(-(cost-c0)/T))){trweek(f,-1);tr[f][a]=old;trweek(f,1);}}
      else if(rr<3 && NH){int h=rnd()%NH,sd=rnd()%2,old=hb[h][sd];halfweek(h,-1);hb[h][sd]=rnd()%H;halfweek(h,1);
        if(!(cost<=c0||urand()<exp(-(cost-c0)/T))){halfweek(h,-1);hb[h][sd]=old;halfweek(h,1);}}
      else{int w=rnd()%NB,x=rnd()%V,y=rnd()%V;int bx=x/4,by=y/4;if(bx==by)continue;
        blockpairs(&base[w][4*bx],w,-1,1);blockpairs(&base[w][4*by],w,-1,1);
        int t=base[w][x];base[w][x]=base[w][y];base[w][y]=t;
        blockpairs(&base[w][4*bx],w,1,1);blockpairs(&base[w][4*by],w,1,1);
        if(!(cost<=c0||urand()<exp(-(cost-c0)/T))){
          blockpairs(&base[w][4*bx],w,-1,1);blockpairs(&base[w][4*by],w,-1,1);
          t=base[w][x];base[w][x]=base[w][y];base[w][y]=t;
          blockpairs(&base[w][4*bx],w,1,1);blockpairs(&base[w][4*by],w,1,1);}}
      if(cost<best)best=cost;
    }
    if(cost>0 && cost<=DEEP){long cb=cost;genmoves();deep();fprintf(stderr,"  deep %ld -> %ld\n",cb,cost);}
    fprintf(stderr,"att %d cost %ld (best %ld)\n",att,cost,best);
    if(cost)continue;
    if(getenv("DUMP")){printf("CAND BASE");for(int w=0;w<NB;w++){printf(" |");for(int i=0;i<V;i++)printf(" %d",base[w][i]);}
      printf(" TR");for(int f=0;f<NT;f++)printf(" %d,%d,%d,%d",tr[f][0],tr[f][1],tr[f][2],tr[f][3]);
      printf(" HALF");for(int h=0;h<NH;h++)printf(" %d,%d",hb[h][0],hb[h][1]);printf("\n");fflush(stdout);
      if(atoi(getenv("DUMP"))==2)continue;}
    int lb=1<<30;
    int ACC=getenv("ACCEPT")?atoi(getenv("ACCEPT")):0;
    for(int tries=0;tries<LTRY;tries++){int lcst=lanes(LIT);if(lcst<lb)lb=lcst;if(lcst<=ACC)break;}
    fprintf(stderr,"  design found; best lane cost %d\n",lb);
    if(lb>(getenv("ACCEPT")?atoi(getenv("ACCEPT")):0))continue;
    fprintf(stderr,"LANECOST %d\n",lb);
    // output weeks
    for(int w=0;w<NB;w++)for(int k=0;k<m;k++){int out[16][4];
      for(int b=0;b<m;b++){int L=(pi[w][b]+k)%m;for(int x=0;x<4;x++){int p=base[w][4*b+x];out[L][x]=m*(p/m)+(p%m+k)%m;}}
      for(int L=0;L<m;L++)for(int x=0;x<4;x++)printf("%d ",out[L][x]);printf("\n");}
    for(int h=0;h<NH;h++){int out[16][4];const int*P=PAIRING[h%3];
      for(int side=0;side<2;side++){int x=P[2*side],y=P[2*side+1],b=hb[h][side];
        for(int t=0;t<H;t++){int L=hl[h][side*H+t];out[L][0]=m*x+t;out[L][1]=m*x+t+H;out[L][2]=m*y+(b+t)%m;out[L][3]=m*y+(b+t+H)%m;}}
      for(int L=0;L<m;L++)for(int x=0;x<4;x++)printf("%d ",out[L][x]);printf("\n");}
    for(int f=0;f<NT;f++){int out[16][4];for(int k=0;k<m;k++){int L=(rf[f]+k)%m;for(int a=0;a<4;a++)out[L][a]=m*a+(tr[f][a]+k)%m;}
      for(int L=0;L<m;L++)for(int x=0;x<4;x++)printf("%d ",out[L][x]);printf("\n");}
    printf("BASE");for(int w=0;w<NB;w++){printf(" |");for(int i=0;i<V;i++)printf(" %d",base[w][i]);}
    printf("\nTR");for(int f=0;f<NT;f++)printf(" %d,%d,%d,%d",tr[f][0],tr[f][1],tr[f][2],tr[f][3]);
    printf("\nHALF");for(int h=0;h<NH;h++)printf(" %d,%d",hb[h][0],hb[h][1]);printf("\n");
    return 0;
  }
  return 1;
}
