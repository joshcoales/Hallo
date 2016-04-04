import time

from xml.dom import minidom
from PermissionMask import PermissionMask
from inc.commons import Commons
from abc import ABCMeta


class Destination(metaclass=ABCMeta):
    """
    Interface for Channel and User. It just means messages can be sent to these entities.
    """
    mType = None  # The type of destination, "channel" or "user"
    mServer = None  # The server object this destination belongs to
    mName = None  # Destination name, where to send messages
    mLogging = True  # Whether logging is enabled for this destination
    mLastActive = None  # Timestamp of when they were last active
    mUseCapsLock = False  # Whether to use caps lock when communicating to this destination
    mPermissionMask = None  # PermissionMask for the destination object

    def getName(self):
        """Name getter"""
        return self.mName.lower()

    def setName(self, name):
        """
        Name setter
        :param name: Name of the destination
        """
        self.mName = name.lower()

    def getType(self):
        """
        Returns whether the destination is a user or channel.
        """
        return self.mType

    def isChannel(self):
        """Boolean, whether the destination is a channel."""
        if self.mType == "channel":
            return True
        else:
            return False

    def isUser(self):
        """Boolean, whether the destination is a user."""
        if self.mType == "channel":
            return False
        else:
            return True

    def getLogging(self):
        """Boolean, whether the destination is supposed to have logging."""
        return self.mLogging

    def setLogging(self, logging):
        """
        Sets whether the destination is logging.
        :param logging: Boolean, whether or not to log destination content
        """
        self.mLogging = logging

    def getServer(self):
        """Returns the server object that this destination belongs to"""
        return self.mServer

    def updateActivity(self):
        """Updates LastActive timestamp"""
        self.mLastActive = time.time()

    def getLastActive(self):
        """Returns when the destination was last active"""
        return self.mLastActive

    def isUpperCase(self):
        """Returns a boolean representing whether to use caps lock"""
        return self.mUseCapsLock

    def setUpperCase(self, upperCase):
        """
        Sets whether the destination uses caps lock
        :param upperCase: Boolean, whether or not this destination is caps-lock only
        """
        self.mUseCapsLock = upperCase

    def isPersistent(self):
        """
        Defines whether a Destination object is persistent.
        That is to say, whether it needs saving, or can be generated anew.
        """
        raise NotImplementedError

    def getPermissionMask(self):
        return self.mPermissionMask

    def send(self, line, msgType="message"):
        """
        Sends a message to a destination.
        :param line: Line of text to send to destination
        :param msgType: Type of message to send to destination
        """
        serverObj = self.getServer()
        serverObj.send(line, self, msgType)

    def toXml(self):
        """Returns the Destination object XML"""
        raise NotImplementedError

    @staticmethod
    def fromXml(xmlString, server):
        """
        Loads a new Destination object from XML
        :param xmlString: XML string to parse to create destination
        :param server: Server on which the destination is located
        """
        raise NotImplementedError


