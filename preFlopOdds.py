import random
from treys import Card, Deck, Evaluator

def preflop_odds(card1, card2, num_players=2, simulations=10000):
    """
    Calculate preflop win odds for Texas Hold'em using Monte Carlo simulation.

    Args:
        card1 (str): First hole card (e.g., 'As', 'Kd')
        card2 (str): Second hole card (e.g., 'Qh', 'Jc')
        num_players (int): Total number of players at the table
        simulations (int): Number of Monte Carlo simulations

    Returns:
        float: Estimated probability of winning preflop
    """
    evaluator = Evaluator()

    # Convert string cards to Treys card objects
    hand = [Card.new(card1), Card.new(card2)]
    wins = 0

    for _ in range(simulations):
        deck = Deck()
        deck.shuffle()
        
        # Remove player's hand from deck
        for card in hand:
            if card in deck.cards:
                deck.cards.remove(card)
        
        # Deal other players' hands
        opponents_hands = []
        for _ in range(num_players - 1):
            opp_hand = [deck.draw(2)]
            opponents_hands.append(opp_hand)
        
        # Deal the board
        board = [deck.draw(1)[0] for _ in range(5)]
        
        # Evaluate hands
        player_score = evaluator.evaluate(board, hand)
        opponent_scores = [evaluator.evaluate(board, opp_hand) for opp_hand in opponents_hands]
        
        if player_score <= min(opponent_scores):
            wins += 1

    odds = wins/simulations
    difference = odds - (1/num_players)

    return odds, difference


