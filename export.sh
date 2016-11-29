#! /bin/sh
### BEGIN INIT INFO

cp ../mumo/modules/twitterstream.py .
cp ../mumo/modules-available/twitterstream.ini .


sed -i.bak 's/CONSUMER_KEY\ *= [a-zA-Z0-9]*$/CONSUMER_KEY        = ########/g' ./twitterstream.ini
sed -i 's/CONSUMER_SECRET\ *= [a-zA-Z0-9]*$/CONSUMER_SECRET     = ########/g' ./twitterstream.ini
sed -i 's/ACCESS_TOKEN\ *= [a-zA-Z0-9\-]*$/ACCESS_TOKEN        = ########/g' ./twitterstream.ini
sed -i 's/ACCESS_TOKEN_SECRET = [a-zA-Z0-9]*$/ACCESS_TOKEN_SECRET = ########/g' ./twitterstream.ini


#echo "DELETE FROM controlled_channels;" |  sqlite3 ./export_createcon/createcon.sqlite
#echo "DELETE FROM controlled_channels_stats;" |  sqlite3 ./export_createcon/createcon.sqlite
#echo "VACUUM;" |  sqlite3 ./export_createcon/createcon.sqlite

#add README.md
#git remote add origin https://github.com/pp-pacman/mumo-conference.git
#git push -u origin master
#git add createcon.ini
#git add createcon.py
#git add createcon.sqlite
#git commit -m "second commit"
#git push -u origin master

                          



