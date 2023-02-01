#include "FS.h"
#include "SPIFFS.h"

/* You only need to format SPIFFS the first time you run a
   test or else use the SPIFFS plugin to create a partition
   SPIFFS文件系统初始化, 第一次运行下载程序改为true, 后面可改为false
   https://github.com/me-no-dev/arduino-esp32fs-plugin */
#define FORMAT_SPIFFS_IF_FAILED true
#include <U8g2lib.h>

#include <Wire.h>
#include "SSD1306.h"

// 初始化OLED
SSD1306 display(0x3c, 17, 16); // ADDRESS, SDA, SCL

// width: 128, height: 64
unsigned char col[128 * 64 / 8] = {0};

void listDir(fs::FS &fs, const char *dirname, uint8_t levels)
{
    Serial.printf("Listing directory: %s\r\n", dirname);

    File root = fs.open(dirname);
    if (!root)
    {
        Serial.println("- failed to open directory");
        return;
    }
    if (!root.isDirectory())
    {
        Serial.println(" - not a directory");
        return;
    }

    File file = root.openNextFile();
    while (file)
    {
        if (file.isDirectory())
        {
            Serial.print("  DIR : ");
            Serial.println(file.name());
            if (levels)
            {
                listDir(fs, file.path(), levels - 1);
            }
        }
        else
        {
            Serial.print("  FILE: ");
            Serial.print(file.name());
            Serial.print("\tSIZE: ");
            Serial.println(file.size());
        }
        file = root.openNextFile();
    }
}

void readFile(fs::FS &fs, const char *path)
{
    Serial.printf("Reading file: %s\r\n", path);

    File file = fs.open(path);
    if (!file || file.isDirectory())
    {
        Serial.println("- failed to open file for reading");
        return;
    }

    Serial.println("- read from file:");
    for (int j = 0; j < file.size() / 1024; j++)
    {
        for (int i = 0; i < sizeof(col) / sizeof(col[0]); i++)
        {
            col[i] = file.read();
        }
        display.clear();
        display.drawXbm(0, 0, 128, 64, col);
        display.display();
        delay(24);
    }
    file.close();
}

void deleteFile(fs::FS &fs, const char *path)
{
    Serial.printf("Deleting file: %s\r\n", path);
    if (fs.remove(path))
    {
        Serial.println("- file deleted");
    }
    else
    {
        Serial.println("- delete failed");
    }
}

void setup()
{
    Serial.begin(115200);

    // Initialising the UI will init the display too.
    display.init();

    // This will make sure that multiple instances of a display driver
    // running on different ports will work together transparently
    display.setI2cAutoInit(true);

    display.flipScreenVertically();
    display.setFont(ArialMT_Plain_10);
    display.setTextAlignment(TEXT_ALIGN_LEFT);

    if (!SPIFFS.begin(FORMAT_SPIFFS_IF_FAILED))
    {
        Serial.println("SPIFFS Mount Failed");
        return;
    }
    delay(5000);
    //    listDir(SPIFFS, "/", 0);
    readFile(SPIFFS, "/video.bin");
    //    deleteFile(SPIFFS, "video.bin");
    Serial.println("Test complete");
}

void loop()
{
    delay(1000);
}
