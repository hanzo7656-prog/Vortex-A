[app]
title = My App
package.name = myapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,ttf
version = 0.1
requirements = kivy,requests,pillow
orientation = portrait
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
android.accept_sdk_license = True
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r25b
android.build_tools_version = 33.0.0
android.api = 33
android.minapi = 21
android.arch = armeabi-v7a
android.permissions = INTERNET
android.allow_backup = False
android.enable_multi_dex = False
android.gradle_dependencies = com.android.support:appcompat-v7:33.0.0

[android]
# مسیر aidl به صورت خودکار از build-tools گرفته میشه
# اگر نیاز به تنظیم دستی بود:
# android.aidl_path = /home/runner/.buildozer/android/platform/android-sdk/build-tools/33.0.0/aidl