class Channel(Destination):
    mType = "channel"  # This is a channel object
    mPassword = None  # Channel password, or none.
    mUserList = None  # Set of users in the channel
    mInChannel = False  # Whether or not hallo is in the channel
    mPassiveEnabled = True  # Whether to use passive functions in the channel
    mAutoJoin = False  # Whether hallo should automatically join this channel when loading
    mPrefix = None  # Prefix for calling functions. None means inherit from Server. False means use nick.

    def __init__(self, name, server):
        """
        Constructor for channel object
        """
        self.mUserList = set()
        self.mName = name.lower()
        self.mServer = server

    def getPassword(self):
        """Channel password getter"""
        return self.mPassword

    def setPassword(self, password):
        """
        Channel password setter
        :param password: Password of the channel
        """
        self.mPassword = password

    def getPrefix(self):
        """Returns the channel prefix."""
        if self.mPrefix is None:
            return self.mServer.getPrefix()
        return self.mPrefix

    def setPrefix(self, newPrefix):
        """
        Sets the channel function prefix.
        :param newPrefix: New prefix to use to identify calls to hallo in this destination
        """
        self.mPrefix = newPrefix

    def getUserList(self):
        """Returns the full user list of the channel"""
        return self.mUserList

    def addUser(self, user):
        """
        Adds a new user to a given channel
        :param user: User object to add to channel's user list
        """
        self.mUserList.add(user)
        user.addChannel(self)

    def setUserList(self, userList):
        """
        Sets the entire user list of a channel
        :param userList: List of users which are currently in the channel.
        """
        self.mUserList = userList
        for user in userList:
            user.addChannel(self)

    def removeUser(self, user):
        """
        Removes a user from a given channel
        :param user: User to remove from channel's user list
        """
        try:
            self.mUserList.remove(user)
            user.removeChannel(self)
        except KeyError:
            pass

    def isUserInChannel(self, user):
        """
        Returns a boolean as to whether the user is in this channel
        :param user: User being checked
        """
        return user in self.mUserList

    def isPassiveEnabled(self):
        """Whether or not passive functions are enabled in this channel"""
        return self.mPassiveEnabled

    def setPassiveEnabled(self, passiveEnabled):
        """
        Sets whether passive functions are enabled in this channel
        :param passiveEnabled: Boolean, whether functions triggered indirectly are enabled for this channel.
        """
        self.mPassiveEnabled = passiveEnabled

    def isAutoJoin(self):
        """Whether or not hallo should automatically join this channel"""
        return self.mAutoJoin

    def setAutoJoin(self, autoJoin):
        """
        Sets whether hallo automatically joins this channel
        :param autoJoin: Boolean, whether or not to join this channel when the server connects.
        """
        self.mAutoJoin = autoJoin

    def isInChannel(self):
        """Whether or not hallo is in this channel"""
        return self.mInChannel

    def setInChannel(self, inChannel):
        """
        Sets whether hallo is in this channel
        :param inChannel: Boolean, whether hallo is in this channel.
        """
        self.mInChannel = inChannel
        if inChannel is False:
            self.mUserList = set()

    def rightsCheck(self, rightName):
        """
        Checks the value of the right with the specified name. Returns boolean
        :param rightName: Name of the user right to check
        """
        if self.mPermissionMask is not None:
            rightValue = self.mPermissionMask.get_right(rightName)
            # If PermissionMask contains that right, return it.
            if rightValue in [True, False]:
                return rightValue
        # Fallback to the parent Server's decision.
        return self.mServer.rights_check(rightName)

    def isPersistent(self):
        """Defines whether Channel is persistent. That is to say, whether it needs saving, or can be generated anew."""
        # If you need to rejoin this channel, then you need to save it
        if self.mAutoJoin is True:
            return True
        # If channel has a password, you need to save it
        if self.mPassword is not None:
            return True
        # If channel has logging disabled, save it
        if self.mLogging is False:
            return True
        # If channel has caps lock, save it
        if self.mUseCapsLock is True:
            return True
        # If channel has specific permissions set, save it
        if not self.mPermissionMask.is_empty():
            return True
        # If channel has passive functions disabled, save it
        if self.mPassiveEnabled is False:
            return True
        # Otherwise it can be generated anew to be identical.
        return False

    def toXml(self):
        """Returns the Channel object XML"""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("channel")
        doc.appendChild(root)
        # create name element
        nameElement = doc.createElement("channel_name")
        nameElement.appendChild(doc.createTextNode(self.mName))
        root.appendChild(nameElement)
        # create logging element
        loggingElement = doc.createElement("logging")
        loggingElement.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.mLogging]))
        root.appendChild(loggingElement)
        # create caps_lock element, to say whether to use caps lock
        capsLockElement = doc.createElement("caps_lock")
        capsLockElement.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.mUseCapsLock]))
        root.appendChild(capsLockElement)
        # create password element
        if self.mPassword is not None:
            passwordElement = doc.createElement("password")
            passwordElement.appendChild(doc.createTextNode(self.mPassword))
            root.appendChild(passwordElement)
        # create passive_enabled element, saying whether passive functions are enabled
        passiveEnabledElement = doc.createElement("passive_enabled")
        passiveEnabledElement.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.mPassiveEnabled]))
        root.appendChild(passiveEnabledElement)
        # create auto_join element, whether or not to automatically join a channel
        autoJoinElement = doc.createElement("auto_join")
        autoJoinElement.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.mAutoJoin]))
        root.appendChild(autoJoinElement)
        # create permission_mask element
        if not self.mPermissionMask.is_empty():
            permissionMaskElement = minidom.parseString(self.mPermissionMask.to_xml()).firstChild
            root.appendChild(permissionMaskElement)
        # output XML string
        return doc.toxml()

    @staticmethod
    def fromXml(xmlString, server):
        """
        Loads a new Channel object from XML
        :param xmlString: XML string representation of the channel
        :param server: Server the channel is on
        """
        doc = minidom.parseString(xmlString)
        newName = doc.getElementsByTagName("channel_name")[0].firstChild.data
        newChannel = Channel(newName, server)
        newChannel.mLogging = Commons.stringFromFile(doc.getElementsByTagName("logging")[0].firstChild.data)
        newChannel.mUseCapsLock = Commons.stringFromFile(doc.getElementsByTagName("caps_lock")[0].firstChild.data)
        if len(doc.getElementsByTagName("password")) != 0:
            newChannel.mPassword = doc.getElementsByTagName("password")[0].firstChild.data
        newChannel.mPassiveEnabled = Commons.stringFromFile(
            doc.getElementsByTagName("passive_enabled")[0].firstChild.data)
        newChannel.mAutoJoin = Commons.stringFromFile(doc.getElementsByTagName("auto_join")[0].firstChild.data)
        if len(doc.getElementsByTagName("permission_mask")) != 0:
            newChannel.mPermissionMask = PermissionMask.from_xml(doc.getElementsByTagName("permission_mask")[0].toxml())
        return newChannel


