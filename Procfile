#web: python steamFriendRater/manage.py runserver 0.0.0.0:$PORT --noreload
web: python steamFriendRater/manage.py run_gunicorn -b "0.0.0.0:$PORT" -w 10
#just commenting out so i can debug
#Bug: timeout getting xml files