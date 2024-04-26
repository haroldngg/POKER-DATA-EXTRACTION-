import pickle
import copy


columns_data = ['sequence']
data = []

chemin = r"C:\Users\augus_zcrxu\OneDrive\Bureau\PSC\extraction\dataset\Export_Holdem_Manager_2.0_12302016144830.txt"


with open(chemin, 'r') as file:
    lines = file.readlines()

def trad_carte(carte):
    ltete = ['T', 'J', 'Q', 'K', 'A']
    if carte[0] in ltete:
        value = float(10 + ltete.index(carte[0]))
    else:
        value = float(carte[0])
    
    lcol = ['h', 'd', 'c', 's']

    col = float(lcol.index(carte[1]))

    return [value, col]



compteur_partie = 0
for i, line in enumerate(lines):
    
    if line.startswith('Game ID:'):
        is_capped = '(Cap)' in line

        compteur_partie +=1
        if compteur_partie%426==0:
            print("Work in Progress : ", int(1000*compteur_partie/42688)/10, "%")
        sequence = []

        skip = False

        ### GAME ID
        game_id = int(line.split(' ')[2])
        valeur_bb = float(line.split(' ')[3].split('/')[1])
        button_seat = int(lines[i+1].split(' ')[1]) -1


        j = i+2
        joueurs = ['']*9 # noms des joueurs
        stack = [0]*9 # taille de leur stacks
        en_jeu = [False]*9 

        while lines[j].startswith('Seat'):
            line = lines[j]
            sep = line.split(' ')
            seat = int(sep[1][0]) -1
            name = sep[2]

            stack_joueur = float((sep[-1].split(')')[0])[1:])

            joueurs[seat] = name
            stack[seat] = min(stack_joueur, 30 * valeur_bb) if is_capped else stack_joueur  # poker cap to 30bb
            en_jeu[seat] = True # signifie que le joueur est en jeu

            j+=1

        joueurs = joueurs[button_seat:] + joueurs[:button_seat]
        stack = stack[button_seat:] +  stack[:button_seat]
        en_jeu = en_jeu[button_seat:] +  en_jeu[:button_seat]


        blinds = []
        while not 'has small blind' in lines[j]: #pb 'sitting out' cf game id : 718934873
            line = lines[j]
            if 'timed out' in line:
                en_jeu[joueurs.index(line.split(' ')[1])] = False
            elif 'sitting out' in line:
                en_jeu[joueurs.index(line.split(' ')[1])] = False
            else:
                print('saut dans les blindes non maitrise (avant sb), game id :', game_id)
            j+=1
        
        line = lines[j]
        sizing = float(line.split('(')[1].split(')')[0])
        player = joueurs.index(line.split(' ')[1])
        blinds.append((player, 0, sizing))
        
        j+=1

        while not 'has big blind' in lines[j]: #pb 'sitting out' cf game id : 718934873
            line = lines[j]
            if 'timed out' in line or 'sitting out' in line:
                en_jeu[joueurs.index(line.split(' ')[1])] = False
            else:
                print('saut dans les blindes non maitrise (avant sb), game id :', game_id)
            j+=1
        
        line = lines[j]
        sizing = float(line.split('(')[1].split(')')[0])
        player = joueurs.index(line.split(' ')[1])
        blinds.append((player, 0, sizing))


        ### CARTES
        cards = []
        j+=1

        while not 'received' in lines[j]: #pb 'dead bet' chelou cf game id : 718933960
            line = lines[j]
            if 'straddle' in line:
                skip = True
            elif "timed out" in line or 'wait' in line:
                en_jeu[joueurs.index(line.split(' ')[1])] = False
            elif 'posts' in line:
                blinds.append((joueurs.index(line.split(' ')[1]), 0.5, valeur_bb))
            else:
                print('saut de ligne imprévu avant la réception des cartes, game id : ', game_id)

            j+=1
        
        while 'received' in lines[j]:
            if 'IlxxxlI' in lines[j]:
                carte = lines[j].split('[')[1].split(']')[0]
                if carte[0] == '1':
                    carte = 'T'+carte[2]
                cards.append(carte)

            j+=1

        if len(cards)!=2:
            print('Erreur de nombre de cartes, Game_ID : ' + str(game_id) + ' cartes obtenues : ' + ' '.join(cards))
            skip = True
        else:
            cartes_hero = [trad_carte(cards[0]),trad_carte(cards[1])]

        hero_pos = joueurs.index('IlxxxlI')


        # position de 'IlxxxlI'
        sequence.append([1., 0., 0., 0., 0., 0., float(hero_pos), 0., 0.])
        # cartes_hero
        for carte in cartes_hero:
            sequence.append([0., 1., 0., 0., 0., 0., carte[0], carte[1], 0.])
        # stack multiplié par en_jeu
        sequence += [[0., 0., 1., 0., 0., 0., float(ind), 0, money]
                        if en_jeu[ind] else
                     [0., 0., 1., 0., 0., 0., float(ind), 0, 0]
                            for ind, money in enumerate(stack)]
        # blindes :
        for ind_joueur, action, sizing in blinds:
            sequence.append([0., 0., 0., 1., 0., 0., float(ind_joueur), float(action), sizing])

        game_status = 'preflop' #Peut être 'preflop', 'flop', 'turn', 'river' 



        while not lines[j].startswith('------ Summary ------') and not skip:
            line = lines[j]
            if line.startswith('*** FLOP'):
                game_status = 'flop'

                flop = []
                for carte in line.split('[')[1].split(']')[0].split(' '):
                    if carte[0] != '1':
                        flop.append(carte)
                    else:
                        flop.append('T'+carte[2])
                
                for i in range(3):
                    val, col = trad_carte(flop[i])
                    sequence.append([0., 0., 0., 0., 0., 1., val, col, 0.])

            elif line.startswith('*** TURN'):
                game_status = 'turn'
                
                carte = line.split('[')[2].split(']')[0]
                if carte[0] != '1':
                    turn = carte #turn
                else:
                    turn = 'T'+carte[2] #turn
                
                val, col = trad_carte(turn)
                sequence.append([0., 0., 0., 0., 0., 1., val, col, 0.])

            elif line.startswith('*** RIVER'):
                game_status = 'river'
                
                carte = line.split('[')[2].split(']')[0]
                if carte[0] != '1':
                    river = carte #turn
                else:
                    river = 'T'+carte[2] #turn
                
                val, col = trad_carte(river)
                sequence.append([0., 0., 0., 0., 0., 1., val, col, 0.])


            elif line.startswith('Player'):
                name = line.split(' ')[1]
                action = -2
                if 'folds' in line:
                    action = -1
                    sizing = 0

                elif 'checks' in line:
                    action = 0
                    sizing = 0

                elif 'bets' in line:
                    action = 2
                    sizing = float(line.split('(')[1].split(')')[0])

                elif 'calls' in line:
                    action = 1
                    sizing = float(line.split('(')[1].split(')')[0])

                elif 'raises' in line or 'allin' in line or 'caps' in line:
                    action = 3
                    sizing = float(line.split('(')[1].split(')')[0])
                    
                if name == 'IlxxxlI' and action !=-2:
                    if action == -1:
                        repr_act = [1., 0., 0.]
                    elif action == 0 or action == 1:
                        repr_act = [0., 1., 0.]
                    elif action == 2 or action == 3:
                        repr_act = [0., 0., 1.]
                    data.append((sequence.copy(), repr_act)) 
                    if 'allin' in line or 'caps' in line or 'fold' in line or 'timed out' in line: # il n'y aura plus de décisions à prendre
                        skip = True

                if action != -2:
                    sequence.append([0., 0., 0., 0., 1., 0., float(joueurs.index(name)), float(action), sizing])
                elif 'mucks' in line or 'timed out': # timed out est déja géré comme cas car après une telle ligne, le jeu le fold
                    pass
                else:
                    print(f'Unexpected action from {name} in line ' +str(j)+', Game_id : ' + str(game_id))
                
            elif 'Uncalled' in line:
                pass
            else:
                print('Unexpected line while reading the game core in line '+str(j)+', Game_id : '+str(game_id))

            j+=1


