

class Server(object):
    '''
    Generic server object. An interface for ServerIRC or ServerSkype or whatever objects.
    '''

    def __init__(self, params):
        '''
        Constructor for server object
        '''
        raise NotImplementedError
    
    def connect(self):
        raise NotImplementedError
    
    def disconnect(self):
        raise NotImplementedError
    
    def run(self):
        '''
        Method to read from stream and process. Will call an internal parsing method or whatnot
        '''
        raise NotImplementedError
