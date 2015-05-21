import urllib.request #, urllib.error, urllib.parse
import math
##from PIL import Image
##import io
import re
import html.parser


import ircbot_chk   #for swear detect function
import mod_lookup
#import megahal_mod  #for recording messages into brains.
import mod_calc      #for auto calculation when calculations posted in channel.


endl = '\r\n'
class mod_passive():
    def fnn_passive(self,args,client,destination):
        # SPANGLE ADDED THIS, should run his extrayammering command, a command to say things (only) when not spoken to... oh god.
        mod_passive.fnn_sweardetect(self,args,client,destination)
#        megahal_mod.megahal_mod.fnn_megahalrecord(self,args,client,destination)
#        if(len(args)>2 and args[:2].lower()=='_s' and '_s' not in [user.lower() for user in self.core['server'][destination[0]]['channel'][destination[1]]['user_list']]):
#            return megahal_mod.megahal_mod.fn_speak(self,args[2:],client,destination)
        ##check if passive functions are disabled.
        if(not self.conf['server'][destination[0]]['channel'][destination[1]]['passivefunc']):
            return None
        out = mod_passive.fnn_urldetect(self,args,client,destination)
        if(out is not None):
            return out
        if(ircbot_chk.ircbot_chk.chk_msg_calc(self,args) and not ircbot_chk.ircbot_chk.chk_msg_numbers(self,args)):
            return mod_calc.mod_calc.fn_calc(self,args,client,destination)

    def fnn_urldetect(self, args, client, destination):
        'Detects URLs posted in channel, then returns the page title.'
        regex = r'\b((https?://|www.)[-A-Z0-9+&?%@#/=~_|$:,.]*[A-Z0-9+\&@#/%=~_|$])'
        if re.search(regex, args, re.I):
            url = re.search(regex, args, re.I).group(1)
            if('127.0.0.1' in url or '192.168.' in url or '10.' in url or '172.' in url):
                return None
            if("://" not in url):
                url = "http://" + url
            pagerequest = urllib.request.Request(url)
            pagerequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
            pageopener = urllib.request.build_opener()
            pageinfo = str(pageopener.open(pagerequest).info())
            if("Content-Type:" in pageinfo):
                pagetype = pageinfo.split()[pageinfo.split().index('Content-Type:')+1]
            else:
                pagetype = ''
            if('speedtest.net' in url):
                return
            elif('imgur.com' in url):
#           3afbdcb1353b72f imgur API client-ID
                if('/a/' in url):
#           http://imgur.com/a/qJctj#0 example imgur album
                    imgur_id = url.split('/')[-1].split('#')[0]
                    api_url = 'https://api.imgur.com/3/album/' + imgur_id
                    api_dict = mod_lookup.mod_lookup.fnn_loadjson(self,api_url,[['Authorization','Client-ID 3afbdcb1353b72f']])
                    title = api_dict['data']['title']
                    views = api_dict['data']['views']
                    if('section' in api_dict['data']):
                        section = api_dict['data']['section']
                        album_info = 'Album title: ' + title + ' | Gallery views: ' + "{:,}".format(views) + ' | Section: ' + section
                    else:
                            album_info = 'Album title: ' + title + ' | Gallery views: ' + "{:,}".format(views)
                    pic_number = url.split('#')[-1]
                    album_count = api_dict['data']['images_count']
                    img_width = api_dict['data']['images'][int(pic_number)]['width']
                    img_height = api_dict['data']['images'][int(pic_number)]['height']
                    img_size = api_dict['data']['images'][int(pic_number)]['size']
                    img_sizestr = mod_passive.fnn_sizestr(self,int(img_size))
                    return "Imgur album> " + album_info + " | Image " + str(int(pic_number)+1) + " of " + str(album_count) + " | Current image: " + str(img_width) + "x" + str(img_height) + ", " + img_sizestr + "."
                else:
