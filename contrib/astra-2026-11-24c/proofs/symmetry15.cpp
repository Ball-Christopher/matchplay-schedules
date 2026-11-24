// Exhaust the lane-word sets invariant under one representative of a cycle type.
// Build with g++ -O3 -std=c++17. Inputs are prime order, week cycles, lane cycles.
#include <algorithm>
#include <array>
#include <bitset>
#include <iostream>
#include <set>
#include <vector>
using Word = std::array<int, 6>;
using Set = std::bitset<1800>;
using Orbit = std::vector<Word>;
std::vector<Orbit> orbits;
std::vector<Set> compatible;
std::vector<int> selected;
int visits[6][5]{};
long long nodes = 0;

bool clash(const Word& first, const Word& second) {
    int matches = 0;
    for (int week = 0; week < 6; ++week)
        matches += first[week] == second[week];
    return matches >= 2;
}

bool search(Set candidates, int remaining) {
    ++nodes;
    if (remaining == 0) return true;
    int capacity = 0;
    for (auto j = candidates._Find_first(); j < candidates.size(); j = candidates._Find_next(j))
        capacity += orbits[j].size();
    for (auto i = candidates._Find_first(); i < candidates.size() && capacity >= remaining;
         i = candidates._Find_next(i)) {
        const int size = orbits[i].size();
        candidates.reset(i);
        capacity -= size;
        if (size > remaining) continue;
        bool valid = true;
        for (const Word& word : orbits[i])
            for (int week = 0; week < 6; ++week)
                if (++visits[week][word[week]] > 3) valid = false;
        if (valid) {
            selected.push_back(i);
            if (search(candidates & compatible[i], remaining - size)) return true;
            selected.pop_back();
        }
        for (const Word& word : orbits[i])
            for (int week = 0; week < 6; ++week)
                --visits[week][word[week]];
    }
    return false;
}

int main(int argc, char** argv) {
    if (argc != 4) return 2;
    const int prime = std::stoi(argv[1]);
    const int weekCycles = std::stoi(argv[2]);
    const int laneCycles = std::stoi(argv[3]);
    std::set<Word> words;
    for (int twice = 0; twice < 5; ++twice) {
        Word word = {0, 1, 2, 3, 4, twice};
        std::sort(word.begin(), word.end());
        do { words.insert(word); } while (std::next_permutation(word.begin(), word.end()));
    }
    if (words.size() != 1800) return 2;
    const auto rotate = [prime](int x, int cycles) {
        return x >= cycles * prime ? x : prime * (x / prime) + (x + 1) % prime;
    };
    while (!words.empty()) {
        const Word start = *words.begin();
        Word word = start;
        Orbit orbit;
        bool valid = true;
        do {
            for (const auto& other : orbit)
                if (clash(word, other)) valid = false;
            words.erase(word);
            orbit.push_back(word);
            Word next;
            for (int i = 0; i < 6; ++i)
                next[i] = rotate(word[rotate(i, weekCycles)], laneCycles);
            word = next;
        } while (word != start);
        if (valid) orbits.push_back(orbit);
    }
    std::stable_sort(orbits.begin(), orbits.end(),
                     [](const Orbit& x, const Orbit& y) { return x.size() < y.size(); });
    compatible.resize(orbits.size());
    Set candidates;
    int fixed = 0;
    for (size_t i = 0; i < orbits.size(); ++i) {
        candidates.set(i);
        fixed += orbits[i].size() == 1;
        for (size_t j = 0; j < i; ++j) {
            // Simultaneous rotation preserves agreements. One representative
            // against the whole other orbit tests all pairs of words.
            bool valid = true;
            for (const Word& word : orbits[j])
                if (clash(word, orbits[i][0])) valid = false;
            if (valid) compatible[j].set(i);
        }
    }
    bool found = search(candidates, 15);
    std::cout << prime << " " << weekCycles << " " << laneCycles << " "
              << fixed << " " << orbits.size()-fixed << " " << nodes << " " << found << "\n";
    if (found)
        for (int i : selected)
            for (const auto& word : orbits[i]) {
                for (int symbol : word) std::cout << symbol;
                std::cout << "\n";
            }
}