class User(Destination):
    mType = "user"  # This is a user object
    mIdentified = False  # Whether the user is identified (with nickserv)
    mChannelList = None  # Set of channels this user is in
    mOnline = False  # Whether or not the user is online
    mUserGroupList = None  # List of UserGroups this User is a member of

    def __init__(self, name, server):
        """
        Constructor for user object
        """
        self.mChannelList = set()
        self.mUserGroupList = {}
        self.mName = name.lower()
        self.mServer = server

    def isIdentified(self):
        """Checks whether this user is identified"""
        if not self.mIdentified:
            self.checkIdentity()
        return self.mIdentified

    def setIdentified(self, identified):
        """
        Sets whether this user is identified
        :param identified: Boolean, whether this user is identified
        """
        self.mIdentified = identified

    def checkIdentity(self):
        """Checks with the server whether this user is identified."""
        identityResult = self.mServer.checkIdentity(self)
        self.mIdentified = identityResult

    def getChannelList(self):
        """Returns the list of channels this user is in"""
        return self.mChannelList

    def addChannel(self, channel):
        """
        Adds a new channel to a given user
        :param channel: Channel to add to user's channel list
        """
        self.mChannelList.add(channel)

    def removeChannel(self, channel):
        """
        Removes a channel from a given user
        :param channel: Channel to remove from user's channel list
        """
        self.mChannelList.remove(channel)

    def setChannelList(self, channelList):
        """
        Sets the entire channel list of a user
        :param channelList: List of channels the user is in
        """
        self.mChannelList = channelList

    def addUserGroup(self, newUserGroup):
        """
        Adds a User to a UserGroup
        :param newUserGroup: User group to add the user to
        """
        newUserGroupName = newUserGroup.getName()
        self.mUserGroupList[newUserGroupName] = newUserGroup

    def getUserGroupByName(self, userGroupName):
        """
        Returns the UserGroup with the matching name
        :param userGroupName: Returns the user group by the specified name that this user is in
        """
        if userGroupName in self.mUserGroupList:
            return self.mUserGroupList[userGroupName]
        return None

    def getUserGroupList(self):
        """Returns the full list of UserGroups this User is a member of"""
        return self.mUserGroupList

    def removeUserGroupByName(self, userGroupName):
        """
        Removes the UserGroup by the given name from a user
        :param userGroupName: Removes the user group matching this name that the user is in
        """
        del self.mUserGroupList[userGroupName]

    def isOnline(self):
        """Whether the user appears to be online"""
        return self.mOnline

    def setOnline(self, online):
        """
        Sets whether the user is online
        :param online: Boolean, whether the user is online
        """
        self.mOnline = online
        if online is False:
            self.mIdentified = False
            self.mChannelList = set()

    def rightsCheck(self, rightName, channelObject=None):
        """
        Checks the value of the right with the specified name. Returns boolean
        :param rightName: Name of the user right to check
        :param channelObject: Channel in which the right is being checked
        """
        if self.mPermissionMask is not None:
            rightValue = self.mPermissionMask.get_right(rightName)
            # If PermissionMask contains that right, return it.
            if rightValue in [True, False]:
                return rightValue
        # Check UserGroup rights, if any apply
        if len(self.mUserGroupList) != 0:
            return any(
                [userGroup.rights_check(rightName, self, channelObject) for userGroup in self.mUserGroupList.values()])
        # Fall back to channel, if defined
        if channelObject is not None and channelObject.isChannel():
            return channelObject.rights_check(rightName)
        # Fall back to the parent Server's decision.
        return self.mServer.rights_check(rightName)

    def isPersistent(self):
        """Defines whether User is persistent. That is to say, whether it needs saving, or can be generated anew."""
        # If user is in any groups, save it
        if len(self.mUserGroupList) != 0:
            return True
        # If user has logging disabled, save it
        if self.mLogging is False:
            return True
        # If user has caps lock, save it
        if self.mUseCapsLock is True:
            return True
        # If user has specific permissions set, save it
        if not self.mPermissionMask.is_empty():
            return True
        # Otherwise it can be generated anew to be identical.
        return False

    def toXml(self):
        """Returns the User object XML"""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("user")
        doc.appendChild(root)
        # create name element
        nameElement = doc.createElement("user_name")
        nameElement.appendChild(doc.createTextNode(self.mName))
        root.appendChild(nameElement)
        # create logging element
        loggingElement = doc.createElement("logging")
        loggingElement.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.mLogging]))
        root.appendChild(loggingElement)
        # create caps_lock element, to say whether to use caps lock
        capsLockElement = doc.createElement("caps_lock")
        capsLockElement.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.mUseCapsLock]))
        root.appendChild(capsLockElement)
        # create user_group list
        userGroupListElement = doc.createElement("user_group_membership")
        for userGroupName in self.mUserGroupList:
            userGroupElement = doc.createElement("user_group_name")
            userGroupElement.appendChild(doc.createTextNode(userGroupName))
            userGroupListElement.appendChild(userGroupElement)
        root.appendChild(userGroupListElement)
        # create permission_mask element
        if not self.mPermissionMask.is_empty():
            permissionMaskElement = minidom.parseString(self.mPermissionMask.to_xml()).firstChild
            root.appendChild(permissionMaskElement)
        # output XML string
        return doc.toxml()

    @staticmethod
    def fromXml(xmlString, server):
        """
        Loads a new User object from XML
        :param xmlString: XML string representation of the user to create
        :param server: Server which the user is on
        """
        doc = minidom.parseString(xmlString)
        newName = doc.getElementsByTagName("user_name")[0].firstChild.data
        newUser = User(newName, server)
        newUser.mLogging = Commons.stringFromFile(doc.getElementsByTagName("logging")[0].firstChild.data)
        newUser.mUseCapsLock = Commons.stringFromFile(doc.getElementsByTagName("caps_lock")[0].firstChild.data)
        # Load UserGroups from XML
        userGroupListXml = doc.getElementsByTagName("user_group_membership")[0]
        for userGroupXml in userGroupListXml.getElementsByTagName("user_group_name"):
            userGroupName = userGroupXml.firstChild.data
            userGroup = server.getHallo().get_user_group_by_name(userGroupName)
            if userGroup is not None:
                newUser.addUserGroup(userGroup)
        # Add PermissionMask, if one exists
        if len(doc.getElementsByTagName("permission_mask")) != 0:
            newUser.mPermissionMask = PermissionMask.from_xml(doc.getElementsByTagName("permission_mask")[0].toxml())
        return newUser
