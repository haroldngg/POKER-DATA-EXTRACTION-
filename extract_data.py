import pickle

with open("data_river", "rb") as temp: # fichiers : data_preflop, data_flop, data_turn, data_river
    datas = pickle.load(temp)

print(len(datas))