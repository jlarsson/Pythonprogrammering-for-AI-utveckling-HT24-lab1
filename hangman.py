import random
from typing import Self

# a simple pluralization utility
# variants hold cases for cardinality of 1,2,3,...
# defaults to last cardinality
def pluralize(n: int, singular: str, *plurals: list[str]) -> str:
    v = [singular, *plurals]
    return v[n-1] if n >= 1 and n <= len(v) else v[-1]

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
        #print(f"facit: {word}")

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


# main
Hangman.create(guessesLeft=5, words=['Apa',"Björn","Cikada", "Dvärghamster", "Elefant", "Flodhäst", "Giraff"]).run()