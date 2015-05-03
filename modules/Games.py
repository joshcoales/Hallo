from Function import Function
import random
import time
from inc.commons import Commons
from xml.dom import minidom

class Card:
    '''
    Card object, for use by higher or lower, blackjack, and any other card games.
    '''
    #Constants
    SUIT_DIAMONDS = "diamonds"
    SUIT_HEARTS = "hearts"
    SUIT_CLUBS = "clubs"
    SUIT_SPADES = "spades"
    COLOUR_RED = "red"
    COLOUR_BLACK = "black"
    CARD_ACE = 1
    CARD_2 = 2
    CARD_3 = 3
    CARD_4 = 4
    CARD_5 = 5
    CARD_6 = 6
    CARD_7 = 7
    CARD_8 = 8
    CARD_9 = 9
    CARD_10 = 10
    CARD_JACK = "jack"
    CARD_QUEEN = "queen"
    CARD_KING = "king"
    #Parameters
    mDeck = None
    mSuit = None
    mColour = None
    mValue = None
    mInDeck = True

    def __init__(self,deck,suit,value):
        '''
        Constructor
        '''
        self.mDeck = deck
        if(suit in [self.SUIT_DIAMONDS,self.SUIT_HEARTS]):
            self.mSuit = suit
            self.mColour = self.COLOUR_RED
        elif(suit in [self.SUIT_CLUBS,self.SUIT_SPADES]):
            self.mSuit = suit
            self.mColour = self.COLOUR_BLACK
        else:
            raise Exception("Invalid suit")
        if(value in [self.CARD_ACE,self.CARD_2,self.CARD_3,self.CARD_4,self.CARD_5,self.CARD_6,self.CARD_7,self.CARD_8,self.CARD_9,self.CARD_10,self.CARD_JACK,self.CARD_QUEEN,self.CARD_KING]):
            self.mValue = value
        else:
            raise Exception("Invalid value")
    
    def __str__(self):
        return self.toString()
    
    def toString(self):
        'Outputs a string representing the card\'s value and suit.'
        if(self.mValue == self.CARD_ACE):
            cardValue = "Ace"
        elif(self.mValue == self.CARD_JACK):
            cardValue = "Jack"
        elif(self.mValue == self.CARD_QUEEN):
            cardValue = "Queen"
        elif(self.mValue == self.CARD_KING):
            cardValue = "King"
        else:
            cardValue = str(self.mValue)
        if(self.mSuit == self.SUIT_CLUBS):
            cardSuit = "clubs"
        elif(self.mSuit == self.SUIT_DIAMONDS):
            cardSuit = "diamonds"
        elif(self.mSuit == self.SUIT_HEARTS):
            cardSuit = "hearts"
        elif(self.mSuit == self.SUIT_SPADES):
            cardSuit = "spades"
        else:
            raise Exception("invalid suit")
        return cardValue + " of " + cardSuit
        
    def sumValue(self):
        'Outputs the value as an integer.'
        if(self.mValue in [self.CARD_JACK,self.CARD_QUEEN,self.CARD_KING]):
            return 10
        return int(self.mValue)
    
    def __int__(self):
        return self.toInt()
    
    def toInt(self):
        'Converts the card value to integer, for higher or lower and similar'
        if(self.mValue == self.CARD_JACK):
            return 11
        if(self.mValue == self.CARD_QUEEN):
            return 12
        if(self.mValue == self.CARD_KING):
            return 13
        return self.mValue
    
    def isInDeck(self):
        'boolean, whether the card is still in the deck.'
        return self.mInDeck
    
    def setInDeck(self,inDeck):
        'mInDeck setter'
        self.mInDeck = inDeck
    
    def getSuit(self):
        'Suit getter'
        return self.mSuit
    
    def getColour(self):
        'Colour getter'
        return self.mColour
    
    def getValue(self):
        'Value getter'
        return self.mValue

