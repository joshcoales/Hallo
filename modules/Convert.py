from xml.dom import minidom
from inc.commons import Commons
from Function import Function
import re
import time
from win32com.test.testall import output_checked_programs

class ConvertRepo:
    '''
    Configuration repository. Stores list of ConvertTypes, ConvertPrefixGroups, etc
    '''
    mTypeList = []
    mPrefixGroupList = []

    def __init__(self):
        '''
        Constructor
        '''
        #Nothing needs doing
        pass
    
    def getTypeList(self):
        'Returns the full list of ConvertType objects'
        return self.mTypeList
    
    def addType(self,newType):
        'Adds a new ConvertType object to the type list'
        self.mTypeList.append(newType)
    
    def removeType(self,delType):
        'Removes a ConvertType object from the type list'
        if(delType in self.mTypeList):
            self.mTypeList.remove(delType)
    
    def getTypeByName(self,name):
        'Gets a ConvertType object with the matching name.'
        for typeObject in self.mTypeList:
            if(typeObject.getName()==name):
                return typeObject
        for typeObject in self.mTypeList:
            if(typeObject.getName().lower()==name.lower()):
                return typeObject
        return None
    
    def getFullUnitList(self):
        'Returns the full list of ConvertUnit objects, in every ConvertType object.'
        convertUnitList = []
        for typeObject in self.mTypeList:
            convertUnitList += typeObject.getUnitList()
        return convertUnitList
    
    def getPrefixGroupList(self):
        'Returns the full list of ConvertPrefixGroup objects'
        return self.mPrefixGroupList
    
    def addPrefixGroup(self,prefixGroup):
        'Adds a new ConvertPrefixGroup object to the prefix group list'
        self.mPrefixGroupList.append(prefixGroup)
    
    def removePrefixGroup(self,prefixGroup):
        'Removes a ConvertPrefixGroup object from the prefix group list'
        if(prefixGroup in self.mPrefixGroupList):
            self.mPrefixGroupList.remove(prefixGroup)
    
    def getPrefixGroupByName(self,name):
        'Gets a ConvertPrefixGroup object with the matching name.'
        for prefixGroupObject in self.mPrefixGroupList:
            if(prefixGroupObject.getName().lower()==name.lower()):
                return prefixGroupObject
        return None
    
    @staticmethod
    def loadFromXml():
        'Loads Convert Repo from XML.'
        doc = minidom.parse("store/convert.xml")
        #Create new object
        newRepo = ConvertRepo()
        #Loop through prefix groups
        for prefixGroupXml in doc.getElementsByTagName("prefix_group"):
            prefixGroupObject = ConvertPrefixGroup.fromXml(newRepo,prefixGroupXml.toxml())
            newRepo.addPrefixGroup(prefixGroupObject)
        #Loop through types
        for typeXml in doc.getElementsByTagName("type"):
            typeObject = ConvertType.fromXml(newRepo,typeXml.toxml())
            newRepo.addType(typeObject)
        #Return new repo object
        return newRepo
    
    def saveToXml(self):
        'Saves Convert Repo to XML.'
        #Create document, with DTD
        docimp = minidom.DOMImplementation()
        doctype = docimp.createDocumentType(
            qualifiedName='convert',
            publicId='', 
            systemId='convert.dtd',
        )
        doc = docimp.createDocument(None,'convert',doctype)
        #get root element
        root = doc.getElementsByTagName("convert")[0]
        #Add prefix groups
        for prefixGroupObject in self.mPrefixGroupList:
            prefixGroupElement = minidom.parse(prefixGroupObject.toXml()).firstChild
            root.appendChild(prefixGroupElement)
        #Add types
        for typeObject in self.mTypeList:
            typeElement = minidom.parse(typeObject.toXml()).firstChild
            root.appendChild(typeElement)
        #save XML
        doc.writexml(open("store/convert.xml","w"),addindent="\t",newl="\n")
    
