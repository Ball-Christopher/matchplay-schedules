// Exact search for a balanced 15-player, five-lane, six-week one-meeting draw.
// Each four-letter prefix contributes one entry to each of six pair projections.
#include <algorithm>
#include <array>
#include <bitset>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

using Word = std::array<int, 4>;
constexpr int injectiveCount = 120;
using Candidates = std::bitset<injectiveCount>;
struct Entry {
    Word word;
    std::array<int, 6> projections;
    int repeat;
};
std::vector<Entry> injective;
std::array<std::vector<Entry>,6> doubled;
std::array<Candidates,120> allowed;
std::array<Candidates,20> byCell;
std::array<std::vector<Candidates>,6> allowedAfterDouble;
std::vector<int> roles;
std::vector<Entry> selected;
int occupancy[4][5]{};
long long exceptionalFamilies = 0, prefixes = 0;
bool exists = false;

bool conflict(const Entry& a, const Entry& b) {
    for (int i = 0; i < 6; ++i)
        if (a.projections[i] == b.projections[i]) return true;
    return false;
}

void initialise() {
    for (int code = 0; code < 625; ++code) {
        Entry e{};
        int digits = code;
        for (int i = 3; i >= 0; --i) {
            e.word[i] = digits % 5;
            digits /= 5;
        }
        int repeated = 0, k = 0;
        for (int b = 1; b < 4; ++b)
            for (int a = 0; a < b; ++a, ++k) {
                e.projections[k] = 5*e.word[a] + e.word[b];
                if (e.word[a] == e.word[b]) {
                    ++repeated;
                    e.repeat = k;
                }
            }
        if (repeated == 0) injective.push_back(e);
        if (repeated == 1) doubled[e.repeat].push_back(e);
    }
    for (int j = 0; j < injectiveCount; ++j) {
        for (int t = 0; t < 4; ++t)
            byCell[5*t + injective[j].word[t]].set(j);
        for (int i = 0; i < injectiveCount; ++i)
            if (!conflict(injective[i], injective[j])) allowed[j].set(i);
    }
    for (int role = 0; role < 6; ++role)
        for (const auto& e : doubled[role]) {
            Candidates legal;
            for (int j = 0; j < injectiveCount; ++j)
                if (!conflict(e, injective[j])) legal.set(j);
            allowedAfterDouble[role].push_back(legal);
        }
}

// Build week five first. A repeated opponent among its proposed occupants
// immediately rules out that group. At week six every missing symbol is forced.
struct Tail {
    int usedSymbols[15]{}, fifth[15]{}, met[15]{};
    int fifthLane[5]{}, sixthLane[5]{}, permitted[15]{};
    static int size(int mask) { return __builtin_popcount(unsigned(mask)); }

    bool lastWeek(int unassigned) {
        if (!unassigned) return true;
        int best = -1, choices = 0, fewest = 6;
        for (int r = unassigned; r; r &= r-1) {
            int i = __builtin_ctz(unsigned(r)), options = permitted[i];
            for (int l = 0; l < 5; ++l)
                if (size(sixthLane[l]) == 3 ||
                    (sixthLane[l] & (met[i] | fifthLane[fifth[i]])))
                    options &= ~(1<<l);
            int n = size(options);
            if (!n) return false;
            if (n < fewest) { best = i; choices = options; fewest = n; }
        }
        for (int c = choices; c; c &= c-1) {
            int lane = __builtin_ctz(unsigned(c));
            sixthLane[lane] |= 1<<best;
            if (lastWeek(unassigned ^ (1<<best))) return true;
            sixthLane[lane] ^= 1<<best;
        }
        return false;
    }
    bool fifthWeek(int i) {
        if (i == 15) return lastWeek((1<<15)-1);
        for (int l = 0; l < 5; ++l) {
            if (size(fifthLane[l]) == 3 || (met[i] & fifthLane[l])) continue;
            int missing = 31 & ~(usedSymbols[i] | (1<<l));
            if (size(missing) > 1) continue;
            permitted[i] = missing ? missing : 31;
            fifth[i] = l;
            fifthLane[l] |= 1<<i;
            if (fifthWeek(i+1)) return true;
            fifthLane[l] ^= 1<<i;
        }
        return false;
    }
    bool run() {
        for (int i = 0; i < 15; ++i) {
            for (int t = 0; t < 4; ++t) usedSymbols[i] |= 1<<selected[i].word[t];
            for (int j = 0; j < i; ++j)
                for (int t = 0; t < 4; ++t)
                    if (selected[i].word[t] == selected[j].word[t]) {
                        met[i] |= 1<<j;
                        met[j] |= 1<<i;
                        break;
                    }
        }
        return fifthWeek(0);
    }
};

