# 画像のノイズリダクション

# RuntimeErrorが出るが、jupyterではちゃんと動いた

import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from amplify import IsingPoly, gen_symbols, Solver, sum_poly
from amplify.client import FixstarsClient

# 元画像のイジング配列を作成
img = Image.open("sample.jpg")
x = np.where(np.array(img) >= 128, 1, -1)
plt.imshow(x, cmap="gray")

# 画像にノイズを追加する関数
def get_noisy_img_array(img_array):
    # 2次元配列を1次元に変換して扱いやすくする
    img_shape = img_array.shape
    flattened_img = img_array.flatten()

    # 最大値と最小値を入れ替える関数を定義
    min_v = min(flattened_img)
    max_v = max(flattened_img)

    def invert_value(v):
        return min_v + max_v - v

    # ノイズの割合
    ratio = 0.02

    # ノイズをのせる画素をランダムに選択して反転
    for idx in np.random.choice(len(flattened_img), int(ratio * len(flattened_img))):
        flattened_img[idx] = invert_value(flattened_img[idx])

    # 元の配列の形に戻す
    return flattened_img.reshape(*img_shape)

# ノイズ画像を作成
y = get_noisy_img_array(x)
plt.imshow(y, cmap="gray")

# イジング変数配列作成（2次元）
h,w = y.shape
s = gen_symbols(IsingPoly, h, w)

#目的関数作成
eta = 0.333

# 真面目に書くと
'''
f1 = IsingPoly()
for i in range(h):
    for j in range(w):
        f1 += y[i][j] * s[i][j]

f1 = -1 * f1

f2 = IsingPoly()
for j in range(h):
    for j in range(w-1):
        f2 += s[i][j] * s[i][j+1]
for j in range(w):
    for i in range(h-1):
        f2 += s[i][j] * s[i+1][j]

f2 = -1 * f2
'''

#sum_polyを使うパターン
f1 = -1 * sum_poly(h, lambda i: sum_poly(w, lambda j: y[i][j]*s[i][j]))

f2 = -1 * (sum_poly(h, lambda i: sum_poly(w-1, lambda j: s[i][j]*s[i][j+1])) + sum_poly(w, lambda j: sum_poly(h-1, lambda i: s[i][j]*s[i+1][j])))

f = f1 + eta * f2

# イジングマシンのパラメタ設定
client = FixstarsClient()
client.token = os.environ["FIXSTARS_AMPLIFY_TOKEN"]
client.parameters.timeout = 10000

#実行
solver = Solver(client)
result = solver.solve(f)


for r in result:
    print(r.energy)
    print(r.values)