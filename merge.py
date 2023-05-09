import os
import pandas as pd

path = "./"

# 获取目录下所有 CSV 文件的文件名
csv_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]

# 将多个 CSV 文件合并成一个 DataFrame
data_frames = []
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    data_frames.append(df)
merged_df = pd.concat(data_frames, ignore_index=True)

# 保存合并后的 CSV 文件
merged_df.to_csv(os.path.join(path, 'merged.csv'), index=False)
