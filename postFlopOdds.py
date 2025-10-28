import random
from treys import Card, Deck, Evaluator
from math import comb
from itertools import combinations

suits = ['s','h','d','c']
ranks = ['A','2','3','4','5','6','7','8','9','T','J','Q','K']
rank_map = {
        12: 'A', 11: 'K', 10: 'Q', 9: 'J', 8: 'T', 
        7: '9', 6: '8', 5: '7', 4: '6', 3: '5', 
        2: '4', 1: '3', 0: '2', -1:'A'
    }

straightSequences = [
    {12, 0, 1, 2, 3}, # A, 2, 3, 4, 5 (Wheel)
    {0, 1, 2, 3, 4},  # 2, 3, 4, 5, 6
    {1, 2, 3, 4, 5},  # 3, 4, 5, 6, 7
    {2, 3, 4, 5, 6},  # 4, 5, 6, 7, 8
    {3, 4, 5, 6, 7},  # 5, 6, 7, 8, 9
    {4, 5, 6, 7, 8}, # 6, 7, 8, 9, T
    {5, 6, 7, 8, 9},# 7, 8, 9, T, J
    {6, 7, 8, 9, 10},# 8, 9, T, J, Q
    {7, 8, 9, 10, 11},# 9, T, J, Q, K
    {8, 9, 10, 11, 12} # T, J, Q, K, A (Broadway)
]


def postFlopOdds(card1,card2, flop, deck, num_players=2):
    
    evaluator = Evaluator()
    hand = [Card.new(card1), Card.new(card2)]
    board = [Card.new(flop[0]), Card.new(flop[1]), Card.new(flop[2])]

    for card in hand:
        if card in deck.cards:
            deck.cards.remove(card)

    for card in board:
        if(card in deck.cards):
            deck.cards.remove(card)

    p1_score = evaluator.evaluate(board, hand)
    p1_class = evaluator.class_to_string(evaluator.get_rank_class(p1_score))

    royalFlushProbability, royalFlushPossibleProbability =  royalFlushEvaluator(hand, board, deck, num_players)

    straightFlushProbability, straightFlushPossibleProbability = straightFlushEvaluator(hand, board, deck, num_players)

    return straightFlushProbability


def royalFlushEvaluator(hand, board, deck, num_players):

    royal_ranks = ['T','J','Q','K','A']


    royalFlush = True
    royalFlush_possible = True
    suitSet = set()
    suitList = []

    count = 0
    for i in range(len(board)):
        if(Card.get_rank_int(board[i])<8):
            count+=1
            royalFlush=False
        else:
            suitSet.add(Card.get_suit_int(board[i]))
            suitList.append(Card.get_suit_int(board[i]))

    if(len(suitSet)!=1):
        royalFlush=False

    if(count>2):
        royalFlush_possible=False

    if(royalFlush==True and royalFlush_possible==False):
        raise Exception("Royal Flush Mismatch") 

    if(royalFlush==True):
        suit= Card.INT_SUIT_TO_CHAR_SUIT[list(suitSet)[0]]

        royalFlushCards = {Card.new("A"+suit), Card.new("K"+suit), Card.new("Q"+suit), Card.new("J"+suit), Card.new("T"+suit)}.difference(set(board))

        for card in hand:
            if(card in royalFlushCards):
                royalFlush=False
        
        if(royalFlush==True):
            royalFlushProbability = (num_players-1)/comb(len(deck.cards),len(list(royalFlushCards)))
    else:
            royalFlushProbability = 0

    if(royalFlush_possible==True):
        known = set(hand + board)
        remaining_cards = [c for c in deck.cards if c not in known]
        N = len(remaining_cards)  # should be 47

        royalFlushPossibleProbability = 0.0

        for s in suits:
            royals = [Card.new(r + s) for r in royal_ranks]
            if any(r in hand for r in royals):
                continue
            
            r_on_flop = sum(1 for r in royals if r in board)   
            if r_on_flop == 0:
                # flop doesn't show any royal ranks of this suit -> not considered (per user)
                continue

            m = 5 - r_on_flop   # number of royal cards of this suit still needed after flop
            
            missing_cards = [r for r in royals if r not in board]
            denom_pairs = comb(N, 2)
            suit_sum = 0.0

            idx = remaining_cards

            # Precompute mapping from index to whether it's a missing royal
            is_missing = [1 if idx[i] in missing_cards else 0 for i in range(N)]

            for i, j in combinations(range(N), 2):
                m_board = is_missing[i] + is_missing[j]
                m_rem = m - m_board   # how many royal cards must come from opponents' hole cards
                N2 = N - 2            # cards left after turn+river
                k = num_players - 1   # number of opponents

                if m_rem <= 0:
                    cond_prob = 1.0

                elif m_rem == 1:
                    # One specific card left — probability that at least one opponent has it
                    total_hole_sets = comb(N2, 2 * k)
                    ways_no_one_has_it = comb(N2 - 1, 2 * k) if N2 - 1 >= 2 * k else 0
                    cond_prob = 1.0 - (ways_no_one_has_it / total_hole_sets)

                elif m_rem == 2:
                    # Two specific cards left — exact combinatorial probability that
                    # at least one opponent has *both* in the same hole pair
                    if 2 * k > N2:
                        cond_prob = 0.0
                    else:
                        p_both_in_dealt = comb(N2 - 2, 2 * k - 2) / comb(N2, 2 * k)
                        p_same_hand_given_in_dealt = k / comb(2 * k, 2)
                        cond_prob = p_both_in_dealt * p_same_hand_given_in_dealt
                        if cond_prob > 1.0:
                            cond_prob = 1.0

                else:
                    cond_prob = 0.0

                
                suit_sum+=cond_prob
            # average over all possible turn/river pairs
            p_suit = suit_sum / denom_pairs
            royalFlushPossibleProbability += p_suit
    else:
        royalFlushPossibleProbability = 0.0

    return royalFlushProbability, royalFlushPossibleProbability

