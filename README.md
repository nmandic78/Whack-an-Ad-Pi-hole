# Whack an Ad (Pi-hole)
Simple Python script to try to identify what server addresses are serving ads on Youtube.

The thesis is that servers with domain XXXXXXXXXX.googlevideo.com serve the ads, but also the video itself, so if we identify ones that are called just before ad started, we can block them with Pi-hole.
Specifically, we try to solve this for smart TV (for PC, there are better solutions available).

We need few things.<br>
Record timestamps when ads began (automatically if possible).<br>
Get query log database from Pi-hole (pihole-FTL.db).<br>
Mark records in Pi-hole database where timestamps are between ad beginning and some seconds before (we don't know when smart TV app loads the ad; probably some time before).<br>
Analyze marked records/addresses to detect potential ad serving addresses.<br>
Block them in Pi-hole.<br>
Monitor for false positives (if blocked, could disable normal video stream) and update detection pattern.<br><br>

**Recording ads timestamps**<br>
There are few options. First, I did it with Shortcuts script on iPhone which takes current timedate and saves it to a local file, and another one to send the list via email. ~~It is easy to click while watching YT video on TV.~~
Well, it is not that easy and soon become frustrating...
Second option/solution use webcam (ESP32-CAM, but any will do) mounted in front of TV (lower right corner) and uses OpenCV template matching to detect SKIP AD banner/button. Timestamps are then saved in CSV file which are loaded by main script for merge with query database.
There are few versions of banners (SKIP AD, SKIP ADS, Video will begin in ...). They are pretty prominent and specific so it is not a problem to reliably detect them.
<br>Take picture of banner you want to detect, crop it and save in same dir as script. [Two examples I use](https://github.com/nmandic78/Whack-an-Ad-Pi-hole/tree/main/images).

**Analysis**<br>
I noticed many (2-6) XXXXXXXXXX.googlevideo.com addresses are called in seconds preceding the ad start. Some of them are our potential suspects. I mark them all and count them. Then count all occurrences of those same addresses in Pi-hole database. If you record ad times regularly, it is to believe that count of recorded addresses versus not recorded count of same addresses will be high for ones serving ads. If we record all, theoretically it should be 100%. Other (false positive suspects) are serving normal videos at other times and share should be small.

[YT_add_detect.py](https://github.com/nmandic78/Whack-an-Ad-Pi-hole/blob/main/YT_add_detect.py) will detect Youtube ads and record timestamps in CSV.

Main script ([PiHole_YT_ad_finder.py](https://github.com/nmandic78/Whack-an-Ad-Pi-hole/blob/main/PiHole_YT_ad_finder.py)) will: 
* connect to Raspberry via SSH
* download pihole-FTL.db
* load CSV with recorded ad timestamps
* mark suspect addresses (containing googlevideos.com, from ad timestamp to 20 seconds in past)
* calculate share and save result in new CSV

Try blocking addresses with high share (depends on ad times recording method so experiment).

Mechanics behind youtube ad serving is unknown so it could be that same addresses are used for both, videos and ads, interchangeably. In that case, blocking youtube ads on TV (or similar devices) is not hit and miss, but unsolvable...

NOTE:
I use Raspberry Pi Zero W for Pi-hole and it showed unreliable (freezing every day). And it seems, it is the case what I wrote in las sentence. Well, it was interesting.
