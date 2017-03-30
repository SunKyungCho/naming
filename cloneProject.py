#-*- coding: utf-8 -*-
import requests
import json
import os

def getUrl():
    ##https://developer.github.com/v3/search/
    # 위 url을 참조하여 API를 호출해 Java star가 제일 많은 순으로 url을 가지고 온다.
    url = []
    URL = 'https://api.github.com/search/repositories'
    data = {
        "q":"stars:>1 language:Java",
        "sort":"stars",
        "order":"desc",
        "type":"repositories",
        "page":1,
        "per_page":10
    }
    response = requests.get(URL, data)
    response.status_code
    data = json.loads(response.text)
    items = data['items']
    for item in items:
        url.append(item['html_url'])

    return url

def main():

    path =  os.path.dirname(os.path.realpath(__file__))
    resource_path = path + "/resource"
    urls = getUrl()


    for url in urls:
        print url
        project_name = url.split("/")[-1]
        command = "git clone " + url +" " + resource_path + "/" +project_name
        print command
        os.system(command)
    print len(urls)


if __name__ == '__main__':
    main()