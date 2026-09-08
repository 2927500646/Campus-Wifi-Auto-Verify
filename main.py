import random
import time
from tool import verify
import json



def main():
    with open("LTaccounts.txt", "r") as LTaccounts: # 读取已知的账户和密码
        LTaccountsList = list(LTaccounts)
    with open("LTpasswords.txt", "r") as LTpasswords:
        LTpasswordsList = list(LTpasswords)
    blocklist = [0] * len(LTaccountsList)           # 账户黑名单次数，若遇到重复则拉黑一次，隔一个小时再次尝试
    while True:
        suc = False                                 # 存储心跳检测结果
        for i in range(len(LTaccountsList)):
            a, p = LTaccountsList[i].strip(), LTpasswordsList[i].strip()
            if a == "" or p == "":                  # 跳过空格
                continue
            if blocklist[i] > 0:                    # 跳过拉黑账户
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 跳过认证账户{a}")
                blocklist[i] -= 1                   # 若有人占用被拉黑，跳过一次
                continue
            result = verify("unicom", a, p)         # 进行一次心跳保活
            print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() json解析 {result}")
            info = json.loads(result)               # 转换json为字典格式
            if info["result"] == 1:                 # 认证成功
                print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 认证成功 account {a}")
                suc = True
                break
            elif info["result"] == 0 and info["ret_code"] == 2:
                print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 重复认证 account {a}")
                suc = True                          # 已经在线
                break
            elif info["result"] == 0 and info["ret_code"] == 1:
                """这个是认证失败，可能是密码错误，也可能是ip对不上导致的AC认证失败"""
                print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 认证失败,密码错误或IP错误 account {a}")
            elif info["result"] == 0 and info["ret_code"] == 3:
                print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 账户占用 account {a}")
                blocklist[i] += random.choice([1, 12, 24, 36])
                                                    # 最少拉黑5分钟, 最多3个小时
                if not suc:                         # 尝试校园网
                    print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 无LT账户，尝试校园网")
                a, p = # 填你自己的哦
                result = verify("xyw", a, p)
                info = json.loads(result)
                if info["result"] == 1:
                    print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 认证成功 account {a}")
                    suc = True  # 同上逻辑
                    break
                elif info["result"] == 0 and info["ret_code"] == 2:
                    print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 重复认证 account {a}")
                    suc = True
                    break
                elif info["result"] == 0 and info["ret_code"] == 1:
                    print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 认证失败,密码错误或IP错误 account {a}")
                elif info["result"] == 0 and info["ret_code"] == 3:
                    """猜测的返回码，有人占用"""
                    print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 账户占用 account {a}")
                else:
                    print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 其他错误 account {a}")
            else:
                print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 其他错误 account {a}")

        if not suc:
            print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 心跳停止")
        else:
            print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 心跳保持")
        print("\n")
        time.sleep(5 * 60)                                  # 每5分钟执行一次心跳检测


if __name__ == "__main__":
        main()
