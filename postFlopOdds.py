import random
from treys import Card, Deck, Evaluator
from math import comb

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

    print("Player 1 hand rank = %d (%s)\n" % (p1_score, p1_class))
    
    Card.print_pretty_cards(hand)
    Card.print_pretty_cards(board)
    print("\n")

    royalFlushEvaluator(hand, board, deck, num_players)

def royalFlushEvaluator(hand, board, deck, num_players):
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
            Card.print_pretty_cards(list(royalFlushCards))

            probability = (num_players-1)/comb(len(deck.cards),2)

            print(probability)

            # print(deck)

    if(royalFlush_possible==True):
        for suit in suitSet:
            suit = Card.INT_SUIT_TO_CHAR_SUIT[suit]
            royalFlushCards = {Card.new("A"+suit), Card.new("K"+suit), Card.new("Q"+suit), Card.new("J"+suit), Card.new("T"+suit)}.difference(set(board))
            for card in hand:
                if(card in royalFlushCards):
                    royalFlush_possible=False
            
            # Card.print_pretty_cards(list(royalFlushCards))

def simulation(card1, card2, flop, target, simulations=100000):


    # Convert string cards to Treys card objects
    hand = [Card.new(card1), Card.new(card2)]
    board = [Card.new(flop[0]), Card.new(flop[1]), Card.new(flop[2])]
    target_hand = [Card.new(target[0]), Card.new(target[1])]



    players = [2, 3, 5, 8, 10, 15, 20, 22]

    for num_players in players:
        oddsList = []
        for _ in range(10):
            wins = 0
            for i in range(simulations):
                # print(i)
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
                    if(opp_hand[0] in target_hand):
                        if(opp_hand[1] in target_hand):
                            # print(opp_hand)
                            wins +=1
                            break

            odds = wins/simulations
            oddsList.append(odds)
        print(f"Number of Players: {num_players}, {(sum(oddsList) / len(oddsList)) * 100:.10f}%")

deck = Deck()

postFlopOdds("5d","7h",["As","Ts","Qs"],deck, 2)

# simulation("5d","7h",["As","Ts","Qs"],["Ks", "Js"])

# Number of Players: 2, 0.0955000000%
# Number of Players: 3, 0.1840000000%
# Number of Players: 5, 0.3655000000%
# Number of Players: 8, 0.6368000000%
# Number of Players: 10, 0.8217000000%
# Number of Players: 15, 1.3052000000%
# Number of Players: 20, 1.7381000000%
# Number of Players: 22, 1.9387000000%