class ConvertType:
    '''
    Conversion unit type object.
    '''
    mRepo = None
    mName = None
    mDecimals = 2
    mBaseUnit = None
    mUnitList = []
    
    def __init__(self,repo,name):
        self.mRepo = repo
        self.mName = name
    
    def getRepo(self):
        'Returns the ConvertRepo which owns this ConvertType object'
        return self.mRepo
    
    def getName(self):
        'Returns the name of the ConvertType object'
        return self.mName
    
    def setName(self,name):
        'Change the name of the ConvertType object'
        self.mName = name
    
    def getDecimals(self):
        'Returns the number of decimals of the ConvertType object'
        return self.mDecimals
    
    def setDecimals(self,decimals):
        'Change the number of decimals of the ConvertType object'
        self.mDecimals = decimals
    
    def getBaseUnit(self):
        'Returns the base unit object of the ConvertType object'
        return self.mBaseUnit
    
    def setBaseUnit(self,baseUnit):
        'Change the base unit object of the ConvertType object'
        self.mBaseUnit = baseUnit
    
    def getUnitList(self):
        'Returns the full list of ConvertUnit objects'
        return self.mUnitList
    
    def addUnit(self,unit):
        'Adds a new ConvertUnit object to unit list'
        self.mUnitList.append(unit)
        
    def removeUnit(self,unit):
        'Removes a ConvertUnit object to unit list'
        if(unit in self.mUnitList):
            self.mUnitList.remove(unit)
    
    def getUnitByName(self,name):
        'Get a unit by a specified name or abbreviation'
        for unitObject in self.mUnitList:
            if(name in unitObject.getNameList()):
                return unitObject
        for unitObject in self.mUnitList:
            if(name.lower() in [unitName.lower() for unitName in unitObject.getNameList()]):
                return unitObject
        for unitObject in self.mUnitList:
            if(name in unitObject.getAbbreviationList()):
                return unitObject
        for unitObject in self.mUnitList:
            if(name.lower() in [unitName.lower() for unitName in unitObject.getAbbreviationList()]):
                return unitObject
        return None

    @staticmethod
    def fromXml(repo,xmlString):
        'Loads a new ConvertType object from XML'
        #Load document
        doc = minidom.parse(xmlString)
        #Get name and create ConvertType object
        newName = doc.getElementsByTagName("name")[0].firstChild.data
        newType = ConvertPrefixGroup(repo,newName)
        #Get number of decimals
        newDecimals = int(doc.getElementsByTagName("decimals")[0].firstChild.data)
        newType.setDecimals(newDecimals)
        #Get base unit
        baseUnitXml = doc.getElementsByTagName("base_unit")[0].getElementsByTagName("unit")[0]
        baseUnitObject = ConvertUnit.fromXml(newType,baseUnitXml.toxml())
        newType.setBaseUnit(baseUnitObject)
        #Loop through unit elements, creating and adding objects.
        for unitXml in doc.getElementsByTagName("unit"):
            unitObject = ConvertUnit.fromXml(self,unitXml.toxml())
            newType.addUnit(unitObject)
        #Return created PrefixGroup
        return newType
    
    def toXml(self):
        'Writes ConvertType object as XML'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("type")
        doc.appendChild(root)
        #Add name element
        nameElement = doc.createElement("name")
        nameElement.appendChild(doc.createTextNode(self.mName))
        root.appendChild(nameElement)
        #Add decimals element
        nameElement = doc.createElement("decimals")
        nameElement.appendChild(doc.createTextNode(str(self.mDecimals)))
        root.appendChild(nameElement)
        #Add base unit element
        baseUnitElement = doc.createElement("base_unit")
        baseUnitUnitElement = minidom.parse(self.mBaseUnit.toXml()).firstChild
        baseUnitElement.appendChild(baseUnitUnitElement)
        root.appendChild(baseUnitElement)
        #Add units
        for unitObject in self.mUnitList:
            unitElement = minidom.parse(unitObject.toXml()).firstChild
            root.appendChild(unitElement)
        #Output XML
        return doc.toxml()

