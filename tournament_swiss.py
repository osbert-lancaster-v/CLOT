
import logging
import random
from copy import deepcopy

from mwmatching import maxWeightMatching
import new_utility_functions
import main
import players
import games
import clot


def seeIfTourneyCanStart_Swiss(tourney_id):
	"""this is the special swiss version of the function"""
	
	ppp = players.Player.all().filter("tourney_id =", tourney_id)
	count = 0
	for p in ppp:
		if p.isParticipating:
			count += 1
	
	if count >= main.getMinimumNumberOfPlayers(tourney_id):
		if (not main.isTourneyInPlay(tourney_id)) and (not main.hasTourneyFinished(tourney_id)):
			if main.areWePastStarttime(tourney_id):
				main.startTourney(tourney_id)
				logging.info('tourney starting')
				return True
	else:
		logging.info('tourney doesnt yet have enough players to start.  num active players = '+str(count)+' num needed players = '+str(main.getMinimumNumberOfPlayers(tourney_id)))
		return False


def getMatchedList_Swiss(tourney_id):
	"""pair up the players according to the swiss tournament matching rules"""

	#head_to_head_biggermat
	head_to_head_biggermat, head_to_head_2d = new_utility_functions.getHeadToHeadTable(tourney_id)

	num_players = len(head_to_head_biggermat)-1
	assert(num_players>=2)

	#in this function, we use ids from 0 to num_players.
	#here, we create a mapping from these ids to the database's player_ids, 
	#randomly shuffled to try and avoid paterns in the matching
	temp = deepcopy(head_to_head_biggermat[0][1:])
	playersidlocal_playerids = [temp[i] for i in range(0,num_players)]
	logging.info('playersidlocal_playerids')
	logging.info(playersidlocal_playerids)

	num_wins = []
	num_games = []
	for i in range(0,num_players):
		num_wins.append(0)
		num_games.append(0)
		for j  in range(0,num_players):
			num_wins[i] += head_to_head_2d[i][j][0]
			num_games[i] += (head_to_head_2d[i][j][0]+head_to_head_2d[i][j][0])/2

	#deal with odd num_players
	player_who_sits_out = -1
	if num_players%2 == 1:
		tmp = zip(num_games,range(0,num_players))
		tmp.sort()
		logging.info('tmp')
		logging.info(tmp)
		player_who_sits_out = tmp[-1][1] #this player is one who has highest number of games
		logging.info('player_who_sits_out')
		logging.info(player_who_sits_out)

	#make edges
	edges=[]
	for i in range(0,num_players):
		for j  in range(i+1,num_players):
			if (head_to_head_2d[i][j][0]==0) and (head_to_head_2d[i][j][1]==0):
				if (player_who_sits_out!=i) and (player_who_sits_out!=j):
					# i,j have not played yet
					abs_win_diff = abs(num_wins[i]-num_wins[j])
					edges.append((i,j,-abs_win_diff+0.1*random.random())) #note the - sign.  the 0.1*random.random() is to randomise things WITHOUT changing the ranking of num wins etc. 
				else:
					edges.append((i,j,-1000000)) #a big number, to ensure we never make this match
	logging.info('edges')
	logging.info(edges)

	#call the clever matching algorithm
	matchups = maxWeightMatching(edges,True)
	logging.info('matchups')
	logging.info(matchups)
	if not matchups:
		return [] #we havent got any matchups.  likely that the tournament is over. 

	#package matchups into right format
	doneq = [False] * num_players
	new_match_list = []
	for i in range(0,len(matchups)):
		if not doneq[i]:
			doneq[i]=True
			j = matchups[i]
			if j != -1:
				doneq[j]=True
			
				i_id = playersidlocal_playerids[i]
				j_id = playersidlocal_playerids[j]
			
				new_match_list.append(str(i_id))
				new_match_list.append(str(j_id))
	##if player_who_sits_out >= 0:
	##	new_match_list.append(str(playersidlocal_playerids[player_who_sits_out])) #he wont get a game though, because of the odd number

	logging.info('new_match_list')
	logging.info(new_match_list)
	
	return new_match_list


