import time
import datetime

class Commons(object):
    '''
    Class of commons methods, useful anywhere, but all static.
    '''
    mEndLine = '\r\n'

    @staticmethod
    def currentTimestamp():
        '''
        Constructor
        '''
        return "[{:02d}:{:02d}:{:02d}]".format(*time.gmtime()[3:6])

    @staticmethod    
    def chunkString(string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))
    
    @staticmethod
    def chunkStringDot(string,length):
        if(len(string)<length):
            return [string]
        else:
            listOfStrings = [string[:length-3]+'...']
            restOfString = string[length-3:]
            while(restOfString>length-3):
                listOfStrings += ['...'+restOfString[:length-6]+'...']
                restOfString = restOfString[length-6:]
            listOfStrings += ['...'+restOfString]
            return listOfStrings
    
    @staticmethod
    def readFiletoList(filename):
        f = open(filename,"r")
        fileList = []
        rawLine = f.readline()
        while rawLine != '':
            fileList.append(rawLine.replace("\n",''))
            rawLine = f.readline()
        return fileList
    
    @staticmethod
    def getDomainName(url):
        'Gets the domain name of a URL, removing the TLD'
        #Sanitise the URL, removing protocol and directories
        url = url.split("://")[-1]
        url = url.split("/")[0]
        url = url.split(":")[0]
        #Get the list of TLDs, from mozilla's publicsuffix.org
        tldList = [x.strip() for x in open("store/tld_list.txt","rb").read().decode("utf-8").split("\n")]
        urlSplit = url.split(".")
        urlTld = None
        for tldTest in ['.'.join(urlSplit[x:]) for x in range(len(urlSplit))]:
            if(tldTest in tldList):
                urlTld = tldTest
                break
        #If you didn't find the TLD, just return the longest bit.
        if(urlTld is None):
            return urlSplit.sort(key=len)[-1]
        #Else return the last part before the TLD
        return url[:-len(urlTld)-1].split('.')[-1]
    
    @staticmethod
    def stringToBool(string):
        'Converts a string to a boolean.'
        string = string.lower()
        if(string in [1,'1','true','t','yes','y']):
            return True
        if(string in [0,'0','false','f','no','n']):
            return False
        return None
    
    @staticmethod
    def ordinal(number):
        'Returns the ordinal of a number'
        if(number%10==1 and number%100!=11):
            return str(number) + "st"
        elif(number%10==2 and number%100!=12):
            return str(number) + "nd"
        elif(number%10==3 and number%100!=13):
            return str(number) + "rd"
        else:
            return str(number) + "th"
    
    @staticmethod
    def formatUnixTime(timeStamp):
        'Returns a string, formatted datetime from a timestamp'
        return str(datetime.datetime.utcfromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S'))
        