#!/usr/bin/env python
"""peastat - simple live web stats
http://www.throwingbeans.org/peastat/

instructions: 
1. configure the 'logfile' and 'rooturl' values below
2. upload peastat.py somewhere it can be executed on your web server (e.g. your cgi-bin)
3. make peastat.py executable (set its permissions to 755)
"""
__version__ = "0.2"
__author__ = "Tom Dyson (tomdyson at spamcop dot net)"
__copyright__ = "(C) 2005 Tom Dyson. GNU GPL 2." 
__url__ = 'http://www.throwingbeans.org/peastat/'

import cgitb
cgitb.enable()
import cgi, os, re, time, urllib
try: import dbm # anydbm is unreliable...
except: import dumbdbm as dbm

# start configuring:
logfile = "/home/jacob/web/log/djangobook.com/www.log" # full path to log file
rooturl = "http://www.djangobook.com/" # root url of site whose logs we're analysing
# configure if you want to:
minresults = 10 # minimum results to include in overview
lastlines = 5000 # number of most recent requests to analyse
ispage = re.compile('/$').search # requests matching this regex count as pages
ignorelines = re.compile('24\.124\.4\.220').search # ignore lines including this regex
recentreferrers = 20 # show this many recent referrers 
recentsearches = 20 # show this many recent search terms
database = "/tmp/jkmpeastat.db" # store DNS lookups here
# stop configuring

url = None; ip = None; atom = False
cgiloc = os.environ.get('SCRIPT_NAME', '')
request_uri = os.environ.get('REQUEST_URI', '')
server_name = os.environ.get('SERVER_NAME', '')
apachetoday = time.strftime('%d/%b/%Y')
# todo ooh

form = cgi.FieldStorage()
if form.has_key( "url" ): url = form["url"].value
if form.has_key( "ip" ): ip = form["ip"].value
if form.has_key( "atom" ): atom = True

def justdomain(url): 
	# Return only the domain of a URL
	try:
		return url.split('//')[1].split('/')[0]
	except IndexError: # catch evil referrers
		return 'bad referrer'

thisdomain = justdomain(rooturl)

def sortByValue(d):
    """ Returns the keys of dictionary d sorted by their values """
    items=d.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort(); backitems.reverse()
    return [ backitems[i][1] for i in range(0,len(backitems))]
    
def tailLines(filename,linesback):
	"""python tail - modified from recipe at 
		http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/157035
		returns list of [linesback] lines from end of [filename]"""
	avgcharsperline=150
	
	file = open(filename,'r')
	while 1:
		try: file.seek(-1 * avgcharsperline * linesback,2)
		except IOError: file.seek(0) 
		if file.tell() == 0: atstart=1 
		else: atstart=0
		lines=file.read().split("\n")
		if (len(lines) > (linesback+1)) or atstart: break
		#The lines are bigger than we thought
		avgcharsperline=avgcharsperline * 1.3 #Inc avg for retry
	file.close()
	
	if len(lines) > linesback: start=len(lines)-linesback -1
	else: start=0
	return lines[start:len(lines)-1]

def timeSinceApacheDate(apacheDate):
	then = time.strptime(apacheDate,'%d/%b/%Y:%H:%M:%S')
	then = time.mktime(then)
	now = time.mktime(time.localtime())
	minutesSince = (now-then) / 60
	hours, minutes = divmod(minutesSince,60)
	return int(hours), int(minutes)

def getDNS(ip):
	# get the domain name, if we've seen it before
	try:
		db = dbm.open(database, "c")
		if db.has_key(ip): addr = db[ip]
		else: addr = ip
		db.close()	
	except: addr = ip
	return addr

def getLogLines(logfile):
	try: logLines = tailLines(logfile,lastlines)
	except: # or try system's tail
		logLines = os.popen('/usr/bin/tail -n ' 
		+ str(lastlines) + ' ' + logfile).readlines()
	if len(logLines) == 0: # can't handle popen exceptions properly
		raise Exception ('No lines found')
	return logLines
	
loglines = getLogLines(logfile)

