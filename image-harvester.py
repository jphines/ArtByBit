# Image Harvester
# 
# by Philip Guo
# Copyright 2005 Philip J. Guo
# 
# Cleaned up & Modified by Justin Hines


from sgmllib import SGMLParser
import urllib
from urlparse import urlparse, urljoin
import re
import os


class ImageHarvester(SGMLParser):
    # Perform all initialization here
    def reset(self):
        SGMLParser.reset(self)
        self.pageURLs = []          # Other webpages linked to from this page
        self.pageRExp = re.compile('[.]htm$|[.]html$|[.]shtml$|[/]$|[.]php$', re.IGNORECASE)

        self.windowsFilenameRExp = re.compile('[\/:*?"<>|]')

        self.thisURL = "" # The URL of the page we are parsing
        self.htmlSource = "" # The HTML source of the page we're
                             # parsing

    # This is called by the SGMLParser superclass every time an
    # <a ...> start tag is encountered in the HTML
    def start_a(self, attrs):
        # 'href' attribute values includes both images and links to
        # other webpages.
        href = [v for k, v in attrs if k=='href']

        # Throw all elements of 'href' into pageURLs for now,
        # and then filter them out later in convert_to_absolute_URLs
        for valueStr in href:
            self.pageURLs.append(valueStr)

    # Filters irrelevant non-HTML links out of pageURLs and
    # converts all relative URLs into absolute URLs
    # Pre: pageURLs is properly filled with URLs that can be anything
    # Post: pageURLs is only filled with ABSOLUTE URLs to other pages
    def convert_to_absolute_URLs(self):
        # Could we compact this into a list comprehension?
        updatedPageURLs = []
        for URL in self.pageURLs:

            filename = urlparse(URL)[4]
            # Find the first 'http://' instance and truncate from there:
            ind = filename.find('http://')
            # Ok, it's an absolute link from the redirect string:
            if ind >= 0:
                newURL = filename[ind:]
                tokens = urlparse(newURL)
                if tokens[0].lower() == 'http' and self.pageRExp.search(tokens[2]):
                    updatedPageURLs.append(newURL)
                    
            # Determine whether it's an absolute or relative link
            else:
                tokens = urlparse(URL)
                if self.pageRExp.search(tokens[2]):
                    if (tokens[0].lower() == 'http'):
                        # Absolute link, just deal with it
                        updatedPageURLs.append(URL)
                    else:
                        # Relative link: Let's use urljoin() to generate an
                        # absolute URL:
                        updatedPageURLs.append(urljoin(self.thisURL, URL))

        self.pageURLs = updatedPageURLs


    # Get munged directory name from URL, which is compatible with the
    # local filesystem's constraints on directory names.
    # This basically replaces all illegal characters with '_', which
    # is a quick & dirty solution that works fine.
    def get_munged_dirname_from_URL(self, URL):
        return self.windowsFilenameRExp.sub('_', URL)


    # Save images to a sub-directory named after self.thisURL.  If the
    # directory already exists, then we have already operated on it,
    # so skip it.  This prevents infinite recursion due to cycles.  
    # Returns True if succeeded, False if failed
    def save_images(self):
        # Create a new directory based on the page URL
        dirName = self.get_munged_dirname_from_URL(self.thisURL)

        print 'Begin saving files into directory named ' + dirName
        
        if os.path.isdir(dirName):
            print 'Aborting image saving!'
            print '  (Directory ' + dirName + ' already exists.)'
            return False
        else:
            os.mkdir(dirName)
            os.chdir(dirName)

            print self.thisURL

            # This is where all of the action happens.
            # Use wget to grab all the images off of self.thisURL
            # -A jpg : only retrieve JPG images           
            # -r  : recursive
            # -l1 : only grab images on this page 
            # -L  : only follow relative links to not snag ads or crap
            #       (unused because some sites use rel. links for real photos)
            # --no-parent : don't fetch anything below the parent of this URL,
            #               again to avoid ads and crap
            # -U \"Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.6) Gecko/20050405 Firefox/1.0 (Ubuntu package 1.0.2)\"
            #          : Set the User Agent to pretend to be Ubuntu Firefox
            # --wait=2 : wait between retrieving images and ...
            # --random-wait : randomly adjust wait times to prevent
            #                 from getting kicked
            # -nd : don't create a mess of sub-directories
            # -nv : don't dump as much output to the terminal

            os.system('wget -r -l1 -A jpg -U \"Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.6) Gecko/20050405 Firefox/1.0 (Ubuntu package 1.0.2)\" -nd --wait=2 --random-wait --no-parent -nv ' + self.thisURL)

#            print "Saving:", self.thisURL
            
            os.chdir("..")
            
            print 'Done saving files into directory named ' + dirName
            return True


    # Input: URL which is an HTML file
    # Post: Parses the HTML file, download .jpg images on and linked
    #       from it, and cleans up after itself
    # Returns True if succeeded, false if failed
    def process_URL(self, url):
        self.reset()
        self.thisURL = url

        print "Begin processing " + url

        # It doesn't do anything when a subdirectory with the munged
        # URL directory name exists:
        dirName = self.get_munged_dirname_from_URL(self.thisURL)

        if os.path.isdir(dirName):
            print 'Aborting HTML processing!'
            print '  (Directory ' + dirName + ' already exists.)'
            return False
        else:
            try:
                sock = urllib.urlopen(url)
                self.htmlSource = sock.read()
                self.feed(self.htmlSource)
                sock.close()
                self.convert_to_absolute_URLs()
                self.close()
                print "Done processing " + url
                return self.save_images()
            except IOError:
                print "IOError!  Aborting HTML processing!"
                return False


    # Returns True if url is in the same domain as self.thisURL
    def same_domain(self, url):
        thisURLtokens = urlparse(self.thisURL)
        URLtokens = urlparse(url)
       
        # The second element is the domain,
        return (thisURLtokens[1] == URLtokens[1])


    # should only be to same-domain URLs)
    def process_URL_and_links(self, url):
        if self.process_URL(url):
            map(self.process_URL_and_same_domain_links, self.pageURLs)


    # Process URL and then process the URL of every URL in pageURLs
    # in the same DOMAIN as this URL.
    def process_URL_and_same_domain_links(self, url):
        if self.process_URL(url):
            # work with map or list comprehensions:
            sameDomainURLs = []
            for u in self.pageURLs:
                if self.same_domain(u):
                    sameDomainURLs.append(u)

            map(self.process_URL, sameDomainURLs)


##def recursive_crawl(harvester, URL):
##    # Propagate only if this is a success!
##    if harvester.process_URL(URL):
##        for URL in harvester.pageURLs:
##            print 'Gonna crawl to ' + URL

##        [recursive_crawl(ImageHarvester(), URL) for URL in harvester.pageURLs]


if __name__ == "__main__":
    import sys
    h = ImageHarvester()
    h.process_URL_and_links(sys.argv[1])
