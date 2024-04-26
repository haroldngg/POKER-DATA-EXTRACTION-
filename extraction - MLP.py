from deuces import Card, deck
from hp import HandPotential_1
from hse import hse_1
import pickle


###### Taches restantes : 

# -  Tester une regression avec raise_all

data_preflop = []
data_flop = []
data_turn = []
data_river = []

columns_preflop = ['game_id', 'stack',         'position',            'nb joueur au depart', 'cards', 'Taille du pot avant décision', 'nb joueur non couches','argent a rajouter pour call', 'position du dernier relanceur au preflop', 'mise en cas de Raise/Bet', 'decision']
columns_flop =    ['game_id', 'stack restant', 'position au flop',    'nb joueur au depart', 'cards', 'Taille du pot avant décision', 'nb joueur non couches','argent a rajouter pour call', 'hand strength', 'hand positive potential', 'hand negative potential', 'position du dernier relanceur au preflop', 'position du dernier relanceur au flop',    'flop', 'mise en cas de Raise/Bet', 'decision']
columns_turn =    ['game_id', 'stack restant', 'position a la turn',  'nb joueur au depart', 'cards', 'Taille du pot avant décision', 'nb joueur non couches','argent a rajouter pour call', 'hand strength', 'hand positive potential', 'hand negative potential', 'position du dernier relanceur au flop',    'position du dernier relanceur a la turn',  'flop', 'turn', 'mise en cas de Raise/Bet', 'decision']
columns_river =   ['game_id', 'stack restant', 'position a la river', 'nb joueur au depart', 'cards', 'Taille du pot avant décision', 'nb joueur non couches','argent a rajouter pour call', 'hand strength', 'hand positive potential', 'hand negative potential', 'position du dernier relanceur a la turn',  'position du dernier relanceur a la river', 'flop', 'turn', 'river', 'mise en cas de Raise/Bet', 'decision']
# a prpos de la position du relanceur de la phase précédente, si ce dernier est couché, la valeur associée sera -1
val_blindes = []

# Test d'une unique liste pour faire converger l'algorythme
data_raise_value_all = []


# On pourrait recréer des listes comme celle ci, mais ca ne sert a rien, toute l'information requise est déja stockée dans les 4 listes principales, il suffira juste de les filtrer
# data_raise_value_preflop = []
# data_raise_value_flop = []
# data_raise_value_turn = []
# data_raise_value_river = []

columns_raise_all = ['game_id',
                   'stack restant', 
                   'position actuelle', 
                   'nb joueur au depart', 
                   'cards', 
                   'Taille du pot avant décision', 
                   'nb joueur non couches',
                   'argent a rajouter pour call', 
                   'hand strength', 
                   'hand potential', 
                   'phase du jeu', # variable en plus, on espére que le reseau de neurone arrivera à s'en servir pour effacer l'influence des variables encore indéfinies
                   'flop', 
                   'turn', 
                   'river', 
                   'mise maximale', 
                   'mise en cas de Raise/Bet', 
                   'decision']


