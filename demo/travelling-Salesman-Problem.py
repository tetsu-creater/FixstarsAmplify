# 巡回セールスマン問題

import numpy as np
from amplify import gen_symbols, BinaryPoly, sum_poly, Solver, decode_solution
from amplify.constraint import equal_to
from amplify.client import FixstarsClient
import os

def gen_random_tsp(ncity:int): #ncityは都市の個数
    # 座標
    locations = np.random.uniform(size=(ncity, 2)) # ncity×2の行列を作成

    # 距離行列
    all_diffs = np.expand_dims(locations, axis=1) - np.expand_dims(locations, axis=0)
    distances = np.sqrt(np.sum(all_diffs ** 2, axis=-1))

    return locations, distances


ncity = 6
locations, distances = gen_random_tsp(ncity)

# バイナリ変数作成
q = gen_symbols(BinaryPoly, ncity, ncity)

# 目的関数作成
cost = BinaryPoly()
for n in range(ncity-1):
    for i in range(ncity-1):
        for j in range(ncity-1):
            cost += distances[i][j] * q[n][i] * q[n+1][j]


# 制約条件①（全ての都市を通る）
through_all_city = sum([equal_to(sum_poly(ncity, lambda n: q[n][i]), 1) for i in range(ncity)])

# 制約条件②（同時に1つの都市を通る）
through_onlyone_city = sum([equal_to(sum_poly(ncity, lambda i: q[n][i]), 1) for n in range(ncity)])

# 制約条件を足し合わせる
constraints = through_all_city + through_onlyone_city


weight = np.amax(distances) #重み（強さ）をdistancesの最大値に設定
model = cost + weight * constraints

client = FixstarsClient()
client.token = os.environ["FIXSTARS_AMPLIFY_TOKEN"]
client.parameters.timeout = 1000

solver = Solver(client)
result = solver.solve(model)

# decode_solutionsを使ってみる
solution = np.array(decode_solution(q, result[0].values))
print(solution)