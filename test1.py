#初めてのFixstars Amplify
from amplify import BinaryPoly, SymbolGenerator, BinaryQuadraticModel, Solver
from amplify.client import FixstarsClient
import os


gen = SymbolGenerator(BinaryPoly)  # 変数変数ジェネレータを定義
q = gen.array(2)  # 長さ2の Binary 配列を生成

f = 1 - q[0] * q[1]

# 2.論理型への変換
model = BinaryQuadraticModel(f)

# 3.イジングマシンのパラメタ設定
client = FixstarsClient()
client.token = os.environ["FIXSTARS_AMPLIFY_TOKEN"]
client.parameters.timeout = 1000    # タイムアウト1秒

# ここまでが準備

# 4. 実行
solver = Solver(client)
result = solver.solve(model)
for solution in result:
    print(f"energy = {solution.energy}\nvalues = {solution.values}")