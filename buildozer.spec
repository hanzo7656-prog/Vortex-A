[app]
title = My App
package.name = myapp
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,ttf

version = 0.1
requirements = python3,kivy

[buildozer]
log_level = 2

[android]
api = 33
minapi = 21
android.auto_accept_license = True

# استفاده از SDK دستی
android.sdk_path = ./android-sdk
