#!/usr/bin/env python
# -*- coding: utf-8

from mumo_module import (commaSeperatedIntegers, MumoModule)
import re, ast, socket, json, sched, time, threading, BaseHTTPServer, uuid
#import twitter

#from twitter import Api
import twitter

def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print repr(k)
                dumpclean(v)
            else:
                print '%s : %s' % (repr(k), repr(v))
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print repr(v)
    else:
        print repr(obj)




class TwitterObject(object):

    def __init__(self, configobj, log):
#        threading.Thread.__init__(self) 
        self.log = log
        self.log.debug('ttt:' + repr(configobj.CONSUMER_KEY))
 
        USERS = ['#bvbfcb']
        self.searchstring = ['#castro']
        
        self.api = twitter.Api(configobj.CONSUMER_KEY,
             configobj.CONSUMER_SECRET,
             configobj.ACCESS_TOKEN,
             configobj.ACCESS_TOKEN_SECRET)
        
        log.debug("server started")


#    def run(self): 
# 
#        for line in self.api.GetUserStream(track=self.searchstring):
#            jsontweet = json.dumps(line)
#            self.log.debug("twitter:" + " - " + line["text"])
#            self.log.debug("twitter:" + " - " + str(dumpclean(line)))
#            self.log.debug("twitter:" + " - " + repr(line))



class TwitterStreamWorker(threading.Thread):
    def __init__(self, configobj, twitterchannel, server, log):
        threading.Thread.__init__(self)
        
        self.channelid = configobj.CHANNELID
        self.log = log
        self.server = server
        
        if (self.channelid is -1):
            # Channelid suchen 
            self.channel = configobj.CHANNEL

        self.twitterchannel = twitterchannel
        self.searchstring = ast.literal_eval(configobj.KEYWORDS)
        self.log.debug('searchstr: ' + repr(self.searchstring[0]))


    def parsemessage(self, twitterobj):
    
        html = ""
        html += "<br />\n"
    
        if 'text' in twitterobj:
            html += twitterobj['text']
    
        return html
        
    
    def run(self):
        for line in self.twitterchannel.api.GetUserStream(track=self.searchstring):
#            jsontweet = json.dumps(line)
#            self.log.debug("\n\ntwitter:" + " - " + repr(line))
            if 'text' in line:
                self.log.debug("twitter:" + " - " + line['text'])
                self.server.sendMessageChannel(0, 1, self.parsemessage(line))
            


class twitterstream(MumoModule):

    default_config = {'twitterstream':(('servers', commaSeperatedIntegers, []), ),
                        lambda x: re.match('(all)|(twitter_\d+)', x):(
                            ('CONSUMER_KEY',        str, ""),
                            ('CONSUMER_SECRET',     str, ""),
                            ('ACCESS_TOKEN',        str, ""),
                            ('ACCESS_TOKEN_SECRET', str, "")
                        ),
                        lambda x: re.match('(engine_\d+)', x):(
                            ('SERVERID',            str, "1"),
                            ('CHANNELID',           str, "-1"),
                            ('CHANNEL',             str, "root"),
                            ('LINKMODE',            str, "off"),
                            ('TWITTERCHANNEL',      str, "1"),
                            ('KEYWORDS',            str, "['#TrashTVTalk']"),
                            ('TEMPLATE',            str, "<tweettext>")
                        )
                     }


    def parseNotification(self, notification):
        feedInfo = notification["feedName"].split('-')
        parsed = "<center>"
        if notification["link"] is not None:
            parsed += "<a href=\"" + notification["link"] + "\">"
        if notification["imageURL"] is not None:
            parsed += "<img src=\"" + notification["imageURL"] + "\"></img><br>"
        if notification["color"] is not None:
            parsed += "<font color=\"" + notification["color"] + "\">"
        parsed += "<b><font size=\"4\">" + notification["title"] + "</font></b><br>"
        if notification["link"] is not None:
            parsed += "</a>"
        parsed += "<font size=\"3\">"
        if notification["extra"] is not None:
            if feedInfo[1] == "4chan":
                parsed += ">>>/" + notification["extra"]["board"] + "/" + str(notification["extra"]["id"])
                parsed += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                parsed += str(notification["extra"]["replies"]) + "/"
                parsed += str(notification["extra"]["images"]) + "/"
                parsed += str(notification["extra"]["page"]) + "<br>"
            elif feedInfo[1] == "youtube":
                parsed += notification["extra"]["displayName"] + "<br>"
            elif feedInfo[1] == "vinesauce":
                parsed += notification["extra"]["displayName"] + "<br>"
            else:
                parsed += str(notification["extra"]) + "<br>"
        parsed += "</font><font size=\"2\">" + feedInfo[0] + " &#8594; " + feedInfo[1]
        if len(feedInfo) > 2:
            parsed += " &#8594; " + feedInfo[2]
        parsed += "</font>"
        if notification["color"] is not None:
            parsed += "</font>"
        parsed += "</center>"
        return parsed


    def __init__(self, name, manager, configuration = None):
        MumoModule.__init__(self, name, manager, configuration)
        self.murmur = manager.getMurmurModule()
        log = self.log()
        
        counter = 1
        twitterstream.twitterchannels = {}
        scfg = 0
        log.debug("Starting #")
        while (not (scfg is None)):
            log.debug("Starting ## " + str(counter))
            try:
                scfg = getattr(self.cfg(), 'twitter_%d' % counter)
                log.debug("Starting " + str(counter))
            except AttributeError:
                scfg = None
                log.debug("Starting failed " + str(counter))
                break
            log.debug("sss:" + repr(scfg.CONSUMER_KEY))

            twitterstream.twitterchannels[counter] = TwitterObject(scfg, log) 
#            twitterstream.twitterchannels[counter].start()

            counter = counter + 1
        
        
    def connected(self):
        manager = self.manager()
        log = self.log()
        log.debug("Register for Server callbacks")

        servers = self.cfg().twitterstream.servers
        if not servers:
            servers = manager.SERVERS_ALL

        manager.subscribeServerCallbacks(self, servers)

        threads = []

#        servers = set()
#        for i in range(cfg.bf2.gamecount):
#            try:
#                servers.add(cfg["g%d" % i].mumble_server)
#            except KeyError:
#                log.error("Invalid configuration. Game configuration for 'g%d' not found.", i)
#                return
#            self.sessions = {} # {serverid:{sessionid:laststate}}
#            manager.subscribeServerCallbacks(self, servers)
#            manager.subscribeMetaCallbacks(self, servers)


        connServers = manager.getMeta().getBootedServers();
        for serv in connServers:
            log.debug("Starting " + str(serv.id()))

            try:
                scfg = getattr(self.cfg(), 'engine_%d' % serv.id())
            except AttributeError:
                scfg = None

            if ( scfg is None):
                return

#                entry = "%i-%s" % (serv.id(), userlist[user].name)
#                setattr(maxusers, entry, userlist[user].channel)
#                userCount = userCount + 1
#            log.debug("Successfully took snap shot of user positions into memory for %i users" % userCount)

            thread = TwitterStreamWorker(scfg, twitterstream.twitterchannels[serv.id()], serv, log) 
            threads += [thread] 
            thread.start() 

    def userTextMessage(self, server, user, message, current=None):
        pass

    def disconnected(self): pass
    def userConnected(self, server, state, context = None): pass
    def userDisconnected(self, server, state, context = None): pass
    def userStateChanged(self, server, state, context = None): pass
    def channelCreated(self, server, state, context = None): pass
    def channelRemoved(self, server, state, context = None): pass
    def channelStateChanged(self, server, state, context = None): pass
