import config
import os
import requests
from bs4 import BeautifulSoup as bs
import json

class worker:
    def __init__(self, username, password):
        # Login POST data
        self.LPData = {
            'f': 'search',
            'u':username, 
            'p':password,
            'pc':'false',
            '__CALLBACKID':'CT_Header$ccHeaderLogin',
            '__CALLBACKPARAM':'',
            '__EVENTTARGET':'',
            '__EVENTARGUMENT':''
            }
        # AJAX Transit Info POST data
        self.TIPData = {
            "s":1,
            "IncludePassSupportsTal":"true"
        }
        self.tkn = '' #TOKEN CHANGES WHEN GETTING CARD
        self.session = requests.Session()
        # 200 OK 
        # 302 FOUND
        # 500 INTERNAL SERVER ERROR
        r = self.session.get('https://www.ventrachicago.com/')
        soup = bs(r.text, 'html.parser')
        token = soup.find(id="hdnRequestVerificationToken")
        tkn = token['value']
        # 0 = session, 1 = token
        _HEAD = self.makeHeader(
            'https://www.ventrachicago.com/', 
            self.tkn,
            'application/x-www-form-urlencoded; charset=UTF-8',
            'none'
            )
        p = self.session.post('https://www.ventrachicago.com/', data = self.LPData, headers = _HEAD, cookies = self.session.cookies)
        #print("[%s] POST /" % p.status_code)
        r = self.session.get('https://www.ventrachicago.com/account/')
        #print("[%s] Get /account/" % p.status_code)
        print('[ Getting All CardInfo ]')
        print('')
    
    # Create header per request
    def makeHeader(self, referer, token, CT, CL):
        if CL != 'none':
            _HEAD = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'AcceptLanguage': 'en-US,en;q=0.9,en-GB;q=0.8',
                'Connection': 'keep-alive',
                'Content-Length': CL,
                'Content-Type': CT,
                #'Cookie': NOT NEEDED bc added throguh req Cookie param
                'DNT': '1',
                'Host': 'www.ventrachicago.com',
                'Origin': 'https://www.ventrachicago.com',
                'Referer': referer,
                'RequestVerificationToken': token,
                'sec-ch-ua': '\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"',
                'sec-ch-ua-mobile': '0',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
        else:
            _HEAD = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'AcceptLanguage': 'en-US,en;q=0.9,en-GB;q=0.8',
                'Connection': 'keep-alive',
                'Content-Type': CT,
                #'Cookie': NOT NEEDED bc added throguh req Cookie param
                'DNT': '1',
                'Host': 'www.ventrachicago.com',
                'Origin': 'https://www.ventrachicago.com',
                'Referer': referer,
                'RequestVerificationToken': token,
                'sec-ch-ua': '\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"',
                'sec-ch-ua-mobile': '0',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
        return _HEAD
        
    def getAllCardInfo(self):
        ses = self.session
        r = ses.get('https://www.ventrachicago.com/account/')
        soup = bs(r.text, 'html.parser')
        _TKN = soup.find(id = 'hdnRequestVerificationToken')['value'] #TOKEN CHANGES
        _VSG = soup.find(id = '__VIEWSTATEGENERATOR')['value']
        _EV = soup.find(id = '__EVENTVALIDATION')['value']
        _VS = soup.find(id = '__VIEWSTATE')['value'] 
        _HEAD = self.makeHeader(
            'https://www.ventrachicago.com/account/',
            _TKN,
            'application/json',
            '37'
        )
        cardList = soup.find(id="optionList").find_all("li")
        for items in cardList:
            cardID = items.find('a')['href']
            cardID = cardID[cardID.index('__doPostBack(\'')+len('__doPostBack(\''):cardID.index('\',\'\')')]
            cardData = {
                '__EVENTTARGET':cardID,
                '__EVENTARGUMENT': '',
                'hdnRequestVerificationToken': self.tkn,
                'hdnSubDirectory': '', 
                'CT_Main_2$drpPaymentExpireMonth': 'Month',
                'CT_Main_2$drpPaymentExpireYear': 'Year',
                'CT_Main_2$drpBillingState': 'IL',
                '__VIEWSTATEGENERATOR': _VSG,
                '__EVENTVALIDATION': _EV,
                '__VIEWSTATE': _VS   
            }
            # post to select card
            p = ses.post('https://www.ventrachicago.com/account/', data = cardData, cookies=ses.cookies, headers=ses.headers)
            # ajax -> transit INFO ex {'d': {'success': True, 'result': {'passes': [], 'balance': '$9.75', 'pretaxBalance': '$0.00', 'totalBalanceAndPretaxBalance': '$9.75', 'autoLoadAmount': 0, 'riderClassId': 1, 'riderClassDescription': 'Full Fare', 'usageTypeId': 'OpenTransitRegular'}}}
            ajax = ses.post('https://www.ventrachicago.com/ajax/NAM.asmx/GetTransitInfo', data=json.dumps(self.TIPData), cookies=ses.cookies, headers=_HEAD)
            #print("[%s] POST /account/%s" % (p.status_code, cardID))
            res = ses.get('https://www.ventrachicago.com/account/')
            #print("[%s] GET /account/%s" % (r.status_code, cardID))
            # Parses all information AJAX and HTML
            info = json.loads(ajax.content)
            infoSoup = bs(res.text, 'html.parser')
            accInfo = infoSoup.find('div', class_='account-data')
            cardBal = info['d']['result']['balance']
            cardRate = info['d']['result']['riderClassDescription']
            cardNumRaw = accInfo.find_all('span')[1].text
            cardNum = cardNumRaw[cardNumRaw.index('(...')+len('(...'):cardNumRaw.index(')')]
            cardTID = accInfo.find_all('div', class_='accnt-rate')[1].find_all('span')[0].text
            cardStatus = accInfo.find_all('div', class_='accnt-rate')[1].find_all('span')[1].text
            # Outputs all information
            print("[%s] %s" %(cardNum, cardBal))
            #cardRate = accInfo.find_all('div', class_='accnt-rate')[0].text NO USE BC OF AJAX
            print("Rate: %s" %cardRate)
            print(cardTID)
            print(cardStatus)
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            """
            print(res.text)
            f = open("reader.html", "w")
            f.write(res.text)
            f.close()
            """
        self.session = ses

def main(): 
    wk = worker(config.username, config.password)
    wk.getAllCardInfo()

if __name__ == "__main__":
    main()
