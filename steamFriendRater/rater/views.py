from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils import simplejson
from pyquery import PyQuery as pq
from lxml import etree 
from collections import defaultdict
import urllib
import re 

#TODO: Remove this function
#TODO: Have the user input their full link to their profile
#	To avoid having to ask them which type it is in order to get a link
def getGameList(username):
	gamesList = []
	page = pq("http://steamcommunity.com/id/"+ username +"/games?tab=all")
	toParse = page("script[language*=javascript]")

	#Use Regex to parse out rgGames array
	re1='.*?'
	re2='(\\[.*?\\])'

	rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
	m = rg.search(str(toParse))
	gameInfo = ""
	if m:
	    gameInfo=m.group(1)
	else:
		 return gamesList   
	
	#Separate each game
	re1 = '\\{(.*?)\\}'
	rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
	games = rg.findall(gameInfo)

	#Save only the name of each game
	for game in games:
		re1 = '.*?'
		re2 = '.*?,'
		re3='(.*?),'
		rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
		m = rg.search(game)
		if not m:
			return gamesList	
		gamesList.append(m.group(1)[8:-1])

	return gamesList

def getFriendGameList(userProfileLink):
	gamesList = []
	page = pq(userProfileLink+"/games?tab=all")
	toParse = page("script[language*=javascript]")

	#Use Regex to parse out rgGames array
	re1='.*?'
	re2='(\\[.*?\\])'

	rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
	m = rg.search(str(toParse))
	gameInfo = ""
	if m:
	    gameInfo=m.group(1)
	else:
		 return gamesList   
	
	#Separate each game
	re1 = '\\{(.*?)\\}'
	rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
	games = rg.findall(gameInfo)

	#Save only the name of each game
	for game in games:
		re1 = '.*?'
		re2 = '.*?,'
		re3='(.*?),'
		rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
		m = rg.search(game)
		if not m:
			return gamesList	
		gamesList.append(m.group(1)[8:-1])

	return gamesList

def getFriendsAndProfileLinks(username):
	friendDic= {}
	page = pq("http://steamcommunity.com/id/"+ username +"/friends")
	# Offline Friends
	offParse = page(".linkFriend_offline")
	offlineCount = len(offParse)
	for i in range(offlineCount):
		friendDic[offParse.eq(i).text()] = [offParse.eq(i).attr("href")]
		
	# Online Friends
	onParse = page(".linkFriend_online")
	onCount = len(onParse)
	for i in range(onCount):
		friendDic[onParse.eq(i).text()] = [onParse.eq(i).attr("href")]
	
	# Ingame Friends
	inGameParse = page(".linkFriend_in-game").filter("a")
	inCount = len(inGameParse)
	for i in range(inCount):
		friendDic[inGameParse.eq(i).text()] = [inGameParse.eq(i).attr("href")]
	return friendDic

def getScore(userGames, friendGames):
	#compute top 20 ranking
	userGames = userGames[:20]
	score = 0

	for game in userGames:
		if(friendGames.count(game) != 0):
			score += 1
	return float(score) / 20.0 * 100

def rank(request):
	userName = request.POST['username']
	userGames = getGameList(userName)

	if not userGames:
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You didn't enter a valid Steam Id.",
		}, context_instance=RequestContext(request))

	userFriendDic = getFriendsAndProfileLinks(userName)

	if not userFriendDic:
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You don't have any friends yet :(",
		}, context_instance=RequestContext(request))

	for friend in userFriendDic:
		gameList = getFriendGameList(userFriendDic[friend][0])
		userFriendDic[friend].append(gameList[:20])
		userFriendDic[friend].append(getScore(userGames, gameList[:20]))

	userFriendDic = sorted(userFriendDic.items(), key=lambda x: -x[1][2])
	return render_to_response('rater/rating.html', {
		'username': userName,
		'user_game_list': userGames[:20],
		'user_friend_dic': userFriendDic,
	}, context_instance=RequestContext(request))