class Deck:
    '''
    Deck object, for use by higher or lower, blackjack, and any other card games.
    Generates 52 cards and can then shuffle them.
    WILL NOT SHUFFLE BY DEFAULT.
    '''
    mCardList = []  #List of cards in the deck.
    mAllCards = []  #All the cards which were originally in the deck.
    
    def __init__(self):
        cardList = []
        for cardSuit in [Card.SUIT_HEARTS,Card.SUIT_CLUBS,Card.SUIT_DIAMONDS,Card.SUIT_SPADES]:
            suitList = []
            for cardValue in [Card.CARD_ACE,Card.CARD_2,Card.CARD_3,Card.CARD_4,Card.CARD_5,Card.CARD_6,Card.CARD_7,Card.CARD_8,Card.CARD_9,Card.CARD_10,Card.CARD_JACK,Card.CARD_QUEEN,Card.CARD_KING]:
                newCard = Card(self,cardSuit,cardValue)
                suitList.append(newCard)
            if(cardSuit in [Card.SUIT_DIAMONDS,Card.SUIT_SPADES]):
                suitList.reverse()
            cardList += suitList
        self.mCardList = cardList
        self.mAllCards = cardList
    
    def shuffle(self):
        'Shuffles the deck'
        random.shuffle(self.mCardList)
    
    def getNextCard(self):
        'Gets the next card from the deck'
        nextCard = self.mCardList.pop(0)
        nextCard.setInDeck(False)
        return nextCard
    
    def isEmpty(self):
        'Boolean, whether the deck is empty.'
        return len(self.mCardList) == 0
    
    def getCard(self,suit,value):
        'Returns the card object for this deck with the specified suit and value.'
        for card in self.mAllCards:
            if(suit == card.getSuit() and value == card.getValue()):
                return card
    
class Hand:
    '''
    Hand of cards, stores a set of cards in an order.
    '''
    mCardList = []
    mPlayer = None
    
    def __init__(self,userObject):
        self.mPlayer = userObject
    
    def shuffle(self):
        'Shuffles a hand'
        random.shuffle(self.mCardList)
    
    def addCard(self,newCard):
        'Adds a new card to the hand'
        self.mCardList.append(newCard)
        
    def getCardList(self):
        'Returns the card list'
        return self.mCardList
        
    def sumTotal(self):
        'Returns the sum total of the hand.'
        return sum([card.sumValue() for card in self.mCardList])
        
    def blackjackTotal(self):
        'Returns the blackjack total of the hand. (Takes aces as 11 if that doesn\'t make you bust.'
        sumTotal = self.sumTotal()
        if(sumTotal<=11 and self.containsValue(Card.CARD_ACE)):
            sumTotal += 11
        return sumTotal
    
    def containsCard(self,cardObject):
        'Checks whether a hand contains a specified card'
        return cardObject in self.mCardList
    
    def containsValue(self,value):
        'Checks whether a hand contains a specified card value'
        return value in [card.getValue() for card in self.mCardList]
    
    def countValue(self,value):
        'Counts how many cards of a specified value are in the hand'
        return [card.getValue() for card in self.mCardList].count(value)
    
    def cardsInHand(self):
        'Returns the number of cards in the hand'
        return len(self.mCardList)
    
    def __str__(self):
        return self.toString()

    def toString(self):
        'Returns a string representing the cards in the hand.'
        return ", ".join([card.toString() for card in self.mCardList])

