#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <random>
#include <unordered_map>
#include <vector>
using namespace std;
using Key=uint64_t;
using Choices=array<int,11>;
struct Opt{Key code{};int mask{};array<int,3> labels{};};
struct Half{Key code;Choices choice;};
int period[11],ids[11][3],grp[11][8][3],n;
Key agg[11][8],con[11][8][3];mt19937 rng;
struct Fixed{Choices g;int shortPlayer;};
vector<Fixed> fixedOptions;
void fixed(int w,Choices &g,Key tally){
 if(w==11){int sp=-1;for(int p=0;p<8;p++){int v=(tally>>(5*p))&31;if(v<2||v>3)return;if(v==2){if(sp!=-1)return;sp=p;}}if(sp>=0)fixedOptions.push_back({g,sp});return;}
 for(int j=0;j<(period[w]==1?2:8);j++){Key next=tally+agg[w][j];bool ok=true;for(int p=0;p<8;p++)if(((next>>(5*p))&31)>3)ok=false;if(ok){g[w]=j;fixed(w+1,g,next);}}
}
vector<Half> sums(const array<vector<Opt>,11>&opts,const vector<int>& subset){
 vector<Half> rows(1);rows[0].code=0;rows[0].choice.fill(0);
 for(int w:subset){vector<Half> next;next.reserve(rows.size()*opts[w].size());
   for(auto &r:rows)for(int j=0;j<(int)opts[w].size();j++){Half v=r;v.code+=opts[w][j].code;v.choice[w]=j;next.push_back(v);}rows.swap(next);}
 return rows;
}
void split(const array<vector<Opt>,11>&opts,vector<int>&a,vector<int>&b){
 vector<int> order;for(int w=0;w<11;w++)order.push_back(w);
 sort(order.begin(),order.end(),[&](int x,int y){return opts[x].size()>opts[y].size();});
 int L=1,R=1;for(int w:order)if(L<R){a.push_back(w);L*=opts[w].size();}else{b.push_back(w);R*=opts[w].size();}
}
bool phase(const Choices&masks,int shortMask,int answer[11][8]){
 array<vector<Opt>,11> opt;
 for(int w=0;w<11;w++){vector<int> groups;for(int j=0;j<8;j++)if(masks[w]>>j&1)groups.push_back(j);
  if(groups.size()==1){int j=groups[0];for(int l=0;l<(w==0?1:3);l++){Opt o;o.code=con[w][j][l];o.labels[0]=l;opt[w].push_back(o);}}
  else {array<int,3> labels={0,1,2};do{Opt o;o.labels=labels;for(int z=0;z<3;z++)o.code+=con[w][groups[z]][labels[z]];opt[w].push_back(o);}while(next_permutation(labels.begin(),labels.end()));}}
 vector<int>a,b;split(opt,a,b);auto L=sums(opt,a),R=sums(opt,b);
 unordered_map<Key,int> first;first.reserve(2*L.size());for(int i=0;i<(int)L.size();i++)first.emplace(L[i].code,i);
 vector<Key> targets{0};
 for(int p=0;p<8;p++){vector<Key> t;for(Key x:targets)for(int k=0;k<(shortMask>>p&1?3:1);k++){
  int a=3,b=3;if(shortMask>>p&1){a-=(k==0);b-=(k==1);}t.push_back(x+(Key(a+16*b)<<(8*p)));}targets.swap(t);}
 for(auto &r:R)for(Key target:targets){auto it=first.find(target-r.code);if(it==first.end())continue;
  auto pick=L[it->second].choice;for(int w:b)pick[w]=r.choice[w];
  for(int w=0;w<11;w++){int z=0;for(int j=0;j<8;j++)if(masks[w]>>j&1)answer[w][j]=opt[w][pick[w]].labels[z++];}return true;}
 return false;
}
bool attempt(Fixed A,Fixed B,long long &tested){
 array<vector<Opt>,11> opt;Choices rem;
 for(int w=0;w<11;w++){
  rem[w]=period[w]==1?((1<<2)|(1<<5)):(255^(1<<A.g[w])^(1<<B.g[w]));
  for(int m=rem[w];m;m=(m-1)&rem[w])if(__builtin_popcount((unsigned)m)==(period[w]==1?1:3)){
    Opt o;o.mask=m;for(int j=0;j<8;j++)if(m>>j&1)o.code+=agg[w][j];opt[w].push_back(o);}
 }
 vector<int>a,b;split(opt,a,b);auto L=sums(opt,a),R=sums(opt,b);shuffle(R.begin(),R.end(),rng);shuffle(L.begin(),L.end(),rng);
 unordered_multimap<Key,int> lookup;lookup.reserve(2*L.size());for(int i=0;i<(int)L.size();i++)lookup.emplace(L[i].code,i);
 int eligible=255^(1<<A.shortPlayer)^(1<<B.shortPlayer);
 vector<pair<Key,int>> targets;
 for(int m=eligible;m;m=(m-1)&eligible)if(__builtin_popcount((unsigned)m)==3){Key target=0;for(int p=0;p<8;p++)target+=Key(9-((m>>p)&1))<<(5*p);targets.emplace_back(target,m);}
 shuffle(targets.begin(),targets.end(),rng);int limit=0;
 for(auto&r:R)for(auto [target,m]:targets){
  auto matches=lookup.equal_range(target-r.code);
  for(auto it=matches.first;it!=matches.second;++it){if(++limit>600)return false;++tested;
   auto pick=L[it->second].choice;for(int w:b)pick[w]=r.choice[w];Choices aMask,bMask;
   for(int w=0;w<11;w++){aMask[w]=opt[w][pick[w]].mask;bMask[w]=rem[w]^aMask[w];}
   int la[11][8]{},lb[11][8]{};
   if(!phase(aMask,m,la)||!phase(bMask,eligible^m,lb))continue;
   int rows[23][8][3]{};
   for(int w=0;w<11;w++){int label[8]{};label[A.g[w]]=0;label[B.g[w]]=1;
    for(int j=0;j<8;j++)if(rem[w]>>j&1){int base=(aMask[w]>>j&1)?2:5,l=(base==2?la[w][j]:lb[w][j]);label[j]=base+l;
      if(period[w]==1)for(int t=1;t<3;t++)label[j+t]=base+(l+t)%3;}
    for(int t=0;t<period[w];t++)for(int j=0;j<8;j++){int l=label[j];if(l>=2)l=2+3*((l-2)/3)+(l-2+t)%3;
     for(int z=0;z<3;z++){int p=grp[w][j][z];rows[ids[w][t]][l][z]=1+3*(p/3)+(p+t)%3;}}
   }
   cout<<0<<"\n";for(auto&w:rows){for(auto&g:w)for(int p:g)cout<<p<<" ";cout<<"\n";}return true;
  }}
 return false;
}
int main(int argc,char**argv){rng.seed(atoi(argv[1]));cin>>n;
 for(int w=0;w<n;w++){cin>>period[w];for(int t=0;t<period[w];t++)cin>>ids[w][t];for(int j=0;j<8;j++)for(int &p:grp[w][j]){
  cin>>p;
  // A fixed invariant triple contributes only one visit by the representative.
  if(period[w]!=1||j>=2||p%3==0)agg[w][j]+=Key(1)<<(5*(p/3));
  for(int l=0;l<3;l++){int actual=(l-p%3+3)%3;if(actual<2)con[w][j][l]+=Key(1)<<(8*(p/3)+4*actual);}
 }}
 Choices c;fixed(0,c,0);long long tested=0;cerr<<"fixed lanes "<<fixedOptions.size()<<endl;if(fixedOptions.empty())return 1;
 for(int k=0;k<5000;k++){auto A=fixedOptions[rng()%fixedOptions.size()],B=fixedOptions[rng()%fixedOptions.size()];if(A.shortPlayer==B.shortPlayer)continue;
 bool ok=true;for(int w=0;w<11;w++)if(A.g[w]==B.g[w])ok=false;if(ok&&attempt(A,B,tested)){cerr<<"phase boards "<<tested<<endl;return 0;}}
 cerr<<"tested "<<tested<<endl;
}
