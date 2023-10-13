## 自动认证东北大学校园网脚本
javascript版本->https://github.com/CalebChen768/NEU_ipgw_login_js/tree/main

### 1. 填写账号密码
在`config.ini`中填写自己的统一登录账号密码，如
``` 
[info]
StudentID = 20001234
password = 12345678 
```

### 2. 环境要求
python3 + requests库

### 3. 运行脚本
```
python3 login.py
```

注：可以搭配自动化脚本，如Mac的“捷径”，实现一键快速登录。
