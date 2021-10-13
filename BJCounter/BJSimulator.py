from BJCounter import BJCounter
import random

class BJDeck:
    def __init__(self, no_of_decks):
        # self.cards = {2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4, 'T': 4, 'J': 4, 'Q': 4, 'K': 4, 'A': 4}
        # self.cards = dict({(i+1 , 4) for i in range(9)})
        # self.cards[10] = 16
        self.cards = []
        
        # Make deck with 2-11 (Ace = 11) 4 of each card
        for i in range(9):
            for j in range(4*no_of_decks):
                self.cards.append(i+3)
        # Add 12 extra 10s per deck
        for j in range(12*no_of_decks):
            self.cards.append(10)
        self.deck = self.cards.copy()

    def update(self, seen_card):
        current = self.cards[seen_card]
        new = current - 1
        self.cards.update({seen_card: new})

    def reset(self):
        self.cards = self.deck

    def as_dict(self):
        d = {}
        for i in range(2, 12):
            d[i] = self.cards.count(i)
        return d

def update_deck_as_list(new_cards, deck):

    for card in new_cards:
        card_popped = deck.pop(deck.index(card))

    return deck

def dealer_simulation(dealer_shown_card, deck):
    dealer_hand = [dealer_shown_card]
        
    dealer_score = sum(dealer_hand)
    
    dealer_aces = 1 if dealer_shown_card == 11 else 0
    
    game_in_progress = True
    
    while game_in_progress:
        while dealer_score > 21 and dealer_aces >0:
            dealer_score-=10
            dealer_aces-=1

        # Dealer pulls new card
        while dealer_score <= 17:
            new_card = random.choice(deck)
            if new_card == 11:
                dealer_aces+=1
            dealer_hand.append(new_card)
            # Update deck
            deck = update_deck_as_list([new_card], deck)

        if (dealer_score>21 and dealer_aces ==0) or dealer_score>= 17:
            game_in_progress = False
    
    if dealer_score > 21: 
        dealer_score = 99
    # Only use dealer_hand for actual simulation, not when calc probabilites. Note that dealer deck depends on player deck after has hit, should perhaps take this into account but expasds tree immensely
    return(dealer_hand, dealer_score)

def player_simulation(player_hand, deck, no_of_hits):
    if no_of_hits>0:
        
        # Make sure this function is without replacement!!
        player_additional_cards = random.choices(deck, k = no_of_hits)
        player_hand.append(player_additional_cards)
        # deck = update_deck_as_list(player_additional_cards)
    
    for card in player_hand:
        if card == 11:
            player_aces+=1
    
    player_score = sum(player_hand)
   
    while player_score > 21 and player_aces >0:
        player_score-=10
        player_aces-=1
    
    if player_score < 17:
        player_score = 1
    if player_score > 21:
        player_score = 100
    # Only use player_hand in actual simulation once bot has been chosen
    return(player_hand, player_score)


def simulation(deck_as_list, type_of_bot):

    dealer_hand = random.choices(deck_as_list, k=2)
    deck = update_deck_as_list(dealer_hand, deck_as_list)
    dealer_shown_card = dealer_hand[0]

    player_hand = random.choices(deck, k=2)
    deck = update_deck_as_list(player_hand, deck)

    # Check if blackjack, if so make blackjack and make win score 1.5
    player_blackjack = True if (21 == sum(player_hand)) else False
    dealer_blackjack = True if (sum(dealer_hand) == 21) else False

    # Need to figure out what type of bot is best, given current situation (Dealer shown card + Player cards)
    
    # 1.Calculate probabilities of dealer hand (99 is bust)
    dealer_prob_dict = {17:0, 18:0, 19:0, 20:0, 21:0, 99: 0}
    
    # Defines number of simulations, make sure to change if wanted
    no_of_sims = 100
    for i in range(no_of_sims):
        dealer_score_sim = dealer_simulation(dealer_shown_card, deck)[1]
        dealer_prob_dict[dealer_score_sim]+=(1/no_of_sims)

    # TODO: Now i have done dealer probs. Need player sims and player probs. 
    # Extra dict item of less than 17 score in which only way of winning is if dealer bust. 
    # The rest have dealer bust probs + probs of being greater than dealer (100 is bust)
    player_prob_dict = {1:0, 17:0, 18:0, 19:0, 20:0, 21:0, 100: 0}
    players_prob_dict = {0: player_prob_dict, 1: player_prob_dict, 2: player_prob_dict, 3: player_prob_dict, 4: player_prob_dict}
    for j in range(no_of_sims):
        players_score_sim = {0: player_simulation(player_hand, deck, 0)[1], 1: player_simulation(player_hand, deck, 1)[1], 2:player_simulation(player_hand, deck, 2)[1], 3: player_simulation(player_hand, deck, 3)[1], 4: player_simulation(player_hand, deck, 4)[1]}
        for player_no in players_score_sim:
            player_score = players_score_sim[player_no]
            players_prob_dict[player_no][player_score]+=(1/no_of_sims)
    
    prob_player_win = {0: 0, 1: 0, 2: 0, 3: 0, 4:0}
    # Commulative Dealer Prob Dict
    cdpd = {17: dealer_prob_dict[17] + dealer_prob_dict[99], 18 : dealer_prob_dict[99] + dealer_prob_dict[17] + dealer_prob_dict[18], 19 : dealer_prob_dict[99] + dealer_prob_dict[17] + dealer_prob_dict[18] + dealer_prob_dict[19], 20: (1- dealer_prob_dict[21]), 21: 1}
    for player in players_prob_dict:
        ppd = players_prob_dict[player]
        winning_prob = 0*ppd[100] + ppd[21]*(cdpd[20] + 0.5(dealer_prob_dict[21]) + ppd[20]*(cdpd)
        winning_prob = 0
        for i in range(17, 22):
            winning_prob+= ppd[i]*(0.5*dealer_prob_dict[i]+ cdpd[i-1])
        prob_player_win[player]+= winning_prob



    # Sum (1*Prob_of_winning -1*Prob_Losing) for each bot. Find Max value of this and assign bot value

    # Now player bots will see how many times they should hit
    

    dealer_aces = 0
    player_aces = 0
    for card in dealer_hand:
        if card == 11:
            dealer_aces+=1
    
    for card in player_hand:
        if card == 11:
            player_aces+=1
        
    player_score = sum(player_hand)
    dealer_score = sum(dealer_hand)
    
    game_in_progress = True
    
    while game_in_progress:
        while player_score > 21 and player_aces >0:
            player_score-=10
            player_aces-=1
        
        while dealer_score > 21 and dealer_aces >0:
            dealer_score-=10
            dealer_aces-=1

        while dealer_score <= 17:
            dealer_hand.append(random.choice(deck))

        if (dealer_score>21 and dealer_aces ==0) or dealer_score>= 17:
            game_in_progress = False
    
    outcome = {"player score": player_score, "dealer score": dealer_score ,"dealer hand": dealer_hand, "player hand": player_hand}
    
    did_win = -1
    if player_score == dealer_score or (player_blackjack and dealer_blackjack):
        did_win = 0 
    if (player_score>dealer_score or (dealer_score>21 and player_score<=21)):
        did_win = 1 
    if player_blackjack and not dealer_blackjack:
        did_win = 1.5
    return(did_win, outcome)
