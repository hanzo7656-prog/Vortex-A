[app]
title = My Python App
package.name = myapp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 0.1
requirements = python3,kivy

[buildozer]
log_level = 2

[android]
api = 33
minapi = 21
# حذف خط ndk یا استفاده از نسخه جدید
# buildozer به طور خودکار NDK را مدیریت می‌کند