class ConvertUnit:
    '''
    Conversion unit object.
    '''
    mType = None
    mNameList = []
    mAbbreviationList = []
    mValidPrefixGroup = None
    mValue = None
    mOffset = None
    mLastUpdated = None
    
    def __init__(self,convertType,names,value):
        self.mType = convertType
        self.mNameList = names
        self.mValue = value
    
    def getType(self):
        'Returns the ConvertType which "owns" this ConvertUnit.'
        return self.mType
    
    def getNameList(self):
        'Returns the full list of names for a unit.'
        return self.mNameList
    
    def addName(self,name):
        'Adds a name to the list of names for a unit.'
        self.mNameList.append(name)
    
    def removeName(self,name):
        'Removes a name from the list of names for a unit.'
        if(name in self.mNameList):
            self.mNameList.remove(name)
    
    def getAbbreviationList(self):
        'Returns the full list of abbreviations for a unit.'
        return self.mAbbreviationList
    
    def addAbbreviation(self,abbreviation):
        'Adds an abbreviation to the list of abbreviations for a unit.'
        self.mAbbreviationList.append(abbreviation)
    
    def removeAbbreviation(self,abbreviation):
        'Removes an abbreviation from the list of abbreviations for a unit.'
        if(abbreviation in self.mAbbreviationList):
            self.mAbbreviationList.remove(abbreviation)
    
    def getPrefixGroup(self):
        'Returns the value of the unit.'
        return self.mValidPrefixGroup
    
    def setPrefixGroup(self,prefixGroup):
        'Changes the value of the unit.'
        self.mValidPrefixGroup = prefixGroup
    
    def getValue(self):
        'Returns the value of the unit.'
        return self.mValue
    
    def setValue(self,value):
        'Changes the value of the unit.'
        self.mLastUpdated = time.time()
        self.mValue = value
    
    def getOffset(self):
        'Returns the offset of the unit.'
        return self.mOffset
    
    def setOffset(self,offset):
        'Changes the offset of the unit.'
        self.mOffset = offset
    
    def getLastUpdated(self):
        'Returns the last updated time of the unit.'
        return self.mLastUpdated
    
    def setLastUpdated(self,updateTime):
        'Changes the last updated time of the unit.'
        self.mLastUpdated = updateTime
        
    def getPrefixFromUserInput(self,userInput):
        'Returns the prefix matching the user inputed unit name. None if no prefix. False if the input does not match this unit at all.'
        for name in self.mNameList:
            #If {X} is in the name, it means prefix goes in the middle.
            if("{X}" in name):
                nameStart = name.split("{X}")[0].lower()
                nameEnd = name.split("{X}")[1].lower()
                #Ensure that userinput starts with first half and ends with second half.
                if(not userInput.lower().startswith(nameStart) or not userInput.lower().endswith(nameEnd)):
                    continue
                userPrefix = userInput[len(nameStart):len(userInput)-len(nameEnd)]
                #If user prefix is blank, return None
                if(userPrefix==""):
                    return None
                #If no prefix group is valid, accept blank string, reject anything else.
                if(self.mValidPrefixGroup is None):
                    continue
                #Get the prefix in the group whose name matches the user input
                prefixObject = self.mValidPrefixGroup.getPrefixByName(userPrefix)
                if(prefixObject is None):
                    continue
                return prefixObject
            #So, {X} isn't in the name, so it's a standard name.
            if(not userInput.lower().endswith(name.lower())):
                continue
            #Find out what the user said was the prefix
            userPrefix = userInput[:len(userInput)-len(name)]
            if(userPrefix==""):
                return None
            #If no prefix group is valid and user didn't input a blank string, reject
            if(self.mValidPrefixGroup is None):
                continue
            #Get group's prefix that matches name
            prefixObject = self.mValidPrefixGroup.getPrefixByName(userPrefix)
            if(prefixObject is None):
                continue
            return prefixObject
        #Do the same as above, but with abbreviations
        for abbreviation in self.mAbbreviationList:
            #If {X} is in the abbreviation, it means prefix goes in the middle.
            if("{X}" in abbreviation):
                abbreviationStart = abbreviation.split("{X}")[0].lower()
                abbreviationEnd = abbreviation.split("{X}")[1].lower()
                #Ensure that userinput starts with first half and ends with second half.
                if(not userInput.lower().startswith(abbreviationStart) or not userInput.lower().endswith(abbreviationEnd)):
                    continue
                userPrefix = userInput[len(abbreviationStart):len(userInput)-len(abbreviationEnd)]
                #If user prefix is blank, return None
                if(userPrefix==""):
                    return None
                #If no prefix group is valid, accept blank string, reject anything else.
                if(self.mValidPrefixGroup is None):
                    continue
                #Get the prefix in the group whose abbreviation matches the user input
                prefixObject = self.mValidPrefixGroup.getPrefixByAbbreviation(userPrefix)
                if(prefixObject is None):
                    continue
                return prefixObject
            #So, {X} isn't in the abbreviation, so it's a standard abbreviation.
            if(not userInput.lower().endswith(abbreviation.lower())):
                continue
            #Find out what the user said was the prefix
            userPrefix = userInput[:len(userInput)-len(abbreviation)]
            if(userPrefix==""):
                return None
            #If no prefix group is valid and user didn't input a blank string, reject
            if(self.mValidPrefixGroup is None):
                continue
            #Get group's prefix that matches abbreviation
            prefixObject = self.mValidPrefixGroup.getPrefixByAbbreviation(userPrefix)
            if(prefixObject is None):
                continue
            return prefixObject
        return False
    
    @staticmethod
    def fromXml(convertType,xmlString):
        'Loads a new ConvertUnit object from XML.'
        #Load document
        doc = minidom.parse(xmlString)
        #Get names, value and create object
        newNameList = []
        for nameXml in doc.getElementsByTagName("name"):
            newName = nameXml.firstChild.data
            newNameList.append(newName)
        newValue = float(doc.getElementsByTagName("value")[0].firstChild.data)
        newUnit = ConvertUnit(convertType,newNameList,newValue)
        #Loop through abbreviation elements, adding them.
        for abbrXml in doc.getElementsByTagName("abbr"):
            newAbbr = abbrXml.firstChild.data
            newUnit.addAbbreviation(newAbbr)
        #Add prefix group
        if(len(doc.getElementsByTagName("valid_prefix_group"))!=0):
            convertRepo = convertType.getRepo()
            validPrefixGroupName = doc.getElementsByTagName("valid_prefix_group")[0].firstChild.data
            validPrefixGroup = convertRepo.getPrefixGroupByName(validPrefixGroupName)
            newUnit.setPrefixGroup(validPrefixGroup)
        #Get offset
        if(len(doc.getElementsByTagName("offset"))!=0):
            newOffset = float(doc.getElementsByTagName("offset")[0].firstChild.data)
            newUnit.setOffset(newOffset)
        #Get update time
        if(len(doc.getElementsByTagName("last_update"))!=0):
            newLastUpdated = float(doc.getElementsByTagName("last_update")[0].firstChild.data)
            newUnit.setLastUpdated(newLastUpdated)
        #Return created ConvertUnit
        return newUnit
    
    def toXml(self):
        'Outputs a ConvertUnit object as XML.'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("unit")
        doc.appendChild(root)
        #Add name elements
        for nameStr in self.mNameList:
            nameElement = doc.createElement("name")
            nameElement.appendChild(doc.createTextNode(nameStr))
            root.appendChild(nameElement)
        #Add abbreviations
        for abbrStr in self.mAbbreviationList:
            abbrElement = doc.createElement("abbr")
            abbrElement.appendChild(doc.createTextNode(abbrStr))
            root.appendChild(abbrElement)
        #Add prefix group
        if(self.mValidPrefixGroup is not None):
            validPrefixGroupName = self.mValidPrefixGroup.getName()
            validPrefixGroupElement = doc.createElement("valid_prefix_group")
            validPrefixGroupElement.appendChild(doc.createTextNode(validPrefixGroupName))
            root.appendChild(validPrefixGroupElement)
        #Add value element
        valueElement = doc.createElement("value")
        valueElement.appendChild(doc.createTextNode(str(self.mValue)))
        root.appendChild(valueElement)
        #Add offset
        if(self.mOffset is not None):
            offsetElement = doc.createElement("offset")
            offsetElement.appendChild(doc.createTextNode(str(self.mOffset)))
            root.appendChild(offsetElement)
        #Add update time
        if(self.mLastUpdated is not None):
            lastUpdateElement = doc.createElement("last_update")
            lastUpdateElement.appendChild(doc.createTextNode(str(self.mLastUpdated)))
            root.appendChild(lastUpdateElement)
        #Output XML
        return doc.toxml()
    
