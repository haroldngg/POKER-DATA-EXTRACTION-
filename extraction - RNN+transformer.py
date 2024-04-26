import pickle


columns_data = ['game id and game status', 'sequence', 'stats_joueurs', 'ind_hero', 'joueurs_presents', 'cartes_hero']
data = []
# game_id : to debug + to define if flop preflop, etc
# sequence [(ind_player, action, sizing)]
# stats_joueurs = [[stackJ1], [stackJ2], [stackJ3], ... , [stackJ9]]
# ind_hero : the indice of 'ilxxxli' among all those players
# cartes_hero : the cards of 'ilxxxli' represented as a list [c1, col1, c2, col2]

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
        sequence.append((player, 0, sizing))
        
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
        sequence.append((player, 0, sizing))


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
                sequence.append((joueurs.index(line.split(' ')[1]), 0.5, valeur_bb))
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
            cartes_hero = trad_carte(cards[0]) + trad_carte(cards[1])

        game_status = 'preflop' #Peut être 'preflop', 'flop', 'turn', 'river' 


        board = [-1.]*10

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
                    board[2*i], board[2*i+1] = trad_carte(flop[i])

                sequence.append(board.copy())

            elif line.startswith('*** TURN'):
                game_status = 'turn'
                
                carte = line.split('[')[2].split(']')[0]
                if carte[0] != '1':
                    turn = carte #turn
                else:
                    turn = 'T'+carte[2] #turn
                
                board[6], board[7] = trad_carte(turn)
                sequence.append(board.copy())

            elif line.startswith('*** RIVER'):
                game_status = 'river'
                
                carte = line.split('[')[2].split(']')[0]
                if carte[0] != '1':
                    river = carte 
                else:
                    river = 'T'+carte[2]
                
                board[8], board[9] = trad_carte(river)
                sequence.append(board.copy())


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
                    hero_pos = joueurs.index('IlxxxlI')
                    if action == -1:
                        repr_act = [1., 0., 0.]
                    elif action == 0 or action == 1:
                        repr_act = [0., 1., 0.]
                    elif action == 2 or action == 3:
                        repr_act = [0., 0., 1.]
                    data.append(((game_id, sequence.copy(), stack, hero_pos, en_jeu, cartes_hero), repr_act)) 
                    if 'allin' in line or 'caps' in line or 'fold' in line or 'timed out' in line: # il n'y aura plus de décisions à prendre
                        skip = True

                if action != -2:
                    sequence.append((joueurs.index(name), action, sizing))
                elif 'mucks' in line or 'timed out': # timed out est déja géré comme cas car après une telle ligne, le jeu le fold
                    pass
                else:
                    print(f'Unexpected action from {name} in line ' +str(j)+', Game_id : ' + str(game_id))
                
            elif 'Uncalled' in line:
                pass
            else:
                print('Unexpected line while reading the game core in line '+str(j)+', Game_id : '+str(game_id))

            j+=1


print(data[:20])


with open("../player_modelisation/RNN+Transformer/data_RNN+transformer", "wb") as temp:
    pickle.dump(data, temp)

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