def straightFlushEvaluator(hand, board, deck, num_players):
    straightFlush=True
    suitSet = set()
    rankList = []
    for card in board:
        suitSet.add(Card.get_suit_int(card))
        if(Card.get_rank_int(card) not in rankList):
            rankList.append(Card.get_rank_int(card))

    if(len(suitSet)!=1):
        straightFlush=False
    if(len(rankList)<3):
        straightFlush=False
    
    if(straightFlush==True):
        rankList.sort(reverse=True)
        distance = rankList[0] - rankList[1] - rankList[2] - 2
        if(distance>2):
            if(rankList[0]==14):
                rankList[0] = 2
                rankList.sort(reverse=True)
                distance = (rankList[0] - rankList[1]) + (rankList[1]-rankList[2]) - 2

                if(distance<2):
                    straightFlush=False
            else:
                straightFlush=False


    straightFlushProbability = 0
    if(straightFlush==True):
        suitNeeded = Card.INT_SUIT_TO_CHAR_SUIT[list(suitSet)[0]]
        cards_ranks_needed=[]

        for sequence in straightSequences:
            difference = sequence.difference(set(rankList))
            if(len(difference)<=2):
                cards_ranks_needed.append(sequence.difference(set(rankList)))
        
        cards_needed = []
        for cards in cards_ranks_needed:
            temp = []
            for rank in cards:
                if(Card.new(rank_map[rank]+suitNeeded) not in hand):
                    temp.append(Card.new(rank_map[rank]+suitNeeded))
            if(len(temp)==2):
                cards_needed.append(temp)

        straightFlushProbability = 1 - (1 - len(cards_needed)/1081) ** num_players

    straightFlushPossibleProbability = 0.0

    return straightFlushProbability, straightFlushPossibleProbability

def simulation(card1, card2, flop, num_players, simulations=1000):
    
    hand = [Card.new(card1), Card.new(card2)]

    evaluator = Evaluator()

    oddsList = []
    for _ in range(10):
        wins = 0
        for i in range(simulations):
            board = [Card.new(flop[0]), Card.new(flop[1]), Card.new(flop[2])]
            deck = Deck()
            deck.shuffle()

            for card in hand:
                if card in deck.cards:
                    deck.cards.remove(card)

            for card in board:
                if card in deck.cards:
                    deck.cards.remove(card)
            # Deal other players' hands
            opponents_hands = []
            for _ in range(num_players - 1):
                opponents_hands.append(deck.draw(2))
            
            for opp_hand in opponents_hands:
                score = evaluator.evaluate(board, opp_hand)
                if(score>=1 and score<=10):
                    wins+=1
                    break

            # deck.draw(1) #burn card (before flop)

            # deck.draw(1) #burn card (before turn)
            # board.append(deck.draw(1)[0]) #turn

            # deck.draw(1) #burn card (before river)
            # board.append(deck.draw(1)[0]) #river


            # for opp_hand in opponents_hands:
            #     score = evaluator.evaluate(board, opp_hand)
            #     if(score>=1 and score<=10):
            #         wins+=1
            #         break

        odds = wins/simulations
        return odds
deck = Deck()

# postFlopOdds("5d","7h",["As","Ts","Qs"],deck, 2)

evaluator = Evaluator()


players = [2, 3, 5, 8, 10, 15, 20, 22]


# calculatedProbability = postFlopOdds("Qc","3d",["Th","Kh","Jh"],Deck(),2)


# for num in players:

#     print(f"Number of players: {num}")

#     for i in range(100):
#         deck1=Deck()
#         card1 = Card.int_to_str(deck1.draw(1)[0])
#         card2= Card.int_to_str(deck1.draw(1)[0])

#         flop1= Card.int_to_str(deck1.draw(1)[0])
#         flop2= Card.int_to_str(deck1.draw(1)[0])
#         flop3= Card.int_to_str(deck1.draw(1)[0])

#         calculatedProbability = postFlopOdds(card1,card2,[flop1,flop2,flop3],Deck(),num)
#         simulatedProbability = simulation(card1,card2,[flop1,flop2,flop3],num)


#         difference = calculatedProbability- simulatedProbability

#         if(abs(difference)>0.01):
#             print("Large difference")
#             print(f"Difference: {calculatedProbability-simulatedProbability}")
#             print(f"{calculatedProbability} , {simulatedProbability}")
#             print([card1,card2])
#             print([flop1,flop2,flop3])

#             print("\n")