print(data[3])

def transform_sequence(sequence, result):
    l_color=[(0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 1, 3), (0, 2, 3, 1), (0, 3, 1, 2), (0, 3, 2, 1), (1, 0, 2, 3), (1, 0, 3, 2), (1, 2, 0, 3), (1, 2, 3, 0), (1, 3, 0, 2), (1, 3, 2, 0), (2, 0, 1, 3), (2, 0, 3, 1), (2, 
1, 0, 3), (2, 1, 3, 0), (2, 3, 0, 1), (2, 3, 1, 0), (3, 0, 1, 2), (3, 0, 2, 1), (3, 1, 0, 2), (3, 1, 2, 0), (3, 2, 0, 1), (3, 2, 1, 0)]
    l_seq = []
    for color_shuffle in l_color:
        new_sequence = copy.deepcopy(sequence)
        for elem in new_sequence:
            if elem[1] > 0.5 or elem[5]>0.5:
                elem[-2] = color_shuffle[round(elem[-2])]
        
        l_seq.append((new_sequence, result))
    
    return l_seq

data_full = []
for sequence, result in data:
    l_seq = transform_sequence(sequence, result)
    data_full += l_seq

print(len(data))
print(len(data_full))
print(data_full[:20])


chem = r"C:\Users\augus_zcrxu\OneDrive\Bureau\PSC\data_transformer_duplicated"
with open(chem, "wb") as temp:
    pickle.dump(data_full, temp)

print("Extraction over")
### Pour récupérer les données, éxécuter : 
# with open("dataflop", "rb") as temp:
#     items = pickle.load(temp)
#for ligne in data_river[:20]:
#    print(ligne)

#df = pd.DataFrame(data, columns=columns)


##############################
# RMQ : 
# - Total de spots préflops 42661
# - Total de mains supprimées à cause des straddle : 47

# - position -1 sb, -2 bb
# - on donne l'argent a mettre pour rentrer dans le coup
# - checks <=> calls, bets <=> raises

# - mode de poker un peu différent, il existe un caps (au plus 30BB mise en jeu par main), équivalent à dire que le joueur à en permanance a un stack de 30BB
