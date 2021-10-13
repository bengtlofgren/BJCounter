class BJCounter:
    def __init__(self, no_of_decks):
        # self.cards = {2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4, 'T': 4, 'J': 4, 'Q': 4, 'K': 4, 'A': 4}
        # self.cards = dict({(i+1 , 4) for i in range(9)})
        # self.cards[10] = 16
        self.cards = []
        for i in range(9):
            for j in range(4*no_of_decks):
                self.cards.append(i+1)
        for j in range(16*no_of_decks):
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
        for i in range(1, 11):
            d[i] = self.cards.count(i)
        return d


b_j = BJCounter(1)

'''class ProbabilityCalculator:
    b_j = BJCounter(1)
    
    def __init__(self, no_of_decks):
        self.b_j = BJCounter(no_of_decks)
    
    def card_updater(self,card1):
        b_j.update(card1)
        b_j.check()

    def sum_prob(self,sum):
        deck = b_j.cards
        sums = []
        # We add combinations for ace low and ace high but they are not two separate draws
        added_aces = 0
        for i in range(len(deck)):
            for j in range(len(deck)):
                if i < j:
                    value_1 = deck[i]
                    value_2 = deck[j]

                    # aces
                    if value_1 == 1:
                        sums.append(11 + value_2)
                        added_aces += 1
                    if value_2 == 1:
                        sums.append(11 + value_1)
                        added_aces += 1

                    sums.append(value_1 + value_2)
                    
        return sums.count(sum) / (len(sums) - added_aces)
        
#pb = ProbabilityCalculator()
#print(pb.sum_prob(20))'''

d = b_j.as_dict()


def calculate_probabilities(main_deck, player_type=-1, outcomes={}, passed_total=0, passed_prob=1, passed_aces=0):
    for i in range(1, 11):
        deck = main_deck.copy()
        try:
            count = deck[i]
        except:
            count = 0
        if count > 0:
            aces = passed_aces
            if i == 1:
                aces += 1

            prob = passed_prob * count / sum(deck.values())
            deck[i] -= 1
            total = passed_total + (11 if i == 1 else i)

            # Deal with aces
            while total > 21 and aces > 0:
                aces -= 1
                total -= 10

            if player_type == -1 and total <= 16:
                calculate_probabilities(deck, outcomes=outcomes, passed_total=total,
                                        passed_prob=prob, passed_aces=aces, player_type=-1)
            elif total == 21 and i == 10 and aces == 1:
                # Blackjack - first card is an ace and then dealt a 10
                num = 'blackjack'
            elif total > 21:
                # Bust
                num = 'bust'
            else:
                num = total

            if player_type > 0 and total < 22:
                player_type -= 1
                calculate_probabilities(deck, outcomes=outcomes, passed_total=total,
                                        passed_prob=prob, passed_aces=aces, player_type=player_type)
            elif player_type == 0 and total > 21:
                # Bust
                num = 'bust'
            elif player_type == 0:
                num = total

            if (player_type == -1 and total > 16) or player_type == 0:
                if num in outcomes:
                    outcomes[num] += prob
                else:
                    outcomes[num] = prob

    return outcomes


# def conditional_dealer_hands(dealer_card, outcome):
#     return outcome[0]==dealer_card
def update_deck(new_cards, main_deck):

    for card in new_cards:
        main_deck[card] -= 1

    return main_deck


def dealer_probs(dealer_card, main_deck, outcomes={}):
    # possible_hands = []
    # for outcome in outcomes:
    #     possible_hands.append(filter(conditional_dealer_hands, outcome))

    new_cards = [dealer_card]

    current_deck = update_deck(new_cards, main_deck.copy())

    if dealer_card == 1:
        dealer_ace = 1
        dealer_card = 11
    else:
        dealer_ace = 0

    conditional_dealer_outcomes = calculate_probabilities(
        current_deck, outcomes={}, passed_total=dealer_card, passed_aces=dealer_ace)

    return(conditional_dealer_outcomes, current_deck)


def probability_of_hand(hand, deck):
    deck = deck.copy()
    if not type(hand) is list:
        hand = [hand]
    prob = 1
    for card in hand:
        prob *= deck[card] / sum(deck.values())
        deck[card] -= 1
    return prob

# run dealer_probs first and pass cond_outcomes and current_deck as arguments for this function


