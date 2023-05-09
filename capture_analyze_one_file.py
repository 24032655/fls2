import subprocess
import time
import signal
import datetime
from threading import Thread
import os
import pandas as pd

def handler(signum, frame):
    # 处理ctrl+c信号，结束循环
    global running
    running = False
   
# 注册ctrl+c信号处理函数
signal.signal(signal.SIGINT, handler)




# 创建全局的 DataFrame 对象
df_all = pd.DataFrame(columns=['frame.number', 'http2.streamid', 'ip.src', 'ip.dst'])

def capture_process(duration, port):
    while running:
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        capture_file = 'capture_' + current_time + '.pcap'
        p = subprocess.Popen(['tshark', '-i', 'ens18', '-a', 'duration:' + str(duration), '-f', 'tcp port ' + str(port), '-w', capture_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(duration)


def analyze_process():
    global df_all
    while running:
        files = [f for f in os.listdir() if f.startswith('capture_') and f.endswith('.pcap')]
        for capture_file in files:
            #csv_file = capture_file.replace('.pcap', '.csv')
            p = subprocess.Popen(['tshark', '-r', capture_file, '-T', 'fields', '-E', 'header=y', '-E', 'separator=,', '-E', 'quote=d', '-e', 'frame.number', '-e', 'http2.streamid',  '-e', 'ip.src', '-e', 'ip.dst', '-e', 'grpc', '-e', 'protobuf.message.name', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Packet', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Data'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            df = pd.read_csv(p.stdout, sep=',')
            #os.remove(capture_file)
            df_all = pd.concat([df_all, df])  # 将每个捕获的 DataFrame 合并
        #df_all.to_csv('result.csv', index=False)  # 将合并后的 DataFrame 保存为CSV
        time.sleep(1)  # Wait for new capture files to be created before checking again
    
    files = [f for f in os.listdir() if f.startswith('capture_') and f.endswith('.pcap')]
    for capture_file in files:
        #csv_file = capture_file.replace('.pcap', '.csv')
        p = subprocess.Popen(['tshark', '-r', capture_file, '-T', 'fields', '-E', 'header=y', '-E', 'separator=,', '-E', 'quote=d', '-e', 'frame.number', '-e', 'http2.streamid',  '-e', 'ip.src', '-e', 'ip.dst', '-e', 'grpc', '-e', 'protobuf.message.name', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Packet', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Data'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        df = pd.read_csv(p.stdout, sep=',')
        #os.remove(capture_file)
        df_all = pd.concat([df_all, df])  # 将每个捕获的 DataFrame 合并
    df_all.to_csv('result.csv', index=False) 




def run(duration, port):
    global running
    running = True

    # 启动抓包和分析线程
    t1 = Thread(target=capture_process,args=(duration, port))
    t2 = Thread(target=analyze_process)
    t1.start()
    t2.start()

    #等待线程结束
    t1.join()
    t2.join()
    os.execl('/bin/bash', '--login')

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python %s duration port" % sys.argv[0], file=sys.stderr)
        sys.exit(1)
    duration = int(sys.argv[1])
    port = int(sys.argv[2])
    run(duration, port)
