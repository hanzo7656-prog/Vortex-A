[app]
title = My App
package.name = myapp
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv

version = 0.1
requirements = python3,kivy

[buildozer]
log_level = 2

[android]
api = 33
minapi = 21
android.accept_sdk_license = True

# اضافه کردن این خط برای قبول خودکار license
android.auto_accept_license = True
