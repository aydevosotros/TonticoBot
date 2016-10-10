import os
import re
import sys
import json
import urllib
import requests

def titleCleaner(title):
    return title.decode("utf-8")

def getBest(results, query):
    better = 0
    selected = None

    for result in results:
        confidence = 0
        for token in query.split(" "):
            confidence += 1 if token in result["title"] else 0
        confidence += int(result["weight"])

        if "remix" not in query or "Remix" not in query:
            if "original" in result["title"] or "Original" in result["title"]:
                confidence += 100

        if confidence > better:
            selected = result
            better = confidence

    selected["title"] = selected["title"].encode("utf-8")
    return selected

def searchInVK(query):
    print "Searching in VK"
    encoded = urllib.unquote(query).decode("utf-8")
    url = "http://www.vkdownload.net/vk.php?query="+encoded

    response = requests.get(url)

    urls = re.findall('downSong"><a href="([^\"]*)', response.content)
    names = re.findall('nameFlux"><a[^>]*>([^<]*)', response.content)
    artists = re.findall('artistFlux">([^<]*)', response.content)
    durations = re.findall('timeFlux">([^<]*)', response.content)

    results = []

    for i in range(len(urls)):
        result = {
            "title": titleCleaner(names[i]+" - "+artists[i]),
            "weight": int(durations[i].split(":")[0])*60+int(durations[i].split(":")[1]),
            "url": "http://www.vkdownload.net"+urls[i]
        }
        results.append(result)

    selected = None if not results else getBest(results, query)

    if selected:
        selected["from"] = "vk"

    return selected

def searchInZS(query):
    print "Searching in ZS"
    encoded = urllib.unquote(query).decode("utf-8")
    url = "https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=10&hl=en&prettyPrint=false&source=gcsc&gss=.com&sig=8bdfc79787aa2b2b1ac464140255872c&cx=017403626561776750866:zdfboy6x73w&q="+encoded+"&sort=&googlehost=www.google.com&oq="+encoded+"&gs_l=partner.12...3533.6579.0.12435.16.15.1.0.0.0.85.879.15.15.0.gsnos%2Cn%3D13...0.4930j4551364j17j1..1ac.1.25.partner..13.3.193.h57p1x_dKPM&callback=google.search.Search.apiary11170&nocache=1472198719337"

    response = requests.get(url)
    jsonObject = response.text.split("\n")[1]
    jsonObject = re.search("^[^\(]*\((.*)\);$",jsonObject).group(1)

    content = json.loads(jsonObject)
    results = []

    for r in content["results"]:
        weight = re.search("Size: ([^ ]*) MB", r["contentNoFormatting"])
        weight = weight.group(1) if weight else "0.0"
        weight = int(weight.split(".")[0])*1024+int(weight.split(".")[1])

        result = {
            "title": titleCleaner(r["title"]),
            "url": r["url"],
            "weight": weight,
        }
        results.append(result)

    selected = None if not results else getBest(results, query)

    if selected:
        #driver = webdriver.PhantomJS()
        #driver.get(selected["url"])
        #selected["url"] = driver.find_element_by_css_selector("#dlbutton").get_attribute("href"),
        selected["from"] = "zs"

    return selected

def launchSearch(query):

    result = searchInVK(query)

    if not result:
        result = searchInZS(query)
    print result
    return result

if __name__ == "__main__":
    launchSearch(sys.argv[1])
