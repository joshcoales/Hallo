from Function import Function
from inc.commons import Commons
import random
from xml.dom import minidom
import difflib
import re
import urllib.parse
import struct       #UrlDetect image size
import imghdr       #UrlDetect image size
import math
import html.parser

class UrbanDictionary(Function):
    '''
    Urban Dictionary lookup function.
    '''
    #Name for use in help listing
    mHelpName = "urban dictionary"
    #Names which can be used to address the function
    mNames = set(["urban dictionary","urban","urbandictionary","ud"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Gives the top urban dictionary definition for a word. Format: urban dictionary <word>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        urlLine = line.replace(' ','+').lower()
        url = 'http://api.urbandictionary.com/v0/define?term=' + urlLine
        urbandict = Commons.loadUrlJson(url)
        if(len(urbandict['list'])>0):
            definition = urbandict['list'][0]['definition'].replace("\r",'').replace("\n",'')
            return definition
        else:
            return "Sorry, I cannot find a definition for " + line + "."
        
class RandomCocktail(Function):
    '''
    Selects and outputs a random cocktail from store/cocktail_list.xml
    '''
    #Name for use in help listing
    mHelpName = "random cocktail"
    #Names which can be used to address the function
    mNames = set(["random cocktail","randomcocktail"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Delivers ingredients and recipes for a random cocktail. Format: random cocktail"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Load XML
        doc = minidom.parse("store/cocktail_list.xml")
        cocktailListXml = doc.getElementsByTagName("cocktail_list")[0]
        randomCocktailXml = random.choice(cocktailListXml.getElementsByTagName("cocktail"))
        randomCocktailName = randomCocktailXml.getElementsByTagName("name")[0].firstChild.data
        randomCocktailInstructions = randomCocktailXml.getElementsByTagName("instructions")[0].firstChild.data
        outputString = "Randomly selected cocktail is: " + randomCocktailName + ". The ingredients are: "
        ingredientList = []
        for ingredientXml in randomCocktailXml.getElementsByTagName("ingredients"):
            ingredientAmount = ingredientXml.getElementsByTagName("amount")[0].firstChild.data
            ingredientName = ingredientXml.getElementsByTagName("name")[0].firstChild.data
            ingredientList.append(ingredientAmount + ingredientName)
        outputString += ", ".join(ingredientList) + ". The recipe is: " + randomCocktailInstructions
        if(outputString[-1]!='.'):
            outputString += "."
        return outputString

class Cocktail(Function):
    '''
    Cocktail lookup function.
    '''
    #Name for use in help listing
    mHelpName = "cocktail"
    #Names which can be used to address the function
    mNames = set(["cocktail"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns ingredients and instructions for a given cocktail (or closest guess). Format: cocktail <name>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        'Returns ingredients and instructions for a given cocktail (or closest guess). Format: cocktail <name>'
        doc = minidom.parse("store/cocktail_list.xml")
        cocktailListXml = doc.getElementsByTagName("cocktail_list")[0]
        cocktailNames = []
        #Loop through cocktails, adding names to list
        for cocktailXml in cocktailListXml.getElementsByTagName("cocktail"):
            cocktailName = cocktailXml.getElementsByTagName("name")[0].firstChild.data
            cocktailNames.append(cocktailName)
        #Find the closest matching names
        closestMatches = difflib.get_close_matches(line.lower(),cocktailNames)
        #If there are no close matches, return error
        if(len(closestMatches)==0 or closestMatches[0]==''):
            return "I haven't got anything close to that name."
        #Get closest match XML
        closestMatchName = closestMatches[0]
        for cocktailXml in cocktailListXml.getElementsByTagName("cocktail"):
            cocktailName = cocktailXml.getElementsByTagName("name")[0].firstChild.data
            if(cocktailName.lower()==closestMatchName.lower()):
                break
        #Get instructions
        cocktailInstructions = cocktailXml.getElementsByTagName("instructions")[0].firstChild.data
        #Get list of ingredients
        ingredientList = []
        for ingredientXml in cocktailXml.getElementsByTagName("ingredients"):
            ingredientAmount = ingredientXml.getElementsByTagName("amount")[0].firstChild.data
            ingredientName = ingredientXml.getElementsByTagName("name")[0].firstChild.data
            ingredientList.append(ingredientAmount + ingredientName)
        #Construct output
        outputString = "Closest I have is " + closestMatchName + "."
        outputString += "The ingredients are: " + ", ".join(ingredientList) + "."
        outputString += "The recipe is: " + cocktailInstructions
        if(outputString[-1]!="."):
            outputString += "."
        return outputString
        
class InSpace(Function):
    '''
    Looks up the current amount and names of people in space
    '''
    #Name for use in help listing
    mHelpName = "in space"
    #Names which can be used to address the function
    mNames = set(["in space","inspace","space"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the number of people in space right now, and their names. Format: in space"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        spaceDict = Commons.loadUrlJson("http://www.howmanypeopleareinspacerightnow.com/space.json")
        spaceNumber = str(spaceDict['number'])
        spaceNames = ", ".join(person['name'] for person in spaceDict['people'])
        outputString = "There are " + spaceNumber + " people in space right now. "
        outputString += "Their names are: " + spaceNames + "."

    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set(Function.EVENT_MESSAGE)
    
    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        cleanFullLine = fullLine.lower()
        if("in space" in cleanFullLine and ("who" in cleanFullLine or "how many" in cleanFullLine)):
            return self.run(cleanFullLine,userObject,channelObject)

class TimestampToDate(Function):
    '''
    Converts an unix timestamp to a date
    '''
    #Name for use in help listing
    mHelpName = "date"
    #Names which can be used to address the function
    mNames = set(["timestamp to date","unix timestamp","unix","unix timestamp to date"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the date from a given unix timestamp. Format: date <timestamp>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        try:
            line = int(line)
        except:
            return "Invalid timestamp"
        return Commons.formatUnixTime(line) + "."

class Wiki(Function):
    '''
    Lookup wiki article and return the first paragraph or so.
    '''
    #Name for use in help listing
    mHelpName = "wiki"
    #Names which can be used to address the function
    mNames = set(["wiki","wikipedia"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Reads the first paragraph from a wikipedia article"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().replace(" ","_")
        url = 'http://en.wikipedia.org/w/api.php?format=json&action=query&titles='+lineClean+'&prop=revisions&rvprop=content&redirects=True'
        articleDict = Commons.loadUrlJson(url)
        pageCode = list(articleDict['query']['pages'])[0]
        articleText = articleDict['query']['pages'][pageCode]['revisions'][0]['*']
        oldScan = articleText
        newScan = re.sub('{{[^{^}]*}}','',oldScan)
        while(newScan!=oldScan):
            oldScan = newScan
            newScan = re.sub('{{[^{^}]*}}','',oldScan)
        plainText = newScan.replace('\'\'','')
        plainText = re.sub(r'<ref[^<]*</ref>','',plainText)
        plainText = re.sub(r'\[\[([^]]*)]]',r'\1',plainText)
        plainText = re.sub(r'\[\[[^]^|]*\|([^]]*)]]',r'\1',plainText)
        plainText = re.sub(r'<!--[^>]*-->','',plainText)
        plainText = re.sub(r'<ref[^>]*/>','',plainText)
        firstParagraph = plainText.strip().split('\n')[0]
        return firstParagraph
    
class Translate(Function):
    '''
    Uses google translate to translate a phrase to english, or to any specified language
    '''
    #Name for use in help listing
    mHelpName = "translate"
    #Names which can be used to address the function
    mNames = set(["translate"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Translates a given block of text. Format: translate <from>-><to> <text>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        if(len(line.split())<=1):
            langChange = ''
            transString = line
        else:
            langChange = line.split()[0]
            transString = ' '.join(line.split()[1:])
        if('->' not in langChange):
            langFrom = "auto"
            langTo = "en"
            transString = langChange+' '+transString
        else:
            langFrom = langChange.split('->')[0]
            langTo = langChange.split('->')[1]
        transSafe = urllib.parse.quote(transString.strip(),'')
        url = "http://translate.google.com/translate_a/t?client=t&text="+transSafe+"&hl=en&sl="+langFrom+"&tl="+langTo+"&ie=UTF-8&oe=UTF-8&multires=1&otf=1&pc=1&trs=1&ssel=3&tsel=6&sc=1"
        transDict = Commons.loadUrlJson(url,[],True)
        translationString = " ".join([x[0] for x in transDict[0]])
        return "Translation: "+translationString
    
class Weather(Function):
    '''
    Currently returns a random weather phrase. In future perhaps nightvale weather?
    '''
    #Name for use in help listing
    mHelpName = "weather"
    #Names which can be used to address the function
    mNames = set(["weather","random weather"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Random weather"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        weather = ['Rain.'] * 10 + ['Heavy rain.'] * 3 + ['Cloudy.'] * 20 + ['Windy.'] * 5 + ['Sunny.']
        return random.choice(weather)
        
class UrlDetect(Function):
    '''
    URL detection and title printing.
    '''
    #Name for use in help listing
    mHelpName = "urldetect"
    #Names which can be used to address the function
    mNames = set(["urldetect"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "URL detection."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        return "This function does not take input."

    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set(Function.EVENT_MESSAGE)

    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        #Search for a link
        urlRegex = re.compile(r'\b((https?://|www.)[-A-Z0-9+&?%@#/=~_|$:,.]*[A-Z0-9+\&@#/%=~_|$])',re.I)
        urlSearch = urlRegex.search(fullLine)
        if(not urlSearch):
            return None
        #Get link address
        urlAddress = urlSearch.group(1)
        #Add protocol if missing
        if("://" not in urlAddress):
            urlAddress = "http://" + urlAddress
        #Ignore local links.
        if('127.0.0.1' in urlAddress or '192.168.' in urlAddress or '10.' in urlAddress or '172.' in urlAddress):
            return None
        #Get page info
        pageRequest = urllib.request.Request(urlAddress)
        pageRequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
        pageOpener = urllib.request.build_opener()
        pageInfo = str(pageOpener.open(pageRequest).info())
        if("Content-Type:" in pageInfo):
            pageType = pageInfo.split()[pageInfo.split().index('Content-Type:')+1]
        else:
            pageType = ''
        #Get the website name
        urlSite = Commons.getDomainName(urlAddress).lower()
        #Get response if link is an image
        if("image" in pageType):
            return self.urlImage(urlAddress,pageOpener,pageRequest,pageType)
        #Get a response depending on the website
        if(urlSite=="amazon"):
            return self.siteAmazon(urlAddress,pageOpener,pageRequest)
        if(urlSite=="e621"):
            return self.siteE621(urlAddress,pageOpener,pageRequest)
        if(urlSite=="ebay"):
            return self.siteEbay(urlAddress,pageOpener,pageRequest)
        if(urlSite=="f-list"):
            return self.siteFList(urlAddress,pageOpener,pageRequest)
        if(urlSite=="furaffinity" or urlSite=="facdn"):
            return self.siteFuraffinity(urlAddress,pageOpener,pageRequest)
        if(urlSite=="imdb"):
            return self.siteImdb(urlAddress,pageOpener,pageRequest)
        if(urlSite=="imgur"):
            return self.siteImgur(urlAddress,pageOpener,pageRequest)
        if(urlSite=="speedtest"):
            return self.siteSpeedtest(urlAddress,pageOpener,pageRequest)
        if(urlSite=="reddit" or urlSite=="redd"):
            return self.siteReddit(urlAddress,pageOpener,pageRequest)
        if(urlSite=="wikipedia"):
            return self.siteWikipedia(urlAddress,pageOpener,pageRequest)
        if(urlSite=="youtube" or urlSite=="youtu"):
            return self.siteYoutube(urlAddress,pageOpener,pageRequest)
        #If other url, return generic URL response
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def urlImage(self,urlAddress,pageOpener,pageRequest,pageType):
        'Handling direct image links'
        #Get the website name
        urlSite = Commons.getDomainName(urlAddress).lower()
        #If website name is speedtest or imgur, hand over to those handlers
        if(urlSite=="speedtest"):
            return self.siteSpeedtest(urlAddress,pageOpener,pageType)
        if(urlSite=="imgur"):
            return self.siteImgur(urlAddress,pageOpener,pageType)
        #Image handling
        imageData = pageOpener.open(pageRequest).read()
        imageWidth, imageHeight = self.getImageSize(imageData)
        imageSize = len(imageData)
        imageSizeStr = self.fileSizeToString(imageSize)
        return "Image: " + pageType + " (" + str(imageWidth) + "px by " + str(imageHeight) + "px) " + imageSizeStr + "."

    def urlGeneric(self,urlAddress,pageOpener,pageRequest):
        'Handling for generic links not caught by any other url handling function.'
        pageCode = pageOpener.open(pageRequest).read(4096).decode('utf-8','ignore')
        if(pageCode.count('</title>')==0):
            return None
        titleSearch = re.search('<title[^>]*>([^<]*)</title>',pageCode,re.I)
        if(titleSearch is None):
            return None
        titleText = titleSearch.group(2)
        htmlParser = html.parser.HTMLParser()
        titleClean = htmlParser.unescape(titleText).replace("\n","").strip()
        if(titleClean!=""):
            return "URL title: " + titleClean.replace("\n","")
        return None

    def siteAmazon(self,urlAddress,pageOpener,pageRequest):
        'Handling for amazon links'
        #I spent ages trying to figure out the amazon API, and I gave up.
        #TODO: write amazon link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteE621(self,urlAddress,pageOpener,pageRequest):
        'Handling for e621 links'
        #TODO: write e621 link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteEbay(self,urlAddress,pageOpener,pageRequest):
        'Handling for ebay links'
        #Get the ebay item id
        itemId = urlAddress.split("/")[-1]
        apiKey = "JoshuaCo-cc2e-4309-b962-df71218f4407"
        #Get API response
        apiUrl = "http://open.api.ebay.com/shopping?callname=GetSingleItem&responseencoding=JSON&appid="+apiKey+"&siteid=0&version=515&ItemID="+itemId+"&IncludeSelector=Details"
        apiDict = Commons.loadUrlJson(apiUrl)
        #Get item data from api response
        itemTitle = apiDict["Item"]["Title"]
        itemPrice = str(apiDict["Item"]["CurrentPrice"]["Value"])+" "+apiDict["Item"]["CurrentPrice"]["CurrencyID"]
        itemEndTime = apiDict["Item"]["EndTime"][:19].replace("T"," ")
        #Start building output
        output = "eBay> Title: " + itemTitle + " | "
        output += "Price: " + itemPrice + " | "
        #Check listing type
        if(apiDict["Item"]["ListingType"]=="Chinese"):
            #Listing type: bidding
            itemBidCount = str(apiDict["Item"]["BidCount"])
            if(itemBidCount=="1"):
                output += "Auction, " + str(itemBidCount) + " bid"
            else:
                output += "Auction, " + str(itemBidCount) + " bids"
        elif(apiDict["Item"]["ListingType"]=="FixedPriceItem"):
            #Listing type: buy it now
            output += "Buy it now | "
        output += "Ends: " + itemEndTime
        return output

    def siteFList(self,urlAddress,pageOpener,pageRequest):
        'Handling for f-list links'
        #TODO: write f-list link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteFuraffinity(self,urlAddress,pageOpener,pageRequest):
        'Handling for furaffinity links'
        #TODO: write furaffinity link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteImdb(self,urlAddress,pageOpener,pageRequest):
        'Handling for imdb links'
        #If URL isn't to an imdb title, just do normal url handling.
        if('imdb.com/title' not in urlAddress):
            return self.siteGeneric(urlAddress,pageOpener,pageRequest)
        #Get the imdb movie ID
        movieIdSearch = re.search('title/(tt[0-9]*)',urlAddress)
        if(movieIdSearch is None):
            return self.siteGeneric(urlAddress,pageOpener,pageRequest)
        movieId = movieIdSearch.group(1)
        #Download API response
        apiUrl = 'http://www.omdbapi.com/?i=' + movieId
        apiDict = Commons.loadUrlJson(apiUrl)
        #Get movie information from API response
        movieTitle = apiDict['Title']
        movieYear = apiDict['Year']
        movieGenre = apiDict['Genre']
        movieRating = apiDict['imdbRating']
        movieVotes = apiDict['imdbVotes']
        #Construct output
        output = "IMDB> Title: " +movieTitle + " (" + movieYear + ") | "
        output += "Rating "+movieRating+"/10, "+movieVotes+" votes. | "
        output += "Genres: " + movieGenre  + "."
        return output

    def siteImgur(self,urlAddress,pageOpener,pageRequest):
        'Handling imgur links'
        #Hand off imgur album links to a different handler function.
        if("/a/" in urlAddress):
            return self.siteImgurAlbum(urlAddress,pageOpener,pageRequest)
        #Handle individual imgur image links
        #Example imgur links: http://i.imgur.com/2XBqIIT.jpg http://imgur.com/2XBqIIT
        imgurId = urlAddress.split('/')[-1].split('.')[0]
        apiUrl = 'https://api.imgur.com/3/image/' + imgurId
        #Load API response (in json) using Client-ID.
        apiDict = Commons.loadUrlJson(apiUrl,[['Authorization','Client-ID 3afbdcb1353b72f']])
        #Get title, width, height, size, and view count from API data
        imageTitle = str(apiDict['data']['title'])
        imageWidth = str(apiDict['data']['width'])
        imageHeight = str(apiDict['data']['height'])
        imageSize = int(apiDict['data']['size'])
        imageSizeString = self.fileSizeToString(imageSize)
        imageViews = apiDict['data']['views']
        #Create output and return
        output = "Imgur> Title: " + imageTitle + " | "
        output += "Size: " + imageWidth + "x" + imageHeight + " | "
        output += "Filesize: " + imageSizeString + " | "
        output += "Views: " + "{:,}".format(imageViews) + "."
        return output

    def siteImgurAlbum(self,urlAddress,pageOpener,pageRequest):
        'Handling imgur albums'
        #http://imgur.com/a/qJctj#0 example imgur album
        imgurId = urlAddress.split('/')[-1].split('#')[0]
        apiUrl = 'https://api.imgur.com/3/album/' + imgurId
        #Load API response (in json) using Client-ID.
        apiDict = Commons.loadUrlJson(apiUrl,[['Authorization','Client-ID 3afbdcb1353b72f']])
        #Get album title and view count from API data
        albumTitle = apiDict['data']['title']
        albumViews = apiDict['data']['views']
        #Start on output
        output = "Imgur album> "
        output += "Album title: " + albumTitle + " | " 
        output += "Gallery views: " + "{:,}".format(albumViews) + " | "
        if('section' in apiDict['data']):
            albumSection = apiDict['data']['section']
            output += "Section: " + albumSection + " | "
        albumCount = apiDict['data']['images_count']
        #If an image was specified, show some information about that specific image
        if("#" in urlAddress):
            imageNumber = int(urlAddress.split('#')[-1])
            imageWidth = apiDict['data']['images'][imageNumber]['width']
            imageHeight = apiDict['data']['images'][imageNumber]['height']
            imageSize = int(apiDict['data']['images'][imageNumber]['size'])
            imageSizeString = self.fileSizeToString(imageSize)
            output += "Image " + str(imageNumber+1) + " of " + str(albumCount) + " | "
            output += "Current image: " + str(imageWidth) + "x" + str(imageHeight) + ", " + imageSizeString + "."
            return output
        output += str(albumCount) + "images."
        return output
    
    def sitePastebin(self,urlAddress,pageOpener,pageRequest):
        'Handling pastebin links'
        #TODO: write pastebin link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)
    
    def siteReddit(self,urlAddress,pageOpener,pageRequest):
        'Handling reddit links'
        #TODO: write reddit link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteSpeedtest(self,urlAddress,pageOpener,pageRequest):
        'Handling speedtest links'
        if(urlAddress[-4:]=='.png'):
            urlNumber = urlAddress[32:-4]
            urlAddress = 'http://www.speedtest.net/my-result/' + urlNumber
            pageRequest = urllib.request.Request(urlAddress)
            pageRequest.add_header('User-Agent','Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0')
            pageOpener = urllib.request.build_opener()
        pageCode = pageOpener.open(pageRequest).read().decode('utf-8')
        pageCode = re.sub(r'\s+','',pageCode)
        download = re.search('<h3>Download</h3><p>([0-9\.]*)',pageCode).group(1)
        upload = re.search('<h3>Upload</h3><p>([0-9\.]*)',pageCode).group(1)
        ping = re.search('<h3>Ping</h3><p>([0-9]*)',pageCode).group(1)
        return "Speedtest> Download: " + download + "Mb/s | Upload: " + upload + "Mb/s | Ping: " + ping + "ms"

    def siteWikipedia(self,urlAddress,pageOpener,pageRequest):
        'Handling for wikipedia links'
        #TODO: write wikipedia link handler
        return self.urlGeneric(urlAddress,pageOpener,pageRequest)

    def siteYoutube(self,urlAddress,pageOpener,pageRequest):
        'Handling for youtube links'
        #Find video id
        if("youtu.be" in urlAddress):
            videoId = urlAddress.split("/")[-1].split("?")[0]
        else:
            videoId = urlAddress.split("/")[-1].split("=")[1].split("&")[0]
        #Find API url
        apiKey = "AIzaSyDdpbzJ2mMTb2mKDBHADnXf4C18Lwc45A4"
        apiUrl = "https://www.googleapis.com/youtube/v3/videos?id="+videoId+"&part=snippet,contentDetails,statistics&key="+apiKey
        #Load API response (in json).
        apiDict = Commons.loadUrlJson(apiUrl)
        #Get video data from API response.
        videoTitle = apiDict['items'][0]['snippet']['title']
        videoDuration = apiDict['items'][0]['contentDetails']['duration'][2:].lower()
        videoViews = apiDict['items'][0]['contentDetails']['views']
        #Create output
        output = "Youtube video> Title: " + videoTitle + " | "
        output += "Length: " + videoDuration + " | "
        output += "Views: " + videoViews + "."
        return output





    def getImageSize(self,imageData):
        '''Determine the image type of fhandle and return its size.
        from draco'''
        #This function is from here: http://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
        imageHead = imageData[:24]
        if len(imageHead) != 24:
            return
        if imghdr.what(None,imageData) == 'png':
            check = struct.unpack('>i', imageHead[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', imageHead[16:24])
        elif imghdr.what(None,imageData) == 'gif':
            width, height = struct.unpack('<HH', imageHead[6:10])
        elif imghdr.what(None,imageData) == 'jpeg':
            try:
                byteOffset = 0
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    byteOffset += size
                    byte = imageData[byteOffset]
                    byteOffset += 1
                    while ord(byte) == 0xff:
                        byte = imageData[byteOffset]
                        byteOffset += 1
                    ftype = ord(byte)
                    size = struct.unpack('>H', imageData[byteOffset:byteOffset+2])[0] - 2
                    byteOffset += 2
                # We are at a SOFn block
                byteOffset += 1  # Skip `precision' byte.
                height, width = struct.unpack('>HH', imageData[byteOffset:byteOffset+4])
                byteOffset += 4
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height

    def fileSizeToString(self,size):
        if(size<2048):
            sizeString = str(size) + "Bytes"
        elif(size<(2048*1024)):
            sizeString = str(math.floor(float(size)/10.24)/100) + "KiB"
        elif(size<(2048*1024*1024)):
            sizeString = str(math.floor(float(size)/(1024*10.24))/100) + "MiB"
        else:
            sizeString = str(math.floor(float(size)/(1024*1024*10.24))/100) + "GiB"
        return sizeString
