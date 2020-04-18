import sensor
import image
import lcd
import time
import KPU as kpu
import audio
from Maix import I2S, GPIO
from fpioa_manager import *

########### settings ############
WIFI_EN_PIN     = 8
# AUDIO_PA_EN_PIN = None  # Bit Dock and old MaixGo
#AUDIO_PA_EN_PIN = 32      # Maix Go(version 2.20)
AUDIO_PA_EN_PIN = 2     # Maixduino


# disable wifi
fm.register(WIFI_EN_PIN, fm.fpioa.GPIO0)
wifi_en=GPIO(GPIO.GPIO0, GPIO.OUT)
wifi_en.value(0)

# open audio PA
if AUDIO_PA_EN_PIN:
    fm.register(AUDIO_PA_EN_PIN, fm.fpioa.GPIO1)
    wifi_en=GPIO(GPIO.GPIO1, GPIO.OUT)
    wifi_en.value(1)

# register i2s(i2s0) pin
fm.register(34,fm.fpioa.I2S0_OUT_D1)
fm.register(35,fm.fpioa.I2S0_SCLK)
fm.register(33,fm.fpioa.I2S0_WS)

# init i2s(i2s0)
wav_dev = I2S(I2S.DEVICE_0)


def play_sound(filename):
    try:
        player = audio.Audio(path = filename)
        player.volume(30)
        wav_info = player.play_process(wav_dev)
        #wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
        wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT ,cycles = I2S.SCLK_CYCLES_32, align_mode = I2S.RIGHT_JUSTIFYING_MODE)
        wav_dev.set_sample_rate(wav_info[1])
        while True:
            ret = player.play()
            if ret == None:
                break
            elif ret==0:
                break
        player.finish()
    except:
        pass

# init audio
#player = audio.Audio(path = "/sd/6.wav")
#player.volume(40)

# read audio info
#wav_info = player.play_process(wav_dev)
#print("wav file head information: ", wav_info)

# config i2s according to audio info
#wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT ,cycles = I2S.SCLK_CYCLES_32, align_mode = I2S.RIGHT_JUSTIFYING_MODE)
#wav_dev.set_sample_rate(wav_info[1])


lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
#sensor.set_vflip(True) #not available
#sensor.set_hmirror(False) #not available
sensor.run(1)
clock = time.clock()                # Create a clock object to track the FPS.

task = kpu.load(0x300000) # you need put model(face.kfpkg) in flash at address 0x300000
# task = kpu.load("/SD/face.kmodel")
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
a = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)

#main loop
while(True):
    img = sensor.snapshot()
    code = kpu.run_yolo2(task, img)
    if code:
        for i in code:
            print(i)
            a = img.draw_rectangle(i.rect())
            a = img.draw_string(2,2, str(i.value()), color=(0,128,0), scale=2)
            a = lcd.display(img)
            play_sound("/sd/gm.wav")
    a = lcd.display(img)
#    print(clock.fps())              # Note: MaixPy's Cam runs about half as fast when connected
a = kpu.deinit(task)
