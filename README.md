# Whack an Ad (Pi-hole)
Simple Python script to try to identify what server addresses are serving ads on Youtube.

Basically, it downloads query log database (pihole-FTL.db) from Pi-hole (Raspberry), marks records with timestamps loaded from CSV (where I recorded times when commerical started in youtube video) + 30 seconds before and saves all in new CVS file for further inspection/analysis. 
The thesis is that servers with domain XXXXXXXXXX.googlevideo.com serve the ads, but also the video itself, so if we identify ones that are called just before ad started, we can block them. 

For recording timestamps of ad starting, I use simple Shortcuts script on iPhone which takes current timedate and saves it to a local file, and another one to send the list via email. It is easy to click while watching YT video on TV. The CSV format is 'yyyy-mm-dd hh:mm:ss' per row.

This is in test phase and if proves useful, I'll try to autmate it (except recording of ad begining timestamp). 
Mechanics behind youtube ad serving is unknown so it could be that same addresses are used for both, videos and ads, interchangeably.
In that case, blocking youtube ads on TV (or similar devices) is not hit and miss, but unsolvable...
