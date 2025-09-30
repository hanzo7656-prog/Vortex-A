[app]
title = My App
package.name = myapp
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json

version = 0.1
requirements = python3,kivy

presplash.filename = %(source.dir)s/presplash.png
icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 33
minapi = 21
ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r25b
sdk_path = /home/runner/.buildozer/android/platform/android-sdk

# جلوگیری از دانلود خودکار
skip_download = True
android.skip_download = True

# قبول خودکار لایسنس‌ها
android.accept_sdk_license = True
android.auto_accept_license = True

# تنظیمات build
android.arch = armeabi-v7a
p4a.branch = develop

# بهینه‌سازی
android.enable_androidx = True
android.gradle_download = True

[ci]
# تنظیمات مخصوص GitHub Actions
app = %(source.dir)s/main.py
requirements = python3,kivy
