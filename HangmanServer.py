#   Title:  HangmanServer.py
#   Author: Osman Arshad
#   Email:  osmanaarshad@gmail.com
#   Description: HangmanServer.py runs the server side of this multiplayer hangman game.
#   Players can connect into the server by running HangmanClient.py while this is running.
#   HangmanServer holds all necessary data, the client does not need to retain any info.
#   All clients that connect to this server are handled separately through different threads.
import socket
import threading
import thread
import random
import sys

# Setting up sockets and preparing to listen for connection
HOST = ''
PORT = 8203

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print 'Socket created'

try:
	s.bind((HOST, PORT))
except socket.error, msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()
print 'Socket bind complete'

s.listen(10)

# Lists server maintains to keep track of game information
connectionsList = []
users = []
unames = []
loggedUsers = []
words = ['basketball', 'dinosaur', 'birthday']
games = []
HallOfFame = []

# Server communicates with each client through a thread
def clientthread(conn):
	while 1:
		mainMenuOption = conn.recv(1024)

		# Player attempts to login
		if mainMenuOption == '1':
			loginInfo = conn.recv(1024)
			loggedIn = False

			pwordPos = loginInfo.index(':')
			uname = loginInfo[:pwordPos]
			
			for x in users:
				if loginInfo == x:
					loggedIn = True

			if len(loggedUsers) != 0:
				for y in loggedUsers:
					if uname == y:
						loggedIn = False
					
			if loggedIn != True:
    				conn.send('bad')

			# Player has correctly logged in
			if loggedIn == True:
				conn.send('good')
				loggedUsers.append(uname)
				while 1:
						loggedInMenuOption = conn.recv(1024)
						
                        # Create a new game and join it
						if loggedInMenuOption == '1':
							difficultyLvl = conn.recv(1024)
							
							gameNum = len(games)
							gameWord = random.choice(words)
							print gameWord

							wordState = ''
							for c in range(0, len(gameWord)):
								wordState = wordState + '_'

							wrongGuesses = ''

							uname = uname
							score = 0
							nameNScore = [uname, score]

							turn = uname

							usersInGame = []
							usersInGame.append(nameNScore)

							quit = 0

							aGame = [gameNum, gameWord, wordState, wrongGuesses, turn, usersInGame, difficultyLvl, quit]
							games.append(aGame)

							gameOn = True
							
                            # Games starts, game logic begins here
							while gameOn:
								try:
    									e = games[gameNum]
								except IndexError:
 	 	  							gameOn = False
									conn.send('gameover')
									break

								theGame = games[gameNum]
								theWord = theGame[1]
								wordstatePkt = theGame[2] + '*'
								guessesPkt = theGame[3] + '%'
								whoseTurnPkt = theGame[4] + '^'
								diffPkt = theGame[6] + '$'

								players = ''
								for p in theGame[5]:
									aPlayer = p[0] + '-' + str(p[1]) + ':'
									players = players + aPlayer
								
								gamePkt = diffPkt + whoseTurnPkt + wordstatePkt + guessesPkt + players
								conn.send(gamePkt)

								updateWord = ''
								points = 0
								anIndex = 0
								whoseTurn = ''
								inGamePlayers = theGame[5]

								playerInput = conn.recv(1024)
								if playerInput[0] == '!':
										namePos = playerInput.index('@')
										whichPlayer = playerInput[1:namePos]
										playerGuess = playerInput[namePos+1:]

										if playerGuess == theWord:
											points = points + len(theWord)
											
											playerIndex = [x[0] for x in inGamePlayers].index(whichPlayer)
											playerInfo = inGamePlayers[playerIndex]
											newScore = playerInfo[1] + points
											updateScore = [whichPlayer, newScore]
											games[gameNum][5][playerIndex] = updateScore
											HallOfFame.append(updateScore)

											gameOn = False
											conn.send('gameover')
											del games[gameNum]
											break

										elif playerGuess != theWord:
											try:
													e = games[gameNum]
											except IndexError:
												gameOn = False
												conn.send('gameover')
												break

											index2 = 0
											playerCount = 1
											numPlayers = len(inGamePlayers)
											for t in inGamePlayers:
												person = t[0]
												if theGame[4] == person:
														if playerCount != numPlayers:
																nextGuy = theGame[5][index2+1]
																newTurn = nextGuy[0]
														else:
																nextGuy = theGame[5][0]
																newTurn = nextGuy[0]
												playerCount = playerCount + 1
												index2 = index2 + 1
											games[gameNum][4] = newTurn

											playerIndex = [x[0] for x in inGamePlayers].index(whichPlayer)
											conn.send('gameover')
											del games[gameNum][5][playerIndex]
											gameOn = False
											break

								else:
										whichPlayer = playerInput[:-1]
										playerGuess = playerInput[-1]

										whoseTurn = theGame[4]
										diff = theGame[6]
										diffLvl = int(diff)
										  								
								rightGuess = False
								if whoseTurn == whichPlayer:
									for x in theWord:
										if playerGuess == x:
											rightGuess = True
											updateWord = updateWord + playerGuess
											points = points + 1
										elif playerGuess != x:
											if theGame[2][anIndex] != '-':
												updateWord = updateWord + theGame[2][anIndex]
											else:
												updateWord = updateWord + '-'
										anIndex += 1
									
									if rightGuess == False:
										badGuesses = theGame[3] + playerGuess
										games[gameNum][3] = badGuesses
										
										numBadGuesses = len(badGuesses)
										wordLen = len(theGame[2])

										if diffLvl == 1:
												wrongsAllowed = wordLen * 3
										elif diffLvl == 2:
												wrongsAllowed = wordLen * 2
										elif diffLvl == 3:
												wrongsAllowed = wordLen
										
										if numBadGuesses == wrongsAllowed:
												gameOn = False

										index2 = 0
										playerCount = 1
										numPlayers = len(inGamePlayers)
										for t in inGamePlayers:
											person = t[0]
											if theGame[4] == person:
													if playerCount != numPlayers:
															nextGuy = theGame[5][index2+1]
															newTurn = nextGuy[0]
													else:
															nextGuy = theGame[5][0]
															newTurn = nextGuy[0]
											playerCount = playerCount + 1
											index2 = index2 + 1
										games[gameNum][4] = newTurn
																
									
									playerIndex = [x[0] for x in inGamePlayers].index(whichPlayer)
									playerInfo = inGamePlayers[playerIndex]
									newScore = playerInfo[1] + points
									updateScore = [whichPlayer, newScore]
									
									games[gameNum][5][playerIndex] = updateScore
									games[gameNum][2] = updateWord

									if updateWord == theWord:
											gameOn = False

									if gameOn == False:
										for q in theGame[5]:
												somePlayer = q[0]
												hisScore = q[1]
												hofEntry = [somePlayer, hisScore]
												HallOfFame.append(hofEntry)
										conn.send('gameover')
										del games[gameNum]

						# Get current list of games and join one
						if loggedInMenuOption == '2':
							numGames = len(games)
							conn.send(str(numGames))
							gameOn = False

							if numGames != 0:
								someNum = conn.recv(1024)
								gameNumToJoin = int(someNum)

								uname = uname
								score = 0
								nameNScore = [uname, score]
								games[gameNumToJoin][5].append(nameNScore)
								gameOn = True
							
							# Game starts
							while gameOn: 							
								try:
    									e = games[gameNumToJoin]
								except IndexError:
 	 	  							gameOn = False
									conn.send('gameover')
									break
    							
								theGame = games[gameNumToJoin]
								theWord = theGame[1]
								wordstatePkt = theGame[2] + '*'
								guessesPkt = theGame[3] + '%'
								whoseTurnPkt = theGame[4] + '^'
								diffPkt = theGame[6] + '$'

								players = ''
								for p in theGame[5]:
									aPlayer = p[0] + '-' + str(p[1]) + ':'
									players = players + aPlayer
								
								gamePkt = diffPkt + whoseTurnPkt + wordstatePkt + guessesPkt + players
								conn.send(gamePkt)

								updateWord = ''
								points = 0
								anIndex = 0
								inGamePlayers = theGame[5]

								playerInput = conn.recv(1024)
								
								if playerInput[0] == '!':
										namePos = playerInput.index('@')
										whichPlayer = playerInput[1:namePos]
										playerGuess = playerInput[namePos+1:]

										if playerGuess == theWord:
											points = points + len(theWord)
											
											playerIndex = [x[0] for x in inGamePlayers].index(whichPlayer)
											playerInfo = inGamePlayers[playerIndex]
											newScore = playerInfo[1] + points
											updateScore = [whichPlayer, newScore]
											games[gameNumToJoin][5][playerIndex] = updateScore
											HallOfFame.append(updateScore)

											gameOn = False
											conn.send('gameover')
											del games[gameNumToJoin]
											break

										elif playerGuess != theWord:
											try:
													e = games[gameNumToJoin]
											except IndexError:
												gameOn = False
												conn.send('gameover')
												break
											index2 = 0
											playerCount = 1
											numPlayers = len(inGamePlayers)
											for t in inGamePlayers:
												person = t[0]
												if theGame[4] == person:
														if playerCount != numPlayers:
																nextGuy = theGame[5][index2+1]
																newTurn = nextGuy[0]
														else:
																nextGuy = theGame[5][0]
																newTurn = nextGuy[0]
												playerCount = playerCount + 1
												index2 = index2 + 1
											games[gameNumToJoin][4] = newTurn

											playerIndex = [x[0] for x in inGamePlayers].index(whichPlayer)
											conn.send('gameover')
											del games[gameNumToJoin][5][playerIndex]
											gameOn = False
											break

								else:
										whichPlayer = playerInput[:-1]
										playerGuess = playerInput[-1]

										whoseTurn = theGame[4]
										diff = theGame[6]
										diffLvl = int(diff)

								rightGuess = False
								if whoseTurn == whichPlayer:
									for x in theWord:
										if playerGuess == x:
											rightGuess = True
											updateWord = updateWord + playerGuess
											points = points + 1
										elif playerGuess != x:
											if theGame[2][anIndex] != '-':
												updateWord = updateWord + theGame[2][anIndex]
											else:
												updateWord = updateWord + '-'
										anIndex += 1
									
									if rightGuess == False:
										badGuesses = theGame[3] + playerGuess
										games[gameNumToJoin][3] = badGuesses
										
										numBadGuesses = len(badGuesses)
										wordLen = len(theGame[2])

										if diffLvl == 1:
    											wrongsAllowed = wordLen * 3
										elif diffLvl == 2:
    											wrongsAllowed = wordLen * 2
										elif diffLvl == 3:
    											wrongsAllowed = wordLen
										
										if numBadGuesses == wrongsAllowed:
    											gameOn = False

										index2 = 0
										playerCount = 1
										numPlayers = len(inGamePlayers)
										for t in inGamePlayers:
											person = t[0]
											if theGame[4] == person:
													if playerCount != numPlayers:
															nextGuy = theGame[5][index2+1]
															newTurn = nextGuy[0]
													else:
															nextGuy = theGame[5][0]
															newTurn = nextGuy[0]
											playerCount = playerCount + 1
											index2 = index2 + 1
										games[gameNumToJoin][4] = newTurn
    															
									playerIndex = [x[0] for x in inGamePlayers].index(whichPlayer)
									playerInfo = inGamePlayers[playerIndex]
									newScore = playerInfo[1] + points
									updateScore = [whichPlayer, newScore]
									
									games[gameNumToJoin][5][playerIndex] = updateScore
									games[gameNumToJoin][2] = updateWord

									if updateWord == theWord:
    										gameOn = False

									if gameOn == False:
										for q in theGame[5]:
												somePlayer = q[0]
												hisScore = q[1]
												hofEntry = [somePlayer, hisScore]
												HallOfFame.append(hofEntry)
										conn.send('gameover')
										del games[gameNumToJoin]

						# Print Hall of Fame
						if loggedInMenuOption == '3':
								players = ''
								for h in HallOfFame:
									playaNScore = h[0] + '-' + str(h[1]) + ':'
									players = players + playaNScore
								conn.send(players)

						# User leaves the game
						if loggedInMenuOption == '4':
								loggedUsers.remove(uname)
								conn.close()
		
		# Create a new account
		if mainMenuOption == '2':
			newUserInfo = conn.recv(1024)
			pwordPos = newUserInfo.index(':')
			uname = newUserInfo[:pwordPos]
			alreadyExists = False
			for x in users:
    				if uname == x[:pwordPos]:
						alreadyExists = True
						conn.send('Username taken')
			
			if alreadyExists != True:			
					users.append(newUserInfo)
					unames.append(uname)
					conn.send(uname)
		
		# Print Hall of Fame
		if mainMenuOption == '3':
			players = ''
			for h in HallOfFame:
				playaNScore = h[0] + '-' + str(h[1]) + ':'
				players = players + playaNScore
			conn.send(players)

		# User leaves game
		if mainMenuOption == '4':
    			loggedUsers.remove(uname)
    			conn.close()

	conn.close()

def serverthread():
	while 1:
		print '1. Current list of the users'
		print '2. Current list of the words'
		print '3. Add new word to the list of words'
		option = raw_input('Enter option:\n')
		
		if option == '1':
			for u in loggedUsers:
				print u
		
		if option == '2':
			for w in words:
				print w

		if option == '3':
			wordToAdd = raw_input('Enter word: ')
			words.append(wordToAdd)

t = threading.Thread(target=serverthread)
t.start()

while 1:
	conn, addr = s.accept()
	print 'Connected with ' + addr[0] + ':' + str(addr[1])
	
	start_new_thread(clientthread ,(conn,))	
	
s.close()