def getOverview():

	t0 = time.time()
	overview = {'cgiloc':cgiloc}
	hits = {}
	pagecount = 0
	overview["totalhits"] = len(loglines)
	referrers = []
	queries = {}
	timeoffirsthit = loglines[0].split(' ')[3].replace('[','')
	
	for line in loglines:
		resource = line.split(' ')[6]
		if ispage(resource) and not ignorelines(line):
			pagecount = pagecount + 1
			hits[resource] = hits.get(resource,0) + 1
			lastres = resource
			line = line.replace('\\"','&quot;') # some agents include escaped quotes
			referrer = line.split('"')[-4]
			if len(referrer) > 1 and referrer.find(thisdomain) == -1:
				# count queries
				querydict = cgi.parse_qs(referrer.split("?")[-1])
				if referrer.count(".yahoo."):
					q = querydict.get("p")
				else: q = querydict.get("q")
				if q: 
					q = q[0].lower()
					queries[q] = queries.get(q,0) + 1
				referrers.append([referrer, q])
				
	t1 = time.time()
	overview["timing"] = int((t1 - t0) * 1000)
	overview["logfile"] = logfile
	overview["timeoffirsthit"] = timeoffirsthit	
	overview["hits"] = hits
	overview["lastrequest"] = lastres
	overview["pagecount"] = pagecount
	overview["referrers"] = referrers
	overview["queries"] = queries
	hourssince, minutessince = timeSinceApacheDate(timeoffirsthit)
	pagehitsperhour = pagecount / (hourssince + ( float(minutessince) / 60 ))
	overview["hourssince"], overview["minutessince"] = hourssince, minutessince
	overview["pagehitsperhour"] = int(round(pagehitsperhour))
	
	return overview
	
def displayOverviewHTML(overview):
	print """
		<p class = "section"><strong>Summary</strong><br />
		First hit counted %(hourssince)s hours, %(minutessince)s minutes ago<br />
		Total hits: %(totalhits)s<br />
		Page hits: %(pagecount)s (%(pagehitsperhour)s per hour)<br />
		Last page request: %(lastrequest)s <a href = "%(cgiloc)s?url=%(lastrequest)s">details</a><br />
		Processing time: %(timing)s ms</p>""" % overview

	print """<p class = "section"><strong>Recent popular pages (%s or more requests)</strong><br />""" % minresults

	hits = overview["hits"]
	for res in sortByValue(hits):
		score = hits[res]
		if score >= minresults:
			print """%s: 
				<a href = "%s?url=%s">%s</a>
				<br />""" % (res, overview["cgiloc"], urllib.quote(res), score)
	
	print  """</p><p class = "section"><strong>%s recent referrers</strong><br />""" % recentreferrers
	
	referrers = overview["referrers"]
	referrers.reverse()
	for referrer, query in referrers[0:recentreferrers]:
		referrer = referrer.replace("&","&amp;")
		print """<a href = "%s" title = "%s" rel = "nofollow">%s</a>""" % (referrer, referrer, justdomain(referrer))
		if query: print "<i> - %s</i>" % query
		print "<br />"
	print "</p>"
	
	print  """<p class = "section"><strong>%s recent popular search terms</strong><br />""" % recentsearches
	
	queries = overview["queries"]
	for query in sortByValue(queries)[0:recentsearches]:
		query_score = queries[query]
		quoted_query = query.replace('"','%22')
		print """<a href = "http://www.google.com/search?q=%(quoted_query)s">%(query)s</a>: 
			%(query_score)s<br />""" % vars()
	print "</p>"

def urldetails(url, cgiloc):

	print """<p class = "section" id = "urldetails">Requests for <b>%s</b><br /><br />""" % url
	counter = 1
	for line in loglines:
		resource = line.split(' ')[6]
		if resource == url and not ignorelines(line):
			time = line.split(' ')[3].replace('[','')
			if time.startswith(apachetoday): time = time.replace(apachetoday +':','today, ')
			ip = line.split(' ')[0]
			addr = getDNS(ip)
			print """%(counter)s: %(time)s: <a href = "%(cgiloc)s?ip=%(ip)s">%(addr)s</a>
			<br />""" % vars()
			counter = counter + 1
	print "</p>"
			
def ipdetails(ip, cgiloc):

	import socket
	try: addr = socket.gethostbyaddr(ip)[0]
	except: addr = 'unknown host'
	if addr != 'unknown host': # add successful lookups to the DNS cache
		try:
			db = dbm.open(database, "c")
			db[ip] = addr
			db.close()
		except: pass # fail silently - lots of things could have gone wrong...
	print """<p class = "section">Visit details for <b>%s</b><br /><b>hostname:</b> %s<br />""" % (ip, addr)
	counter = 1; pagecounter = 1
	for line in loglines:
		address = line.split(' ')[0]
		if address == ip:
			time = line.split(' ')[3].replace('[','')
			if time.startswith(apachetoday): time = time.replace(apachetoday +':','today, ')
			resource = line.split(' ')[6]
			if counter == 1:
				referrer = line.split('"')[-4]
				user_agent = line.split('"')[-2]
				if len(user_agent) > 50: user_agent = user_agent[0:50].strip() + "..."
				if len(referrer) > 1: 
					print """<b>referrer:</b> <a href = "%(referrer)s">%(referrer)s</a><br />""" % vars()
				print """<b>browser:</b> %(user_agent)s<br /><br />""" % vars()
			if ispage(resource):
				quotedresource = urllib.quote(resource)
				print """%(pagecounter)s: <b>%(time)s</b>: %(resource)s [<a href = "%(cgiloc)s?url=%(quotedresource)s">details</a>]
				<br />""" % vars()
				pagecounter += 1
			counter += 1
	print "</p>"	