class ConvertPrefixGroup:
    '''
    Group of Conversion Prefixes.
    '''
    mRepo = None
    mName = None
    mPrefixList = []
    
    def __init__(self,repo,name):
        self.mRepo = repo
        self.mName = name
    
    def getRepo(self):
        'Returns the ConvertRepo owning this prefix group'
        return self.mRepo
    
    def getName(self):
        'Returns the prefix group name'
        return self.mName
    
    def setName(self,name):
        'Sets the prefix group name'
        self.mName = name
    
    def getPrefixList(self):
        'Returns the full list of prefixes in the group'
        return self.mPrefixList
    
    def addPrefix(self,prefix):
        'Adds a new prefix to the prefix list'
        self.mPrefixList.append(prefix)
        
    def removePrefix(self,prefix):
        'Removes a prefix from the prefix list'
        if(prefix in self.mPrefixList):
            self.mPrefixList.remove(prefix)
    
    def getPrefixByName(self,name):
        'Gets the prefix with the specified name'
        for prefixObject in self.mPrefixList:
            if(prefixObject.getName() == name):
                return prefixObject
        for prefixObject in self.mPrefixList:
            if(prefixObject.getName().lower() == name.lower()):
                return prefixObject
        return None
    
    def getPrefixByAbbreviation(self,abbreviation):
        'Gets the prefix with the specified abbreviation'
        for prefixObject in self.mPrefixList:
            if(prefixObject.getAbbreviation() == abbreviation):
                return prefixObject
        for prefixObject in self.mPrefixList:
            if(prefixObject.getAbbreviation().lower() == abbreviation.lower()):
                return prefixObject
        return None
    
    def getAppropriatePrefix(self,value):
        multiplierBiggerThanOne = True
        for prefixObject in self.mPrefixList:
            multiplier = prefixObject.getMultiplier()
            if(multiplierBiggerThanOne and multiplier<1):
                multiplierBiggerThanOne = False
                if(value>1):
                    return None
            afterPrefix = value/prefixObject.getMultiplier()
            if(afterPrefix>1):
                return prefixObject
        return None
    
    @staticmethod
    def fromXml(repo,xmlString):
        'Loads a new ConvertUnit object from XML.'
        #Load document
        doc = minidom.parse(xmlString)
        #Get name and create object
        newName = doc.getElementsByTagName("name")[0].firstChild.data
        newPrefixGroup = ConvertPrefixGroup(repo,newName)
        #Loop through prefix elements, creating and adding objects.
        for prefixXml in doc.getElementsByTagName("prefix"):
            prefixObject = ConvertPrefix.fromXml(self,prefixXml.toxml())
            newPrefixGroup.addPrefix(prefixObject)
        #Return created PrefixGroup
        return newPrefixGroup
    
    def toXml(self):
        'Outputs a ConvertUnit object as XML.'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("prefix_group")
        doc.appendChild(root)
        #Add name element
        nameElement = doc.createElement("name")
        nameElement.appendChild(doc.createTextNode(self.mName))
        root.appendChild(nameElement)
        #Add prefixes
        for prefixObject in self.mPrefixList:
            prefixElement = minidom.parse(prefixObject.toXml()).firstChild
            root.appendChild(prefixElement)
        #Output XML
        return doc.toxml()

class ConvertPrefix:
    '''
    Conversion prefix.
    '''
    mPrefixGroup = None
    mPrefix = None
    mAbbreviation = None
    mMultiplier = None
    
    def __init__(self,prefixGroup,prefix,abbreviation,multiplier):
        self.mPrefixGroup = prefixGroup
        self.mPrefix = prefix
        self.mAbbreviation = abbreviation
        self.mMultiplier = multiplier
    
    def getPrefixGroup(self):
        'Returns the prefix group of the prefix'
        return self.mPrefixGroup
    
    def getPrefix(self):
        'Returns the name of the prefix'
        return self.mPrefix
    
    def setPrefix(self,name):
        'Sets the name of the prefix'
        self.mPrefix = name
    
    def getAbbreviation(self):
        'Returns the abbreviation for the prefix'
        return self.mAbbreviation
    
    def setAbbreviation(self,abbreviation):
        'Sets the abbreviation for the prefix'
        self.mAbbreviation = abbreviation
    
    def getMultiplier(self):
        'Returns the multiplier the prefix has'
        return self.mMultiplier
    
    def setMultiplier(self,multiplier):
        'Sets the multiplier the prefix has'
        self.mMultiplier = multiplier
    
    @staticmethod
    def fromXml(prefixGroup,xmlString):
        'Loads a new ConvertUnit object from XML.'
        doc = minidom.parse(xmlString)
        newName = doc.getElementsByTagName("name")[0].firstChild.data
        newAbbreviation = doc.getElementsByTagName("abbr")[0].firstChild.data
        newValue = float(doc.getElementsByTagName("value")[0].firstChild.data)
        newPrefix = ConvertPrefix(prefixGroup,newName,newAbbreviation,newValue)
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
        #Add abbreviation
        abbrElement = doc.createElement("abbr")
        abbrElement.appendChild(doc.createTextNode(self.mAbbreviation))
        root.appendChild(abbrElement)
        #Add multiplier
        valueElement = doc.createElement("value")
        valueElement.appendChild(doc.createTextNode(str(self.mMultiplier)))
        root.appendChild(valueElement)
        #Return XML
        return doc.toxml()
    
