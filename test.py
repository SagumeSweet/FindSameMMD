import json
from pathlib import Path

with open("SameFileProcesser_result.json", "r", encoding="utf-8") as f:
    data = json.load(f)
for key in data.keys():
    result = {}
    for item in data[key]:
        path = Path(item)
        size = path.stat().st_size
        if size not in result:
            result[size] = [item]
        else:
            result[size].append(item)
    for size_key in result.keys():
        if len(result[size_key]) > 1:
            result[size_key].sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
            print(f"Size: {size_key} bytes:")
            print(result[size_key])
            print(f"保留：{result[size_key][0]}")
            print("删除：")
            for file in result[size_key][1:]:
                print(f"   {file}")
