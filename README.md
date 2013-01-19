steam-friend-diff
=================

Django site that shows the library differences and similarities between 2 Steam users. Debug site is live on heroku [here] (http://safe-woodland-4385.herokuapp.com/rateMyFriends/)

Current problems:
 * Steam Community API is currently heavily rate limited and has long loading times and HTTP 503 errors. See [here] (http://steamcommunity.com/discussions/forum/7/846941710472857299/) for a conversation.
 * The new Steam web Api has no easy way to get a list of games owned by a user (which is easily accessible in the older Steam Community Api (which is cripplingly slow at times as mentioned above).