def should_i_hit(p_hand, main_deck, conditional_dealer_outcomes, prob_of_getting_hand=1, outcomes={}):

    try:
        prob_dealer_bust = conditional_dealer_outcomes['bust']
    except:
        prob_dealer_bust = 0

    new_cards = p_hand

    current_deck = update_deck(new_cards, main_deck.copy())
    p_total = sum(p_hand)

    player_aces = p_hand.count(1)

    player_bots = []
    for i in range(1, 5):
        player_bots.append(calculate_probabilities(current_deck, player_type=i, outcomes={
        }, passed_total=p_total, passed_aces=player_aces))

    # try:
    #     prob_player_bust_after_hit = conditional_player_outcomes['bust']
    # except:
    #     prob_player_bust_after_hit = 0
    prob_player_bust = 0
    prob_win = prob_dealer_bust*(1-prob_player_bust)
    prob_tie = 0
    if p_total >= 16 and p_total < 22:
        try:
            prob_tie = conditional_dealer_outcomes[p_total]
        except:
            prob_tie = 0
        for i in range(17, p_total):
            prob_win += conditional_dealer_outcomes[i]
    bot_wins_array = []

    for outcome in player_bots:
        try:
            prob_bot_bust = outcome['bust']
        except:
            prob_bot_bust = 0

        prob_bot_wins = prob_dealer_bust*(1-prob_bot_bust)
        prob_bot_tie = 0
        for i in range(18, 21):
            try:
                prob_bot_tie += outcome[i] * conditional_dealer_outcomes[i]
            except:
                pass
            for j in range(17, i):
                try:
                    prob_bot_wins += outcome[i] * \
                        conditional_dealer_outcomes[j]
                except:
                    pass
        bot_wins_array.append(prob_bot_wins)
    # Have ignored for ties here, maybe should incorporate, maybe use prob_win += prob_tie * 1/2 or smthn
    # should_hit = prob_win <= prob_win_with_a_hit
    maximum_prob = max(bot_wins_array)

    maximum_index = bot_wins_array.index(maximum_prob)
    # print('bot number', maximum_index)

    # print(bot_wins_array)
    # print(maximum_prob)
    # print(prob_win)
    
    should_hit = maximum_prob > prob_win
    return (should_hit, max(prob_win, maximum_prob))


def pre_flop(deck):
    prob_of_winning_pre_flop_list = []
    for dealer_card in range(1, 11):
        # doesn't include probability of full hand, only prob of player hand given dealer hand. Should multiply by prob of dealer hand.
        prob_dealer_hand = probability_of_hand(dealer_card, deck)

        cond_dealer_outcomes, deck = dealer_probs(dealer_card, deck, outcomes={})

        for card_1 in range(1, 11):
            for card_2 in range(1, 11):
                p_hand = [card_1, card_2]
                prob_of_hand_given_dealer_card = probability_of_hand(
                    p_hand, deck)
                prob_of_full_hand = prob_of_hand_given_dealer_card * prob_dealer_hand

                prob_win = keep_track_of_hits(
                    p_hand, prob_of_full_hand, deck, cond_dealer_outcomes)

                prob_of_winning_pre_flop_list.append(prob_win)

    prob_of_winning_pre_flop = sum(prob_of_winning_pre_flop_list)
    return(prob_of_winning_pre_flop)


def keep_track_of_hits(p_hand, prob_of_hand, deck, cond_dealer_outcomes, should_hit=False):

    should_hit, prob_of_win = should_i_hit(p_hand, deck, cond_dealer_outcomes)

    prob_array = []

    if should_hit and len(p_hand) < 6:
        for card_value in range(1, 11):
            working_deck = deck.copy()

            # try:
            working_deck[card_value] -= 1

            p_hand_hit = p_hand.copy()
            p_hand_hit.append(card_value)

            keep_track_of_hits(p_hand_hit, prob_of_hand,
                                working_deck, cond_dealer_outcomes)

            
            # except:
                # pass  
    else:
        prob_array.append(prob_of_win * prob_of_hand)
        
    final_prob = sum(prob_array)
    return(final_prob)

    '''how_many_hits=[]
    how_many_hits[0]=prob_win
    how_many_hits.append(prob_win_with_a_hit*prob_of_getting_hand)
    for i in range(1,11):
        hand = p_hand.copy()
        hand.append(i)
        prob_getting_hand = probability_of_hand(hand, current_deck)
        should_i_hit(hand,current_deck,conditional_dealer_outcomes,outcomes={},prob_of_getting_hand=prob_getting_hand)
    
    binary_tree = how_many_hits
    return(binary_tree)

    # return{'should_hit': should_hit, 'prob_win': prob_win_with_hit,'deck': current_deck] '''

    '''if should_hit:
        prob_win = prob_win_with_hit.copy()
        prob_tie = prob_tie_with_hit.copy()
        prob_player_bust = prob_player_bust_after_hit.copy()
        prob_win_with_hit = 0
        for outcome in conditional_player_outcomes:
            if outcome[0] !< 21:
                continue
            card_drawn = outcome[0] - p_total
            ace_after_hit=0
            if card_drawsn == 1:
                ace_after_hit = 1
            deck_after_hit = update_deck(card_drawn, current_deck)
            conditional_player_outcomes_with_hit = calculate_probabilities(deck_after_hit, passed_total=outcome[1], passed_aces=ace_after_hit, dealer=False)
            
            prob_win_with_cond_hit = prob_dealer_bust*(1-prob_player_bust_after_hit)
            prob_tie_with_cond_hit = 0
            for i in range(18,21):
                prob_tie_with_cond_hit+= (conditional_player_outcomes_with_hit[i] * conditional_dealer_outcomes[i])
                for j in range (17, i):
                    prob_win_with_cond_hit+= (conditional_player_outcomes_with_hit[i] * conditional_dealer_outcomes[j])
            
            prob_win_with_hit += outcome[1]*prob_win_with_cond_hit
            # Run above code again'''


print(pre_flop(d))
