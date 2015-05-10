from xml.dom import minidom

class ConvertRepo:
    '''
    Configuration repository. Stores list of ConvertTypes, ConvertPrefixGroups, etc
    '''
    mTypeList = []

    def __init__(self):
        '''
        Constructor
        '''
        raise NotImplementedError
    
    def getTypeList(self):
        'Returns the full list of ConvertType objects'
        raise NotImplementedError

    def findTypes(self,name1,name2):
        'Finds out what types are valid for a pair of names.'
        raise NotImplementedError
    
    @staticmethod
    def loadFromXml(self):
        'Loads Convert Repo from XML.'
        raise NotImplementedError
    
    def saveToXml(self):
        'Saves Convert Repo to XML.'
        raise NotImplementedError
    
class ConvertType:
    '''
    Conversion unit type object.
    '''
    mName = None
    mUnitList = []
    
    def __init__(self,name):
        raise NotImplementedError
    
    def getUnitList(self):
        'Returns the full list of ConvertUnit objects'
        raise NotImplementedError
    
    def getUnitByName(self,name):
        'Get a unit by a specified name'
        raise NotImplementedError

    @staticmethod
    def fromXml(xmlString):
        'Loads a new ConvertType object from XML'
        raise NotImplementedError
    
    def toXml(self):
        'Writes ConvertType object as XML'
        raise NotImplementedError

class ConvertUnit:
    '''
    Conversion unit object.
    '''
    mNames = []
    mValue = None
    mType = None
    mOffset = None
    mLastUpdated = None
    
    def __init__(self,convertType,names,value):
        raise NotImplementedError
    
    def getNames(self):
        'Returns the full list of names for a unit.'
        raise NotImplementedError
    
    def removeName(self,name):
        'Removes a name from the list of names for a unit.'
        raise NotImplementedError
    
    def addName(self,name):
        'Adds a name to the list of names for a unit.'
        raise NotImplementedError
    
    def getValue(self):
        'Returns the value of the unit.'
        raise NotImplementedError
    
    def setValue(self,value):
        'Changes the value of the unit.'
        raise NotImplementedError
    
    def getType(self):
        'Returns the ConvertType which "owns" this ConvertUnit.'
        raise NotImplementedError
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new ConvertUnit object from XML.'
        raise NotImplementedError
    
    def toXml(self):
        'Outputs a ConvertUnit object as XML.'
        raise NotImplementedError
    
class ConvertMeasure:
    '''
    Convert meaure object. An amount with a unit.
    '''
    mAmount = None
    mUnit = None
    
    def __init__(self,amount,unit):
        raise NotImplementedError
    
    def getUnit(self):
        'Returns the unit of the measure.'
        raise NotImplementedError
    
    def getAmount(self):
        'Returns the amount of the measure.'
        raise NotImplementedError
    
    def convertTo(self,unit):
        'Creates a new measure, equal in value but with a different unit.'
        raise NotImplementedError

class ConvertPrefix:
    '''
    Conversion prefix.
    '''
    mPrefix = None
    mMultiplier = None
    
    def __init__(self,prefix,multiplier):
        raise NotImplementedError
    
    def getPrefix(self):
        raise NotImplementedError
    
    def getMultiplier(self):
        raise NotImplementedError
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new ConvertUnit object from XML.'
        doc = minidom.parse(xmlString)
        newName = doc.getElementsByTagName("name")[0].firstChild.data
        newValue = doc.getElementsByTagName("value")[0].firstChild.data
        newPrefix = ConvertPrefix(newName,newValue)
        return newPrefix
    
    def toXml(self):
        'Outputs a ConvertUnit object as XML.'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("prefix")
        doc.appendChild(root)
        #Add name
        nameElement = doc.createElement("name")
        nameElement.appendChild(doc.createTextNode(self.mPrefix))
        root.appendChild(nameElement)
        #Add multiplier
        valueElement = doc.createElement("value")
        valueElement.appendChild(doc.createTextNode(str(self.mMultiplier)))
        root.appendChild(valueElement)
        return doc.toxml()
    
class ConvertPrefixGroup:
    '''
    Group of Conversion Prefixes.
    '''
    mName = None
    mPrefixList = []
    
    def __init__(self,name):
        raise NotImplementedError
    
    def getName(self):
        return self.mName
    
    def getPrefixList(self):
        return self.mPrefixList
    
    def getPrefixByName(self):
        raise NotImplementedError
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new ConvertUnit object from XML.'
        raise NotImplementedError
    
    def toXml(self):
        'Outputs a ConvertUnit object as XML.'
        raise NotImplementedError









