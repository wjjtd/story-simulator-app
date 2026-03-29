[app]

# 应用基本信息
title = AI故事模拟器
package.name = storysimulator
package.domain = org.example

# 源码路径
source.dir = .

# 应用版本
version = 1.0

# 入口文件
requirements = python3,kivy,requests,urllib3,chardet,idna,certifi

# 应用图标和启动画面
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/splash.png

# 编译选项
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE
android.api = 27
android.minapi = 21
android.ndk = 23b
android.sdk = 30

[buildozer]

# 日志级别
log_level = 2