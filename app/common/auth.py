import json
import os
import hashlib
import secrets

class AuthManager:
    # 配置文件放在 app/config 目录下
    USER_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'users.json')

    @classmethod
    def _load_users(cls):
        """读取本地 JSON 用户数据"""
        if not os.path.exists(cls.USER_FILE):
            # 如果文件不存在，初始化一个默认包含 admin 的空文件
            return {}
        with open(cls.USER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    @classmethod
    def _save_users(cls, data):
        """将数据保存回 JSON"""
        # 确保目录存在
        os.makedirs(os.path.dirname(cls.USER_FILE), exist_ok=True)
        with open(cls.USER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def generate_hash(cls, password, salt=None):
        """对密码进行 SHA-256 加盐哈希处理"""
        if salt is None:
            # 注册时生成一个随机的32字节盐值，并转为16进制字符串
            salt = secrets.token_hex(16)
        
        # 将密码和盐值结合计算 Hash
        # 使用 pbkdf2_hmac 是为了增加计算时间，防范暴力破解
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000  # 迭代次数，越大越安全但稍微耗时
        )
        return salt, hash_obj.hex()

    @classmethod
    def add_user(cls, username, password):
        """管理员添加新用户的方法"""
        users = cls._load_users()
        if username in users:
            return False, "用户已存在"
        
        salt, hash_password = cls.generate_hash(password)
        users[username] = {
            "salt": salt,
            "hash_password": hash_password
        }
        cls._save_users(users)
        return True, "添加成功"

    @classmethod
    def verify_login(cls, username, password):
        """验证用户登录"""
        users = cls._load_users()
        user_info = users.get(username)
        
        if not user_info:
            return False  # 用户名不存在
        
        saved_salt = user_info.get("salt")
        saved_hash = user_info.get("hash_password")
        
        # 用保存的盐值和用户输入的密码，重新计算一遍 Hash
        _, current_hash = cls.generate_hash(password, saved_salt)
        
        # 比较计算出的 Hash 与保存的 Hash 是否一致
        # 使用 compare_digest 防止计时攻击
        return secrets.compare_digest(current_hash, saved_hash)


# 生成初始的 admin 账号
if __name__ == '__main__':
    # 第一次运行此代码生成 admin 的 JSON 凭证
    AuthManager.add_user("admin", "123456")
    print("初始 admin 账户创建完毕！")