def data_add(status, decision, nbutton):

    if decision == 'raises' or decision == 'bets':
        data_raise_value_all.append(formated())

    if status == 'preflop':
        spot[1] = bankroll
        spot[2] = position(joueurs, nbutton, 'IlxxxlI', status)
        spot[5] = pot_value
        spot[6] = number_of_players - number_of_folded_players
        spot[7] = betting_status - joueurs[1][joueurs[0].index('IlxxxlI')]
        if nom_dernier_relanceur != '':
            spot[8] = position(joueurs, nbutton, nom_dernier_relanceur, status)
        else:
            spot[8] = -3 # valeur par défaut
        spot[-1] = decision #[-1] = [10]

        data_preflop.append(spot.copy())
    elif status == 'flop':
        spot[1] = bankroll
        spot[2] = position(joueurs, nbutton, 'IlxxxlI', status)
        spot[5] = pot_value
        spot[6] = number_of_players - number_of_folded_players
        spot[7] = betting_status - joueurs[1][joueurs[0].index('IlxxxlI')]
        spot[8], spot[9], spot[10] = hand_strength_potential(spot[4], spot[13])


        if nom_dernier_relanceur_phase_precedente != '':
            spot[11] = position(joueurs, nbutton, nom_dernier_relanceur_phase_precedente, status)
        else:
            spot[11] = -1 #valeur par défaut au flop
        
        if nom_dernier_relanceur != '':
            spot[12] = position(joueurs, nbutton, nom_dernier_relanceur, status)
        else:
            spot[12] = -1 #valeur par défaut au flop
        spot[-1] = decision #[-1] = [13] (10 = flop)

        data_flop.append(spot.copy())
    elif status == 'turn':
        spot[1] = bankroll
        spot[2] = position(joueurs, nbutton, 'IlxxxlI', status)
        spot[5] = pot_value
        spot[6] = number_of_players - number_of_folded_players
        spot[7] = betting_status - joueurs[1][joueurs[0].index('IlxxxlI')]
        spot[8], spot[9], spot[10] = hand_strength_potential(spot[4], spot[13] + ' ' + spot[14])


        if nom_dernier_relanceur_phase_precedente != '':
            spot[11] = position(joueurs, nbutton, nom_dernier_relanceur_phase_precedente, status)
        else:
            spot[11] = -1

        if nom_dernier_relanceur != '':
            spot[12] = position(joueurs, nbutton, nom_dernier_relanceur, status)
        else:
            spot[12] = -1
        spot[-1] = decision #[-1] = [14] (10, 11 = flop, turn)

        data_turn.append(spot.copy())
    elif status == 'river':
        spot[1] = bankroll
        spot[2] = position(joueurs, nbutton, 'IlxxxlI', status)
        spot[5] = pot_value
        spot[6] = number_of_players - number_of_folded_players
        spot[7] = betting_status - joueurs[1][joueurs[0].index('IlxxxlI')]
        spot[8], spot[9], spot[10] = hand_strength_potential(spot[4], spot[13] + ' ' + spot[14] + ' ' + spot[15])
        

        if nom_dernier_relanceur_phase_precedente != '':
            spot[11] = position(joueurs, nbutton, nom_dernier_relanceur_phase_precedente, status)
        else:
            spot[11] = -1

        if nom_dernier_relanceur != '':
            spot[12] = position(joueurs, nbutton, nom_dernier_relanceur, status)
        else:
            spot[12] = -1
        spot[-1] = decision #[-1] = [15] (10, 11, 12 = flop, turn, river)

        data_river.append(spot.copy())

def formated(): #A DEFINIR
    return []

def reinit(l):
    for i in range(len(l[0])):
        l[1][i] = 0


def hand_strength_potential(hand, board):
    h = [Card.new(carte) for carte in hand.split(' ')]
    b = [Card.new(carte) for carte in board.split(' ')]
    if len(b)<5:
        try:
            hpp, hpn = HandPotential_1(b, h)
        except:
            print(board, hand)
    else:
        hpp, hpn = 0,0
    return (hse_1(b,h),hpp,hpn)


#BUG calcul position lorsque qqn se couche pour les sb/bb.

def position(lplayer, name_button, name, g_status):
    ecart = 0
    compteur_ecart = 0
    nb_of_unfolded_players = 0 # Normalement sera égal à number_of_players - number_of_folded_players

    for i in range(len(lplayer[0])):
        
        if lplayer[2][i]:
            nb_of_unfolded_players+=1
            ecart += compteur_ecart
        
        if name_button == lplayer[0][i]:
            compteur_ecart-=1

        if name == lplayer[0][i]:
            compteur_ecart+=1

    if ecart <0:
        ecart+=nb_of_unfolded_players

    if g_status == 'preflop':
        # Ensuite, on ajuste pour la small blinde et la big blinde (pour les représentées par -1 et -2 ) si on est au préflop
        if ecart-number_of_players >=-2:
            return ecart-number_of_players
        else:
            return ecart
    else:
        return ecart
    
    
    


chemin = r"C:\Users\augus_zcrxu\OneDrive\Bureau\PSC\extraction\dataset\Export_Holdem_Manager_2.0_12302016144830.txt"


with open(chemin, 'r') as file:
    lines = file.readlines()

