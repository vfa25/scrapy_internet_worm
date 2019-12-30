from zheye import zheye
import sys
sys.path.append('/Users/a/Documents/pythonCode/ScrapyDemo')
z = zheye()
positions = z.Recognize('./zhihu_image/a.gif')
last_position = []

# [(47.5398383463051, 278.1807425580302), (50.66963709386455, 39.793204526702226)]
# 坐标系统一：如上，解析结果是[y, x]的结构，且可能随机索引
if len(positions) == 2:
    if positions[0][1] > positions[1][1]:
        last_position.append([positions[1][1], positions[1][0]])
        last_position.append([positions[0][1], positions[0][0]])
    else:
        last_position.append([positions[0][1], positions[0][0]])
        last_position.append([positions[1][1], positions[1][0]])
else:
    last_position.append([positions[0][1], positions[0][0]])

print(last_position)