class ConvertMeasure:
    '''
    Convert measure object. An amount with a unit.
    '''
    mAmount = None
    mUnit = None
    
    def __init__(self,amount,unit):
        self.mAmount = amount
        self.mUnit = unit
    
    def getUnit(self):
        'Returns the unit of the measure.'
        return self.mUnit
    
    def getAmount(self):
        'Returns the amount of the measure.'
        return self.mAmount
    
    def convertTo(self,unit):
        'Creates a new measure, equal in value but with a different unit.'
        #Check units are the same type
        if(self.mUnit.getType() != unit.getType()):
            raise Exception("These are not the same unit type.")
        #get base unit
        baseUnit = self.mUnit.getType().getBaseUnit()
        newAmount = self.mAmount * baseUnit.getValue()
        baseOffset = baseUnit.getOffset()
        if(baseOffset is not None):
            newAmount = newAmount + baseOffset
        #Convert from base unit to new unit
        unitOffset = unit.getOffset()
        if(baseOffset is not None):
            newAmount = newAmount - unitOffset
        newAmount = newAmount / unit.getValue()
        newMeasure = ConvertMeasure(newAmount,unit)
        return newMeasure
    
    def convertToBase(self):
        'Creates a new measure, equal in value, but with the base unit of the unit type.'
        baseUnit = self.mUnit.getType().getBaseUnit()
        newUnit = baseUnit
        unitValue = baseUnit.getValue()
        newAmount = self.mAmount * unitValue
        offset = baseUnit.getOffset()
        if(offset is not None):
            newAmount = newAmount + offset
        newMeasure = ConvertMeasure(newAmount,newUnit)
        return newMeasure
    
    def toString(self):
        'Converts the measure to a string for output.'
        decimalPlaces = self.mUnit.getType().getDecimals()
        decimalFormat = "{:"+str(decimalPlaces)+"f}"
        prefixGroup = self.mUnit.getPrefixGroup()
        #If there is no prefix group, output raw.
        if(prefixGroup is None):
            return decimalFormat.format(self.mAmount) + " " + self.mUnit.getName()
        #Ask the prefix group for the most appropriate prefix for the value.
        appropriatePrefix = prefixGroup.getAppropriatePrefix(self.mAmount)
        outputAmount = self.mAmount / appropriatePrefix.getMultiplier()
        #Output string
        return decimalFormat.format(outputAmount) + " " + appropriatePrefix.getName() + self.mUnit.getName()
    
    def __str__(self):
        return self.toString()
    
    def toStringWithPrefix(self,prefix):
        'Converts the measure to a string with the specified prefix.'
        decimalPlaces = self.mUnit.getType().getDecimals()
        decimalFormat = "{:"+str(decimalPlaces)+"f}"
        #Calculate the output amount
        outputAmount = self.mAmount / prefix.getMultiplier()
        #Output string
        return decimalFormat.format(outputAmount) + " " + prefix.getName() + self.mUnit.getName()
    
    @staticmethod
    def buildListFromUserInput(repo,userInput):
        'Creates a new measure from a user inputed line'
        userInputClean = userInput.strip()
        #Search through the line for digits, pull them amount as a preliminary amount and strip the rest of the line.
        #TODO: add calculation?
        preliminaryAmountString = Commons.getDigitsFromStartOrEnd(userInputClean)
        if(preliminaryAmountString is None):
            raise Exception("Cannot find amount.")
        preliminaryAmountValue = float(preliminaryAmountString)
        #Loop all units, seeing which might match userInput with prefixes. Building a list of valid measures for this input.
        newMeasureList = []
        for unitObject in repo.getFullUnitList():
            prefixObject = unitObject.getPrefixFromUserInput(userInput)
            if(prefixObject is False):
                continue
            newAmount = preliminaryAmountValue * prefixObject.getMultiplier()
            newMeasure = ConvertMeasure(newAmount,unitObject)
            newMeasureList.append(newMeasure)
        #If list is still empty, throw an exception.
        if(len(newMeasureList)==0):
            raise Exception("Unrecognised unit.")
        #Return list of matching measures.
        return newMeasureList

