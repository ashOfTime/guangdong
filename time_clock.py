import threading
import muti_superSpider
import time

"""
这是多线程的父进程，负责调用子进程执行，并定时，时间到了无论如何，整个爬虫会被停止
"""

round_time = 600
t1 = threading.Thread(target=muti_superSpider.main)
t1.setDaemon(True)
t1.start()
time.sleep(round_time)#执行600s后，这个程序就会停止
print('restart {}'.format(time.asctime()))