compteur_partie = 0
for i, line in enumerate(lines):
    
    if line.startswith('Game ID:'):
        compteur_partie +=1
        if compteur_partie%50==0:
            print("Work in Progress : ", int(1000*compteur_partie/42688)/10, "%")
        spot = []
        skip = False

        ### GAME ID
        game_id = int(line.split(' ')[2])
        spot.append(game_id)

        valeur_bb = float(line.split(' ')[3].split('/')[1])

        val_blindes.append((game_id, valeur_bb))

        number_of_players = 0
        number_of_folded_players = 0

        bankroll = 0

        button_seat = int(lines[i+1].split(' ')[1])
        ecart = 0 #permet de determiner la position du joueur à la table par rapport au boutton
        compteur_ecart = 0

        j = i+2
        joueurs = [[],[], []]
        #Premier ligne : nom du joueur,
        #Deuxième ligne : valeur de leur dernière mise dans le statu actuel du jeu ('preflop', flop', 'turn', 'river') (utile pour déterminer la valeur des relances (lorsque le joueur à déja miser avant) et donc calculer l'argent à rajouter dans le pot de notre joueur dans le pot)
        #Troisième ligne : booléen : est ce que le joueur est encore en jeu (=pas couché)

        while lines[j].startswith('Seat'):
            number_of_players+=1
            line = lines[j]
            sep = line.split(' ')
            seat = int(sep[1][0])
            name = sep[2]

            joueurs[0].append(name)
            joueurs[1].append(0)
            joueurs[2].append(True) # signifie que le joueur est en jeu

            if seat == button_seat:
                button_name = name

            if 'IlxxxlI' in lines[j]:
                bankroll = min(30*valeur_bb, float(line.split('(')[1].split(')')[0])) ### A cause du mode de jeu particulier (cap), la bankeroll est au plus de 30bb

            j+=1

        ### BANKROLL
        if bankroll <= 0: #Le joueur IlxxxlI ne joue pas, on sort de la boucle
            print('Erreur de bankroll, Game_ID : ' + str(game_id))
            skip = True
        else:
            spot.append(bankroll)
            
        ### POSITION
        spot.append(position(joueurs, button_name, 'IlxxxlI', 'preflop'))

        ### NOMBRE DE JOUEURS DANS LA PARTIE
        spot.append(number_of_players)

        #On incremente le pot des SB et BB + on corrige les mises des deux joueurs concernés :
        pot_value = 0

        while not 'has small blind' in lines[j]: #pb 'sitting out' cf game id : 718934873
            line = lines[j]
            if 'timed out' in line:
                joueurs[2][joueurs[0].index(line.split(' ')[1])] = False
                number_of_folded_players +=1 # le joueur ne sera pas foldé automatiquement, on le fait donc ici
            elif not 'sitting out' in line:
                print('saut dans les blindes non maitrise (avant sb), game id :', game_id)
            j+=1
        
        line = lines[j]
        sb = float(line.split('(')[1].split(')')[0])
        joueurs[1][joueurs[0].index(line.split(' ')[1])] = sb
        if 'IlxxxlI' in line:
            bankroll -= sb
        pot_value += sb

        j+=1
        while not 'has big blind' in lines[j]: #pb 'sitting out' cf game id : 718934873
            if 'timed out' in lines[j]: # le joueur ne sera pas foldé automatiquement, on le fait donc ici
                joueurs[2][joueurs[0].index(line.split(' ')[1])] = False
                number_of_folded_players +=1
            elif not 'sitting out' in lines[j]:
                print('saut dans les blindes non maitrise (avant bb), game id :', game_id)
            j+=1
        line = lines[j]
        bb = float(line.split('(')[1].split(')')[0])
        joueurs[1][joueurs[0].index(line.split(' ')[1])] = bb
        if 'IlxxxlI' in line:
            bankroll -= bb
        pot_value += bb 

        #RMQ: la variable bb pourrait être inferieure à la valeur de value bb si le joueur en big blinde a moins d'une bb en stack (automatiquement all in)

        ### CARTES
        cards = []
        j+=1

        while not 'received' in lines[j]: #pb 'dead bet' chelou cf game id : 718933960
            line = lines[j]
            if 'straddle' in line:
                skip = True
            elif "timed out" in line:
                joueurs[2][joueurs[0].index(line.split(' ')[1])] = False
                number_of_folded_players +=1
            elif not 'wait' in line and not 'posts' in line:
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
            spot.append(' '.join(cards))

        nom_dernier_relanceur = ''
        nom_dernier_relanceur_phase_precedente = ''
        game_status = 'preflop' #Peut être 'preflop', 'flop', 'turn', 'river' 
        betting_status = valeur_bb

        # On rajoute des valeurs de défaut pour les spots au preflop
        spot = spot + [pot_value, number_of_players - number_of_folded_players, 0, -3, 0, "none"] # les quatres derniers éléments sont respectivements l'argent à rajouter dans le pot pour call, la position du dernier relanceur, la valeur d'un éventuel raise, et l'action finale de 'IlxxxlI'

        while not lines[j].startswith('------ Summary ------') and not skip:
            line = lines[j]
            if line.startswith('*** FLOP'):
                game_status = 'flop'
                reinit(joueurs)

                nom_dernier_relanceur_phase_precedente = nom_dernier_relanceur
                nom_dernier_relanceur = ''

                spot.append(0) # pour la hand strength
                spot.append(0) # pour la hand potential pos
                spot.append(0) # pour la hand potential neg
                spot.append(0) # pour la position du dernier relanceur de la phase précédente

                flop = []
                for carte in line.split('[')[1].split(']')[0].split(' '):
                    if carte[0] != '1':
                        flop.append(carte)
                    else:
                        flop.append('T'+carte[2])
                spot[13] = ' '.join(flop) # le flop

                spot.append('none') # la decision reste écrite à la fin
                spot[-2] = 0

                betting_status = 0

            elif line.startswith('*** TURN'):
                game_status = 'turn'
                reinit(joueurs)

                nom_dernier_relanceur_phase_precedente = nom_dernier_relanceur
                nom_dernier_relanceur = ''

                carte = line.split('[')[2].split(']')[0]
                if carte[0] != '1':
                    spot[14] = carte #turn
                else:
                    spot[14] = 'T'+carte[2] #turn
                
                spot.append('none') #decision
                spot[-2] = 0

                betting_status = 0

            elif line.startswith('*** RIVER'):
                game_status = 'river'
                reinit(joueurs)

                nom_dernier_relanceur_phase_precedente = nom_dernier_relanceur
                nom_dernier_relanceur = ''

                carte = line.split('[')[2].split(']')[0]
                if carte[0] != '1':
                    spot[15] = carte #turn
                else:
                    spot[15] = 'T'+carte[2] #turn

                spot.append('none') #decision
                
                spot[-2] = 0


                betting_status = 0
            elif line.startswith('Player'):
                name = line.split(' ')[1]
                if 'IlxxxlI' == name:
                    if 'folds' in line:
                        data_add(game_status, 'folds', button_name)
                        skip = True

                    elif 'checks' in line:
                        data_add(game_status, 'checks', button_name)

                    elif 'bets' in line:
                        betting_status = float(line.split('(')[1].split(')')[0])
                        spot[-2] = betting_status
                        data_add(game_status, 'bets', button_name)
                        spot[-2] = 0

                        nom_dernier_relanceur = name

                        pot_value += betting_status
                        bankroll -= betting_status

                    elif 'calls' in line:
                        data_add(game_status, 'calls', button_name)
                        money = float(line.split('(')[1].split(')')[0])
                        pot_value += money
                        bankroll -= money


                    elif 'raises' in line or 'allin' in line or 'caps' in line:
                        money_added = float(line.split('(')[1].split(')')[0])
                        spot[-2] = money_added
                        data_add(game_status, 'raises', button_name)
                        spot[-2] = 0

                        nom_dernier_relanceur = name

                        betting_status = joueurs[1][joueurs[0].index('IlxxxlI')] + money_added
                        pot_value += money_added
                        bankroll -= money_added
                        if 'allin' in line or 'caps' in line: # il n'y aura plus de décisions à prendre
                            skip = True
                    elif 'timed out' in line:
                        skip = True
                    elif 'mucks' in line or 'Uncalled' in line:
                        pass
                    
                    else:
                        print('Unexpected action from IlxxxlI in line ' +str(j)+', Game_id : ' + str(game_id))
                else:
                    if ' folds' in line:
                        joueurs[2][joueurs[0].index(line.split(' ')[1])] = False
                        number_of_folded_players +=1

                    elif ' bets' in line:
                        betting_status = float(line.split('(')[1].split(')')[0]) # en cas de bet, il n'y a pas de valeur avant
                        pot_value += betting_status

                        nom_dernier_relanceur = name

                    elif ' calls' in line:
                        pot_value += float(line.split('(')[1].split(')')[0])

                    elif ' raises' in line or ' allin' in line or ' caps' in line:
                        money_added = float(line.split('(')[1].split(')')[0])
                        betting_status = joueurs[1][joueurs[0].index(name)] + money_added
                        pot_value += money_added

                        nom_dernier_relanceur = name

                    elif ' checks' in line or ' mucks' in line or ' timed out' in line: # Change rien, cas banal. Un joueurtimed out est fold automatiquement
                        pass

                    else:
                        print('Unexpected action from ' + name + ' in line ' +str(j)+', Game_id : ' + str(game_id))
            elif 'Uncalled' in line:
                pass
            else:
                print('Unexpected line while reading the game core in line '+str(j)+', Game_id : '+str(game_id))

            j+=1


print(data_flop[:20])

print(compteur_partie)

with open("data_flop", "wb") as temp:
    pickle.dump(data_flop, temp)

with open("data_turn", "wb") as temp:
    pickle.dump(data_turn, temp)

with open("data_river", "wb") as temp:
    pickle.dump(data_river, temp)

with open("data_preflop", "wb") as temp:
    pickle.dump(data_preflop, temp)

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
