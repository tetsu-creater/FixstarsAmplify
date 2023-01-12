from amplify import IsingPoly, SymbolGenerator, Solver, decode_solution
from amplify.client import FixstarsClient
import os

A = [2, 10, 3, 8, 5, 7, 9, 5, 3, 2]
n = len(A)

gen = SymbolGenerator(IsingPoly)  # 変数変数ジェネレータを定義
s = gen.array(n)  # 長さnの Ising変数の配列を生成

# 目的関数の構築
f = IsingPoly()

for i in range(n):
    f += A[i] * s[i]

f = f**2

client = FixstarsClient()
client.token = os.environ["FIXSTARS_AMPLIFY_TOKEN"]
client.parameters.timeout = 1000
#client.parameters.outputs.duplicate = True  # 同じエネルギー値の解を列挙するオプション（解が複数個あるため）

solver = Solver(client)
result = solver.solve(f)

# 結果の確認
energy = result[0].energy
values = result[0].values
print("f=",energy) # エネルギー
print(values) # イジング変数の配列


solution = decode_solution(s, values)
print(solution)

# sが−1ならA0に、sが1ならA1に振り分ける
A0, A1 = [], []

for i in range(n):
    if solution[i] == -1:
        A0.append(A[i])
    else :
        A1.append(A[i])

print(A0)
print(A1)