# ちょっと応用（ナップザック問題）

from amplify import BinaryPoly, gen_symbols, Solver
from amplify.constraint import less_equal
from amplify.client import FixstarsClient
import os

volumes = [3, 4, 6, 1, 5] # 体積
values = [6, 7, 8, 1, 4] # 価値

# 5つのバイナリ変数の作成
q = gen_symbols(BinaryPoly, 5)

f = BinaryPoly() #価値用
g = BinaryPoly() #体積用

for i in range(len(volumes)):
    f += q[i] * values[i]
    g += q[i] * volumes[i] 

f *= -1 #最小化問題だから-1倍する

volume_constrain = less_equal(g, 12)  # f<=12 を表す制約条件オブジェクトを作成

model = volume_constrain + f  # 目的関数と制約条件をドッキング
client = FixstarsClient()
client.token = os.environ["FIXSTARS_AMPLIFY_TOKEN"]
client.parameters.timeout = 1000

solver = Solver(client)
result = solver.solve(model)

for r in result:
    print(r.energy)
    print(r.values)