# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
import re
####################################################################################################

VIDEO_PREFIX = "/video/ubuweb"
MUSIC_PREFIX = "/music/ubuweb"

RSS_FEED = 'http://interglacial.com/rss/ubuweb.rss'
BASE_ADDRESS = 'http://www.ubuweb.com'
FILM_PAGE = 'http://www.ubuweb.com/film'
AUDIO_PAGE = 'http://www.ubuweb.com/sound'
RADIO_URL = 'http://ubustream.wfmu.org:80/'

NAME = L('Title')

ART           = 'art-default.jpg'
ICON          = 'icon-default.png'
RADIO         = 'radio.png'
RSS           = 'rss.png'
SEARCH        = 'search.png'

####################################################################################################

def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

    Plugin.AddPrefixHandler(MUSIC_PREFIX, MusicMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

def VideoMainMenu():
    dir = MediaContainer(viewGroup="List")
    dir.Append(Function(DirectoryItem(VideoRSSParsingMenu,"Video from RSS feed",thumb=R(RSS),art=R(ART))))
    dir.Append(Function(DirectoryItem(VideoByAuthorMenu,"by Author",thumb=R(ICON),art=R(ART))))
    dir.Append(Function(DirectoryItem(ExploreAuthor,"Roulette TV",thumb=R(ICON),art=R(ART)),url=FILM_PAGE+'/roulette.html'))
    dir.Append(Function(InputDirectoryItem(SearchResults,"Search...","Search...",thumb=R(SEARCH),art=R(ART))))

    return dir
    
def ExplorePage(sender,url):
    dir = MediaContainer(viewGroup="List")
    pagetoscrape = HTTP.Request(url)
    list = re.findall(r"file=(.*)'\);",pagetoscrape)
    for l in list:
      Log(l)
      dir.Append(VideoItem(l,sender.title2,thumb=R(ICON),art=R(ART)))
    return dir

def VideoRSSParsingMenu(sender):
    dir = MediaContainer(viewGroup="List")
    rssfeed = XML.ElementFromURL(RSS_FEED)
    
    for item in rssfeed.xpath('//item'):
      title = item.find('title').text
      link =  item.find('link').text
      page = HTTP.Request(link)
      if re.findall('(.*).flv',page) != [] :
        #dir.Append(Function(DirectoryItem(ExplorePage,title,thumb=R(ICON),art=R(ART)),url = link))
        try:
          pagetoscrape = HTTP.Request(link)
          list = re.findall(r"file=(.*)'\);",pagetoscrape)
          if list != []:
            for l in list:
              Log(l)
              dir.Append(VideoItem(l,title,thumb=R(ICON),art=R(ART)))
        except:
          pagetoscrape =''
    return dir
    
def ExploreAuthor(sender,url):
    dir = MediaContainer(viewGroup="InfoList")
    rawpage = HTTP.Request(url)
    if (rawpage == None):
      return MessageContainer("404 - Page does not exist","A problem has been detected as this page does not exists or has been removed")
    videos = re.findall('(.*).flv',rawpage)
    if videos != [] :
      for v in re.findall(r"file=(.*)'\);",rawpage):
        title = v[v.rfind('/')+1:v.rfind('.')]
        dir.Append(VideoItem(v,title = title,thumb=R(ICON),art=R(ART)))
    page = XML.ElementFromString(rawpage,isHTML=True)
    for item in page.xpath('//a'):
      link = item.get('href')
      title = item.text
      Log(link)
      if link.startswith('http') == False:
        if (title.startswith('Roulette') == False):
          link = FILM_PAGE + '/' + item.get('href')
          #dir.Append(Function(DirectoryItem(ExplorePage,title,thumb=R(ICON),art=R(ART)),url = link))
          try:
            pagetoscrape = HTTP.Request(link)
            Log(pagetoscrape)
            list = re.findall(r"file=(.*)'\);",pagetoscrape)
            for l in list:
              Log(l)
              dir.Append(VideoItem(l,title,thumb=R(ICON),art=R(ART)))
            list =  re.findall(r'<embed src="(.*).mov',pagetoscrape)
            for l in list:
              Log(l)
              dir.Append(VideoItem(l+'.mov',title,thumb=R(ICON),art=R(ART)))
          except:
            pagetoscrape =''
      else:
        if link.endswith('mov') == True:
          dir.Append(VideoItem(link,title,thumb=R(ICON),art=R(ART)))
    return dir

def VideoByAuthorMenu(sender):
    dir = MediaContainer(viewGroup="InfoList")
    page = XML.ElementFromURL(FILM_PAGE,isHTML=True)
    for item in page.xpath('//table//a'):
      if item.get('href').startswith('http') == False:
        author = item.text
        link = FILM_PAGE + item.get('href')[1:]
        dir.Append(Function(DirectoryItem(ExploreAuthor,title = author,thumb=R(ICON),art=R(ART)),url = link))
    return dir
    
def VideoforRouletteMenu(sender):
    dir = MediaContainer(viewGroup="InfoList")
    page = XML.ElementFromURL(FILM_PAGE+'/roulette.html',isHTML=True)
    for item in page.xpath('//a'):
      href = item.get('href') 
      if href.startswith('roulette') == True:
        author = item.text
        link = FILM_PAGE + "/" + item.get('href')
        dir.Append(Function(DirectoryItem(ExploreAuthor,title = author,thumb=R(ICON),art=R(ART)),url = link))
    return dir

def MusicMainMenu():

    dir = MediaContainer(viewGroup="List")
    dir.Append(Function(DirectoryItem(AudioRSSParsingMenu,"Audio from RSS feed",thumb=R(RSS),art=R(ART))))
    dir.Append(Function(DirectoryItem(AudioByAuthorMenu,"by Author",thumb=R(ICON),art=R(ART))))
    dir.Append(TrackItem(RADIO_URL,"UbuWeb Radio",thumb=R(RADIO),art=R(ART)))
    dir.Append(Function(InputDirectoryItem(SearchResults,"Search...","Search...",thumb=R(SEARCH),art=R(ART))))

    return dir
    
def AudioRSSParsingMenu(sender):
    dir = MediaContainer(viewGroup="List")
    rssfeed = XML.ElementFromURL(RSS_FEED)
    
    for item in rssfeed.xpath('//item'):
      title = item.find('title').text
      link =  item.find('link').text
      page = HTTP.Request(link)
      if re.findall('(.*).mp3',page) != [] :
        dir.Append(Function(DirectoryItem(ExploreAudioPage,title,thumb=R(ICON),art=R(ART)),url = link))
    return dir

def AudioByAuthorMenu(sender):
    dir = MediaContainer(viewGroup="InfoList")
    page = XML.ElementFromURL(AUDIO_PAGE,isHTML=True)
    for item in page.xpath('//table//a'):
      if item.get('href').startswith('http') == False:  
        author = item.text
        link = AUDIO_PAGE + item.get('href')[1:]
        dir.Append(Function(DirectoryItem(ExploreAudioPage,title = author,thumb=R(ICON),art=R(ART)),url = link))
    return dir
    
def ExploreAudioPage(sender,url):
    dir = MediaContainer(viewGroup="List")
    pagetoscrape =XML.ElementFromURL(url,isHTML=True)
    for l in pagetoscrape.xpath('//a'):
      if l.get('href').find("mp3")!=-1:
        dir.Append(TrackItem(l.get('href'),l.text.split('<br>')[0],thumb=R(ICON),art=R(ART)))
    return dir
    
def SearchResults(sender,query=None):
    return MessageContainer(
        "Disabled for now",
        "The search feature on the ubuweb.com website is not currently working. This will be implemented in Plex once ubuweb.com is working normally"
    )
    
  