# http://i.imgur.com/2XBqIIT.jpg example imgur direct link
# http://imgur.com/2XBqIIT example imgur link
                    imgur_id = url.split('/')[-1].split('.')[0]
                    api_url = 'https://api.imgur.com/3/image/' + imgur_id
                    api_dict = mod_lookup.mod_lookup.fnn_loadjson(self,api_url,[['Authorization','Client-ID 3afbdcb1353b72f']])
                    title = str(api_dict['data']['title'])
                    img_width = str(api_dict['data']['width'])
                    img_height = str(api_dict['data']['height'])
                    img_size = api_dict['data']['size']
                    img_sizestr = str(mod_passive.fnn_sizestr(self,int(img_size)))
                    views = api_dict['data']['views']
                    return "Imgur> Title: " + title + " | Size: " + img_width + "x" + img_height + " | Filesize: " + img_sizestr + " | Views: " + "{:,}".format(views) + "."
            elif("image" in pagetype):
                return
            elif('youtube.com' in url or 'youtu.be' in url):
                code = pageopener.open(pagerequest).read().decode('utf-8','ignore')
                length = re.search('length_seconds": "([0-9]*)', code).group(1)
                length_str = str(int(int(length)/60)) + "m " + str(int(length)-(60*(int(int(length)/60)))) + "s"
                views = re.search('class="watch-view-count[^>]*>[\n\r\s]*([0-9,+]*)',code).group(1)
                #title = ' '.join(re.search('<title[-A-Z0-9"=' + "'" + ' ]*>\b*([^<]*)\b*</title>',code).group(1)[:-10].split()).replace('&lt;','<').replace('&gt;','>').replace('&#39;',"'").replace('&#039;',"'").replace('&quot;','"').replace('&amp;','&')
                title = ' '.join(re.search('<title[-A-Z0-9"=' + "'" + ' ]*>\b*([^<]*)\b*</title>',code,re.I).group(1)[:-10].split())
                h = html.parser.HTMLParser()
                title = h.unescape(title)
                return "Youtube video> Title: " + title + " | Length: " + length_str + " | Views: " + views + "."
            elif('amazon.co.uk' in url or 'amazon.com' in url):
                code = pageopener.open(pagerequest).read().decode('utf-8','ignore')
                title = re.search('<title>([^<]*)</title>',code,re.I).group(1)
                price = re.search('<b class="priceLarge">([^<]*)</b>',code).group(1)
                if(code.count('There are no customer reviews yet.')!=0):
                    reviewstr = "No reviews yet."
                else:
                    stars = re.search('<span>([0-9.]*) out of 5 stars',code).group(1)
                    reviews = re.search('>([0-9]*) customer reviews',code).group(1)
                    reviewstr = stars + "/5 stars, from " + reviews + " reviews"
                return "Amazon> Title: " + title + " | Price: " + price + " | " + reviewstr + "."
            elif('ebay.co.uk' in url or 'ebay.com' in url):
                code = pageopener.open(pagerequest).read().decode('utf-8','ignore')
                title = re.search('<meta property="og:title" content="([^"]*)">',code).group(1)
                price = re.search('itemprop="price"([^>]*)>([^<]*)</span>',code).group(2)
                if(code.count('Current bid:')==1):
                    page_type = 'Buy it now.'
                    time_left = re.search('id="vi-cdown_timeLeft">([^<]*)<',code).group(1)
                else:
                    page_type = 'Auction'
                    bids = re.search('<span id="qty-test">([0-9]*)</span> <span>bids',code).group(1)
                    if(bids==1):
                        page_type = page_type + ", " + bids + "bid."
                    else:
                        page_type = page_type + ", " + bids + "bids."
                    time_left = re.search('id="vi-cdown_timeLeft">([^<]*)<',code).group(1)
                #time left
                return "eBay> Title: " + title + " | " + page_type + " | Time left: " + time_left + "."
            elif('imdb.com/title' in url):
                code = pageopener.open(pagerequest).read().decode('utf-8')
                movie_code = re.search('title/(tt[0-9]*)',code).group(1)
                api_url = 'http://www.omdbapi.com/?i=' + movie_code
                api_dict = mod_lookup.mod_lookup.fnn_loadjson(self,api_url)
                title = api_dict['Title']
                year = api_dict['Year']
                genre = api_dict['Genre']
                rating = api_dict['imdbRating']
                votes = api_dict['imdbVotes']
                return "IMDB> Title: " + title + " (" + year + ") | Rated " + rating + "/10, " + votes + " votes. | Genres: " + genre  + "."
            else:
                return

    def fnn_sizestr(self,size):
        if(size<2048):
            sizestr = str(size) + "Bytes"
        elif(size<(2048*1024)):
            sizestr = str(math.floor(float(size)/10.24)/100) + "KiB"
        elif(size<(2048*1024*1024)):
            sizestr = str(math.floor(float(size)/(1024*10.24))/100) + "MiB"
        else:
            sizestr = str(math.floor(float(size)/(1024*1024*10.24))/100) + "GiB"
        return sizestr

