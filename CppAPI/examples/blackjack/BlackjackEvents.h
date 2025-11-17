#ifndef _BLACKJACK_EVENTS_
#define _BLACKJACK_EVENTS_

#include <string>

namespace BlackjackEvents
{
    // Event types for Blackjack game
    enum eventTypes
    {
        GAME_START = 100,        // New game started
        GAME_END,                // Game ended
        HAND_DEALT,              // Initial cards dealt
        PLAYER_HIT,              // Player requested a card
        PLAYER_STAND,            // Player stands
        PLAYER_BUST,             // Player busted (over 21)
        PLAYER_BLACKJACK,        // Player got blackjack
        DEALER_TURN,             // Dealer's turn started
        DEALER_HIT,              // Dealer drew a card
        DEALER_BUST,             // Dealer busted
        PLAYER_WIN,              // Player won the hand
        PLAYER_LOSE,             // Player lost the hand
        PLAYER_PUSH,             // Push (tie)
        BET_PLACED,              // Bet was placed
        CARD_DEALT,              // Individual card dealt
        MAX_EVENT_TYPES
    };

    static const char* const eventTypeNames[MAX_EVENT_TYPES - 100] = {
        "Game Started",
        "Game Ended",
        "Hand Dealt",
        "Player Hit",
        "Player Stand",
        "Player Bust",
        "Player Blackjack",
        "Dealer Turn",
        "Dealer Hit",
        "Dealer Bust",
        "Player Win",
        "Player Lose",
        "Push",
        "Bet Placed",
        "Card Dealt"
    };

    // Card suits as event subtypes
    enum cardSuits
    {
        HEARTS = 0,
        DIAMONDS,
        CLUBS,
        SPADES,
        MAX_SUITS
    };

    static const char* const suitNames[MAX_SUITS] = {
        "Hearts",
        "Diamonds",
        "Clubs",
        "Spades"
    };

    // Card ranks
    enum cardRanks
    {
        ACE = 1,
        TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN,
        JACK, QUEEN, KING,
        MAX_RANKS
    };

    static const char* const rankNames[MAX_RANKS] = {
        "", "Ace", "Two", "Three", "Four", "Five", "Six",
        "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"
    };
}

#endif
