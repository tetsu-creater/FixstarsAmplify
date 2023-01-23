#  グラフ彩色問題

import numpy as np
from amplify import gen_symbols, BinaryPoly, sum_poly, BinaryConstraint, Solver, decode_solution, BinaryQuadraticModel
from amplify.constraint import equal_to
import japanmap as jm
from japanmap import adjacent, pref_names, picture
from amplify.client import FixstarsClient
import os
import matplotlib.pyplot as plt


colors = ["red", "green", "blue", "yellow"]
num_colors = len(colors)
num_region = len(pref_names) - 1  # 都道府県数を取得（ただしpref_namesの0番目は空なので注意）

# バイナリ変数作成
q = gen_symbols(BinaryPoly, num_region, num_colors)

# 制約条件①（1領域一色）
reg_constraints = sum([equal_to(sum_poly(num_colors, lambda j: q[i][j]), 1) for i in range(num_region)])
#print(reg_constraints)

# 制約条件②（同じ色は隣接してはいけない）
adjacent_constraints = BinaryConstraint()
for i in range(1, num_region+1):
    adjacent_region_list = adjacent(i)

    for j in range(len(adjacent_region_list)):
        for r in range(num_colors):
            adjacent_constraints += equal_to(q[i-1][r] * q[adjacent_region_list[j]-1][r], 0)

del adjacent_constraints[0]

# 制約条件を足し合わせる
model = reg_constraints + adjacent_constraints

client = FixstarsClient()
client.token = os.environ["FIXSTARS_AMPLIFY_TOKEN"]
client.parameters.timeout = 1000

solver = Solver(client)
result = solver.solve(model)

# result が空の場合、制約条件を満たす解が得られなかったことを示す
if len(result) == 0:
    raise RuntimeError("Given constraint conditions are not satisfied")
        
# decode_solutionsを使ってみる
solution = np.array(decode_solution(q, result[0].values))
print(solution)

# 地図にプロットしてみる
reg_color_list = {}
for r in result:

    for i in range(188):
        if r.values[i] == 1:
            reg_index = i // 4
            color_index = i % 4

            reg_color_list[pref_names[reg_index+1]] = colors[color_index]

print(reg_color_list)
plt.imshow(picture(reg_color_list));
plt.show()