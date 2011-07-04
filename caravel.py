#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       caravel.py
#       
#       Copyright 2011 RedMonkey
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os
import sys
import socket
import time
import thread
import urllib2
import re
import BeautifulSoup

__USER_AGENT__='Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
__URL_PROXY_LIST__="http://hidemyass.com/proxy-list/"
__MENU__='''
Caravel - Version 0.0.1 - Created RedMonkey
This program gets a list of proxy sites and you can get in through proxies

Execute: caravel --[Options]

Options:
	--help				Displays this message
	--version			Displays the version of program
	--proxy-list			Displays proxy list
	
	(The following actions can be long!)
	
	--proxy-list <Country>		Displays proxy list from a given country
	--site-proxy  http://site.com	Go to site for proxy 
'''




def main():
	
	#DEFINE TIMEOUT
	socket.setdefaulttimeout(15)
	
	# PROGRAM OPTIONS 
	if len(sys.argv) == 2:
		if sys.argv[1].startswith('--'):
			option = sys.argv[1][2:]
			if option == 'help':
				os.system("clear")
				print __MENU__
			elif option == 'version':
				print 'version 0.0.1'
			elif option == 'proxy-list':
				show_proxy_list()
			elif option == '':
				os.system("clear")
				print __MENU__
			sys.exit()		
	elif len(sys.argv) == 3:
		if sys.argv[1].startswith('--'):
			option = sys.argv[1][2:]
			if option == 'site-proxy':
				visit_site_proxy(sys.argv[2])
			elif option == 'proxy-list':
				show_proxy_list(sys.argv[2])
			sys.exit()	
	
	os.system("clear")
	print __MENU__
	sys.exit()


def request_page(url,user_agent='Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'):
	
	# Header
	#headers={ 'User-Agent' : user_agent}
	
	# Request page
	#request=urllib2.Request(url,"",headers)
	response=urllib2.urlopen(url)
	page=response.read()

	return page


def request_page_proxy(url,proxy,user_agent='Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'):
	
	# Request page
	addproxy = urllib2.ProxyHandler({"http":proxy})
	opener = urllib2.build_opener(addproxy)
	urllib2.install_opener(opener)
	response=urllib2.urlopen(url)	
	page=response.read()
	
	return page
	

def getproxy_list(url):
	
	# Read proxy list
	PROXY_PAGE_LIST=request_page(url)

	# Return BeautifulSoup tags objects
	SOUP_PAGE=soup=BeautifulSoup.BeautifulSoup(PROXY_PAGE_LIST) 

	# Find to tag: <td>
	PROXY_PAGE_LIST_FILTERED=td_filter=SOUP_PAGE.findAll("td")
	#print td_filter
	
	
	# FIND IPs
	IP_LIST=ip_list=[]
	regexp=re.compile("(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)")
	for string in PROXY_PAGE_LIST_FILTERED:
		ip=re.findall(regexp,str(string))
		if len(ip) > 0:
			IP_LIST.append(str(ip[0]))
	#print IP_LIST
	
	# FIND PORTs
	PORT_LIST=port_list=[]
	for string in PROXY_PAGE_LIST_FILTERED:
		regexp=re.compile("[0-9][0-9][0-9]?[0-9]?</td>")
		port=re.findall(regexp,str(string))
		if len(port) > 0:
			port=str(port[0])
			port=port.strip("</td>")
			PORT_LIST.append(port)	
	#print PORT_LIST
	
	
	# FIND COUNTRIES
	COUNTRY_LIST=country_list=[]
	for string in PROXY_PAGE_LIST_FILTERED:
		regexp=re.compile("/> .*</span>")
		country=re.findall(regexp,str(string))
		if len(country) > 0:
			country=str(country[0])
			# DELETE TAGs
			country=country.strip("/>") 
			country=country.strip("span")
			country=country.strip("</")
			COUNTRY_LIST.append(country[1:])
	#print COUNTRY_LIST

	#RETURN TUPLE WITH THREE ARRAYS
	if (len(IP_LIST)+len(PORT_LIST)+len(COUNTRY_LIST))/3 == len(IP_LIST):
		return (IP_LIST,PORT_LIST,COUNTRY_LIST)
	else:
		return([],[],[])


