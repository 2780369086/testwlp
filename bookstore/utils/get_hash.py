from hashlib import sha1

# 这个函数用来避免存储明文密码
def get_hash(str):
    # 取一个字符串的hash值
    sh = sha1()
    sh.update(str.encode('utf8'))
    return sh.hexdigest()