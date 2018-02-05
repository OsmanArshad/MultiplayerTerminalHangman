#   Title:  HangmanClient.py
#   Author: Osman Arshad
#   Email:  osmanaarshad@gmail.com
#   Description: HangmanClient.py runs the client side of this multiplayer hangman game.
#   Players connect into the server by running HangmanClient.py when HangmanServer.py is running.
#   HangmanServer holds all necessary data, the client does not need to retain any info.
import socket
from sys import stdout
import sys

try:
	s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
	print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
	sys.exit()

print 'Socket Created'

host = 'localhost'
port = 8203

try:
	remote_ip = socket.gethostbyname( host )
except socket.gaierror:
	print 'Hostname could not be resolved. Exiting'
	sys.exit()

s.connect((remote_ip , port))

successfulLogin = 'bad'

while 1:
	print '1. Login'
	print '2. Make New User'
	print '3. Hall of Fame'
	print '4. Exit'
	option = raw_input('Enter option: ')
	
	# Client logs in
	if option == '1':
		s.sendto(option, (host, port))

		if successfulLogin != 'good':
			uname = raw_input('Enter Your User Name: ')
			pword = raw_input('Enter Your Password: ')
			loginInfoPkt = uname + ':' + pword
			s.sendto(loginInfoPkt, (host, port))
			successfulLogin = s.recv(4096)
			if successfulLogin != 'good':
				print 'Incorrect User Name/Password. Try again\n'

		if successfulLogin == 'good':
    			while 1:		
						print '\nLogged in!'
						print '1. Start New Game'
						print '2. Get list of the Games'
						print '3. Hall of Fame'
						print '4. Exit \n'
						option2 = raw_input('Enter Option: ')
						s.sendto(option2, (host, port))
						
						if option2 == '1':
							print 'Choose the difficulty:'
							print '1. Easy'
							print '2. Medium'
							print '3. Hard\n'
							difficultyLvl = raw_input('Enter option: ')
							difficultyPkt = difficultyLvl
							s.sendto(difficultyPkt, (host, port))

							gameOn = True
							while gameOn:
								gamePkt = s.recv(1024)

								if gamePkt == 'gameover':
									gameOn = False
									break

								diffPos = gamePkt.index('$')
								diff = gamePkt[:diffPos]
								diffStr = str(diff)

								turnPos = gamePkt.index('^')
								turn = gamePkt[diffPos+1:turnPos]

								wordPos = gamePkt.index('*')
								wordState = gamePkt[turnPos+1:wordPos]
								wordLen = len(wordState)
								print '\n' + wordState + '\n'
								
								guessPos = gamePkt.index('%')
								guesses = gamePkt[wordPos+1:guessPos]
								rowCntr = 0
								for g in guesses:
									sys.stdout.write(g + ' ')
									if rowCntr == wordLen:
											sys.stdout.write('\n')
											rowCntr = 0
									rowCntr = rowCntr + 1
								print '\n'
								allPlayers = gamePkt[guessPos+1:]
								numUsersInGame = allPlayers.count(':')

								for i in range(numUsersInGame):
									playernamePos = allPlayers.index('-')
									scorePos = allPlayers.index(':')
									playerName = allPlayers[:playernamePos]
									playerScore = allPlayers[playernamePos+1:scorePos]
									if playerName == turn:
											print playerName + ' ' + playerScore + ' *'
									else:
    										print playerName + ' ' + playerScore + ''
									allPlayers = allPlayers[scorePos+1:]
									
								playerGuess = raw_input('Enter Guess: ')
								if len(playerGuess) == 1:	
									playaInput = uname + playerGuess
									s.sendto(playaInput, (host, port))
								elif len(playerGuess) != 1:
										playaInput = '!' + uname + '@' + playerGuess
										s.sendto(playaInput, (host, port))

						if option2 == '2':
							print 'List of Already Started Games'
							numOfGames = s.recv(1024)
							gamesAvail = int(numOfGames)

							if gamesAvail != 0:
								someNum = 0
								someNumStr = str(someNum)
								for i in range(gamesAvail):
									print 'Game number: ' + someNumStr + ' \n'
									someNum = someNum + 1
								gameToJoin = raw_input('Enter Game Number to Join: ')
								s.sendto(gameToJoin, (host, port))
								gameOn = True

							if gamesAvail == 0:
								print 'No games started'
								gameOn = False

							while gameOn:
    								
								gamePkt = s.recv(1024)

								if gamePkt == 'gameover':
									gameOn = False
									break

								diffPos = gamePkt.index('$')
								diff = gamePkt[:diffPos]
								diffStr = str(diff)

								turnPos = gamePkt.index('^')
								turn = gamePkt[diffPos+1:turnPos]

								wordPos = gamePkt.index('*')
								wordState = gamePkt[turnPos+1:wordPos]
								wordLen = len(wordState)
								print '\n' + wordState + '\n'
								
								guessPos = gamePkt.index('%')
								guesses = gamePkt[wordPos+1:guessPos]
								rowCntr = 0
								for g in guesses:
									sys.stdout.write(g + ' ')
									if rowCntr == wordLen:
											sys.stdout.write('\n')
											rowCntr = 0
									rowCntr = rowCntr + 1
								print '\n'
								allPlayers = gamePkt[guessPos+1:]
								numUsersInGame = allPlayers.count(':')

								for i in range(numUsersInGame):
									playernamePos = allPlayers.index('-')
									scorePos = allPlayers.index(':')
									playerName = allPlayers[:playernamePos]
									playerScore = allPlayers[playernamePos+1:scorePos]
									if playerName == turn:
											print playerName + ' ' + playerScore + ' *'
									else:
    										print playerName + ' ' + playerScore + ''
									allPlayers = allPlayers[scorePos+1:]
									
								playerGuess = raw_input('Enter Guess: ')
								if len(playerGuess) == 1:	
									playaInput = uname + playerGuess
									s.sendto(playaInput, (host, port))
								elif len(playerGuess) != 1:
										playaInput = '!' + uname + '@' + playerGuess
										s.sendto(playaInput, (host, port))

						# View hall of fame while logged in
						if option2 == '3':
							hof = s.recv(1024)
						
							numEntriesInHof = hof.count(':')
							print '\tHall of Fame\t'

							for i in range(numEntriesInHof):
								playernamePos = hof.index('-')
								scorePos = hof.index(':')
								playerName = hof[:playernamePos]
								playerScore = hof[playernamePos+1:scorePos]
								print playerName + ' ' + playerScore
								hof = hof[scorePos+1:]
					
						# Client exits and connection closes while logged in
						if option2 == '4':
							s.close()
			
	# Create new user
	if option == '2':
			s.sendto(option, (host, port))
			newUname = raw_input('What is Your User Name? ')
			newPword = raw_input('What is Your Password? ')
			newAccountPkt = newUname + ':' + newPword
			s.sendto(newAccountPkt, (host, port))
			stuff = s.recv(4096)
			if stuff == 'Username taken':
    				print 'User not created because username is taken\n'
			if stuff != 'Username taken':
    				print 'User created: ' + stuff
	
	# View hall of fame
	if option == '3':
		hof = s.recv(1024)
	
		numEntriesInHof = hof.count(':')
		print '\tHall of Fame\t'

		for i in range(numEntriesInHof):
			playernamePos = hof.index('-')
			scorePos = hof.index(':')
			playerName = hof[:playernamePos]
			playerScore = hof[playernamePos+1:scorePos]
			print playerName + ' ' + playerScore
			hof = hof[scorePos+1:]
	
	# Client exits and connection closes
	if option == '4':
		s.close()
s.close()
