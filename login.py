import os
import configparser
import requests

class Ipgw_login(object):
    def __init__(self):
        self.stu_ID = ""
        self.stu_password = ""
        self.login_url = 'https://pass.neu.edu.cn/tpass/login?service=http://ipgw.neu.edu.cn/srun_portal_sso?ac_id={}'

    
    def config(self,Fname="config.ini"):
        # 获取当前的路径
        filepath = os.path.split(os.path.realpath(__file__))[0]
        filename = os.path.join(filepath, Fname)
        # print(filename)

        # 获取账号，密码
        conf = configparser.ConfigParser()
        conf.read(filename)

        self.stu_ID = conf.get("info","StudentID")
        self.stu_password = conf.get("info","password")

        # print(self.stu_ID,self.stu_password)


    def login_with_acid(self,ac_id):
        # 访问统一登录获取lt
        session = requests.Session()
        get_pass_page = session.get(self.login_url.format(ac_id))
        if get_pass_page.status_code != 200:
            return False, f'访问pass.neu.edu.cn失败，状态码：{get_pass_page.status_code}'
        # text = ...<input type="hidden" id="lt" name="lt" value="LT-29360-**********-tpass" />\r\n\t\t\t
        text = get_pass_page.text

        # 获取lt (login token)
        target = '<input type="hidden" id="lt" name="lt" value="'
        # half = LT-29360-**********-tpass" />\r\n\t\t\t
        half = text[text.index(target) + len(target):]
        # lt = LT-29360-**********-tpass
        lt = half[:half.index('"')]

        # 获取execution
        target = '<input type="hidden" name="execution" value="'
        half = text[text.index(target) + len(target):]
        execution = half[:half.index('"')]

        # 拼接rsa
        rsa = self.stu_ID + self.stu_password + lt
        ul = len(self.stu_ID)
        pl = len(self.stu_password)

        # 获取用于sso链接，其中含有ticket
        get_sso_href = session.post(self.login_url.format(ac_id),
                                    allow_redirects=False,  # 禁用转跳
                                    data={'rsa': rsa,
                                        'ul': ul,
                                        'pl': pl,
                                        'lt': lt,
                                        'execution': execution,
                                        '_eventId': 'submit'})
        
        text = get_sso_href.text

        # 检测是否账号错误
        if '账号不存在' in text:
            return False, '可能是①账号或密码错误 ③登录流程需要更新'

        # 获取ticket
        target = 'ticket='
        half = text[text.index(target) + len(target):]
        href = half[:half.index('"')]
        sso_login = session.get(f'http://ipgw.neu.edu.cn/v1/srun_portal_sso?ac_id={ac_id}&ticket=' + href)
        if 'success' in sso_login.text:
            return True, None
        else:
            return False, f'sso登录返回{sso_login.text}'


    def login(self):
        """
        登录ipgw，要点：
        ① 以get方式访问https://pass.neu.edu.cn页面，响应中含有lt (login token)
        ② 以post方式访问https://pass.neu.edu.cn页面，提交学号密码lt等参数，响应中含有用于单点登录(sso)的ticket
        ③ 访问http://ipgw.neu.edu.cn/v1/srun_portal_sso?ac_id=xx&ticket=xxx，提交ticket即可上网
        其中使用无线网时ac_id=15，使用有线连接时ac_id=1

        :param student_id: 学号
        :param password: 密码
        :return: (bool,reason) 若第一项为True则登录成功，否则登录失败，此时第二项会说明原因
        """
        wifi_acid = 15 # 无线网登录
        lan_acid = 1 # 有线网登录

        results = {}
        for acid in [wifi_acid, lan_acid]:
            print("acid:",acid)

            result, message = self.login_with_acid(acid)
            if result:
                return True, message
            results[acid] = message
        return False, results

def main():
    _login = Ipgw_login()
    _login.config()
    result, message = _login.login()
    # print(result, message)

if __name__ == '__main__':
    main()