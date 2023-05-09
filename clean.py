import pandas as pd
import sys

def main(filename):
    # 读取 CSV 文件并删除包含 NaN 值的行
    df = pd.read_csv(filename)
    df.dropna(inplace=True)

    # 完成清洗后，将新的 DataFrame 存储为新的 CSV 文件
    output_filename = 'cleaned_' + filename
    df.to_csv(output_filename, index=False)

    # 输出完成消息
    print('Cleaning complete! Output file saved as', output_filename)

if __name__ == '__main__':
  # 获取文件名作为命令行参数
  csv_file = sys.argv[1]
  main(csv_file)