class RandomCard(Function):
    '''
    Returns a random card from a fresh deck.
    '''
    #Name for use in help listing
    mHelpName = "card"
    #Names which can be used to address the function
    mNames = set(["card","random card","randomcard"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Picks a random card from a deck. Format: random_card"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        newDeck = Deck()
        newDeck.shuffle()
        randomCard = newDeck.getNextCard()
        return "I have chosen the " + randomCard.toString() + "."

class HighScores(Function):
    '''
    High scores function, also stores all high scores.
    '''
    #Name for use in help listing
    mHelpName = "highscores"
    #Names which can be used to address the function
    mNames = set(["highscores","high scores","highscore","high score","hiscore","hiscores"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "View the highscores for all games. Format: highscores"
    
    mHighScores = {}
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def isPersistent(self):
        'Returns boolean representing whether this function is supposed to be persistent or not'
        return True
    
    @staticmethod
    def loadFunction():
        'Loads the function, persistent functions only.'
        try:
            highScoreDict = {}
            doc = minidom.parse("store/high_score_list.xml")
            #Loop through high scores
            for highScoreXml in doc.getElementsByTagName("high_score"):
                gameDict = {}
                #Get name
                gameName = highScoreXml.getElementsByTagName("game_name")[0].firstChild.data
                #Get date, add to dict
                gameDate = highScoreXml.getElementsByTagName("date")[0].firstChild.data
                gameDict['date'] = float(gameDate)
                #Get player name, add to dict
                playerName = highScoreXml.getElementsByTagName("player_name")[0].firstChild.data
                gameDict['player'] = playerName
                #Get score, add to dict
                gameScore = highScoreXml.getElementsByTagName("score")[0].firstChild.data
                gameDict['score'] = gameScore
                #Get extra data
                gameData = {}
                for dataXml in highScoreXml.getElementsByTagName("data"):
                    dataVar = dataXml.getElementsByTagName("var")[0].firstChild.data
                    dataValue = dataXml.getElementsByTagName("value")[0].firstChild.data
                    gameData[dataVar] = dataValue
                gameDict['data'] = gameData
                #Add game to list
                highScoreDict[gameName] = gameDict
            #Create new object, set the highscore list and return it
            newHighScores = HighScores()
            newHighScores.mHighScores = highScoreDict
            return newHighScores
        except (FileNotFoundError, IOError):
            return HighScores()
    
    def saveFunction(self):
        'Saves the function, persistent functions only.'
        #TODO: save all games to XML perhaps?
        #Create document, with DTD
        docimp = minidom.DOMImplementation()
        doctype = docimp.createDocumentType(
            qualifiedName='high_score_list',
            publicId='', 
            systemId='high_score_list.dtd',
        )
        doc = docimp.createDocument(None,'high_score_list',doctype)
        #get root element
        root = doc.getElementsByTagName("high_score_list")[0]
        #Loop through games
        for gameName in self.mHighScores:
            highScoreXml = doc.createElement("high_score")
            #add game_name element
            gameNameXml = doc.createElement("game_name")
            gameNameXml.appendChild(doc.createTextNode(gameName))
            highScoreXml.appendChild(gameNameXml)
            #Add date element
            dateXml = doc.createElement("date")
            dateXml.appendChild(doc.createTextNode(self.mHighScores[gameName]['date']))
            highScoreXml.appendChild(dateXml)
            #add player_name element
            playerNameXml = doc.createElement("player_name")
            playerNameXml.appendChild(doc.createTextNode(self.mHighScores[gameName]['player']))
            highScoreXml.appendChild(playerNameXml)
            #add score element
            scoreXml = doc.createElement("score")
            scoreXml.appendChild(doc.createTextNode(self.mHighScores[gameName]['score']))
            highScoreXml.appendChild(scoreXml)
            #Loop through extra data, adding that.
            for dataVar in self.mHighScores[gameName]['data']:
                dataXml = doc.createElement("data")
                #Add variable name element
                varXml = doc.createElement("var")
                varXml.appendChild(doc.createTextNode(dataVar))
                dataXml.appendChild(varXml)
                #Add value name element
                valueXml = doc.createElement("value")
                valueXml.appendChild(doc.createTextNode(self.mHighScores[gameName]['data'][dataVar]))
                dataXml.appendChild(valueXml)
                #Add the data element to the high score
                highScoreXml.appendChild(dataXml)
            root.appendChild(highScoreXml)
        #save XML
        doc.writexml(open("store/high_score_list.xml","w"),addindent="\t",newl="\r\n")
    
    def run(self,line,userObject,destinationObject=None):
        outputLines = ["High scores:"]
        for gameName in self.mHighScores:
            score = self.mHighScores[gameName]['score']
            player = self.mHighScores[gameName]['player']
            date = self.mHighScores[gameName]['date']
            outputLines.append(gameName + "> Score: "+score+", Player: "+player+", Date: "+date)
        return "\n".join(outputLines)
    
    def addHighScore(self,gameName,score,userName,data={}):
        'Adds a new highscore to the list. Overwriting the old high score for that game if it exists'
        newDict = {}
        newDict['score'] = score
        newDict['player'] = userName
        newDict['date'] = time.time()
        newDict['data'] = data
        self.mHighScores[gameName] = newDict
    
    def getHighScore(self,gameName):
        'Returns the high score for a specified game.'
        if(gameName in self.mHighScores):
            return self.mHighScores[gameName]
        return None

class Game:
    '''
    Generic Game object. Stores players and location.
    '''
    mPlayers = set()
    mChannel = None
    mStartTime = None
    mLastTime = None
    mLost = False
    
    def __init__(self,playerList,channelObject):
        self.mPlayers = set(playerList)
        self.mChannel = channelObject
        self.mStartTime = time.time()
        self.mLastTime = time.time()
    
    def updateTime(self):
        'Updates the time that something last happened to this game'
        self.mLastTime = time.time()
    
    def getPlayers(self):
        'Returns the list of players'
        return self.mPlayers
    
    def containsPlayer(self,userObject):
        'Whether or not this game contains a specified player'
        return userObject in self.mPlayers
    
    def getChannel(self):
        'Returns the channel (or destination) this game is happening in'
        return self.mChannel
    
    def isLost(self):
        'Lost getter. (Avoided the getLost() joke.)'
        return self.mLost
    

class HigherOrLowerGame(Game):
    '''
    Game of Higher or Lower.
    '''
    HIGH_SCORE_NAME = "higher_or_lower"
    mDeck = None
    mLastCard = None
    mCardList = []
    mTurns = 0
    mHighScoresObject = None
    
    
    def __init__(self,userObject,channelObject):
        self.mPlayers = set([userObject])
        self.mChannel = channelObject
        self.mStartTime = time.time()
        self.mLastTime = time.time()
        self.mDeck = Deck()
        self.mDeck.shuffle()
        functionDispatcher = userObject.getServer().getHallo().getFunctionDispatcher()
        highScoresClass = functionDispatcher.getFunctionByName("highscores")
        self.mHighScoresObject = functionDispatcher.getFunctionObject(highScoresClass)

    def getNextCard(self):
        'Gets a new card from the deck and adds to the list'
        self.updateTime()
        self.mTurns += 1
        nextCard = self.mDeck.getNextCard()
        self.mCardList.append(nextCard)
        self.mLastCard = nextCard
        return nextCard
    
    def getTurns(self):
        'Turns getter'
        return self.mTurns
    
    def checkHighScore(self):
        'Checks if this game is a high score. Returns boolean'
        highScore = self.mHighScoresObject.getHighScore(self.HIGH_SCORE_NAME)
        if(highScore is None):
            return True
        lastScore = int(highScore['data']['cards'])
        currentScore = self.mTurns
        if(self.mLost):
            currentScore = self.mTurns-1
        if(currentScore>lastScore):
            return True
        return False
        
    def startGame(self):
        'Starts the new game'
        firstCard = self.getNextCard()
        return "You have started a game of higher or lower. Your first card is: " + firstCard.toString() + "."
    
    def updateHighScore(self):
        'Updates the high score with current game. Checks that it is high score first.'
        if(not self.checkHighScore()):
            return False
        currentScore = self.mTurns
        if(self.mLost):
            currentScore = self.mTurns-1
        userName = list(self.mPlayers)[0].getName()
        score = str(currentScore)+" cards"
        gameData = {}
        gameData['cards'] = currentScore
        self.mHighScoresObject.addHighScore(self.HIGH_SCORE_NAME,score,userName,gameData)
        return True
    
    def guessHigher(self):
        'User has guessed the next card is higher.'
        lastCard = self.mLastCard
        nextCard = self.getNextCard()
        if(nextCard.toInt() > lastCard.toInt()):
            outputString = "Your " + Commons.ordinal(self.mTurns) + " card is " + nextCard.toString() + ", which is higher! "
            outputString += "Congrats! Do you think the next card will be higher or lower?"
            return outputString
        if(nextCard.toInt() == lastCard.toInt()):
            outputString = "Your " + Commons.ordinal(self.mTurns) + " card is " + nextCard.toString() + ", which is the same (that's fine.) "
            outputString += "Do you think the next card will be higher or lower?"
            return outputString
        if(nextCard.toInt() < lastCard.toInt()):
            self.mLost = True
            #high scores
            isHighScore = self.checkHighScore()
            if(isHighScore):
                previousScore = self.mHighScoresObject.getHighScore(self.HIGH_SCORE_NAME)
                previousScoreText = "(previous highscore was: " + previousScore['score'] + ", set by " + previousScore['player'] + " " + Commons.formatUnixTime(previousScore['date']) + ".)"
                self.updateHighScore()
            #Output message
            outputString = "Your " + Commons.ordinal(self.mTurns) + " card is " + nextCard.toString() + ". Sorry, that's lower, you lose."
            if(isHighScore):
                outputString += " You managed " + str(self.mTurns-1) + " cards though, that's a new highscore!" + previousScoreText
            else:
                outputString += " You managed " + str(self.mTurns-1) + " cards though."
            return outputString

    def guessLower(self):
        'User has guessed the next card is higher.'
        lastCard = self.mLastCard
        nextCard = self.getNextCard()
        if(nextCard.toInt() < lastCard.toInt()):
            outputString = "Your " + Commons.ordinal(self.mTurns) + " card is " + nextCard.toString() + ", which is lower! "
            outputString += "Congrats! Do you think the next card will be higher or lower?"
            return outputString
        if(nextCard.toInt() == lastCard.toInt()):
            outputString = "Your " + Commons.ordinal(self.mTurns) + " card is " + nextCard.toString() + ", which is the same (that's fine.) "
            outputString += "Do you think the next card will be higher or lower?"
            return outputString
        if(nextCard.toInt() > lastCard.toInt()):
            self.mLost = True
            #high scores
            isHighScore = self.checkHighScore()
            if(isHighScore):
                previousScore = self.mHighScoresObject.getHighScore(self.HIGH_SCORE_NAME)
                previousScoreText = "(previous highscore was: " + previousScore['score'] + ", set by " + previousScore['player'] + " " + Commons.formatUnixTime(previousScore['date']) + ".)"
                self.updateHighScore()
            #Output message
            outputString = "Your " + Commons.ordinal(self.mTurns) + " card is " + nextCard.toString() + ". Sorry, that's higher, you lose."
            if(isHighScore):
                outputString += " You managed " + str(self.mTurns-1) + " cards though, that's a new highscore!" + previousScoreText
            else:
                outputString += " You managed " + str(self.mTurns-1) + " cards though."
            return outputString
        
    def quitGame(self):
        'User has quit the game'
        #check high scores
        isHighScore = self.checkHighScore()
        if(isHighScore):
            previousScore = self.mHighScoresObject.getHighScore(self.HIGH_SCORE_NAME)
            previousScoreText = "(previous highscore was: " + previousScore['score'] + ", set by " + previousScore['player'] + " " + Commons.formatUnixTime(previousScore['date']) + ".)"
            self.updateHighScore()
        #Create output
        if(isHighScore):
            return "Sorry to see you quit, you had managed " + str(self.mTurns-1) + " cards, which is a new highscore!" + previousScoreText
        else:
            return "Sorry to see you quit, you had managed " + str(self.mTurns-1) + " cards."
    

class HigherOrLower(Function):
    '''
    Function to play Higher or Lower
    '''
    #Name for use in help listing
    mHelpName = "card"
    #Names which can be used to address the function
    mNames = set(["card","random card","randomcard"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Picks a random card from a deck. Format: random_card"
    
    mGameList = []
    mStartCommands = ["start"]
    mEndCommands = ["end","quit","escape"]
    mHighCommands = ["higher","high","more","more","greater","greater","bigger",">"]
    mLowCommands = ["lower","low","less","small","<"]
    
    #Boring functions
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def isPersistent(self):
        'Returns boolean representing whether this function is supposed to be persistent or not'
        return True
    
    @staticmethod
    def loadFunction():
        'Loads the function, persistent functions only.'
        return HigherOrLower()
    
    def saveFunction(self):
        'Saves the function, persistent functions only.'
        #TODO: save all games to XML perhaps?
        pass

    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set(Function.EVENT_MESSAGE)

    #Interesting functions from here
    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().lower()
        if(lineClean in [""]+self.mStartCommands):
            return self.newGame(userObject,destinationObject)
        elif(any(cmd in lineClean for cmd in self.mEndCommands)):
            return self.quitGame(userObject,destinationObject)
        elif(any(cmd in lineClean for cmd in self.mHighCommands)):
            return self.guessHigher(userObject,destinationObject)
        elif(any(cmd in lineClean for cmd in self.mLowCommands)):
            return self.guessLower(userObject,destinationObject)
        outputString = "I don't understand this input." 
        outputString += ' Syntax: "higher_or_lower start" to start a game, '
        outputString += '"higher_or_lower higher" to guess the next card will be higher, '
        outputString += '"higher_or_lower lower" to guess the next card will be lower, '
        outputString += '"higher_or_lower end" to quit the game.'
        return outputString
    
    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        cleanFullLine = fullLine.strip().lower()
        if(any(cmd in cleanFullLine for cmd in self.mEndCommands)):
            return self.quitGame(userObject,channelObject,True)
        elif(any(cmd in cleanFullLine for cmd in self.mHighCommands)):
            return self.guessHigher(userObject,channelObject,True)
        elif(any(cmd in cleanFullLine for cmd in self.mLowCommands)):
            return self.guessLower(userObject,channelObject,True)
        pass
    
    def findGame(self,userObject):
        'Finds the game a specified user is in, None otherwise.'
        for game in self.mGameList:
            if(game.containsPlayer(userObject)):
                return game
        return None
    
    def newGame(self,userObject,destinationObject):
        'User request to create a new game'
        currentGame = self.findGame(userObject)
        if(currentGame is not None):
            return "You're already playing a game."
        newGame = HigherOrLowerGame(userObject,destinationObject)
        self.mGameList.append(newGame)
        outputString = newGame.startGame()
        return outputString
        
    def quitGame(self,userObject,destinationObject,passive=False):
        'User request to quit game'
        currentGame = self.findGame(userObject)
        if(currentGame is None):
            if(not passive):
                return "You're not playing a game."
            else:
                return None
        outputString = currentGame.quitGame()
        self.mGameList.remove(currentGame)
        return outputString
    
    def guessHigher(self,userObject,destinationObject,passive=False):
        'User guessed next card is higher'
        currentGame = self.findGame(userObject)
        if(currentGame is None):
            if(not passive):
                return "You're not playing a game."
            else:
                return None
        outputString = currentGame.guessHigher()
        if(currentGame.isLost()):
            self.mGameList.remove(currentGame)
        return outputString
    
    def guessLower(self,userObject,destinationObject,passive=False):
        'User guessed next card is lower'
        currentGame = self.findGame(userObject)
        if(currentGame is None):
            if(not passive):
                return "You're not playing a game."
            else:
                return None
        outputString = currentGame.guessLower()
        if(currentGame.isLost()):
            self.mGameList.remove(currentGame)
        return outputString
    
        
class BlackjackGame(Game):
    '''
    Game of Blackjack.
    '''
    HIGH_SCORE_NAME = "blackjack"
    mDeck = None
    mPlayerHand = None
    mDealerHand = None
    mLastCard = None
    mLost = False
    mHighScoresObject = None
    
    
    def __init__(self,userObject,channelObject):
        self.mPlayers = set([userObject])
        self.mChannel = channelObject
        self.mStartTime = time.time()
        self.mLastTime = time.time()
        self.mDeck = Deck()
        self.mDeck.shuffle()
        self.mPlayerHand = Hand()
        self.mDealerHand = Hand()
    
    def startGame(self):
        'Starts the game. Returns the opening line'
        #Deal out the opening hands
        firstCard = self.mDeck.getNextCard()
        self.mPlayerHand.addCard(firstCard)
        secondCard = self.mDeck.getNextCard()
        self.mDealerHand.addCard(secondCard)
        thirdCard = self.mDeck.getNextCard()
        self.mPlayerHand.addCard(thirdCard)
        forthCard = self.mDeck.getNextCard()
        self.mDealerHand.addCard(forthCard)
        #Write the first half of output
        outputString = "You have started a game of Blackjack (H17), you have been dealt a " + firstCard.toString() + " and a " + thirdCard.toString() + "."
        #Check if they have been dealt a blackjack
        if(self.mPlayerHand.containsValue(Card.CARD_ACE) and any([self.mPlayerHand.containsValue(value) for value in [Card.CARD_10,Card.CARD_JACK,Card.CARD_QUEEN,Card.CARD_KING]])):
            return outputString + "Congratulations! That's a blackjack! You win."
        #Write the rest of the output
        outputString += " The dealer has a " + secondCard.toString() + " and another, covered, card. Would you like to hit or stick?"
        return outputString
    
    def hit(self):
        'Player decided to hit.'
        newCard = self.mDeck.getNextCard()
        self.mPlayerHand.addCard(newCard)
        outputString = "You have been dealt a " + newCard.toString() + ","
        if(self.mPlayerHand.sumTotal()>21):
            self.mLost = True
            return outputString + " which means your hand sums to " + str(self.mPlayerHand.sumTotal()) + ". You've gone bust. You lose, sorry."
        return outputString + " would you like to hit or stick?"
        
    def stick(self):
        'Player decided to stick.'
        #Get total of player's hand
        playerSum = self.mPlayerHand.blackjackTotal()
        outputString = "Your hand is: " + self.mPlayerHand.toString() + "\n"
        #Dealer continues to deal himself cards, in accordance with H17 rules
        dealerNewCards = 0
        if(self.mDealerHand.blackjackTotal()<17 or (self.mDealerHand.blackjackTotal()==17 and self.mDealerHand.containsValue(Card.CARD_ACE))):
            dealerNewCards += 1
            dealerNewCard = self.mDeck.getNextCard()
            self.mDealerHand.addCard(dealerNewCard)
        #if dealer has dealt himself more cards, say that.
        if(dealerNewCards!=0):
            cardPlural = 'card'
            if(dealerNewCards!=1):
                cardPlural = 'cards'
            outputString += "The dealer deals himself " + str(dealerNewCards) + " more " + cardPlural + ".\n"
        #Say the dealer's hand
        outputString += "The dealer's hand is: " + self.mDealerHand.toString() + "\n"
        #Check if dealer is bust
        if(self.mDealerHand.blackjackTotal()>21):
            outputString += "Dealer busts.\n"
        #See who wins
        if(self.mDealerHand.blackjackTotal()==playerSum):
            outputString += "It's a tie, dealer wins."
        elif(self.mDealerHand.blackjackTotal() > playerSum and self.mDealerHand.blackjackTotal() <= 21):
            outputString += "Dealer wins."
        else:
            outputString += "You win! Congratulations!"
        return outputString

    def quitGame(self):
        'Player wants to quit'
        return "You have quit the game. You had " + str(self.mPlayerHand.blackjackTotal()) + " and the dealer had " + str(self.mDealerHand.blackjackTotal()) + "."


class Blackjack(Function):
    '''
    Function to play Blackjack
    '''
    #Name for use in help listing
    mHelpName = "blackjack"
    #Names which can be used to address the function
    mNames = set(["blackjack","twentyone","twenty one","twenty-one","21"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Picks a random card from a deck. Format: random_card"
    
    mGameList = []
    mStartCommands = ["start"]
    mEndCommands = ["end","quit","escape"]
    mHitCommands = ["hit"]
    mStickCommands = ["stick","stand"]
    
    #Boring functions
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def isPersistent(self):
        'Returns boolean representing whether this function is supposed to be persistent or not'
        return True
    
    @staticmethod
    def loadFunction():
        'Loads the function, persistent functions only.'
        return Blackjack()
    
    def saveFunction(self):
        'Saves the function, persistent functions only.'
        #TODO: save all games to XML perhaps?
        pass

    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set(Function.EVENT_MESSAGE)

    #Interesting functions from here
    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().lower()
        if(lineClean in [""]+self.mStartCommands):
            return self.newGame(userObject,destinationObject)
        elif(any(cmd in lineClean for cmd in self.mEndCommands)):
            return self.quitGame(userObject,destinationObject)
        elif(any(cmd in lineClean for cmd in self.mHitCommands)):
            return self.hit(userObject,destinationObject)
        elif(any(cmd in lineClean for cmd in self.mStickCommands)):
            return self.stick(userObject,destinationObject)
        outputString = "I don't understand this input." 
        outputString += ' Syntax: "blackjack start" to start a game, '
        outputString += '"blackjack hit" to hit, "blackjack stick" to stick, '
        outputString += 'and "blackjack end" to quit the game.'
        return outputString
    
    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        cleanFullLine = fullLine.strip().lower()
        if(any(cmd in cleanFullLine for cmd in self.mEndCommands)):
            return self.quitGame(userObject,channelObject,True)
        elif(any(cmd in cleanFullLine for cmd in self.mHitCommands)):
            return self.hit(userObject,channelObject,True)
        elif(any(cmd in cleanFullLine for cmd in self.mStickCommands)):
            return self.stick(userObject,channelObject,True)
        pass
    
    def findGame(self,userObject):
        'Finds the game a specified user is in, None otherwise.'
        for game in self.mGameList:
            if(game.containsPlayer(userObject)):
                return game
        return None
    
    def newGame(self,userObject,destinationObject):
        'User request to create a new game'
        currentGame = self.findGame(userObject)
        if(currentGame is not None):
            return "You're already playing a game."
        newGame = BlackjackGame(userObject,destinationObject)
        outputString = newGame.startGame()
        self.mGameList.append(newGame)
        return outputString
        
    def quitGame(self,userObject,destinationObject,passive=False):
        'User request to quit game'
        currentGame = self.findGame(userObject)
        if(currentGame is None):
            if(not passive):
                return "You're not playing a game."
            else:
                return None
        outputString = currentGame.quitGame()
        self.mGameList.remove(currentGame)
        return outputString
    
    def hit(self,userObject,destinationObject,passive=False):
        'User wants to hit'
        currentGame = self.findGame(userObject)
        if(currentGame is None):
            if(not passive):
                return "You're not playing a game."
            else:
                return None
        outputString = currentGame.hit()
        if(currentGame.isLost()):
            self.mGameList.remove(currentGame)
        return outputString
    
    def stick(self,userObject,destinationObject,passive=False):
        'User wants to stick'
        currentGame = self.findGame(userObject)
        if(currentGame is None):
            if(not passive):
                return "You're not playing a game."
            else:
                return None
        return
        outputString = currentGame.stick()
        self.mGameList.remove(currentGame)
        return outputString
    
class DDRGame(Game):
    '''
    Game of DDR.
    '''
    DIFFICULTY_EASY = "easy"
    DIFFICULTY_MEDIUM = "medium"
    DIFFICULTY_HARD = "hard"
    HIGH_SCORE_NAME = "ddr"
    mLastMove = None
    mDifficulty = None
    mPlayers = set()
    mChannel = None
    mPlayersMoved = set()
    mPlayerDict = {}
    mCanJoin = True
    mGameOver = False
    
    def __init__(self,gameDifficulty,userObject,channelObject):
        self.mDifficulty = gameDifficulty
        self.mPlayers = set([userObject])
        self.mChannel = channelObject
        self.mStartTime = time.time()
        self.mLastTime = time.time()
    
    def startGame(self):
        pass
    
    def run(self):
        'Launched into a new thread, this function actually plays the DDR game.'
        pass
    
    def canJoin(self):
        'Boolean, whether players can join.'
        return self.mCanJoin
    
    def isGameOver(self):
        'Boolean, whether the game is over.'
        return self.mGameOver
    
    def joinGame(self,userObject):
        if(self.canJoin()):
            self.mPlayers.add(userObject)
            return userObject.getName() + " has joined."
        else:
            return "This game cannot be joined now."
    
    def makeMove(self):
        pass
    
    def quitGame(self):
        pass

class DDR(Function):
    '''
    Function to play IRC DDR (Dance Dance Revolution)
    '''
    #Name for use in help listing
    mHelpName = "ddr"
    #Names which can be used to address the function
    mNames = set(["ddr","dance dance revolution","dansu dansu","dancing stage"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Plays dance dance revolution. Hallo says directions and users must respond to them correctly and in the fastest time they can"
    
    mGameList = []
    mStartCommands = ["start","easy","medium","med","hard"]
    mJoinCommands = ["join"]
    mEndCommands = ["end","quit","escape"]
    mMoveCommands = ["^",">","<","v","w","a","d","s"]
    
    #Boring functions
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def isPersistent(self):
        'Returns boolean representing whether this function is supposed to be persistent or not'
        return True
    
    @staticmethod
    def loadFunction():
        'Loads the function, persistent functions only.'
        return DDR()
    
    def saveFunction(self):
        'Saves the function, persistent functions only.'
        #TODO: save all games to XML perhaps?
        pass

    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set(Function.EVENT_MESSAGE)

    #Interesting functions from here
    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().lower()
        if(lineClean in [""]+self.mStartCommands):
            return self.newGame(lineClean,userObject,destinationObject)
        elif(any(cmd in lineClean for cmd in self.mJoinCommands)):
            return self.joinGame(lineClean,userObject,destinationObject)
        elif(any(cmd in lineClean for cmd in self.mEndCommands)):
            return self.quitGame(lineClean,userObject,destinationObject)
        elif(any(cmd in lineClean for cmd in self.mMoveCommands)):
            return self.makeMove(lineClean,userObject,destinationObject)
        outputString = "Invalid difficulty mode. Please specify easy, medium or hard."
        return outputString
    
    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        cleanFullLine = fullLine.strip().lower()
        if(any(cmd in cleanFullLine for cmd in self.mJoinCommands)):
            return self.joinGame(cleanFullLine,userObject,channelObject,True)
        elif(any(cmd in cleanFullLine for cmd in self.mEndCommands)):
            return self.quitGame(cleanFullLine,userObject,channelObject,True)
        elif(any(cmd in cleanFullLine for cmd in self.mMoveCommands)):
            return self.makeMove(cleanFullLine,userObject,channelObject,True)
        pass
    
    def findGame(self,destinationObject):
        'Finds the game running in a specified channel, None otherwise.'
        for game in self.mGameList:
            if(game.getChannel()==destinationObject):
                return game
        return None
    
    def newGame(self,lineClean,userObject,destinationObject):
        'Starts a new game'
        currentGame = self.findGame(destinationObject)
        if(currentGame is not None):
            return "You're already playing a game."
        #Find out the game difficulty
        if("easy" in lineClean):
            gameDifficulty = DDRGame.DIFFICULTY_EASY
        elif("med" in lineClean):
            gameDifficulty = DDRGame.DIFFICULTY_MEDIUM
        elif("hard" in lineClean):
            gameDifficulty = DDRGame.DIFFICULTY_HARD
        else:
            "Invalid difficulty mode. Please specify easy, medium or hard."
        #Create the new game and start it
        newGame = DDRGame(gameDifficulty,userObject,destinationObject)
        outputString = newGame.startGame()
        self.mGameList.append(newGame)
        return outputString
    
    def joinGame(self,lineClean,userObject,destinationObject):
        'Player requests to join a game'
        pass
    
    def quitGame(self,lineClean,userObject,destinationObject):
        'Player requests to quit a game'
        pass
    
    def makeMove(self,lineClean,userObject,destinationObject):
        'Player makes a move'
        pass





        