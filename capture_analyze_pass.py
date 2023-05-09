import subprocess
import time
import signal
import datetime
from threading import Thread
import os

def handler(signum, frame):
    # 处理ctrl+c信号，结束循环
    global running
    running = False
   
# 注册ctrl+c信号处理函数
signal.signal(signal.SIGINT, handler)

def capture_process(duration, port):
    while running:
        # 获取当前时间作为文件名的一部分
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        print("Cony, Please press Ctrl+C when capture is done. :)")

        # 进程1，调用tshark抓包并存储到本地文件
        capture_file = 'capture_' + current_time + '.pcap'
        p = subprocess.Popen(['tshark', '-i', 'ens18', '-a', 'duration:' + str(duration), '-f', 'tcp port ' + str(port), '-w', capture_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(duration)

        # 检查文件大小，如果文件小于1kb，则删除文件
        #capture_file_size = os.path.getsize(capture_file)
        #if capture_file_size < 1024:
            #print(f'{capture_file} is too small ({capture_file_size} bytes), deleted.')
            #os.remove(capture_file)

def analyze_process():
    while running:
        files = [f for f in os.listdir() if f.startswith('capture_') and f.endswith('.pcap')]
        for capture_file in files:
            # 使用tshark对抓包文件进行解析后生成csv文件
            csv_file = capture_file.replace('.pcap', '.csv')
            p = subprocess.Popen(['tshark', '-r', capture_file, '-T', 'fields', '-E', 'header=y', '-E', 'separator=,', '-E', 'quote=d', '-e', 'frame.number', '-e', 'http2.streamid',  '-e', 'ip.src', '-e', 'ip.dst', '-e', 'grpc', '-e', 'protobuf.message.name', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Packet', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Data'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            with open(csv_file, 'w') as f:
                f.write(p.communicate()[0].decode('utf-8'))

    # running变为False时，检查是否还有文件未处理完，如果有，则处理完
    files = [f for f in os.listdir() if f.startswith('capture_') and f.endswith('.pcap')]
    for capture_file in files:
        # 使用tshark对抓包文件进行解析后生成csv文件
        print("Cony, Please wait to exit...")
        csv_file = capture_file.replace('.pcap', '.csv')
        p = subprocess.Popen(['tshark', '-r', capture_file, '-T', 'fields', '-E', 'header=y', '-E', 'separator=,', '-E', 'quote=d', '-e', 'frame.number', '-e', 'http2.streamid',  '-e', 'ip.src', '-e', 'ip.dst', '-e', 'grpc', '-e', 'protobuf.message.name', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Packet', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Data'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(csv_file, 'w') as f:
            f.write(p.communicate()[0].decode('utf-8'))


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
