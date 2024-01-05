import json
import re
import requests
from common.agent import Agent
from urllib.parse import urlparse

class SimilarwebAgent(Agent):
    def __init__(self, web_url, cookies, output, log_fd):
        Agent.__init__(self, output, log_fd)
        self._web_url = web_url
        self._cookies = cookies

    # [{'Key': '2023-09-01', 'Value': 1493.12}, {'Key': '2023-10-01', 'Value': 1698.80}, {'Key': '2023-11-01', 'Value': 1682.66}]
    def record_visits_info(self, line, vinfo):
        vv = [line]
        for item in vinfo:
            ivalue = item['Value']
            if ivalue:
                vv.append(str(int(ivalue)))
            else:
                vv.append(str(int(0)))
        msg = "\t".join(vv)
        if self._output:
            with open(self._output, "a") as file:
                file.write(msg + "\n")
        else:
            print(msg)

    def requests_get_with_params(self, url, params):
        headers = {
            "Referer": self._web_url,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            #"X-Requested-With": "XMLHttpRequest",
        }
        jd = ""
        i = 0
        while i < 2:
            try:
                r = requests.get(url, params=params, headers=headers, cookies=self._cookies, timeout=5)
                jd = json.loads(r.text)
            except Exception as e:
                i += 1
            else:
                break
        return jd

    #url like: https://www.xuexiaigc.com
    def get_url_visits_graph(self, url):
        parts = urlparse(url)
        domain = parts.netloc
        fdomain = domain.replace("www.", "")
        params = {
            "country": "999",
            "from": "2023|09|01",
            "to": "2023|11|30",
            "timeGranularity": "Monthly",
            "ShouldGetVerifiedData": "false",
            "includeSubDomains": "true",
            "isWindow": "false",
            "keys": fdomain,
            "webSource": "Total"
        }
        jd = self.requests_get_with_params(self._web_url + '/widgetApi/WebsiteOverview/EngagementVisits/Graph', params)
        #print(jd)
        if ('Data' in jd) == False:
            return None
        vdata = jd['Data']
        if (fdomain in vdata) == False:
            return None
        vvalue = vdata[fdomain]['Total'][0]
        return vvalue

    def get_url_overview_header(self, url):
        params = {
            "keys": url,
            "mainDomainOnly": "false",
            "includeCrossData": "true"
        }
        jd = self.requests_get_with_params(self._web_url + '/api/WebsiteOverview/getheader', params)
        #print(jd)
        return jd

    def process_one_record(self, record):
        print("processing record: ", record)
        tlist = re.split('\t', record)
        url = tlist[0]

        vinfo = self.get_url_visits_graph(url)
        if vinfo == None:
            return False
        #print(vinfo)
        self.record_visits_info(record, vinfo)
        return True
 
