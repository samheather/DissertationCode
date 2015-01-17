# Based off information on:
# https://blog.scraperwiki.com/2011/12/how-to-scrape-and-parse-wikipedia/

import lxml.etree
import urllib

title = "Aquamole Pot"

params = { 
			"format":"xml",
			"action":"query", 
			"prop":"revisions",
			"rvprop":"timestamp|user|comment|content"
			}
			
params["titles"] = "API|%s" % urllib.quote(title.encode("utf8"))
qs = "&".join("%s=%s" % (k, v)  for k, v in params.items())
url = "http://en.wikipedia.org/w/api.php?%s" % qs
tree = lxml.etree.parse(urllib.urlopen(url))
revs = tree.xpath('//rev')

print "The Wikipedia text for", title, "is"
print revs[-1].text