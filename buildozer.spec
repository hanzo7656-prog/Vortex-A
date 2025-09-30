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

# جلوگیری از دانلود خودکار
android.skip_download = True
android.skip_update = True

# استفاده از مسیرهای دستی
android.sdk_dir = /home/runner/.buildozer/android/platform/android-sdk
android.ndk_dir = /home/runner/.buildozer/android/platform/android-sdk/ndk/25.1.8937393