def getTourneyRoundsAndGameInfo(tourney_id):
	"""this function returns a table of strings, 
	for display on the  /tourneys/tourney_id  html page.  the information is specific to swiss tournaments.
	the information is just a list of the game in each round, showing who won and who lost"""
	
	#Load all finished games
	finished_games = clot.getFinishedGames(tourney_id)
	finished_games_sorted_by_creation_date = [game for game in finished_games]
	finished_games_sorted_by_creation_date.sort(key=lambda x: x.dateCreated)
	logging.info("finished_games_sorted_by_creation_date:")
	logging.info(finished_games_sorted_by_creation_date)

	#get player_id : name   dict
	players_id_name_dict = clot.getPlayersIDNameDict(tourney_id)
	logging.info('players_id_name_dict')
	logging.info(players_id_name_dict)

	#get list of players, sorted by currentRank, highest First.
	players_sorted_by_rank = [[p.player_id, p.currentRank] for p in players.Player.all().filter("tourney_id =", tourney_id)]
	players_sorted_by_rank.sort(key=lambda x: x[1])
	players_ids_sorted_by_rank = [int(p[0]) for p in players_sorted_by_rank]
	##logging.info('players_ids_sorted_by_rank')
	##logging.info(players_ids_sorted_by_rank)


	#~~~~~~
	player_game_count = {} #key is player_id
	for player_id in players_ids_sorted_by_rank:
		player_game_count[player_id] = 0

	#make the games_string_table
	i_round = 0
	games_string_table = [['round 1']]
	tmp = []
	for game in finished_games_sorted_by_creation_date:
		winner_id = game.winner
		loser_id = game.loser
		winner_name = players_id_name_dict[winner_id].name
		loser_name = players_id_name_dict[loser_id].name
		game_name_str = winner_name +'\n beat '+ loser_name
		
		player_game_count[winner_id] += 1
		player_game_count[loser_id] += 1
		if (player_game_count[winner_id]>i_round) or (player_game_count[loser_id]>i_round): #we have moved on to the next round
			assert abs( player_game_count[winner_id] - player_game_count[loser_id] ) <= 1
			i_round += 1
			
			if i_round > 1:
				games_string_table.append(['round '+str(i_round)])

				tmp.sort()
				logging.info('tmp:')
				logging.info(tmp)
				for g in tmp:
					games_string_table[i_round-2].append(g[1])
				tmp = []
		
		best_rank = min(players_ids_sorted_by_rank.index(winner_id) , players_ids_sorted_by_rank.index(loser_id))
		
		if tmp==[]:
			tmp = [[best_rank,game_name_str]]
		else:
			tmp.append([best_rank,game_name_str])

	tmp.sort()
	for g in tmp:
		games_string_table[i_round-1].append(g[1])


	logging.info('games_string_table:')
	logging.info(games_string_table)

	games_string_table_transposed = zip(*games_string_table) #transpose the table
	return games_string_table_transposed


def createGames_Swiss(tourney_id):
	"""This is called periodically to check if a round has finished.  If so, new games are created.
	the 'swiss' part is that we match players based on ranking - we match players with similar 
	rankings who have not yet played each other.  if there are an odd number of players, 
	then someone randomly misses a game (and we prefer players who have not yet missed a game) """

	logging.info('')
	logging.info('in createGames_Swiss()')

	if main.hasTourneyFinished(tourney_id):
		logging.info('swiss tourney has finished')
		return

	#Retrieve all games that are ongoing
	activeGames = list(games.Game.all().filter("winner =", None).filter("tourney_id =", tourney_id))
	activeGameIDs = dict([[g.key().id(), g] for g in activeGames])
	logging.info("Active games: " + str(activeGameIDs))

	if activeGames:
		logging.info('games still in progress.  cannot start next round until these games finish.')
	else:
		logging.info('no games in progress.  so we move on to the next round.')
		
		if main.getRoundNumber(tourney_id) == main.getNumRounds(tourney_id):
			main.endTourney(tourney_id)
			logging.info('')
			logging.info('all rounds have been played, so TOURNAMENT IS OVER !!!!!!!!!!!!!!')
			logging.info('')
			return

		players_ids_matched_list = getMatchedList_Swiss(tourney_id)

		if not players_ids_matched_list:
			main.endTourney(tourney_id)
			logging.info('')
			logging.info('seems everyone has played everyone else, so TOURNAMENT IS OVER !!!!!!!!!!!!!!')
			logging.info('')
			return

		players_ids_names_dict = dict([[gp.player_id, gp] for gp in players.Player.all().filter("tourney_id =", tourney_id)])
		logging.info('players_ids_names_dict')
		logging.info(players_ids_names_dict)

		players_names_matched_list = [players_ids_names_dict[i] for i in players_ids_matched_list]

		#The template ID defines the settings used when the game is created.  You can create your own template on warlight.net and enter its ID here
		templateID = main.getTemplateID(tourney_id)

		#Create a game for everyone not in a game.
		gamesCreated = [games.createGame(pair, templateID, tourney_id) for pair in clot.pairs(players_names_matched_list)]
		logging.info("Created games " + str(gamesCreated))
		
		main.incrementRoundNumber(tourney_id)
		logging.info("\n ------------------------------------ \n swiss tourney round " + str(main.getRoundNumber(tourney_id))+ " starting.  \n ---------------------------")
	logging.info('')













