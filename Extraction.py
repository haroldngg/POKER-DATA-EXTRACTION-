chemin = r"C:\Users\ngoup\Downloads\Export Holdem Manager 2.0 12302016144830.txt"

data = []
with open(chemin, 'r') as file:
    lines = file.readlines()

current_hand = []
player_cards = []
pot_size = 0
player_count = 0
players_folded = 0
final_action = ""
player_position = 0
last_action_line = -1
odd = 0


for i, line in enumerate(lines):
    if line.startswith('Game ID:'):
        debut = i
        hand_id = re.search(r'Game ID: (\d+)', line).group(1)
        current_hand.append(hand_id)
        player_cards = []
        pot_size = 0
        player_count = 0
        players_folded = 0
        final_action = ""
        player_position = 0
        last_action_line = -1
        odd = 0
        end_of_hand_line = 0
    elif 'Seat' in line:
        player_count += 1
        if 'IlxxxlI' in line:
            player_position = int(line.split(':')[0].split(' ')[1])
            bankroll = float(line.split('(')[1].split(')')[0])
            current_hand.append(bankroll)
    elif 'Player IlxxxlI received card:' in line:
        card = re.search(r'\[(.*?)\]', line).group(1)
        player_cards.append(card)
        if len(player_cards) == 2:
            current_hand.append(' '.join(player_cards))
    elif 'Player' in line and 'folds' in line and 'IlxxxlI' not in line:
        players_folded += 1
    elif 'Player IlxxxlI' in line and 'mucks' not in line and 'Bets' not in line and 'received' not in line and 'blind' not in line:
        final_action = re.findall(r'Player IlxxxlI (\w+)', line)[-1]
        last_action_line = i
        

    if line.startswith('Game ended at:') or 'Summary' in line or 'FLOP' in line:
        for j in range(debut, last_action_line ):
            inner_line = lines[j]
            if 'blind' in inner_line or ('Player' in inner_line and 'received' not in inner_line):
                bet_amounts = re.findall(r'\((\d+(\.\d+)?)\)', inner_line)
                for amount in bet_amounts:
                    temp = amount[0]
                    pot_size += float(temp)
                odd =  1 /((pot_size/float(temp)) + 1)

        if len(current_hand) == 3:
            current_hand.extend([player_position, pot_size, player_count - 1, player_count - players_folded,odd, final_action])
            data.append(current_hand)
        current_hand = []

columns = ['hand_id', 'stack', 'cards', 'position', 'Taille du pot avant décision', 'nb_start', 'nb_final','cote', 'decision']
df = pd.DataFrame(data, columns=columns)

df