def show_proxy_list(*country):

	# GET PROXY LIST
	IP_LIST,PORT_LIST,COUNTRY_LIST=getproxy_list(__URL_PROXY_LIST__)
	
	# SHOW PROXY LIST FILTERED TO COUNTRY
	if country:
		while COUNTRY_LIST.count(country[0]) == 0: 
			# GET PROXY LIST
			IP_LIST,PORT_LIST,COUNTRY_LIST=getproxy_list(__URL_PROXY_LIST__)
			
		#SHOW PROXY LIST(FILTERED)	
		for x in range(len(IP_LIST)):
			if COUNTRY_LIST[x] == country[0]:
				print "%s:%s" %(IP_LIST[x],PORT_LIST[x])
	else:
		# SHOW PROXY LIST
		for x in range(len(IP_LIST)):
			print "%s:%s" %(IP_LIST[x],PORT_LIST[x])
	
	sys.exit()
	
def visit_site_proxy(url):
	
	# GET PROXY LIST
	os.system("clear")
	print "\n\n\t\t\tCaravel - Version 0.0.1\n\nWait get proxy list... "
	IP_LIST,PORT_LIST,COUNTRY_LIST=getproxy_list(__URL_PROXY_LIST__)
	
	# GO TO VISIT URL CHOSEN
	site=request_page(url)
	
	os.system("clear")
	print  "\33[34;1m\tPROXY\t\t\t\33[m","\33[34;1m\t\tCOUNTRY\t\33[m"
	
	
	# GO TO VISIT URL WITH PROXY
	CLOSE_THREAD=[]
	for x in range(len(IP_LIST)):
		
		def visit(orig_site,url,ip,port,country,id):
			#print "\n[Open Thread " + str(id) + ']'
			#print  "\33[34;1m\n%s:%s \t\t\t%s\33[m" %(ip,port,country)
			try:
				# GO TO VISIT URL CHOSEN WITH PROXY
				page=request_page_proxy(url,ip + ':' + port)
				#print "\n[Close Thread " + str(id) + ']'
				#print  "\33[34;1m  %s:%s \t\t\t\t%18s\n \33[m" %(ip,port,country)
				print "\33[33;1m \n * Size page load w/ proxy: %s \33[m" %len(page),"\33[33;1m \n * Size page load w/ direct connection  %s \33[m" %len(orig_site),"\n","\33[32;1m \n * VISIT URL OK!\n \33[m"
				
				# Create Page
				os.system("mkdir -p caravel")
				page_file=open('caravel/' + url[7:] + str(id) + '.html','w')
				for line in page: 
					page_file.write(line)
				page_file.close()
				
				CLOSE_THREAD.append(id)
			except:
				#print "\n[Close Thread " + str(id) + ']'
				#print  "\33[34;1m  %s:%s \t\t\t\t%18s \33[m" %(ip,port,country)
				print "\33[31;1m \n * The Problem Ocurred! Skipping!\n \33[m"
				CLOSE_THREAD.append(id)
			print "\n[Close Thread " + str(id) + ']'	
			print  "\33[34;1m  %s:%s \t\t\t\t%18s \33[m" %(ip,port,country)
			return	

		thread.start_new_thread(visit,(site,url,IP_LIST[x],PORT_LIST[x],COUNTRY_LIST[x],x,))
		if x%3 == 0:
			time.sleep(1)


	while len(CLOSE_THREAD) <= len(IP_LIST):
		if len(CLOSE_THREAD) == len(IP_LIST):
			os.system("clear")
			print "\n\n\t\t\tCaravel - Version 0.0.1\n\n\nFinished!"
			sys.exit()
		else:
			#os.system("clear")
			parcial=len(CLOSE_THREAD)
			#print "\n\n\t\t\tCaravel - Version 0.0.1\n\nWait the last proxies responses...."
			time.sleep(1)

	sys.exit()
			
if __name__ == '__main__':
	main()