void remove(const Entry& e) {
    selected.pop_back();
    for (int t = 0; t < 4; ++t) --occupancy[t][e.word[t]];
}
Candidates add(const Entry& e, Candidates pool) {
    selected.push_back(e);
    for (int t = 0; t < 4; ++t)
        if (++occupancy[t][e.word[t]] == 3) pool &= ~byCell[5*t+e.word[t]];
    return pool;
}

void fillInjective(Candidates pool, int focus = -1) {
    if (exists) return;
    if (selected.size() == 15) {
        ++prefixes;
        Tail tail;
        exists = tail.run();
        return;
    }
    if (focus < 0) {
        int best = 121;
        // Select a lane cell with the smallest surplus of candidates.
        for (int t = 3; t >= 0; --t)
            for (int l = 4; l >= 0; --l) {
                int deficit = 3 - occupancy[t][l];
                if (!deficit) continue;
                int cell = 5*t+l, slack = int((pool & byCell[cell]).count()) - deficit;
                if (slack < 0) return;
                if (slack < best) { best = slack; focus = cell; }
            }
    }
    Candidates choices = pool & byCell[focus];
    for (auto i = choices._Find_first(); i < 120; i = choices._Find_next(i)) {
        pool.reset(i);  // force increasing choices while filling this same cell
        Candidates next = add(injective[i], pool & allowed[i]);
        fillInjective(next, occupancy[focus/5][focus%5] == 3 ? -1 : focus);
        remove(injective[i]);
    }
}

void fillDoubled(size_t at, int preceding, Candidates pool) {
    if (exists) return;
    if (at == roles.size()) {
        ++exceptionalFamilies;
        fillInjective(pool);
        return;
    }
    int role = roles[at];
    // Role zero's distinguished word was fixed before this function. It does
    // not impose an ordering on the other words of that role.
    int first = at > 1 && roles[at-1] == role ? preceding+1 : 0;
    for (int j = first; j < int(doubled[role].size()); ++j) {
        const auto& e = doubled[role][j];
        bool valid = true;
        for (int t = 0; t < 4; ++t)
            if (occupancy[t][e.word[t]] == 3) valid = false;
        for (const auto& other : selected)
            if (conflict(e, other)) { valid = false; break; }
        if (!valid) continue;
        Candidates next = add(e, pool & allowedAfterDouble[role][j]);
        fillDoubled(at+1, j, next);
        remove(e);
    }
}

int main(int argc, char** argv) {
    if (argc != 2 || std::string(argv[1]).size() != 6) return 2;
    std::string pattern(argv[1]);
    for (int r = 0; r < 6; ++r) {
        if (pattern[r] < '0' || pattern[r] > '5') return 2;
        roles.insert(roles.end(), pattern[r]-'0', r);
    }
    initialise();
    if (roles.empty()) {
        fillInjective(add(injective[0], allowed[0]));
    } else {
        if (roles[0] != 0) return 2;
        const auto& group = doubled[0];
        int j = 0;
        while (group.at(j).word != Word{0,0,1,2}) ++j;
        fillDoubled(1, -1, add(group[j], allowedAfterDouble[0][j]));
    }
    std::cout << pattern << " " << exceptionalFamilies << " " << prefixes
              << " " << exists << std::endl;
}
