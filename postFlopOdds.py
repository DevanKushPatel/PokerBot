import random
from treys import Card, Deck, Evaluator

def postFlopOdds(card1,card2, flop, num_players=2):
    
    evaluator = Evaluator()
    hand = [Card.new(card1), Card.new(card2)]
    board = [Card.new(flop[0]), Card.new(flop[1]), Card.new(flop[2])]

    deck = Deck()

    for card in hand:
        if card in deck.cards:
            deck.cards.remove(card)

    for card in board:
        if(card in deck.cards):
            deck.cards.remove(card)

    p1_score = evaluator.evaluate(board, hand)
    p1_class = evaluator.get_rank_class(p1_score)

    print("Player 1 hand rank = %d (%s)\n" % (p1_score, evaluator.class_to_string(p1_class)))
    
    Card.print_pretty_cards(hand)
    Card.print_pretty_cards(board)


postFlopOdds("5d","7h",["Js","7s","Ks"],3)