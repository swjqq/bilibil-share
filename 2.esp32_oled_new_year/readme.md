# [我用ESP32+0.96寸OLED摆烂了你的AE作业](https://www.bilibili.com/video/BV1ai4y197u9/?share_source=copy_web&vd_source=d566c4debdbc1f345d192d2abafa3b67) 代码
- 使用Arduino平台，
- 使用了SPIFFS文件系统，data中bin文件是二值化后的视频文件，可使用[此工具](https://github.com/RegularTriangle/bilibil-share/tree/master/3.128x64_video_bin_create_tool)生成，并且使用[Arduino ESP32 filesystem uploader](https://github.com/me-no-dev/arduino-esp32fs-plugin)插件上传到esp32
- 需要安装库