class Convert(Function):
    '''
    Function to convert units from one to another
    '''
    #Name for use in help listing
    mHelpName = "convert"
    #Names which can be used to address the Function
    mNames = set(["convert","conversion"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "converts values from one unit to another. Format: convert <value> <old unit> to <new unit>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        return self.convertParse(line)
        
    def convertParse(self,line,passive=False):
        #Create regex to find the place to split a user string.
        splitRegex = re.compile(' into | to |->| in ',re.IGNORECASE)
        #Load ConvertRepo
        repo = ConvertRepo.loadFromXml()
        #See if the input needs splitting.
        if(splitRegex.search(line) is None):
            try:
                fromMeasureList = ConvertMeasure.buildListFromUserInput()
                return self.convertOneUnit(fromMeasureList,passive)
            except Exception as e:
                if(passive):
                    return None
                return "I don't understand your input. ("+str(e)+") Please format like so: convert <value> <old unit> to <new unit>"
        #Split input
        lineSplit = splitRegex.split(line)
        #If there are more than 2 parts, be confused.
        if(len(lineSplit)>2):
            if(passive):
                return None
            return "I don't understand your input. (Are you specifying 3 units?) Please format like so: convert <value> <old unit> to <new unit>"
        #Try loading the first part as a measure 
        try:
            fromMeasureList = ConvertMeasure.buildListFromUserInput(repo,lineSplit[0])
            return self.convertTwoUnit(fromMeasureList,lineSplit[1],passive)
        except:
            #Try loading the second part as a measure
            try:
                fromMeasureList = ConvertMeasure.buildListFromUserInput(repo,lineSplit[1])
                return self.convertTwoUnit(fromMeasureList,lineSplit[0],passive)
            except Exception as e:
                #If both fail, send an error message
                if(passive):
                    return None
                return "I don't understand your input. ("+str(e)+") Please format like so: convert <value> <old unit> to <new unit>"
    
    
    def convertOneUnit(self,fromMeasureList,passive):
        'Converts a single given measure into whatever base unit of the type the measure is.'
        outputLines = []
        for fromMeasure in fromMeasureList:
            toMeasure = fromMeasure.convertToBase()
            outputLines.append(self.outputLine(fromMeasure,toMeasure))
        if(len(outputLines)==0):
            if(passive):
                return None
            return "I don't understand your input. (No units specified.) Please format like so: convert <value> <old unit> to <new unit>"
        return "\n".join(outputLines)
    
    def convertTwoUnit(self,fromMeasureList,userInputTo,passive):
        'Converts a single given measure into whatever unit is specified.'
        outputLines = []
        for fromMeasure in fromMeasureList:
            for toUnitObject in fromMeasure.getUnit().getType().getUnitList():
                prefixObject = toUnitObject.getPrefixFromUserInput(userInputTo)
                if(prefixObject is False):
                    continue
                toMeasure = fromMeasure.convertTo(toUnitObject)
                outputLines.append(self.outputLineWithToPrefix(fromMeasure,toMeasure,prefixObject))
        if(len(outputLines)==0):
            if(passive):
                return None
            return "I don't understand your input. (No units specified or found.) Please format like so: convert <value> <old unit> to <new unit>"
        return "\n".join(outputLines)
        
    def outputLine(self,fromMeasure,toMeasure):
        'Creates a line to output for the equality of a fromMeasure and toMeasure.'
        lastUpdate = toMeasure.getUnit().getLastUpdated() or fromMeasure.getUnit().getLastUpdated()
        outputString = fromMeasure.toString() + " = " + toMeasure.toString() + "."
        if(lastUpdate is not None):
            outputString += " (Last updated: " + Commons.formatUnixTime(lastUpdate) + ")"
        return outputString

    def outputLineWithToPrefix(self,fromMeasure,toMeasure,toPrefix):
        'Creates a line to output for the equality of a fromMeasure and toMeasure, with a specified prefix for the toMeasure.'
        lastUpdate = toMeasure.getUnit().getLastUpdated() or fromMeasure.getUnit().getLastUpdated()
        outputString = fromMeasure.toString() + " = " + toMeasure.toStringWithPrefix(toPrefix) + "."
        if(lastUpdate is not None):
            outputString += " (Last updated: " + Commons.formatUnixTime(lastUpdate) + ")"
        return outputString

    def getPassiveEvents(self):
        return Function.EVENT_MESSAGE
    
    def passiveRun(self,event,fullLine,serverObject,userObject,channelObject):
        return self.convertParse(fullLine,True)

class UpdateCurrencies(Function):
    '''
    Updates all currencies in the ConvertRepo
    '''
    #Name for use in help listing
    mHelpName = "update currencies"
    #Names which can be used to address the Function
    mNames = set(["update currencies","convert update currencies"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Update currency conversion figures, using data from the money converter, the European central bank, forex and preev."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        outputLines = []
        #Load convert repo.
        repo = ConvertRepo()
        #Update with Money Converter
        outputLines.append(self.updateFromMoneyConverterData(repo) or "Updated currency data from The Money Converter.")
        #Update with the European Bank
        outputLines.append(self.updateFromEuropeanBankData(repo) or "Updated currency data from The European Bank.")
        #Update with Forex
        outputLines.append(self.updateFromForexData(repo) or "Updated currency data from Forex.")
        #Update with Preev
        outputLines.append(self.updateFromPreevData(repo) or "Updated currency data from Preev.")
        #Save repo
        repo.saveToXml()
        #Return output
        return "\n".join(outputLines)

    def getPassiveEvents(self):
        return Function.EVENT_HOUR
    
    def passiveRun(self,event,fullLine,serverObject,userObject,channelObject):
        #Load convert repo.
        repo = ConvertRepo()
        #Update with Money Converter
        self.updateFromMoneyConverterData(repo)
        #Update with the European Bank
        self.updateFromEuropeanBankData(repo)
        #Update with Forex
        self.updateFromForexData(repo)
        #Update with Preev
        self.updateFromPreevData(repo)
        #Save repo
        repo.saveToXml()
        return None

    def updateFromMoneyConverterData(self,repo):
        'Updates the value of conversion currency units using The Money Convertor data.'
        #Get currency ConvertType
        currencyType = repo.getTypeByName("currency")
        #Pull xml data from monet converter website
        url = 'http://themoneyconverter.com/rss-feed/EUR/rss.xml'
        xmlString = Commons.loadUrlString(url)
        #Parse data
        doc = minidom.parseString(xmlString)
        root = doc.getElementsByTagName("rss")[0]
        channelElement = root.getElementsByTagName("channel")[0]
        #Loop through items, finding currencies and values
        for itemElement in channelElement.getElementsByTagName("item"):
            #Get currency code from title
            itemTitle = itemElement.getElementsByTagName("title")[0].firstChild.data
            currencyCode = itemTitle.replace("/EUR","")
            #Load value from description and get the reciprocal
            itemDescription = itemElement.getElementsByTagName("description")[0].firstChild.data
            currencyValue = 1/float(Commons.getDigitsFromStartOrEnd(itemDescription.split("=")[1].strip().replace(",","")))
            #Get currency unit, set currency value.
            currencyUnit = currencyType.getUnitByName(currencyCode)
            #If unrecognised currency, continue
            if(currencyUnit is None):
                continue
            #Set value
            currencyUnit.setValue(currencyValue)

    def updateFromEuropeanBankData(self,repo):
        'Updates the value of conversion currency units using The European Bank data.'
        #Get currency ConvertType
        currencyType = repo.getTypeByName("currency")
        #Pull xml data from european bank website
        url = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
        xmlString = Commons.loadUrlString(url)
        #Parse data
        doc = minidom.parseString(xmlString)
        root = doc.getElementsByTagName("gesmes:Envelope")[0]
        cubeOneElement = root.getElementsByTagName("Cube")[0]
        cubeTwoElement = cubeOneElement.getElementsByTagName("Cube")[0]
        for cubeThreeElement in cubeTwoElement.getElementsByTagName("Cube"):
            #Get currency code from currency Attribute
            currencyCode = cubeThreeElement.getAttributeNode("currency").nodeValue
            #Get value from rate attribute and get reciprocal.
            currencyValue = 1/float(cubeThreeElement.getAttributeNode("rate").nodeValue)
            #Get currency unit
            currencyUnit = currencyType.getUnitByName(currencyCode)
            #If unrecognised currency, SKIP
            if(currencyUnit is None):
                continue
            #Set Value
            currencyUnit.setValue(currencyValue)
    
    def updateFromForexData(self,repo):
        'Updates the value of conversion currency units using Forex data.'
        #Get currency ConvertType
        currencyType = repo.getTypeByName("currency")
        #Pull xml data from forex website
        url = 'http://rates.fxcm.com/RatesXML3'
        xmlString = Commons.loadUrlString(url)
        #Parse data
        doc = minidom.parseString(xmlString)
        ratesElement = doc.getElementsByTagName("Rates")
        for rateElement in ratesElement.getElementsByTagName("Rate"):
            #Get data from element
            symbolData = rateElement.getElementsByTagName("Symbol")[0].firstChild.data
            if(not symbolData.startswith("EUR")):
                continue
            bidData = float(rateElement.getElementsByTagName("Bid")[0].firstChild.data)
            askData = float(rateElement.getElementsByTagName("Ask")[0].firstChild.data)
            #Get currency code and value from data
            currencyCode = symbolData[3:]
            currencyValue = 1/(0.5*bidData*askData)
            #Get currency unit
            currencyUnit = currencyType.getUnitByName(currencyCode)
            #If unrecognised code, skip
            if(currencyUnit is None):
                continue
            #Set Value
            currencyUnit.setValue(currencyValue)
    
    def updateFromPreevData(self,repo):
        'Updates the value of conversion cryptocurrencies using Preev data.'
        #Get currency ConvertType
        currencyType = repo.getTypeByName("currency")
        #Pull json data from preev website, combine into 1 dict
        jsonDict = {}
        jsonDict['ltc'] = Commons.loadUrlJson("http://preev.com/pulse/units:ltc+usd/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken")
        jsonDict['ppc'] = Commons.loadUrlJson("http://preev.com/pulse/units:ppc+usd/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken")
        jsonDict['btc'] = Commons.loadUrlJson("http://preev.com/pulse/units:btc+eur/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken")
        jsonDict['xdg'] = Commons.loadUrlJson("http://preev.com/pulse/units:xdg+btc/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken")
        #Loop through currency codes
        for jsonKey in jsonDict:
            currencyCode = jsonKey
            #currencyDict contains the actual information about the currency
            currencyDict = jsonDict[jsonKey][jsonKey]
            currencyRef = list(currencyDict)[0]
            #Add up the volume and trade from each market, to find average trade price across them all
            totalVolume = 0
            totalTrade = 0
            for market in currencyDict[currencyRef]:
                marketVolume = currencyDict[currencyRef][market]['volume']
                marketLast = currencyDict[currencyRef][market]['last']
                totalVolume += marketVolume
                totalTrade += marketLast * marketVolume
            #Calculate currency value, compared to referenced currency, from total market average
            currencyValueRef = totalTrade/totalVolume
            #Get the ConvertUnit object for the currency reference
            currencyRefObject = currencyType.getUnitByName(currencyRef)
            if(currencyRefObject is None):
                continue
            #Work out the value compared to base unit by multiplying value of each
            currencyValue = currencyValueRef * currencyRefObject.getValue()
            #Get the currency unit and update the value
            currencyUnit = currencyType.getUnitByName(currencyCode)
            if(currencyUnit is None):
                continue
            currencyUnit.setValue(currencyValue)

class ConvertViewRepo(Function):
    '''
    Lists types, units, names, whatever.
    '''
    #Name for use in help listing
    mHelpName = "convert view repo"
    #Names which can be used to address the Function
    mNames = set(["convert view repo","convert view","convert list"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns information about the conversion repository."
    
    NAMES_TYPE = ["type","t"]
    NAMES_UNIT = ["unit","u"]
    NAMES_PREFIXGROUP = ["prefixgroup","prefix_group","prefix-group","group","g","pg"]
    NAMES_PREFIX = ["prefix","p"]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load repo
        repo = ConvertRepo.loadFromXml()
        #Check if type is specified
        if(self.findAnyParameter(self.NAMES_TYPE,line)):
            #Check if unit & type are specified
            if(self.findAnyParameter(self.NAMES_UNIT,line)):
                return "type and unit"
            else:
                return "type, no unit"
        #Check if prefix group is specified
        if(self.findAnyParameter(self.NAMES_PREFIXGROUP,line)):
            #Check if prefix & group are specified
            if(self.findAnyParameter(self.NAMES_PREFIX,line)):
                return "group and prefix"
            else:
                return "group, no prefix"
        #Check if unit is specified
        if(self.findAnyParameter(self.NAMES_UNIT,line)):
            return "unit, no type"
        #Check if prefix is specified
        if(self.findAnyParameter(self.NAMES_PREFIX,line)):
            return "prefix, no group"
        #Nothing was specified, return info on the repo.
        return self.outputRepoAsString(repo)
    
    def findParameter(self,paramName,line):
        'Finds a parameter value in a line, if the format parameter=value exists in the line'
        paramValue = None
        paramRegex = re.compile("(^|\s)"+paramName+"=([^\s]+)(\s|$)",re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if(paramSearch is not None):
            paramValue = paramSearch.group(2)
        return paramValue

    def findAnyParameter(self,paramList,line):
        'Finds one of any parameter in a line.'
        for paramName in paramList:
            if(self.findParameter(paramName,line) is not None):
                return self.findParameter(paramName,line)
        return False
    
    def outputRepoAsString(self,repo):
        'Outputs a Conversion Repository as a string'
        outputString = "Conversion Repo:\n"
        outputString += "Unit types: " + ", ".join([typeObject.getName() for typeObject in repo.getTypeList()]) + "\n"
        outputString += "Prefix groups: " + ", ".join([typeObject.getName() for typeObject in repo.getTypeList()])
        return outputString

    def outputTypeAsString(self,typeObject):
        'Outputs a Conversion Type object as a string'
        outputString = "Conversion Type: (" + typeObject.getName() + ")\n"
        outputString += "Decimals: " + str(typeObject.getDecimals()) + "\n"
        outputString += "Base unit: " + typeObject.getBaseUnit().getNameList()[0] + "\n"
        outputString += "Other units: " 
        outputString += ", ".join([unitObject.getNames()[0] for unitObject in typeObject.getUnitList()])
        return outputString

    def outputUnitAsString(self,unitObject):
        'Outputs a Conversion Unit object as a string'
        outputLines = []
        outputLines.append("Conversion Unit: (" + unitObject.getNameList()[0] + ")")
        outputLines.append("Type: " + unitObject.getType().getName())
        outputLines.append("Name list: " + ", ".join(unitObject.getNameList()))
        outputLines.append("Abbreviation list: " + ", ".join(unitObject.getAbbreviationList()))
        outputLines.append("Value: 1 " + unitObject.getNameList()[0] + " = " + str(unitObject.getValue()) + " " + unitObject.getType().getBaseUnit().getNameList()[0])
        outputLines.append("Offset: 0 " + unitObject.getNameList()[0] + " = " + str(unitObject.getOffset()) + " " + unitObject.getType().getBaseUnit().getNameList()[0])
        lastUpdate = unitObject.getLastUpdated()
        if(lastUpdate is not None):
            outputLines.append("Last updated: " + Commons.formatUnixTime(lastUpdate))
        prefixGroupName = unitObject.getValidPrefixGroup().getName()
        if(prefixGroupName is not None):
            outputLines.append("Prefix group: " + prefixGroupName)
        return "\n".join(outputLines)

    def outputPrefixGroupAsString(self,prefixGroupObject):
        'Outputs a Conversion PrefixGroup object as a string'
        outputString = "Prefix group: (" + prefixGroupObject.getName() + ")\n"
        outputString += "Prefix list: " + ", ".join([prefixObject.getName() for prefixObject in prefixGroupObject.getPrefixList()])
        return outputString
    
    def outputPrefixAsString(self,prefixObject):
        'Outputs a Conversion prefix object as a string'
        outputString = "Prefix: (" + prefixObject.getPrefix() + ")\n"
        outputString += "Abbreviation: " + prefixObject.getAbbreviation() + "\n"
        outputString += "Multiplier: " + str(prefixObject.getName())
        return outputString
    
