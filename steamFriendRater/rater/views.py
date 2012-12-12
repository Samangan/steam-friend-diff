from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from pyquery import PyQuery as pq
from lxml import etree 
from collections import defaultdict
from urlparse import urlparse
import urllib
import urllib2
import re 
import socket
import time

#TODO: change all non views to something_something_etc
#		0check out python coding standards

#TODO: 
#	-See Xin convo:
#		-Display only your friend's list??
#		-Display them both side by-side..--> yes I think
#		-Filter by game genre (mutliplayer, mmo, casual, indie, etc)
#			-THINK: how to get that information:
#			-Keep a database of lists of game genres and games
#			-update changes to that DB every night (by scraping the store pages for each genre)
def retry(ExceptionToCheck, tries=10, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        excpetions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            try_one_last_time = True
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                    try_one_last_time = False
                    break
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if try_one_last_time:
                return f(*args, **kwargs)
            return
        return f_retry  # true decorator
    return deco_retry

def getUserName(userProfileLink):
	#socket.setdefaulttimeout(30)
	@retry(urllib2.URLError)
	def urlOpenRetry():
		return pq(userProfileLink+"/games?tab=all&xml=1", parser="xml")	
	return urlOpenRetry()('gamesList')('steamID').text()

def getGameList(userProfileLink):
	gamesList = []
	#socket.setdefaulttimeout(30)
	@retry(urllib2.URLError)
	def urlOpenRetry():
		return pq(userProfileLink+"/games?tab=all&xml=1", parser="xml")
	games = urlOpenRetry()('gamesList')('games')('game')
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
	#socket.setdefaulttimeout(30)
	@retry(urllib2.URLError)
	def urlOpenRetry():
		return pq(userProfileLink+"/games?tab=all&xml=1", parser="xml")
	#print page('gamesList')('steamID').text()
	games = urlOpenRetry()('gamesList')('games')('game')

	i = 0
	for i in range(len(games)):
		gamesList.append(games.eq(i)('name').text())

	return urlOpenRetry()('gamesList')('steamID').text(), gamesList

def getFriendsAndProfileLinks(userProfileLink):
	friendDic = {}
	#socket.setdefaulttimeout(30)
	@retry(urllib2.URLError)
	def urlOpenRetry():
		return pq(userProfileLink +"/friends?xml=1", parser="xml")
	friends = urlOpenRetry()('friendsList')('friends')('friend')

	i = 0
	for i in range(len(friends)):
		iD = friends.eq(i).text()
		friendDic[getUserName("http://steamcommunity.com/profiles/"+iD)] = ["http://steamcommunity.com/profiles/"+iD]
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
		'username': getUserName(userName),
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
	if urlTest.scheme not in ['http', 'https'] or urlTest.netloc != "steamcommunity.com":
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You didn't enter a valid url to your Steam Profile Page",
		}, context_instance=RequestContext(request))

	urlTest = urlparse(friend)
	if urlTest.scheme not in ['http', 'https'] or urlTest.netloc != "steamcommunity.com":
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You didn't enter a valid url for your Friend's Steam Profile Page",
		}, context_instance=RequestContext(request))

	userName, userGames = getFullGameList(userName)

	if not userGames:
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You didn't enter a valid url to your Steam Profile Page",
		}, context_instance=RequestContext(request))

	friend, friendGames = getFullGameList(friend)

	if not friendGames:
		return render_to_response('rater/index.html', {
			'error_message': "Rating Failed! You didn't enter a valid url to your Friend's Steam Profile Page",
		}, context_instance=RequestContext(request))

	intersectionCount = 0
	for game in userGames:
		if game in friendGames:
			intersectionCount += 1
	
	userCount = len(userGames) - intersectionCount
	friendCount = len(friendGames) - intersectionCount

	return render_to_response('rater/compare.html', {
		'username': userName,
		'friend': friend,
		'user_game_list': userGames,
		'friend_game_list': friendGames,
		'intersection_count': intersectionCount,
		'user_count':userCount,
		'friend_count':friendCount,
	}, context_instance=RequestContext(request))
