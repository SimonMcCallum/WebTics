#include <iostream>
#include <vector>
#include <string>
#include <ctime>
#include <cstdlib>
#include <sstream>
#include "../../inc/WebTics.h"
#include "../../inc/WebTicsDefines.h"
#include "BlackjackEvents.h"

using namespace std;
using namespace BlackjackEvents;

// Card structure
struct Card {
    cardRanks rank;
    cardSuits suit;

    string toString() const {
        stringstream ss;
        ss << rankNames[rank] << " of " << suitNames[suit];
        return ss.str();
    }

    int getValue() const {
        if (rank >= JACK) return 10;
        if (rank == ACE) return 11; // Aces can be 1 or 11, handled separately
        return rank;
    }
};

// Deck class
class Deck {
private:
    vector<Card> cards;
    int currentCard;

public:
    Deck() {
        reset();
    }

    void reset() {
        cards.clear();
        currentCard = 0;

        // Create a standard 52-card deck
        for (int s = 0; s < MAX_SUITS; s++) {
            for (int r = ACE; r <= KING; r++) {
                Card card;
                card.rank = static_cast<cardRanks>(r);
                card.suit = static_cast<cardSuits>(s);
                cards.push_back(card);
            }
        }
        shuffle();
    }

    void shuffle() {
        srand(static_cast<unsigned int>(time(NULL)));
        for (int i = cards.size() - 1; i > 0; i--) {
            int j = rand() % (i + 1);
            Card temp = cards[i];
            cards[i] = cards[j];
            cards[j] = temp;
        }
        currentCard = 0;
    }

    Card deal() {
        if (currentCard >= cards.size()) {
            cout << "\n[Reshuffling deck...]" << endl;
            shuffle();
        }
        return cards[currentCard++];
    }
};

// Hand class
class Hand {
private:
    vector<Card> cards;

public:
    void addCard(const Card& card) {
        cards.push_back(card);
    }

    void clear() {
        cards.clear();
    }

    int getValue() const {
        int value = 0;
        int aces = 0;

        for (const Card& card : cards) {
            value += card.getValue();
            if (card.rank == ACE) aces++;
        }

        // Adjust for Aces
        while (value > 21 && aces > 0) {
            value -= 10;
            aces--;
        }

        return value;
    }

    bool isBust() const {
        return getValue() > 21;
    }

    bool isBlackjack() const {
        return cards.size() == 2 && getValue() == 21;
    }

    void display(bool hideFirst = false) const {
        cout << "  Cards: ";
        for (size_t i = 0; i < cards.size(); i++) {
            if (i == 0 && hideFirst) {
                cout << "[Hidden]";
            } else {
                cout << cards[i].toString();
            }
            if (i < cards.size() - 1) cout << ", ";
        }

        if (!hideFirst) {
            cout << " (Value: " << getValue() << ")";
        }
        cout << endl;
    }

    size_t getCardCount() const {
        return cards.size();
    }

    const Card& getCard(size_t index) const {
        return cards[index];
    }
};

// Blackjack Game with WebTics integration
class BlackjackGame {
private:
    Deck deck;
    Hand playerHand;
    Hand dealerHand;
    int playerChips;
    int currentBet;
    WebTics* metrics;
    int handNumber;
    int gamesPlayed;
    int gamesWon;
    int gamesLost;
    int gamesPushed;

public:
    BlackjackGame() : playerChips(1000), currentBet(0), handNumber(0),
                      gamesPlayed(0), gamesWon(0), gamesLost(0), gamesPushed(0) {
        metrics = WebTics::GetInstance();
    }

    void initialize() {
        cout << "\n=== WebTics Blackjack Server ===" << endl;
        cout << "Initializing WebTics telemetry system..." << endl;

        // Initialize WebTics
        string server = "localhost";
        string path = "/WebTics/";
        metrics->Initialise(&server, &path);

        // Open metric session with unique ID
        string uniqueID = "BlackjackServer_v1.0";
        metrics->OpenMetricSession(uniqueID);

        cout << "WebTics telemetry active!" << endl;
        cout << "\nStarting chips: $" << playerChips << endl;
    }

    void placeBet() {
        cout << "\nYou have $" << playerChips << " in chips." << endl;
        cout << "Enter bet amount (or 0 to quit): $";
        cin >> currentBet;

        if (currentBet == 0) {
            return;
        }

        while (currentBet < 0 || currentBet > playerChips) {
            cout << "Invalid bet! Enter amount between $1 and $" << playerChips << ": $";
            cin >> currentBet;
        }

        // Log bet event
        string betData = "Bet: $" + to_string(currentBet) + ", Chips: $" + to_string(playerChips);
        metrics->LogEvent(BET_PLACED, currentBet, &betData);
    }

