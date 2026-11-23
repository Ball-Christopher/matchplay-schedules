// Randomised exact cover (dancing links, MRV) with restarts.  Input from mkdlx.py.
// usage: dlx instance seed nodes_per_restart s0 s1 s2 s3 > solution (week ids and colours)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static uint64_t s[2];
static inline uint64_t rnd(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
int NI,NO,NWK; int *L,*R,*U,*D,*C,*S,*ROW; int *ow,*oc; int nn;
int size[4],cnt[4]; long nodes,limit; int sol[400],ns; int bestdepth;
static void cover(int c){L[R[c]]=L[c];R[L[c]]=R[c];for(int i=D[c];i!=c;i=D[i])for(int j=R[i];j!=i;j=R[j]){U[D[j]]=U[j];D[U[j]]=D[j];S[C[j]]--;}}
static void uncover(int c){for(int i=U[c];i!=c;i=U[i])for(int j=L[i];j!=i;j=L[j]){S[C[j]]++;U[D[j]]=j;D[U[j]]=j;}L[R[c]]=c;R[L[c]]=c;}
static int search(void){
  if(R[0]==0)return 1;
  if(++nodes>limit)return -1;
  int c=0,best=1<<30;for(int j=R[0];j!=0;j=R[j])if(S[j]<best){best=S[j];c=j;if(best<=1)break;}
  if(best==0)return 0;
  cover(c);
  for(int r=D[c];r!=c;r=D[r]){
    int o=ROW[r];int col=oc[o];
    if(ow[o]>=0){if(cnt[col]>=size[col])continue;cnt[col]++;int t=cnt[0]+cnt[1]+cnt[2]+cnt[3];if(t>bestdepth)bestdepth=t;}
    sol[ns++]=o;for(int j=R[r];j!=r;j=R[j])cover(C[j]);
    int res=search();
    for(int j=L[r];j!=r;j=L[j])uncover(C[j]);ns--;if(ow[o]>=0)cnt[col]--;
    if(res){if(res==1){sol[ns++]=o;}uncover(c);return res;}
  }
  uncover(c);return 0;
}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"r");long seed=atol(argv[2]);limit=atol(argv[3]);for(int i=0;i<4;i++)size[i]=atoi(argv[4+i]);
  fscanf(f,"%d %d %d",&NI,&NO,&NWK);
  int **oi=malloc(NO*sizeof(int*));int *on=malloc(NO*sizeof(int));ow=malloc(NO*sizeof(int));oc=malloc(NO*sizeof(int));long tot=0;
  char *line=malloc(1<<16);fgets(line,1<<16,f);
  for(int o=0;o<NO;o++){fgets(line,1<<16,f);char*p=line;int w,c,n=0,x,k;sscanf(p,"%d %d%n",&w,&c,&k);p+=k;ow[o]=w;oc[o]=c;int tmp[64];while(sscanf(p,"%d%n",&x,&k)==1){tmp[n++]=x;p+=k;}oi[o]=malloc(n*sizeof(int));memcpy(oi[o],tmp,n*sizeof(int));on[o]=n;tot+=n;}
  int M=NI+1+tot;L=malloc(M*sizeof(int));R=malloc(M*sizeof(int));U=malloc(M*sizeof(int));D=malloc(M*sizeof(int));C=malloc(M*sizeof(int));ROW=malloc(M*sizeof(int));S=malloc((NI+1)*sizeof(int));
  int *perm=malloc(NO*sizeof(int));
  for(int rs=0;;rs++){
    s[0]=(seed*1000003+rs)*0x9E3779B97F4A7C15ULL+1;s[1]=(seed+rs*7919)^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rnd();
    for(int i=0;i<=NI;i++){L[i]=i-1;R[i]=i+1;U[i]=D[i]=i;C[i]=i;S[i]=0;}L[0]=NI;R[NI]=0;
    for(int i=0;i<NO;i++)perm[i]=i;for(int i=NO-1;i>0;i--){int j=rnd()%(i+1);int t=perm[i];perm[i]=perm[j];perm[j]=t;}
    nn=NI+1;
    for(int q=0;q<NO;q++){int o=perm[q];int first=nn;for(int t=0;t<on[o];t++){int c=oi[o][t]+1;int x=nn++;C[x]=c;ROW[x]=o;U[x]=U[c];D[x]=c;D[U[c]]=x;U[c]=x;S[c]++;L[x]=x-1;R[x]=x+1;}L[first]=nn-1;R[nn-1]=first;}
    nodes=0;ns=0;bestdepth=0;memset(cnt,0,sizeof cnt);
    int res=search();
    if(res==1){printf("FOUND rs %d nodes %ld\n",rs,nodes);for(int i=0;i<ns;i++)if(ow[sol[i]]>=0)printf("W %d %d\n",ow[sol[i]],oc[sol[i]]);fflush(stdout);return 0;}
    if(res==0){printf("NO SOLUTION (exhaustive) rs %d nodes %ld\n",rs,nodes);fflush(stdout);return 0;}
    fprintf(stderr,"rs %d maxweeks %d\n",rs,bestdepth);
  }
}
