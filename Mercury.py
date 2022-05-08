import json
from time import sleep
import requests


class Mercury:
    def __init__(self, password: str) -> None:
        self.stok = self.login(password)
        self.opUrl = f'http://melogin.cn/stok={self.stok}/ds'

    def login(self, psw: str) -> str:
        """Login by password
        ---
        login and return stok(or token)

        :param : `psw`: password for router admin

        :return : `str`: stok for furthur authentication
        """

        login_url = 'http://melogin.cn/'
        data = {"method": "do", "login": {"password": meLoginEnc(psw)}}
        r = requests.post(login_url, data=json.dumps(data)).json()
        if r['error_code'] == 0:
            print(r['stok'])
            return r['stok']
        else:
            raise Exception('Login Failed')

    def devicesList(self) -> list:
        """Get connected devices
        ---
        get all devices connecting to host wifi
        Not guest wifi

        :param : `None`

        :return : `list`: devices list
        """

        url = self.opUrl
        data = {"hyfi": {"table": ["connected_ext"]}, "hosts_info": {
            "table": "host_info", "name": "cap_host_num"}, "method": "get"}
        r = requests.post(url, data=json.dumps(data)).json()
        if r['error_code'] == 0:
            return r['hosts_info']['host_info']
        else:
            print(r)
            raise Exception('Query Failed: devicesList')

    def getHostnameByMac(self, macAddr: str) -> str:
        """getHostnameByMac
        ---
        return hostname of a device by mac address

        :param : `macAddr`: mac address of that devices

        :return : `str`: hostname of that device, '' for not found
        """

        macAddr = macAddr.lower()
        for i, e in enumerate(self.devicesList()):
            device = e['host_info_' + str(i)]
            if device['mac'] == macAddr:
                hostname = device['hostname']
                return hostname

        return ''

    def blockByMac(self, macAddr: str, is_block: int = 1) -> bool:
        """blockByMac
        ---
        Block a device by mac address

        :param : `macAddr`: mac address of that devices
                    `is_block`: block or not, default to 1

        :return : `bool`: status of block operation
        """

        url = self.opUrl
        macAddr = macAddr.lower()
        # find hostname
        hostname = self.getHostnameByMac(macAddr)
        if hostname == '':
            # return False if device not found
            return False

        data = {"hosts_info":
                {"set_block_flag":
                 {"mac": macAddr,
                  "is_blocked": is_block,
                  "name": hostname,
                  "down_limit": "0",
                  "up_limit": "0"}}, "method": "do"}

        r = requests.post(url, data=json.dumps(data)).json()
        return not r['error_code']

    def unBlockByMac(self, macAddr: str) -> bool:
        self.blockByMac(macAddr, 0)

    def limitByMac(self, macAddr: str, down_limit: int, up_limit: int) -> bool:
        """limitByMac
        ---
        limit a device's speed by mac address

        :param : `macAddr`: mac address of that devices
                    `down_limit`: download speed limit
                    `up_limit`: upload speed limit

        :return : `bool`: status of limit operation
        """

        url = self.opUrl
        macAddr = macAddr.lower()
        # find hostname
        hostname = self.getHostnameByMac(macAddr)
        if hostname == '':
            # return False if device not found
            return False

        data = {"hosts_info":
                {"set_flux_limit":
                 {"mac": macAddr,
                  "down_limit": down_limit,
                  "up_limit": up_limit,
                  "name": hostname,
                  "is_blocked": "0"}
                 }, "method": "do"}

        r = requests.post(url, data=json.dumps(data)).json()
        return not r['error_code']

    def unLimitByMac(self, macAddr: str) -> bool:
        self.limitByMac(macAddr, 0, 0)

    def trickByMac(self, macAddr: str, loop_times: bool = 3) -> bool:
        """trickByMac
        ---
        trick a device by mac address, trick it by limit it's speed and unlimit repeatedly.

        :param : `macAddr`: mac address of that devices
                    `loop_times`: True to trick in infinite loop, default to 3, 0 forever

        :return : `bool`: status of trick operation
        """

        if(loop_times == 0):
            while True:
                self.limitByMac(macAddr, 200, 20)
                sleep(0.3)
                self.unLimitByMac(macAddr)
                print('tricking...')
        else:
            for i in range(loop_times):
                self.limitByMac(macAddr, 200, 20)
                sleep(0.3)
                self.unLimitByMac(macAddr)
                print('times:', i+1)


def securityEncode(a: str, b: str, d: str) -> str:
    c = ''
    g = len(a)
    h = len(b)
    m = len(d)
    # e is max (g,h)
    e = (h, g)[g > h]
    for k in range(e):
        r = p = 187
        if k >= g:
            r = ord(b[k])
        elif k >= h:
            p = ord(a[k])
        else:
            p = ord(a[k])
            r = ord(b[k])
        c += d[(p ^ r) % m]
    return c


def meLoginEnc(plaintext: str) -> str:
    a = 'RDpbLfCPsJZ7fiv'
    d = 'yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW'
    return securityEncode(a, plaintext, d)