    void dealInitialCards() {
        playerHand.clear();
        dealerHand.clear();

        // Deal two cards to player
        Card card1 = deck.deal();
        playerHand.addCard(card1);
        logCardDealt(card1, true);

        // Deal one card to dealer (face up)
        Card dealerCard1 = deck.deal();
        dealerHand.addCard(dealerCard1);
        logCardDealt(dealerCard1, false);

        // Deal second card to player
        Card card2 = deck.deal();
        playerHand.addCard(card2);
        logCardDealt(card2, true);

        // Deal second card to dealer (face down)
        Card dealerCard2 = deck.deal();
        dealerHand.addCard(dealerCard2);

        // Log hand dealt event
        handNumber++;
        string handData = "Hand #" + to_string(handNumber) + ", Player: " +
                         to_string(playerHand.getValue()) + ", Dealer up card: " +
                         dealerCard1.toString();
        metrics->LogEvent(HAND_DEALT, handNumber, &handData);
    }

    void logCardDealt(const Card& card, bool toPlayer) {
        string cardData = card.toString() + " to " + (toPlayer ? "Player" : "Dealer");
        metrics->LogEvent(CARD_DEALT, card.suit, card.getValue(), &cardData);
    }

    bool playerTurn() {
        cout << "\n--- Your Turn ---" << endl;

        while (true) {
            cout << "\nDealer shows: " << dealerHand.getCard(0).toString() << endl;
            cout << "Your hand:" << endl;
            playerHand.display();

            if (playerHand.isBust()) {
                cout << "\nBUST! You lose." << endl;
                string bustData = "Player bust with " + to_string(playerHand.getValue());
                metrics->LogEvent(PLAYER_BUST, playerHand.getValue(), &bustData);
                return false;
            }

            if (playerHand.isBlackjack() && playerHand.getCardCount() == 2) {
                cout << "\nBLACKJACK!" << endl;
                string bjData = "Player blackjack!";
                metrics->LogEvent(PLAYER_BLACKJACK, 21, &bjData);
                return true;
            }

            cout << "\n(H)it or (S)tand? ";
            char choice;
            cin >> choice;
            choice = tolower(choice);

            if (choice == 'h') {
                Card newCard = deck.deal();
                cout << "\nYou drew: " << newCard.toString() << endl;
                playerHand.addCard(newCard);
                logCardDealt(newCard, true);

                string hitData = "Player hit, new total: " + to_string(playerHand.getValue());
                metrics->LogEvent(PLAYER_HIT, playerHand.getValue(), &hitData);
            } else if (choice == 's') {
                string standData = "Player stands at " + to_string(playerHand.getValue());
                metrics->LogEvent(PLAYER_STAND, playerHand.getValue(), &standData);
                break;
            } else {
                cout << "Invalid choice. Please enter H or S." << endl;
            }
        }

        return true;
    }

    void dealerTurn() {
        cout << "\n--- Dealer's Turn ---" << endl;
        cout << "Dealer reveals:" << endl;
        dealerHand.display();

        string dealerStart = "Dealer starts with " + to_string(dealerHand.getValue());
        metrics->LogEvent(DEALER_TURN, dealerHand.getValue(), &dealerStart);

        // Dealer must hit on 16 or less, stand on 17 or more
        while (dealerHand.getValue() < 17) {
            cout << "\nDealer hits..." << endl;
            Card newCard = deck.deal();
            cout << "Dealer drew: " << newCard.toString() << endl;
            dealerHand.addCard(newCard);
            logCardDealt(newCard, false);

            string hitData = "Dealer hit, new total: " + to_string(dealerHand.getValue());
            metrics->LogEvent(DEALER_HIT, dealerHand.getValue(), &hitData);

            dealerHand.display();
        }

        if (dealerHand.isBust()) {
            cout << "\nDealer BUSTS!" << endl;
            string bustData = "Dealer bust with " + to_string(dealerHand.getValue());
            metrics->LogEvent(DEALER_BUST, dealerHand.getValue(), &bustData);
        } else {
            cout << "\nDealer stands at " << dealerHand.getValue() << endl;
        }
    }

