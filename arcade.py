import random
from typing import Self
import functools

# a simple pluralization utility
# variants hold cases for cardinality of 1,2,3,...
# defaults to last cardinality
def pluralize(n: int, singular: str, *plurals: list[str]) -> str:
    v = [singular, *plurals]
    return v[n-1] if n >= 1 and n <= len(v) else v[-1]

# a simple natural choice text generator
# naturalchoice(["a","b","c"], "or") -> "a, b or c"
def naturalchoice(alternatives: list[str], sep: str) -> str:
    last = alternatives[-1]
    upToLast = alternatives[:-1]
    return f"{", ".join(upToLast)}{sep}{last}"

# Abstract base class for guessing games that request input, displays status and progresses to next state in a loop
class GameState:
    # game loop terminator
    def done(self) -> bool:
        return True
    # message to player
    def info(self) -> str:
        return ""
    # prompt for input
    def prompt(self) -> str:
        return ""
    # handle non empty inoput and progress to next state
    def next(self, answer: str) -> Self:
        return self
    # interactive game loop
    def run(self) -> Self:
        game = self
        while (not game.done()):
            answer = input(game.prompt())
            if answer:
                game = game.next(answer)
                info = game.info()
                if (info):
                    print(info)
        return game

# A finished game. Just repeats itself and doesnt progress
class FinishedGame(GameState):
    message: str
    def __init__(self, word: str):
        self.message = word
    def next(self, answer: str) -> Self:
        return self
    def info(self):
        return self.message

############################################################
#
# Hangman section
#
############################################################
# A round of hangman. Tracks correct word, guesses etc and acts as a factory for next round
class Hangman(GameState):
    word: str
    guessed: set[str]
    guessesLeft: int

    @staticmethod
    def create(guessesLeft: int, words: list[str]):
        return Hangman(guessesLeft, random.choice(words))

    def __init__(self, guessesLeft: int, word: str, guessed: set[str] = set()):
        self.guessesLeft = guessesLeft
        self.word = word
        self.guessed = guessed

    def prompt(self) -> str:
        return f"Gissa en bokstav i ordet ({self.maskedWord()}) ({self.guessesLeft} {pluralize(self.guessesLeft, "gissning", "gissningar")} kvar)? "

    def next(self, answer) -> Self:
        guessedChar,*_ = answer.lower()
        correctGuess = guessedChar in self.word.lower()
        print(f"Du gissage {"rätt :)" if correctGuess else "fel"}")
        gl = self.guessesLeft if guessedChar in self.guessed or correctGuess else self.guessesLeft - 1
        g = self.guessed.union([guessedChar])
        foundWord = set(self.word.lower()).issubset(g)
        return FinishedGame(f"Du hittade ordet {self.word}") if foundWord else FinishedGame(f"Du hittade inte ordet {self.word}") if gl < 1 else Hangman(gl, self.word, g)

    def maskedWord(self) -> str:
        return "".join([c if c.lower() in self.guessed else "_" for c in self.word])

    def done(self) -> bool:
        return False

############################################################
#
# Rock Scissor Paper section
#
############################################################
class RockScissorPaper(GameState):
    alternatives = ['sten', 'sax', 'påse']
    winsOver = [1, 2, 0]

    def done(self):
        return False

    def prompt(self):
        return f"Välj något av {naturalchoice(self.alternatives," eller ")}: "

    def next(self, answer):
        if not answer in self.alternatives:
            return self
        userChoiceIndex = self.alternatives.index(answer)
        computerChoiceIndex = random.randint(0, len(self.alternatives)-1)
        computerChoice = self.alternatives[computerChoiceIndex]
        if (computerChoiceIndex == userChoiceIndex):
            return FinishedGame('Oavgjort')
        if (self.winsOver[userChoiceIndex] == computerChoiceIndex):
            return FinishedGame(f"Du vann mot {computerChoice}")
        return FinishedGame(f"Du förlorar mot {computerChoice}")

