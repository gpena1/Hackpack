
/**
 * Author: Benjamin Qi
 * Date: 2009-10-28
 * License: CC0
 * Source: USACO
 * Description: Perform queries on subtrees
 * Time: O(E + V)
 * Status: not tested
 */
#include <iostream>
#include <vector>

using std::vector;

// The graph represented as an adjacency list (0-indexed)
vector<vector<int>> neighbors{{1, 2}, {0}, {0, 3, 4}, {2}, {2}};
vector<int> start(neighbors.size());
vector<int> end(neighbors.size());
int timer = 0;

void euler_tour(int at, int prev) {
	start[at] = timer++;
	for (int n : neighbors[at]) {
		if (n != prev) { euler_tour(n, at); }
	}
	end[at] = timer;
}
