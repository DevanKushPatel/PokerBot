import random
from treys import Card, Deck, Evaluator
from itertools import combinations, product

def preflop_odds_all(num_players=2, simulations=10000):
    """
    Calculate preflop win odds for all starting hands in Texas Hold'em using Monte Carlo simulation.
    
    Args:
        num_players (int): Total number of players at the table
        simulations (int): Number of Monte Carlo simulations
        
    Returns:
        dict: Dictionary mapping starting hands to estimated winning probabilities
    """
    ranks = '23456789TJQKA'
    suits = 'cdhs'  # clubs, diamonds, hearts, spades
    evaluator = Evaluator()
    
    odds_dict = {}

    # Generate all starting hand combinations
    for r1 in ranks:
        for r2 in ranks:
            if r1 == r2:
                # Pocket pair: only one combination (suits don't matter)
                hand_str = r1 + r2
                card_combos = [Card.new(r1+s1) for s1 in suits[:2]]  # pick first two suits arbitrarily
            else:
                # Suited combination
                hand_str_suited = r1 + r2 + 's'
                hand_str_offsuit = r1 + r2 + 'o'
                
                # Suited: pick one suit arbitrarily
                card_combos_suited = [Card.new(r1+suits[0]), Card.new(r2+suits[0])]
                # Offsuit: pick two different suits arbitrarily
                card_combos_offsuit = [Card.new(r1+suits[0]), Card.new(r2+suits[1])]
                
                # Store odds for suited
                odds_dict[hand_str_suited] = estimate_odds(card_combos_suited, num_players, simulations)
                # Store odds for offsuit
                odds_dict[hand_str_offsuit] = estimate_odds(card_combos_offsuit, num_players, simulations)
                continue

            # Store odds for pocket pair
            odds_dict[hand_str] = estimate_odds(card_combos, num_players, simulations)
    
    return odds_dict


def estimate_odds(hand, num_players, simulations):
    evaluator = Evaluator()
    wins = 0
    
    for _ in range(simulations):
        deck = Deck()
        deck.shuffle()
        # Remove player's hand from deck
        for card in hand:
            if card in deck.cards:
                deck.cards.remove(card)
        
        # Deal opponents' hands
        opponents_hands = []
        for _ in range(num_players - 1):
            opponents_hands.append([deck.draw(1)[0], deck.draw(1)[0]])
        
        # Deal the board
        board = [deck.draw(1)[0] for _ in range(5)]
        
        player_score = evaluator.evaluate(board, hand)
        opponent_scores = [evaluator.evaluate(board, opp_hand) for opp_hand in opponents_hands]
        
        if player_score <= min(opponent_scores):
            wins += 1
    
    return wins / simulations


# Example usage:
num_players = 6
simulations = 10000  # reduce to speed up computation
all_odds = preflop_odds_all(num_players, simulations)

# Print some examples
for hand, odds in list(all_odds.items())[:10]:
    print(f"{hand}: {odds*100:.2f}%")
