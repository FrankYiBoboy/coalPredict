import json
import os
import hashlib
import secrets

class AuthManager:
    # 配置文件放在 app/config 目录下
    USER_FILE = os.path.join(os.getcwd(), 'app', 'config', 'users.json')

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

    @classmethod
    def create_auto_login_token(cls, username):
        """生成自动登录的 Token 并将 Hash 值存入数据库(users.json)"""
        users = cls._load_users()
        if username not in users:
            return None
        
        # 生成一个高度随机的 32 字节明文 Token
        raw_token = secrets.token_urlsafe(32)
        # 为 Token 生成专属 Salt，并计算 Hash
        token_salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256', 
            raw_token.encode('utf-8'), 
            token_salt.encode('utf-8'), 
            50000 # Token 的哈希迭代次数可以略低，因为其本身就是高强度随机数
        )
        token_hash = hash_obj.hex()
        
        # 将 Token 的 Hash 存入该用户的节点下
        users[username]["token_salt"] = token_salt
        users[username]["token_hash"] = token_hash
        cls._save_users(users)
        
        return raw_token
    
    @classmethod
    def verify_auto_login_token(cls, username, raw_token):
        """校验本地 Token 是否合法"""
        if not username or not raw_token:
            return False
            
        users = cls._load_users()
        user_info = users.get(username)
        
        if not user_info or "token_hash" not in user_info:
            return False
            
        # 提取数据库中保存的 Token Salt 和 Hash
        saved_salt = user_info.get("token_salt")
        saved_hash = user_info.get("token_hash")
        
        # 对传入的明文 Token 重新计算 Hash
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256', 
            raw_token.encode('utf-8'), 
            saved_salt.encode('utf-8'), 
            50000
        )
        current_hash = hash_obj.hex()
        
        # 安全比对
        return secrets.compare_digest(current_hash, saved_hash)
    
    @classmethod
    def get_all_users(cls):
        """获取系统内所有操作员用户名列表"""
        users = cls._load_users()
        return list(users.keys())
    
    @classmethod
    def delete_user(cls, admin_name, target_user):
        """删除用户"""
        if admin_name != "admin":
            return False, "越权操作：仅管理员可删除用户"
        if target_user == "admin":
            return False, "非法操作：管理员账号不可删除"
        
        users = cls._load_users()
        if target_user in users:
            del users[target_user]
            cls._save_users(users)
            return True, f"用户 {target_user} 已成功注销"
        return False, "用户不存在"
    
    @classmethod
    def update_password(cls, admin_name, target_user, new_password):
        """修改用户密码"""
        if admin_name != "admin":
            return False, "越权操作"
        
        users = cls._load_users()
        if target_user not in users:
            return False, "用户不存在"
        
        # 重新生成哈希和盐值
        salt, hash_password = cls.generate_hash(new_password)
        users[target_user]["salt"] = salt
        users[target_user]["hash_password"] = hash_password
        
        # 密码被管理员重置后，强制免密Token失效
        if "token_hash" in users[target_user]:
            del users[target_user]["token_hash"]
            del users[target_user]["token_salt"]
            
        cls._save_users(users)
        return True, f"用户{target_user} 的密码已重置"

    @classmethod
    def init_system(cls, default_password="123456"):
        """
        系统环境初始化自检：
        如果 user.json 不存在，或其中没有 admin 账号，则自动生成。
        """
        # 确保配置文件夹路径存在
        os.makedirs(os.path.dirname(cls.USER_FILE), exist_ok=True)
        
        # 读取现有数据
        users = cls._load_users()
        
        # 3. 检查是否存在 admin 账号
        if "admin" not in users:
            # 初始化admin账户
            cls.add_user("admin", default_password)