    void determineWinner() {
        int playerValue = playerHand.getValue();
        int dealerValue = dealerHand.getValue();

        cout << "\n=== Results ===" << endl;
        cout << "Your hand: " << playerValue << endl;
        cout << "Dealer hand: " << dealerValue << endl;

        if (playerHand.isBust()) {
            cout << "\nYou LOSE! (Bust)" << endl;
            playerChips -= currentBet;
            gamesLost++;
            string loseData = "Player lost $" + to_string(currentBet) + " (Bust)";
            metrics->LogEvent(PLAYER_LOSE, currentBet, &loseData);
        } else if (dealerHand.isBust()) {
            cout << "\nYou WIN! (Dealer bust)" << endl;
            int winAmount = currentBet;
            if (playerHand.isBlackjack()) {
                winAmount = static_cast<int>(currentBet * 1.5);
                cout << "BLACKJACK pays 3:2!" << endl;
            }
            playerChips += winAmount;
            gamesWon++;
            string winData = "Player won $" + to_string(winAmount) + " (Dealer bust)";
            metrics->LogEvent(PLAYER_WIN, winAmount, &winData);
        } else if (playerValue > dealerValue) {
            cout << "\nYou WIN!" << endl;
            int winAmount = currentBet;
            if (playerHand.isBlackjack()) {
                winAmount = static_cast<int>(currentBet * 1.5);
                cout << "BLACKJACK pays 3:2!" << endl;
            }
            playerChips += winAmount;
            gamesWon++;
            string winData = "Player won $" + to_string(winAmount);
            metrics->LogEvent(PLAYER_WIN, winAmount, &winData);
        } else if (playerValue < dealerValue) {
            cout << "\nYou LOSE!" << endl;
            playerChips -= currentBet;
            gamesLost++;
            string loseData = "Player lost $" + to_string(currentBet);
            metrics->LogEvent(PLAYER_LOSE, currentBet, &loseData);
        } else {
            cout << "\nPUSH! (Tie)" << endl;
            gamesPushed++;
            string pushData = "Push at " + to_string(playerValue);
            metrics->LogEvent(PLAYER_PUSH, 0, &pushData);
        }

        cout << "\nCurrent chips: $" << playerChips << endl;
    }

    void playHand() {
        gamesPlayed++;

        // Log game start
        string gameData = "Game #" + to_string(gamesPlayed) + ", Starting chips: $" + to_string(playerChips);
        metrics->LogEvent(GAME_START, gamesPlayed, &gameData);

        dealInitialCards();

        // Check for immediate blackjack
        if (playerHand.isBlackjack()) {
            cout << "\n*** BLACKJACK! ***" << endl;
            playerHand.display();
            cout << "\nDealer shows:" << endl;
            dealerHand.display();

            if (dealerHand.isBlackjack()) {
                cout << "\nDealer also has blackjack! PUSH!" << endl;
                gamesPushed++;
                string pushData = "Both blackjack, push";
                metrics->LogEvent(PLAYER_PUSH, 0, &pushData);
            } else {
                cout << "\nYou WIN with Blackjack! Pays 3:2" << endl;
                int winAmount = static_cast<int>(currentBet * 1.5);
                playerChips += winAmount;
                gamesWon++;
                string winData = "Player won $" + to_string(winAmount) + " with blackjack";
                metrics->LogEvent(PLAYER_WIN, winAmount, &winData);
            }
        } else {
            // Normal gameplay
            bool playerStanding = playerTurn();

            if (playerStanding) {
                dealerTurn();
                determineWinner();
            } else {
                // Player busted
                playerChips -= currentBet;
                gamesLost++;
            }
        }

        // Log game end
        string endData = "Game #" + to_string(gamesPlayed) + " ended, Chips: $" +
                        to_string(playerChips) + ", Win rate: " +
                        to_string(gamesWon * 100.0 / gamesPlayed) + "%";
        metrics->LogEvent(GAME_END, playerChips, &endData);
    }

    void run() {
        initialize();

        while (playerChips > 0) {
            cout << "\n" << string(50, '=') << endl;
            placeBet();

            if (currentBet == 0) {
                cout << "\nThanks for playing!" << endl;
                break;
            }

            playHand();

            if (playerChips <= 0) {
                cout << "\n*** OUT OF CHIPS! Game Over! ***" << endl;
                break;
            }
        }

        // Display final statistics
        displayStatistics();

        // Close WebTics session
        cout << "\nClosing WebTics telemetry session..." << endl;
        metrics->StopPlaySession();
        metrics->CloseMetricSession();
        cout << "Session closed. All telemetry data has been saved." << endl;
    }

    void displayStatistics() {
        cout << "\n" << string(50, '=') << endl;
        cout << "=== Game Statistics ===" << endl;
        cout << string(50, '=') << endl;
        cout << "Total hands played: " << gamesPlayed << endl;
        cout << "Hands won: " << gamesWon << endl;
        cout << "Hands lost: " << gamesLost << endl;
        cout << "Pushes: " << gamesPushed << endl;
        if (gamesPlayed > 0) {
            cout << "Win rate: " << (gamesWon * 100.0 / gamesPlayed) << "%" << endl;
        }
        cout << "Final chips: $" << playerChips << endl;
        cout << "Net gain/loss: $" << (playerChips - 1000) << endl;
        cout << string(50, '=') << endl;
    }
};

// Main function
int main() {
    cout << "WebTics Blackjack Server - Text-based Blackjack with Telemetry" << endl;
    cout << "=============================================================" << endl;

    BlackjackGame game;
    game.run();

    cout << "\nPress Enter to exit...";
    cin.ignore();
    cin.get();

    return 0;
}
