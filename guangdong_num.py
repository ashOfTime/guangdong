import requests
import json
import pymysql
from math import ceil
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

class GuangDong(object):
  def __init__(self): 
    self.session = requests.Session()

  def login(self, username, password):
    """
    用于登陆 
    username:z账号
    passwprd:密码

    """
    self.username = username
    self.password = password

    cookies = {
    'login_username': username,
    'JSESSIONID': 'DF0309BF3728997682B41B6AF05C6E9B',
    }

    data = [
      ('j_username', self.username),
      ('j_password', self.password),
      ]

    headers = {
    'Origin': 'http://www.cnipsun.com',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'http://www.cnipsun.com/patent/searchResult.do',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    }

    loginurl = 'http://www.cnipsun.com/j_spring_security_check'
    response = self.session.post(loginurl, headers=headers, data=data, cookies=cookies)

    if '我的下载' in response.text:
      print('login suss')
      print(self.session.cookies)
      cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
      cookies_json = json.dumps(cookies_dict)
      with open('login_json', 'w') as f:
        f.write(cookies_json)

    else:
      print('login fail')

  def get_allNum(self, year_start, year_end ):
    """
    根据日期范围，返回该范围内共有多少专利记录
    year_start:日期开始
    year_end :日期结束
    """

    headers = {
        'Origin': 'http://www.cnipsun.com',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'http://www.cnipsun.com/patent/searchResult.do',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }

    data = [
      ('searchExpression', '  \u516C\u5F00\uFF08\u516C\u544A\uFF09\u65E5=\'{}\' to \'{}\''.format(year_start, year_end) ),
      ('searchExpressionDesc', '  \u516C\u5F00\u65E5=\'{}\' to \'{}\''.format(year_start, year_end) ),
      ('sortMethod', ''),
      ('ascOrder', ''),
      ('cnSources', 'fmzl_ft,syxx_ft,wgzl_ab,fmsq_ft'),
      ('woSources', 'twpatent,hkpatent'),
      ('field1', '0'),
      ('field1Val', ''),
      ('field2', '0'),
      ('field2Val', ''),
      ('field3', '0'),
      ('field3Val', ''),
      ('pageSize', '40'),
    ]

    rsp_all_num = self.session.post('http://www.cnipsun.com/patent/search.do', headers=headers, data=data).content
    rsp_all_num = json.loads(rsp_all_num)

    all_num = rsp_all_num['total']
    return all_num

  def get_detai(self, year_start, year_end, pageNo):
    headers = {
        'Origin': 'http://www.cnipsun.com',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'http://www.cnipsun.com/patent/searchResult.do',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }

    data = [
      ('searchExpression', '  \u516C\u5F00\uFF08\u516C\u544A\uFF09\u65E5=\'{}\' to \'{}\''.format(year_start, year_end) ),
      ('searchExpressionDesc', '  \u516C\u5F00\u65E5=\'{}\' to \'{}\''.format(year_start, year_end) ),
      ('sortMethod', ''),
      ('ascOrder', ''),
      ('cnSources', 'fmzl_ft,syxx_ft,wgzl_ab,fmsq_ft'),
      ('woSources', 'twpatent,hkpatent'),
      ('field1', '0'),
      ('field1Val', ''),
      ('field2', '0'),
      ('field2Val', ''),
      ('field3', '0'),
      ('field3Val', ''),
      ('pageNo', str(pageNo)),
      ('pageSize', '40'),
            ]

    response = self.session.post('http://www.cnipsun.com/patent/search.do', headers=headers,  data=data)
    return response.content

def create_datetime_db(datetime, allNum):
  db = pymysql.connect('localhost', 'root', 'password', 'guangdong')
  cur = db.cursor()
  allPage = allNum
  sql_insert = 'insert into content  values (%s,%s,%s,%s)'
  allPage = ceil(allNum/40)

  for page in range(2,100):
    print(page+1)
    cur.execute(sql_insert, [None, datetime, page+1, 'F'])
    db.commit()
    

  cur.close()
  db.close()

