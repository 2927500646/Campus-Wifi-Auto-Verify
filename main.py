import random
import time
from tool import verify, HOUR, MINITE
import json
from datetime import datetime



def main():
    sleep_time = MINITE
    last_verify_account = None
    with open("LTaccounts.txt", "r") as LTaccounts: # 读取已知的账户和密码
        LTaccountsList = list(LTaccounts)
    with open("LTpasswords.txt", "r") as LTpasswords:
        LTpasswordsList = list(LTpasswords)
    blocklist = [0] * len(LTaccountsList)           # 账户黑名单拉黑分钟数，若遇到占用则拉黑一次，隔一分钟再次尝试
    last_verify_time = [None] * len(LTaccountsList)    # 账号上次连接的时间
    while True:
        print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 心跳检测")
        suc = False                                 # 存储心跳检测结果

        a, p = None, None

        # 首先尝试上一次认证成功的账号
        if last_verify_account is not None:
            a, p = LTaccountsList[last_verify_account]
            result = verify("unicom", a, p)
            print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() json解析 {result}")
            info = json.loads(result)               # 转换json为字典格式
            if info["result"] == 1:                 # 认证成功
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 认证成功 account {a}")
                suc = True
                now_verify_time = datetime.now()    # 记录认证时间
					    # 5分钟内认证过了, 说明有人抢号, 那就拉黑一次
                if last_verify_time[i] is not None and (now_verify_time-last_verify_time[i]).total_seconds() / 60 < 5:
                    blocklist[i] += random.choice([1, 2] * HOUR)
                    sleep_time = MINITE
                    last_verify_time[i] = now_verify_time
            elif info["result"] == 0 and info["ret_code"] == 2:
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 重复认证 account {a}")
                sleep_time = 5 * MINITE
                suc = True                          # 已经在线
            elif info["result"] == 0 and info["ret_code"] == 1:
                """这个是认证失败，可能是密码错误，也可能是ip对不上导致的AC认证失败,以及抢占登录导致的结果"""
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 认证失败 account {a}")
                if "正在为您抢占登陆，请尝试再次登陆" in info["msg"]:
                    print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 账户占用 account {a}")
                    blocklist[i] += random.choice([1, 2] * HOUR)
                elif "请选择运营商账号登录" in info["msg"]:
                    print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 夜间断网")
                    for _ in blocklist:
                        _ += 5  * HOUR                    # 夜间全部拉黑5个小时
            elif info["result"] == 0 and info["ret_code"] == 3:
                print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 账户占用 account {a}")
                blocklist[i] += random.choice([MINITE, HOUR, 2*HOUR, 3*HOUR])
                                                    # 最少拉黑5分钟, 最多3个小时
                                                # for循环执行完后，再用校园网兜底
            else:
                print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 其他错误 account {a}")

        if suc:
            print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 保持连接 account {a}")
        else:
            print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 网络断连 account {a}\n尝试其他账号")

        # 然后再尝试认证其他账号
        for i in range(len(LTaccountsList)):
            a, p = LTaccountsList[i].strip(), LTpasswordsList[i].strip()
            if a == "" or p == "":                  # 跳过空格
                continue
            if blocklist[i] > 0:                    # 跳过拉黑账户
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 跳过认证账户{a}")
                blocklist[i] -= sleep_time                   # 若有人占用被拉黑，跳过一次
                continue
            result = verify("unicom", a, p)
            print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() json解析 {result}")
            info = json.loads(result)               # 转换json为字典格式
            if info["result"] == 1:                 # 认证成功
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 认证成功 account {a}")
                suc = True
                now_verify_time = datetime.now()    # 记录认证时间
						    # 5分钟内认证过了, 说明有人抢号, 那就拉黑一次
                if last_verify_time[i] is not None and (now_verify_time-last_verify_time[i]).total_seconds() / 60 < 5:
                    blocklist[i] += random.choice([1, 2] * HOUR)
                    sleep_time = MINITE
                last_verify_time[i] = now_verify_time
                last_verify_account = i
                break
            elif info["result"] == 0 and info["ret_code"] == 2:
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 重复认证 account {a}")
                suc = True                          # 已经在线
                sleep_time = 5 * MINITE
                break
            elif info["result"] == 0 and info["ret_code"] == 1:
                """这个是认证失败，可能是密码错误，也可能是ip对不上导致的AC认证失败,以及抢占登录导致的结果"""
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 认证失败 account {a}")
                if "正在为您抢占登陆，请尝试再次登陆" in info["msg"]:
                    print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 账户占用 account {a}")
                    blocklist[i] += random.choice([MINITE, HOUR, 2*HOUR, 3*HOUR])
                                                    # 最少拉黑1分钟, 最多3个小时
                elif "请选择运营商账号登录" in info["msg"]:
                    print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 夜间断网 account {a}")
                    for _ in blocklist:
                        _ += 5  * HOUR                    # 夜间全部拉黑5个小时
                """这个是认证失败，可能是密码错误，也可能是ip对不上导致的AC认证失败"""
            else:
                print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} main() 其他错误 account {a}")

        if not suc:                        	    # 尝试校园网
            print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 无LT账户，尝试校园网")
            a, p = "B20240304419", "180451"
            result = verify("xyw", a, p)
            info = json.loads(result)
            if info["result"] == 1:
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 认证成功 account {a}")
                suc = True
            elif info["result"] == 0 and info["ret_code"] == 2:
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 重复认证 account {a}")
                suc = True
            else:
                print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 认证失败 account {a}")

        if not suc:
            print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 心跳停止")
        else:
            print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} main() 心跳保持")
        time.sleep(sleep_time)
        print("\n")
    print("程序意外结束，请检查break语句")


if __name__ == "__main__":
        main()
