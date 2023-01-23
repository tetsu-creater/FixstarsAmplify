# タクシーマッチング問題

import numpy as np
from amplify import gen_symbols, BinaryPoly, sum_poly, Solver, decode_solution
from amplify.constraint import equal_to
from amplify.client import FixstarsClient
import os


# 顧客とタクシーの座標をランダムに生成し、顧客とタクシーの距離を計算
def gen_random_locations(N_customers: int, N_taxies: int):

    # 顧客の座標。（0,0）から（1,1）までの範囲。顧客の人数分
    loc_customers = np.random.uniform(size=(N_customers, 2))

    # タクシーの座標（0,0）から（1,1）までの範囲。タクシーの台数分
    loc_taxies = np.random.uniform(size=(N_taxies, 2))

    # 顧客とタクシーの距離を行列形式で計算
    all_diffs = np.expand_dims(loc_customers, axis=1) - np.expand_dims(loc_taxies, axis=0)
    distances = np.sqrt(np.sum(all_diffs ** 2, axis=-1))

    return loc_customers, loc_taxies, distances


#顧客数(タクシー数でもある)
N = 5

Lc, Lt, d = gen_random_locations(N_customers=N, N_taxies=N)

# バイナリ変数作成
q = gen_symbols(BinaryPoly, N, N)

# 目的関数作成
cost = BinaryPoly()
for i in range(N):
    for j in range(N):
        cost += d[i][j] * q[i][j]

# 制約条件①（1人の顧客に必ず1台のタクシーが割り当たる）
customer_has_one_taxi = sum([equal_to(sum_poly(N, lambda j: q[i][j]), 1) for i in range(N)])

# 制約条件②（1台のタクシーに必ず1人の顧客が割り当たる）
taxi_has_one_customer = sum([equal_to(sum_poly(N, lambda i: q[i][j]), 1) for j in range(N)])

# 制約条件を足し合わせる
constraints = customer_has_one_taxi + taxi_has_one_customer

weight = np.amax(d) #重み（強さ）をdの最大値に設定
model = cost + weight * constraints

client = FixstarsClient()
client.token = os.environ["FIXSTARS_AMPLIFY_TOKEN"]
client.parameters.timeout = 1000

solver = Solver(client)
result = solver.solve(model)


# decode_solutionsを使ってみる
solution = np.array(decode_solution(q, result[0].values))
print(solution)

customer_taxi_list = {}
# 最後は辞書型で出力しよう
for r in result:

    for i in range(25):
        if r.values[i] == 1:
            customer_index = i // 5
            taxi_index = i % 5

            customer_taxi_list["顧客" + str(customer_index+1)] = "タクシー" + str(taxi_index+1)

print(customer_taxi_list)