def header():
	print "Content-type: text/html\n\n"
	print """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
		"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
		<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
		<head>
			<title>peastat</title>
			<link rel="alternate" type="application/atom+xml" title="Atom" href="http://%s%s?atom=true" />""" % (server_name, request_uri)
	print """<meta http-equiv="content-type" content="text/html" />
			<meta http-equiv="content-language" content="en" />
			<style>
				#container {width: 450px; margin: 10px auto 10px auto; 	text-align: left; border: dotted 0px #999}
				body{
					margin: 0px 0px 0px 0px;
					background-color: #F5F5F5;
					text-align: center;
					font-family: 'Lucida Grande', 'Lucida Sans Unicode', Lucida, 'Trebuchet MS', Trebuchet, Verdana, Geneva, Arial, Helvetica, sans-serif;
					#border-color: #CCF; border-width: 6px; border-style: dotted none none none; 
					border-color: white; border-width: 8px; border-style: dotted none none none; 
					font-size: small;
					color: #333;line-height: 150%;
				}
				strong {color:orange}
				a:visited, a:active, a:link {color: #C30; text-decoration: none; border-bottom: dotted 1px #999;}
				a:hover {color: red; text-decoration: none; border-bottom: dotted 1px #999;}
				h4 {font-weight: bold; font-size: 26px; color: #666; margin-bottom: 3px; margin-top:3px}
				h4 a {border-bottom: dotted 0px white !important}
				.section {padding:4px;  border:1px solid #ddd; background-color:#FFF}
				.greysection {
					padding:4px;  border:1px solid #ddd; background-color:#F5F5F5;
					color:grey}
				.greysection a {color: gray}
				.section:hover {border:1px dotted red;}
				#urldetails a:visited {color:#333;}
			</style>
			<script type="text/javascript">
				// simple AJAX library
				// see http://homepage.mac.com/kevinmarks/staticjah.html
				function jah(url,target) {
					// native XMLHttpRequest object
					document.getElementById(target).innerHTML = 'sending...';
					if (window.XMLHttpRequest) {
						req = new XMLHttpRequest();
						req.onreadystatechange = function() {jahDone(target);};
						req.open("GET", url, true);
						req.send(null);
					// IE/Windows ActiveX version
					} else if (window.ActiveXObject) {
						req = new ActiveXObject("Microsoft.XMLHTTP");
						if (req) {
							req.onreadystatechange = function() {jahDone(target);};
							req.open("GET", url, true);
							req.send();
						}
					}
				}    
				function jahDone(target) {
					// only if req is "loaded"
					if (req.readyState == 4) {
						// only if "OK"
						if (req.status == 200) {
							results = req.responseText;
							document.getElementById(target).innerHTML = results;
						} else {
							document.getElementById(target).innerHTML="jah error: " + req.statusText;
						}
					}
				}
			</script>
		</head>
		<body><div id = "container">"""
	
	print """<h4><a href = "%s">peastat</a></h4>""" % (cgiloc)
		
def footer(): print """
	<p class = "greysection">
		peastat %s 
		&copy; <a href = "http://www.throwingbeans.org/">tom dyson</a> 2005 // 
		<a href = "http://www.throwingbeans.org/peastat/">updates, bugs, suggestions</a>
	</p>
	</div></body></html>""" % (__version__)

def atomHeader():
	basehref = server_name + request_uri
	cleanurl = rooturl.replace("http://","")
	timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
	print """Content-type: application/atom+xml\n\n<?xml version='1.0' encoding='UTF-8'?>
		<feed xmlns="http://www.w3.org/2005/Atom">
			<title>peastat for %(cleanurl)s</title>
			<link href="http://%(basehref)s/"/>
			<updated>%(timestamp)s</updated>
			<author><name>peastat</name></author>
			<id>http://%(basehref)s/</id>""" % vars()
					
def atomSummary(overview):
	basehref = server_name + request_uri
	cleanurl = rooturl.replace("http://","")
	timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
	print """<entry>
		<title>Summary for %(cleanurl)s</title>
		<link href='%(basehref)s' />
		<id>http://%(basehref)s</id>
		<updated>%(timestamp)s</updated>
		<content type="xhtml">
      		<div xmlns="http://www.w3.org/1999/xhtml">""" % vars()
			
	displayOverviewHTML(overview)
			
	print """</div></content></entry>"""
			
def atomFooter():
	print "</feed>"

if __name__ == "__main__":
	if atom:
		atomHeader()
		overview = getOverview()
		atomSummary(overview)
		atomFooter()
	else:
		header()
		if url: urldetails(url, cgiloc)
		elif ip: ipdetails(ip, cgiloc)
		else: 
			overview = getOverview()
			displayOverviewHTML(overview)
		footer()
