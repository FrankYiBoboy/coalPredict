import os

class SessionManager:
    _current_user = None

    @classmethod
    def set_current_user(cls, username: str):
        """登录成功后设置当前用户"""
        cls._current_user = username

    @classmethod
    def get_current_user(cls) -> str:
        """获取当前用户，预留防错机制"""
        if not cls._current_user:
            return "unknown_user"
        return cls._current_user

    @classmethod
    def get_user_history_path(cls) -> str:
        """获取当前用户专属的历史记录物理路径"""
        base_path = os.path.join(os.getcwd(), "saved_history")
        user_path = os.path.join(base_path, cls.get_current_user())
        # 如果该用户的专属文件夹不存在，则自动创建
        if not os.path.exists(user_path):
            os.makedirs(user_path, exist_ok=True)
            
        return user_path