def get_content():
    
  guangdong = GuangDong()
  guangdong.login('441045808@qq.com', 'Woaixuexi@123')

  db = pymysql.connect('localhost', 'root', 'password', 'guangdong')
  cursor = db.cursor()
  sql_select = "select * from content where content = 'F' limit 0,1"
  sql_update = "update content set content = %s where id =%s"
  cursor.execute(sql_select)
  t = cursor.fetchone()
  content = guangdong.get_detai(t[1].split('#')[0], t[1].split('#')[1], t[-2])
  cursor.execute(sql_update,(content,t[0]))
  db.commit()

  cursor.close()
  db.close()








def login(username,password):
  cookies = {
    'login_username': username,
    'JSESSIONID': 'DF0309BF3728997682B41B6AF05C6E9B',
    }

  data = [
    ('j_username', username),
    ('j_password', password),
    ]

  headers = {
  'Origin': 'http://www.cnipsun.com',
  'Accept-Encoding': 'gzip, deflate',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'Referer': 'http://www.cnipsun.com/patent/searchResult.do',
  'X-Requested-With': 'XMLHttpRequest',
  'Connection': 'keep-alive',
  }

  loginurl = 'http://www.cnipsun.com/j_spring_security_check'
  response = requests.session.post(loginurl, headers=headers, data=data, cookies=cookies)

  if '我的下载' in response.text:
    print('login suss')
    print(self.session.cookies)
    cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
    cookies_json = json.dumps(cookies_dict)
    with open('login_json', 'w') as f:
      f.write(cookies_json)

  else:
    print('login fail')

def get_datetime(num=8):
  db = pymysql.connect('localhost', 'root', 'password', 'guangdong')
  cursor = db.cursor()
  sql_select = "select * from content where content = 'F' limit 0,{}".format(num)
  cursor.execute(sql_select)
  t = cursor.fetchall()

  return t

def get_detail(post_data):
  id = post_data[0]
  year_start = post_data[1].split('#')[0]
  year_end = post_data[1].split('#')[1]
  pageNo = post_data[2]
  cookies = post_data[-1]
  headers = {
        'Origin': 'http://www.cnipsun.com',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'http://www.cnipsun.com/patent/searchResult.do',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }

  data = [
    ('searchExpression', '  \u516C\u5F00\uFF08\u516C\u544A\uFF09\u65E5=\'{}\' to \'{}\''.format(year_start, year_end) ),
    ('searchExpressionDesc', '  \u516C\u5F00\u65E5=\'{}\' to \'{}\''.format(year_start, year_end) ),
    ('sortMethod', ''),
    ('ascOrder', ''),
    ('cnSources', 'fmzl_ft,syxx_ft,wgzl_ab,fmsq_ft'),
    ('woSources', 'twpatent,hkpatent'),
    ('field1', '0'),
    ('field1Val', ''),
    ('field2', '0'),
    ('field2Val', ''),
    ('field3', '0'),
    ('field3Val', ''),
    ('pageNo', str(pageNo)),
    ('pageSize', '40'),
          ]

  response = requests.post('http://www.cnipsun.com/patent/search.do', headers=headers,  data=data, cookies=cookies)
  return response.content,id

def write_db(result):
  db = pymysql.connect('localhost', 'root', 'password', 'guangdong')
  cursor = db.cursor()
  id = result[-1]
  content = result[0]
  sql_update = "update content set content = %s where id =%s"
  cursor.execute(sql_update,(content,id))
  db.commit()

def control():
  """
  中央控制
  """
  threads = 8#线程数目，以及一次从数据库里读取多少个任务数

  #读取cookies
  with open('login_json', 'r') as f:
    cookies = f.read()
    cookies = json.loads(cookies)

  #把cookies和post_data拼接起来，发个spider
  task = list(get_datetime(threads))
  task = [list(i)  for i in task]
  for i in task:
    i.append(cookies)

  #多线程，爬
  pool = ThreadPool(threads)
  result = pool.map(get_detail, task)

  #用于判断返回的值是否正常，正常则写入数据库，否则做相应的更新
  #status=0 正常
  #status=2 登陆过期
  status = 0
  for r in result:
    print(r[-1])
    #如果 请输注册邮箱 在返回的数据中，说明登陆过期
    if '请输入注册邮箱' in r[0].decode('utf-8'):
      print('login outof time')
      status = 2
    else:
      write_db(r)
  if status == 2:
    print('try login again')
    login('441045808@qq.com', 'Woaixuexi@123')

  

control()

    
