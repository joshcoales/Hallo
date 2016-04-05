from Function import Function
from inc.commons import Commons
import datetime


class Printer:
    """
    Printing class. This is created and stored by the Hallo object.
    It exists in order to provide a single entry point to all printing to screen.
    """
    mHallo = None
    mEventDict = None

    def __init__(self, hallo):
        """
        Constructor
        """
        self.mHallo = hallo
        self.mEventDict = {}
        self.mEventDict[Function.EVENT_SECOND] = self.printSecond
        self.mEventDict[Function.EVENT_MINUTE] = self.printMinute
        self.mEventDict[Function.EVENT_HOUR] = self.printHour
        self.mEventDict[Function.EVENT_DAY] = self.printDay
        self.mEventDict[Function.EVENT_PING] = self.printPing
        self.mEventDict[Function.EVENT_MESSAGE] = self.printMessage
        self.mEventDict[Function.EVENT_JOIN] = self.printJoin
        self.mEventDict[Function.EVENT_LEAVE] = self.printLeave
        self.mEventDict[Function.EVENT_QUIT] = self.printQuit
        self.mEventDict[Function.EVENT_CHNAME] = self.printNameChange
        self.mEventDict[Function.EVENT_KICK] = self.printKick
        self.mEventDict[Function.EVENT_INVITE] = self.printInvite
        self.mEventDict[Function.EVENT_NOTICE] = self.printNotice
        self.mEventDict[Function.EVENT_MODE] = self.printModeChange
        self.mEventDict[Function.EVENT_CTCP] = self.printCtcp
    
    def output(self, event, fullLine, serverObject=None, userObject=None, channelObject=None):
        """The function which actually prints the messages."""
        # If channel or server are set to all, set to None for getting output
        if serverObject == Commons.ALL_SERVERS:
            serverObject = None
        if channelObject == Commons.ALL_CHANNELS:
            channelObject = None
        # Check what type of event and pass to that to create line
        if event not in self.mEventDict:
            return None
        printFunction = self.mEventDict[event]
        printLine = printFunction(fullLine, serverObject, userObject, channelObject)
        # Output the log line
        print(printLine)
        return None
    
    def outputFromSelf(self, event, fullLine, serverObject=None, userObject=None, channelObject=None):
        """Prints lines for messages from hallo."""
        # Check what type of event and pass to that to create line
        if event not in self.mEventDict:
            return None
        printFunction = self.mEventDict[event]
        halloUserObject = serverObject.get_user_by_name(serverObject.get_nick())
        printLine = printFunction(fullLine, serverObject, halloUserObject, channelObject)
        # Write the log line
        print(printLine)
        return None
    
    def printSecond(self, fullLine, serverObject, userObject, channelObject):
        return None
    
    def printMinute(self, fullLine, serverObject, userObject, channelObject):
        return None
    
    def printHour(self, fullLine, serverObject, userObject, channelObject):
        return None
    
    def printDay(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.currentTimestamp() + " "
        output += "Day changed: "+datetime.datetime.now().strftime("%Y-%m-%d")
        return output
    
    def printPing(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.currentTimestamp() + " "
        if userObject is None:
            output += "["+serverObject.get_name() + "] PING"
        else:
            output += "["+serverObject.get_name() + "] PONG"
        return output
    
    def printMessage(self, fullLine, serverObject, userObject, channelObject):
        destinationObject = channelObject
        if channelObject is None:
            destinationObject = userObject
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.get_name() + "] "
        output += destinationObject.getName() + " "
        output += "<" + userObject.get_name() + "> " + fullLine
        return output
    
    def printJoin(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.get_name() + "] "
        output += userObject.get_name() + " joined " + channelObject.get_name()
        return output
    
    def printLeave(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.get_name() + "] "
        output += userObject.get_name() + " left " + channelObject.get_name()
        if fullLine.strip() != "":
            output += " (" + fullLine + ")"
        return output
    
    def printQuit(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.get_name() + "] "
        output += userObject.get_name() + " has quit."
        if fullLine.strip() != "":
            output += " (" + fullLine + ")"
        return output
    
    def printNameChange(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.get_name() + "] "
        output += "Nick change: " + fullLine + " -> " + userObject.get_name()
        return output
    
    def printKick(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.get_name() + "] "
        output += userObject.get_name() + " was kicked from " + channelObject.get_name()
        if fullLine.strip() != "":
            output += " (" + fullLine + ")"
        return output
    
    def printInvite(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.get_name() + "] "
        output += "Invite to " + channelObject.get_name() + ' from ' + userObject.get_name()
        return output
    
    def printNotice(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.get_name() + "] "
        output += "Notice from " + userObject.get_name() + ": " + fullLine
        return output
    
    def printModeChange(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.get_name() + "] "
        output += userObject.get_name() + ' set ' + fullLine + ' on ' + channelObject.get_name()
        return output
    
    def printCtcp(self, fullLine, serverObject, userObject, channelObject):
        # Get useful data and objects
        ctcpCommand = fullLine.split()[0]
        ctcpArguments = ' '.join(fullLine.split()[1:])
        destinationObject = channelObject
        if channelObject is None:
            destinationObject = userObject
        # Print CTCP actions differently to other CTCP commands
        if ctcpCommand.lower() == "action":
            output = Commons.currentTimestamp() + " "
            output += "[" + serverObject.get_name() + "] "
            output += destinationObject.getName() + " "
            output += "**" + userObject.get_name() + " " + ctcpArguments + "**"
            return output
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.get_name() + "] "
        output += destinationObject.getName() + " "
        output += "<" + userObject.get_name() + " (CTCP)> " + fullLine
        return output
