from bs4 import BeautifulSoup
import requests
from requests.utils import quote

def searchInVK(query):
    print("Searching in VK")
    url = "http://www.vkdownload.net/vk.php?query={}".format(quote(query))

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for row in soup.find_all("tr"):
        if len(row.find_all("td", "artistFlux")) > 0:
            try:
                nameRow = row.find_all("td", "nameFlux")[0]
                results.append({
                    "url": "http://www.vkdownload.net" + nameRow.find("a")["href"],
                    "name": nameRow.find("a").text,
                    "artist": row.find_all("td", "artistFlux")[0].text,
                    "duration": row.find_all("td", "timeFlux")[0].text
                })
                print(results[-1])
            except Exception as ex:
                print("Excepción en el parseo de los tr \n{}".format(row))
                print(ex)
                raise ex
    return results
