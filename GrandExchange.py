#!/usr/bin/python

import json
import urllib
import re
import datetime as d
import math
import datetime as d
import Gnuplot, Gnuplot.funcutils
import os
import time
import sys
from threading import Thread

class RSItemDatabase:
    
    def __init__(self):
        datafile = "id_info.dat"
        data = json.load(open(datafile))
        self.items = {}
        for id in data:
            self.items[id['id']]=id['name']
    
    def pulldata(self):
        i = 0
        total = len(self.items)
        self.id = {}
        for item in self.items:
            self.id[item] = {}
            self.id[item]['name'] = self.items[item]
            url = "http://services.runescape.com/m=itemdb_rs/api/graph/" + str(item) + ".json"
            #url = "http://api.rsapi.net/ge/graph/" + str(item) + ".json"
            htmlfile = urllib.urlopen(url)
            #data = json.load(htmlfile)[0]['graphdata']['daily']
            data = json.load(htmlfile)['daily']
            self.id[item]['prices'] = []
            self.id[item]['timestamps'] = []                            
            for record in data:
                self.id[item]['prices'].append(data[record])
                self.id[item]['timestamps'].append(int(record)/1000)
            i += 1
            completion = float(i)/float(total)
            print "{:.2%} completed (url: {})".format(completion,url)
    
    def _multi_pull(self,item,i):
        
        self.id[item] = {}
        self.id[item]['name'] = self.items[item]
        #url = "http://services.runescape.com/m=itemdb_rs/api/graph/" + str(item) + ".json"
        url = "http://api.rsapi.net/ge/graph/" + str(item) + ".json"
        try:            
            htmlfile = urllib.urlopen(url)
            data = json.load(htmlfile)[0]['graphdata']['daily']
            #data = json.load(htmlfile)['daily']
            self.multi_success.append('Pulled: "'+str(self.id[item]['name'])+'" (id: '+str(item)+')' )
        except:
            self.multi_failure.append('Failed: "'+str(self.id[item]['name'])+'" (id: '+str(item)+')')
            self.multi_fail_id.append(item)
            return
        self.id[item]['prices'] = []
        self.id[item]['timestamps'] = []                            
        for record in data:
            self.id[item]['prices'].append(data[record])
            self.id[item]['timestamps'].append(int(record)/1000)
        self.completion = float(len(self.multi_success)+len(self.multi_failure))/float(len(self.items))
        print "{:.2%} completed. Got {}".format(self.completion,self.id[item]['name'])
    
    def multi_pull(self):
        threadlist = []
        self.multi_failure = []
        self.multi_success = []
        self.multi_fail_id = []
        self.id = {}
        i = 0        
        for item in self.items:
            t = Thread(target=self._multi_pull,args=(item,i,))
            threadlist.append(t)
            t.start()
            i += 1
            #if i>= 50:
            #    break
        for f in threadlist:
            f.join()
    
    def details(self,identifier):
        print "-----------Item Details----------"
        print "Item: ", self.id[identifier]['name']
        print "ID: ", identifier
        self.plot(identifier)
        print "---------------------------------"
            
    def plot(self,identifier):
        x = self.id[identifier]['timestamps']
        y = self.id[identifier]['prices']
        name = self.id[identifier]['name']
        filename = "data/"+str(identifier)+" - "+str(self.id[identifier]['name'])+".png"        
        g = Gnuplot.Gnuplot(debug=0)
        p = Gnuplot.Data(x,y, with_='lines',using='1:2 smooth unique')
        g.xlabel('Time')
        g.ylabel('Value')
        g.title('Data scraped from Runescape.com - Price of ' + name )
        g('set term pngcairo enhanced font "Verdana,8"')
        g('set output "' + filename + '"')
        g('set xdata time')
        g('set timefmt "%s"')
        g('set format x "%d-%b-%y"')
        g.plot(p)
        #time.sleep(2)
        #os.system("open " + filename)
    
    def multi_f(self):
        for fail in self.multi_failure:
            print fail
    
    def multi_s(self):
        for pull in self.multi_success:
            print pull
    
    def mkfile(self):
        for item in self.id:
            with open("RS_Data/"+str(item)+".txt", "w") as f:
                for t,p in zip(self.id[item]['timestamps'],self.id[item]['prices']):
                    print >> f,t,p
    
    def plotall(self):
        for item in self.items:
            self.plot(item)
    def pullfailed(self):
        while self.completion < 1:
            print "pulling failed items..."
            i = 0
            total = len(self.multi_fail_id)
            for item in self.multi_fail_id:
                self.id[item] = {}
                self.id[item]['name'] = self.items[item]
                url = "http://services.runescape.com/m=itemdb_rs/api/graph/" + str(item) + ".json"
                try:            
                    htmlfile = urllib.urlopen(url)
                    data = json.load(htmlfile)[0]['graphdata']['daily']
                    #data = json.load(htmlfile)['daily']
                    self.multi_success.append('Pulled: "'+str(self.id[item]['name'])+'" (id: '+str(item)+')' )
                    self.multi_fail_id.remove(item)
                    self.multi_failure.remove('Failed: "'+str(self.id[item]['name'])+'" (id: '+str(item)+')')
                except:
                    break
                self.id[item]['prices'] = []
                self.id[item]['timestamps'] = []                            
                for record in data:
                    self.id[item]['prices'].append(data[record])
                    self.id[item]['timestamps'].append(int(record)/1000)
                i += 1
                self.completion = float(i)/float(total)
                print "{:.2%} completed (url: {})".format(self.completion,url)


if '__main__' == __name__:
    x = RSItemDatabase()
    x.multi_pull()
    x.pullfailed()
    x.mkfile()
    x.plotall()