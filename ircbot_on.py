import time

import ircbot_chk
import ircbot_base

endl = '\r\n'

class ircbot_on:

    def on_init(self):
        pass # override this method to do any startup code

    def on_ping(self,server,code):
        # handle pings from servers.
        pass

    def on_join(self,server,client,channel):
        # handle join events from other users (or from hallo!)
        if(client.lower() in self.conf['server'][server]['channel'][channel]['voice_list']):
            for x in range(7):
                if(ircbot_chk.ircbot_chk.chk_userregistered(self,server,client)):
                    self.core['server'][server]['socket'].send(('MODE ' + channel + ' +v ' + client + endl).encode('utf-8'))
                    time.sleep(5)
                    break
        if(client.lower() == self.conf['server'][server]['nick'].lower()):
            self.conf['server'][server]['channel'][channel]['in_channel'] = True
            namesonline = ircbot_chk.ircbot_chk.chk_names(self,server,channel)
            namesonline = [x.lower() for x in namesonline]
            for user in self.conf['server'][server]['channel'][channel]['voice_list']:
                if(user in namesonline and "+" + user not in namesonline):
                    for x in range(7):
                        if(ircbot_chk.ircbot_chk.chk_userregistered(self,server,user)):
                            self.core['server'][server]['socket'].send(('MODE ' + channel + ' +v ' + user + endl).encode('utf-8'))
                            break
                        time.sleep(5)
        else:
            self.core['server'][server]['channel'][channel]['user_list'].append(client)

    def on_part(self,server,client,channel,args):
        #pass # override this method to handle PART events from other users
        self.core['server'][server]['channel'][channel]['user_list'].remove(client)

    def on_quit(self,server,client,args):
        #pass # override this method to handle QUIT events from other users
        for channel in self.conf['server'][server]['channel']:
            if(client in self.core['server'][server]['channel'][channel]['user_list']):
                self.core['server'][server]['channel'][channel]['user_list'].remove(client)

    def on_mode(self,server,client,channel,mode,args):
         #pass # override this method to handle MODE changes
        if(mode=='-k'):
            self.conf['server'][server]['channel'][channel]['pass'] = ''
        elif(mode=='+k'):
            self.conf['server'][server]['channel'][channel]['pass'] = args

    def on_ctcp(self,server,client,args):
        # handle ctcp messages and events to privmsg
        if(args.lower()=='version'):
            self.core['server'][server]['socket'].send(('NOTICE ' + client + ' :\x01VERSION Hallobot:vX.Y:An IRC bot by dr-spangle.\x01' + endl).encode('utf-8'))
        elif(args.lower()=='time'):
            self.core['server'][server]['socket'].send(('NOTICE ' + client + ' :\x01TIME Fribsday 15 Nov 2024 ' + str(time.gmtime()[3]+100).rjust(2,'0') + ':' + str(time.gmtime()[4]+20).rjust(2,'0') + ':' + str(time.gmtime()[5]).rjust(2,'0') + 'GMT\x01' + endl).encode('utf-8'))
        elif(len(args)>4 and args[0:4].lower()=='ping'):
            self.core['server'][server]['socket'].send(('NOTICE ' + client + ' :\x01PING ' + args[5:] + '\x01' + endl).encode('utf-8'))
        elif(len(args)>=8 and args[0:8].lower()=='userinfo'):
            self.core['server'][server]['socket'].send(('NOTICE ' + client + " :\x01Hello, I'm hallo, I'm a robot who does a few different things, mostly roll numbers and choose things, occassionally giving my input on who is the best pony. dr-spangle built me, if you have any questions he tends to be better at replying than I.\x01" + endl).encode('utf-8'))
        elif(len(args)>=10 and args[0:10].lower()=='clientinfo'):
            self.core['server'][server]['socket'].send(('NOTICE ' + client + ' :\x01VERSION, NOTICE, TIME, USERINFO and obviously CLIENTINFO are supported.\x01' + endl).encode('utf-8'))

    def on_pm(self,server,client,destination,message):
        pass # override this method to handle messages alternately

    def on_notice(self,server,client,channel,args):
        # handle notices
        if(self.core['server'][server]['connected'] == False):
            self.core['server'][server]['connected'] = True
            print(self.base_timestamp() + ' [' + server + "] ok we're connected now.")
        if('endofmessage' in args.replace(' ','').lower() and self.core['server'][server]['motdend'] == False):
            self.core['server'][server]['motdend'] = True
        if(any(nickservmsg in args.replace(' ','').lower() for nickservmsg in self.conf['nickserv']['online']) and client.lower()=='nickserv' and self.core['server'][server]['check']['userregistered'] == False):
            self.core['server'][server]['check']['userregistered'] = True
        if(any(nickservmsg in args.replace(' ','').lower() for nickservmsg in self.conf['nickserv']['registered']) and client.lower()=='nickserv' and self.core['server'][server]['check']['nickregistered'] == False):
            self.core['server'][server]['check']['nickregistered'] = True
        pass # override this method to handle notices alternatively

    def on_nickchange(self,server,client,newnick):
        # handle people changing their nick
        for channel in self.conf['server'][server]['channel']:
            if(client in self.core['server'][server]['channel'][channel]['user_list']):
                self.core['server'][server]['channel'][channel]['user_list'].remove(client)
                self.core['server'][server]['channel'][channel]['user_list'].append(newnick)
        if(client == self.conf['server'][server]['nick']):
            self.conf['server'][server]['nick'] = newnick
        for channel in self.conf['server'][server]['channel']:
            if(newnick in self.conf['server'][server]['channel'][channel]['voice_list']):
                for x in range(7):
                    if(ircbot_chk.ircbot_chk.chk_userregistered(self,server,client)):
                        self.core['server'][server]['socket'].send(('MODE ' + channel + ' +v ' + newnick + endl).encode('utf-8'))
                        time.sleep(5)
                        break

    def on_invite(self,server,client,channel):
        if(ircbot_chk.ircbot_chk.chk_op(self,server,client)):
            ircbot_base.ircbot_base.fn_join(self,channel,client,[server,''])
        pass # override to do something on invite

    def on_kick(self,server,client,channel,message):
        self.core['server'][server]['channel'][channel]['user_list'].remove(client)
        if(client == self.conf['server'][server]['nick']):
            self.conf['server'][server]['channel'][channel]['in_channel'] = False

    def on_numbercode(self,server,code,data):
        #handle 3 digit number codes sent by servers.
        if(code == "376"):
            self.core['server'][server]['motdend'] = True
        elif(code == "303"):
            self.core['server'][server]['check']['recipientonline'] = ':'.join(data.split(':')[2:])
            if(self.core['server'][server]['check']['recipientonline']==''):
                self.core['server'][server]['check']['recipientonline'] = ' '
        elif(code == "353"):
            channel = data.split(':')[1].split()[-1].lower()
            self.core['server'][server]['check']['names'] = ':'.join(data.split(':')[2:])
            self.core['server'][server]['channel'][channel]['user_list'] = [nick.replace('~','').replace('&','').replace('@','').replace('%','').replace('+','') for nick in self.core['server'][server]['check']['names'].split()]
            if(self.core['server'][server]['check']['names']==''):
                self.core['server'][server]['check']['names'] = ' '


    def on_rawdata(self,server,data,unhandled):
        pass # override this method to do general data handling



