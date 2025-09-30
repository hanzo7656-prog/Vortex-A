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

[android]
api = 33
minapi = 21
arch = armeabi-v7a
permissions = INTERNET
allow_backup = False
enable_multi_dex = False
