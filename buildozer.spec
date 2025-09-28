[app]
title = My Complete App
package.name = mycompleteapp
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
ndk_path = ./android-ndk/r25b
sdk_path = ./android-sdk

# اجتناب از دانلود خودکار
android.skip_download = True