############################################################
#
# Blackjack section
#
############################################################
# a card have a human readable description and a numeric value
class BlackjackCard:
    value: int
    label: str

    def __init__(self, label: str, value: int) -> None:
        self.label = label
        self.value = value

# A deck is a shuffled list of unique cards from wich indivuídual cards can be drawn
class BlackjackDeck:
    cardColor = ['Spader','Hjärter','Ruter','Klöver']
    cardName = ["Ess","Två","Tre","Fyra","Fem","Sex","Sju","Åtta","Nio","Tio","Knekt","Dam","Kung"]
    cardValue = [11,2,3,4,5,6,7,8,9,10,10,10,10] # we dont consider that Ace can have values 1 or 11
    cards: list[BlackjackCard]

    def __init__(self) -> None:
        cards = [BlackjackCard(f"{self.cardColor[i % 4]} {self.cardName[i % 13]}", self.cardValue[i % 13]) for i in range(1, 52)]
        random.shuffle(cards)
        self.cards = cards

    def drawCard(self) -> BlackjackCard:
        return self.cards.pop()

# A hand is a list of cards that can be extended with more cards from a deck
class BlackjackHand:
    deck: BlackjackDeck
    cards: list[BlackjackCard]

    def __init__(self, deck: BlackjackDeck) -> None:
        self.deck = deck
        self.cards = []

    def takeCard(self) -> Self:
        self.cards.append(self.deck.drawCard())
        return self

    def takeCardsUntilValue(self, v: int):
        while (self.value() < v):
            self.takeCard()

    def value(self) -> int:
        return functools.reduce(lambda a, c: a + c.value, self.cards, 0)

# A Blackjack game tracks hands of the bank and a player
class Blackjack(GameState):
    bankHand: BlackjackHand
    playerHand: BlackjackHand

    def __init__(self) -> None:
        super().__init__()
        deck = BlackjackDeck()
        self.bankHand = BlackjackHand(deck).takeCard().takeCard()
        self.playerHand = BlackjackHand(deck).takeCard().takeCard()

    def done(self) -> bool:
        return False

    def prompt(self) -> str:
        return f"""
            Bankens hand: (Dolt kort), {self.bankHand.cards[0].label}
            Din hand: {", ".join(card.label for card in self.playerHand.cards)}, totalt värde {self.playerHand.value()}
            Ditt val (hit eller stand): """

    def next(self, answer: str) -> Self:
        if (answer == "stand"):
            self.bankHand.takeCardsUntilValue(17)
            return self.end()
        if (answer == "hit"):
            self.playerHand.takeCard()
            if (self.playerHand.value() > 21):
                return self.end()
        return self

    def end(self):
        bankValue = self.bankHand.value()
        playerValue = self.playerHand.value()
        playerWon = (playerValue > bankValue and playerValue <= 21) or bankValue > 21
        return FinishedGame(f"""
            Bankens hand: {", ".join(card.label for card in self.bankHand.cards)}, totalt värde {bankValue}
            Din hand: {", ".join(card.label for card in self.playerHand.cards)}, totalt värde {playerValue}

            {"Du vann" if playerWon else "Banken vann"}
                            """)

############################################################
#
# Arcade/Menu section
#
############################################################
class Menu(GameState):
    def done(self) -> bool:
        return False

    def prompt(self) -> str:
        return """
            Vad vill du spela?
            (1) Blackjack
            (2) Hänga gubbe
            (3) Sten, sax, påse
            (x) Avsluta
            ? """

    def next(self, answer):
        print(answer)
        if (answer == "1"):
            Blackjack().run()
        if (answer == "2"):
            Hangman.create(guessesLeft=5, words=['Apa',"Björn","Cikada", "Dvärghamster", "Elefant", "Flodhäst", "Giraff"]).run()
        if (answer == "3"):
            RockScissorPaper().run()
        if (answer == "x"):
            return FinishedGame("")
        return self


# Main program
Menu().run()
