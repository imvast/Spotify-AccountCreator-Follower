import os
import httpx
import random
import tasksio
import asyncio
import logging
import itertools
import threading
from httpx_socks import AsyncProxyTransport

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[38;5;147m[\x1b[0m%(asctime)s\x1b[38;5;147m]\x1b[0m %(message)s",
    datefmt="%H:%M:%S"
)

with httpx.Client() as client:
    #r1 = client.get("")
    r2 = client.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt")
    r3 = client.get("https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt")
    with open("proxies.txt", 'wb') as f: f.write(r2.content);f.write(r3.content);f.close()


class Spotify():
    
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain;q=0.2, */*;q=0.1",
            "Qezy": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Accept-Language": "en-TZ;q=1.0", 
            "Accept-Encoding": "gzip;q=1.0, compress;q=0.5", 
            "spotify-app-version": "1.1.52.204.ge43bc405",
            "Referer": "https://www.spotify.com/"
        }
    
        with open("proxies.txt", encoding="utf-8") as f:
            self.proxies = [i.strip() for i in f]
            self.rotating = itertools.cycle(self.proxies)

        with open("usernames.txt", encoding="utf-8") as f:
            self.usernames = [i.strip() for i in f]
            
    async def create_session(self):
        try:
            transport = AsyncProxyTransport.from_url('http://%s' % (next(self.rotating)))
            session = httpx.AsyncClient(headers=self.headers, transport=transport)#proxies={'http://': 'http://%s' % (next(self.rotating))})
            address = await session.get("https://wtfismyip.com/text")
            logging.info("Created Session (\x1b[38;5;147m%s\x1b[0m)" % (address.text.strip("\n")))
            return session
        except:
            return await self.create_session()
    
    
    async def create_account(self, session: httpx.AsyncClient):
        try:
            email = "%s@vastmail.gg" % (os.urandom(5).hex())
            payload = "birth_day=1&birth_month=01&birth_year=1990&collect_personal_info=undefined&creation_flow=&creation_point=https://www.spotify.com/uk/&displayname=%s&email=%s&gender=neutral&iagree=1&key=a1e486e2729f46d6bb368d6b2bcda326&password=D8c7mc82chb4sd@X2Q&password_repeat=D8c7mc82chb4sd@X2Q&platform=www&referrer=&send-email=1&thirdpartyemail=0&fb=0" % (random.choice(self.usernames), email)
            response = await session.post("https://spclient.wg.spotify.com/signup/public/v1/account", data=payload)
            if int(response.status_code) == 320: return print("[!] Proxy Detected.")
            response = response.json()
            
            if response.get("login_token") == None: return await self.create_account(session)
            access_token = response["login_token"]
            logging.info("Created Account (\x1b[38;5;147m%s\x1b[0m)" % (access_token))
            with open("Created.txt", "a") as f:
                f.write(f'{email}:D8c7mc82chb4sd@X2Q\n')
            return access_token
        except:
            return await self.create_account(session)
    
    async def get_token(self, session: httpx.AsyncClient, access_token: str):
        try:
            csrf = await session.get("https://www.spotify.com/uk/signup/?forward_url=https://accounts.spotify.com/en/status&sp_t_counter=1")
            print(csrf.text)
            session.headers["X-CSRF-Token"] = str(csrf.text.split('csrfToken":"')[1].split('"')[0])
            await session.post("https://www.spotify.com/api/signup/authenticate", data="splot=%s" % (access_token))
            response = await session.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player")
            json = response.json()
            if json.get("accessToken") == None: return
            auth_token = json["accessToken"]
            logging.info("Retrieved Access Token (\x1b[38;5;147m%s\x1b[0m)" % (auth_token[:30]))
            return auth_token
        except Exception as e:
            print(e)
            return await self.get_token(session, access_token)
    
    async def follow_user(self, profile_id: str):
        session = await self.create_session()
        access_token = await self.create_account(session)
        auth_token = await self.get_token(session, access_token)
        session.headers = {
            "accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "accept-language": "en",
            "Qezy": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
            "app-platform": "WebPlayer",
            "Referer": "https://open.spotify.com/",
            "spotify-app-version": "1.1.52.204.ge43bc405",
            "authorization": "Bearer {}".format(auth_token),
        }
        response = await session.put("https://api.spotify.com/v1/me/following?type=user&ids=%s" % (profile_id))
        if response.status_code == 204:
            logging.info("Successfully Followed (\x1b[38;5;147m%s\x1b[0m)" % (profile_id))
        else:
            logging.error('[Follow Error] %s ~ %s' % (response.status_code, response.json()))
    
    

    async def task(self):
        while True:
           await self.follow_user("twerk")
            
    async def start(self):
        async with tasksio.TaskPool(workers=1000) as pool: 
            for x in range(1000): await pool.put(self.task())
        
        
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(Spotify().start())