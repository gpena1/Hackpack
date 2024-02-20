/**
 * Author: Siyong Huang, Aakash Gokhale
 * License: CC0
 * Source: USACO
 * Description: Efficiently compute the sum of all the subsets of an array.
 * Time: O(n * 2^n)
 * Status: not tested 
 */
#pragma once

int n = 20;
vector<int> a(1 << n);

// keeps track of the sum over subsets
// with a certain amount of matching bits in the prefix
vector<vector<int>> dp(1 << n, vector<int>(n));

vector<int> sos(1 << n);
for (int mask = 0; mask < (1 << n); mask++) {
	dp[mask][-1] = a[mask];
	for (int x = 0; x < n; x++) {
		dp[mask][x] = dp[mask][x - 1];
		if (mask & (1 << x)) { dp[mask][x] += dp[mask - (1 << x)][x - 1]; }
	}
	sos[mask] = dp[mask][n - 1];
}
