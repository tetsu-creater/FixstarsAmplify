# 会議割り当て問題
import itertools
from amplify import gen_symbols, BinaryPoly, BinaryIntConstraint, Solver, sum_poly
from amplify.constraint import equal_to, penalty
from amplify.client import FixstarsClient
import os

# 会議のスケジュール
schedules = {
    "meeting1": ["10:00", "13:00"],
    "meeting2": ["10:00", "12:00"],
    "meeting3": ["10:00", "11:00"],
    "meeting4": ["11:00", "13:00"],
    "meeting5": ["11:00", "12:00"],
    "meeting6": ["11:00", "15:00"],
    "meeting7": ["12:00", "16:00"],
    "meeting8": ["12:00", "15:00"],
    "meeting9": ["13:00", "15:00"],
    "meeting10": ["13:00", "14:00"],
    "meeting11": ["14:00", "17:00"],
    "meeting12": ["15:00", "19:00"],
    "meeting13": ["15:00", "17:00"],
    "meeting14": ["15:00", "16:00"],
    "meeting15": ["16:00", "18:00"],
    "meeting16": ["16:00", "18:00"],
    "meeting17": ["17:00", "19:00"],
    "meeting18": ["17:00", "18:00"],
    "meeting19": ["18:00", "19:00"],
}

#会議室
rooms = ['会議室A', '会議室B', '会議室C', '会議室D', '会議室E', '会議室F', '会議室G', '会議室H']

# 会議の数
Nm = len(schedules)

# 会議室の数
Nr = len(rooms)

# 時刻を時間単位の数値に変換する関数
def time2num(time: str):
    h, m = map(float, time.split(":")) #時刻を:で分割している
    return h + m / 60


# 2つの会議時間に重なりがあるかをチェックする関数
def check_overlap(time_slot1, time_slot2):
    start1, end1 = map(time2num, time_slot1)
    start2, end2 = map(time2num, time_slot2)

    return start1 < end2 and start2 < end1 #重なりがあれば、Trueを返す


# 会議名のリストを取得
mtg_names = list(schedules.keys())

# 会議名とインデックスの辞書を作成
mtg_name2idx = {mtg_names[i]: i for i in range(Nm)}

# スケジュールの重なりがある会議のインデックスをタプルで格納
overlaps = []
for mtg1, mtg2 in itertools.combinations(mtg_names, 2): #combinationsは、2つのミーティングの組み合わせを全て取り出している
    if check_overlap(schedules[mtg1], schedules[mtg2]): #もし、会議の時間が重なっていたら...
        overlaps.append(tuple(sorted([mtg_name2idx[mtg1], mtg_name2idx[mtg2]]))) #重なっているミーティングのインデックスを保存


# バイナリ変数作成
q = gen_symbols(BinaryPoly, Nm, Nr)


# 制約条件①（1つの会議は必ず1つの会議室に割り当てられる必要あり）
room_constraints = BinaryIntConstraint()
for i in range(Nm):

    binary_sum = q[i][0]
    for j in range(Nr-1):
        binary_sum += q[i][j+1] #0か1が加算される

    room_constraints += equal_to(binary_sum, 1)
del room_constraints[0]

#制約条件②（会議時間が重なっているミーティングに関して、同じ会議室は利用してはいけない）
overlap_constraints = BinaryIntConstraint()
for i in range(Nr):
    for j in range(len(overlaps)):
        product = q[overlaps[j][0]][i] * q[overlaps[j][1]][i]
        overlap_constraints += equal_to(product, 0)
del overlap_constraints[0]

'''
room_constraints = sum(
    [equal_to(sum_poly(Nr, lambda r: q[i][r]), 1) for i in range(Nm)]
)

overlap_constraints = sum(
    [penalty(q[i][r] * q[j][r]) for (i, j) in overlaps for r in range(Nr)]
)
'''
# 制約条件を足し算
model = room_constraints + overlap_constraints

client = FixstarsClient()
client.token = os.environ["FIXSTARS_AMPLIFY_TOKEN"]
client.parameters.timeout = 1000

solver = Solver(client)
result = solver.solve(model)

# result が空の場合、制約条件を満たす解が得られなかったことを示す
if len(result) == 0:
    raise RuntimeError("Given constraint conditions are not satisfied")

schedules_rooms_list = {}
for r in result:
    #print(r.energy)
    #print(r.values)

    for i in range(151):
        if r.values[i] == 1:
            meeting_index = i // 8
            room_index = i % 8

            meeting_name = [k for k, v in mtg_name2idx.items() if v == meeting_index] #ミーティングインデックスから、ミーティングネームを取得

            #schedules_rooms_listに追加
            schedules_rooms_list[meeting_name[0]] = rooms[room_index]

print(schedules_rooms_list)

