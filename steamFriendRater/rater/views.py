from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from pyquery import PyQuery as pq
from lxml import etree 
from collections import defaultdict
from urlparse import urlparse
import urllib
import re 
import socket


def getUserName(userProfileLink):
	#TODO: below breaks if user gives an invalid userProfileLink
	#TODO: regex check a valid userProfileLink before continuing
	#    return gamesList if invalid userProfileLink
	socket.setdefaulttimeout(30)
	page = pq(userProfileLink+"/games?tab=all&xml=1", parser="xml", timeout=30)
	return page('gamesList')('steamID').text()

def getGameList(userProfileLink):
	gamesList = []
	socket.setdefaulttimeout(30)
	page = pq(userProfileLink+"/games?tab=all&xml=1", parser="xml", timeout=30)
	#print page('gamesList')('steamID').text()
	games = page('gamesList')('games')('game')

	hasPlayedLastTwoWeeks = True
	i = 0
	while hasPlayedLastTwoWeeks:
		if games.eq(i)('hoursLast2Weeks'):
			#print games.eq(i)('name').text()
			gamesList.append(games.eq(i)('name').text())
			i += 1
		else:
			hasPlayedLastTwoWeeks = False

	return gamesList

def getFullGameList(userProfileLink):
	gamesList = []
	socket.setdefaulttimeout(30)
	page = pq(userProfileLink+"/games?tab=all&xml=1", parser="xml", timeout=30)
	#print page('gamesList')('steamID').text()
	games = page('gamesList')('games')('game')

	i = 0
	for i in range(len(games)):
		gamesList.append(games.eq(i)('name').text())

	return gamesList

def getFriendsAndProfileLinks(userProfileLink):
	friendDic = {}
	socket.setdefaulttimeout(30)
	page = pq(userProfileLink +"/friends?xml=1", parser="xml", timeout=30)
	friends = page('friendsList')('friends')('friend')

	i = 0
	for i in range(len(friends)):
		iD = friends.eq(i).text()
		friendDic[iD] = ["http://steamcommunity.com/profiles/"+iD]
	return friendDic

def getScore(userGames, friendGames):
	score = 0
	for game in userGames:
		if(friendGames.count(game) != 0):
			score += 1
	return float(score) / len(userGames) * 100.0

def normalizeRankings(rankings):
	normRanks = []
	## TODO: Implement me maybe
	return normRanks

def rank(request):
	#numGames = 20 --> old implementation
	if not 'username' in request.POST:
		return render_to_response('rater/index.html', context_instance=RequestContext(request))

	userName = request.POST['username']
	userGames = getGameList(userName)

	if not userGames:
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You didn't enter a valid url to the Steam Profile Page",
		}, context_instance=RequestContext(request))

	userFriendDic = getFriendsAndProfileLinks(userName)

	if not userFriendDic:
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You don't have any friends yet :(",
		}, context_instance=RequestContext(request))

	for friend in userFriendDic:
		gameList = getGameList(userFriendDic[friend][0])
		userFriendDic[friend].append(gameList)
		userFriendDic[friend].append(getScore(userGames, gameList))

	userFriendDic = sorted(userFriendDic.items(), key=lambda x: -x[1][2])
	return render_to_response('rater/rating.html', {
		'username': userName,
		'user_game_list': userGames,
		'user_friend_dic': userFriendDic,
	}, context_instance=RequestContext(request))


def compare(request):
	if not 'username' in request.POST:
		return render_to_response('rater/index.html', context_instance=RequestContext(request))
	if not 'friend' in request.POST:
		return render_to_response('rater/index.html', context_instance=RequestContext(request))

	userName = request.POST['username']
	friend = request.POST['friend']

	urlTest = urlparse(userName)
	if urlTest.scheme not in ['http', 'https'] :
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You didn't enter a valid url to your Steam Profile Page",
		}, context_instance=RequestContext(request))

	urlTest = urlparse(friend)
	if urlTest.scheme not in ['http', 'https'] :
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You didn't enter a valid url for your Friend's Steam Profile Page",
		}, context_instance=RequestContext(request))

	userGames = getFullGameList(userName)

	if not userGames:
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You didn't enter a valid url to your Steam Profile Page",
		}, context_instance=RequestContext(request))

	friendGames = getFullGameList(friend)

	if not friendGames:
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You didn't enter a valid url to your Friend's Steam Profile Page",
		}, context_instance=RequestContext(request))

	userName = getUserName(userName)
	friend = getUserName(friend)

	return render_to_response('rater/compare.html', {
		'username': userName,
		'friend': friend,
		'user_game_list': userGames,
		'friend_game_list': friendGames,
	}, context_instance=RequestContext(request))
