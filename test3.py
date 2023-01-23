# アルゴリズムとデータ構造 後半レポート 基礎問題11-1（iii）

from amplify import BinaryPoly, gen_symbols, Solver
from amplify.constraint import less_equal
from amplify.client import FixstarsClient
import os

volumes = [26, 32, 30, 16, 40, 8, 16, 9] # 重量
values = [11, 9, 11, 11, 5, 15, 9, 2] # 価値

# 8つのバイナリ変数の作成
q = gen_symbols(BinaryPoly, 8)

f = BinaryPoly() #価値用
g = BinaryPoly() #体積用

for i in range(len(volumes)):
    f += q[i] * values[i]
    g += q[i] * volumes[i] 

f *= -1 #最小化問題だから-1倍する

volume_constrain = less_equal(g, 65)  # f<=12 を表す制約条件オブジェクトを作成

model = volume_constrain + f  # 目的関数と制約条件をドッキング
client = FixstarsClient()
client.token = os.environ["FIXSTARS_AMPLIFY_TOKEN"]
client.parameters.timeout = 1000

solver = Solver(client)
result = solver.solve(model)

for r in result:
    print(r.energy)
    print(r.values)