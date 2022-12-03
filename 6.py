import math
# https://github.com/Default2882/Music-Visualizer-in-Python/blob/master/script.py
import numpy as np
import pygame
from pydub import AudioSegment
from scipy.io import wavfile as wav
import scipy.signal
import time

choice = input("Use default filename or not?(y/n)\n")
if choice != 'y':
    fmt = input("use .mp3 or .wav?(1/2)\n1:mp3\n2:wav\n")
    if fmt == '1':
        filename = input("filename:")
        # filname = "D:\FDU\大三上\计算机图形学\音乐可视化/Nova-Blast-master/Nova-Blast-master/Nova Blast\Music/2.mp3"
        sound = AudioSegment.from_mp3(filename)
        sound.export("testfile.wav", format="wav")
        pygame.mixer.init()
        pygame.mixer.music.load("converted2.wav")
        rate, data = wav.read('converted2.wav')
    else:
        filename = input("filename:")
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        rate, data = wav.read(filename)
else:
    pygame.mixer.init()
    pygame.mixer.music.load("converted2.wav")
    rate, data = wav.read('converted2.wav')
percentage_displayed_f = 0.6  # 0.1 采样频率
max_height_percentile = 99.8
fftlength = 2048
entertainment = True
screen_w = 1000
# print(green("Stereo to Mono Conversion"))
music = scipy.mean(data, axis=1)
# a = music[-1]
mmax = scipy.percentile(music, 99.5)
mmin = scipy.percentile(music, 0.05)
music = (music - mmin) / (mmax - mmin)


f, t, Sxx = scipy.signal.spectrogram(music, rate, nperseg=fftlength)
# f:采样频率数组 t:采样时间数组 Sxx：频谱图
no_of_displayed_f = int(len(f) * percentage_displayed_f + 0.5)  # 展示的采样频率
Sxx = Sxx[:no_of_displayed_f - 2].transpose()  # (718,6939)-->(6939,716)==(T, num)
f = f[:no_of_displayed_f - 2]  # 1025-->716


pygame.init()
screen = pygame.display.set_mode((1000, 500))  # 初始化窗口 W*H
bgimg = pygame.image.load("img.jpg")
per = scipy.percentile(Sxx, max_height_percentile)
# 求Sxx的max_height_percentile分位数，也就是在Sxx中有max_height_percentile%的数比per小
rect_scale_factor = 500 / per
dt = t[1] - t[0]  # 采样时间间隔



for i in range(len(Sxx)):
    smax = max(Sxx[i])
    smin = min(Sxx[i])
    Sxx[i] = (Sxx[i] - smin) / smax - smin
amplitude = scipy.mean(Sxx, axis = 1)
amplitude = np.array(amplitude)
amax = scipy.percentile(amplitude, 98)
mag = 300 / amax # 放大倍数，即最大的振幅对应半径为300
amplitude = mag * amplitude

colours = []
if not entertainment:
    colour_f = 0.0087
else:
    colour_f = 0.0348
for i in range(no_of_displayed_f):
    green = math.sin(colour_f * i + 0) * 127 + 128
    blue = math.sin(colour_f * i + 2) * 127 + 128
    red = math.sin(colour_f * i + 4) * 127 + 128
    colours.append((red, green, blue))
start_time = time.time()

rect_width = 2 * 1000 / no_of_displayed_f  # nf就是有多少个柱子，rect_width是每一个柱子的宽度

pygame.mixer.music.play()  # 播放音乐
globalindex = 0
# Animation Loop
while True:
    try:
        cur_time = time.time() - start_time  # 当前时间

        main_time_index = int(cur_time // dt)  # 第几个时间帧

        for index, frequency in enumerate(Sxx[main_time_index]): # Sxx(T, num_of+column)
            height = max(frequency * 300, 2)

            if entertainment:
                R1 = amplitude[0]
                if index % 100 == 0 and abs(amplitude[main_time_index] - R1) > 20:
                    rr = int(index / 150) % 3 + 1 # 粗细
                    R = amplitude[main_time_index]
                    R1 = R
                    iii = (40 + globalindex) % 60
                    iii = (int(R / rect_width) + 5) % len(colours)
                    pygame.draw.circle(screen, colours[iii],
                                       [1000 / 2, 500 / 2], R, rr)
                    globalindex += np.random.randint(1, 5)
                ii = 1 if index % 2 else -1
                if index % 2:
                    pygame.draw.rect(screen, colours[index], pygame.Rect(
                        (index)*rect_width + screen_w/2, 300 - height, rect_width, height))
                else:
                    pygame.draw.rect(screen, colours[index], pygame.Rect(
                        (index + 1)*rect_width*(-1) + screen_w/2, 300 - height, rect_width, height))

            else:
                pygame.draw.rect(screen, colours[index],
                                 pygame.Rect((index + 1) * rect_width, 300 - height, rect_width, height))

        pygame.display.flip()
        # screen.fill((255, 255, 255))
        screen.blit(bgimg, (0, 0))
        screen.set_alpha(255)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or not pygame.mixer.music.get_busy():
                pygame.display.quit()
                pygame.mixer.music.stop()
                break

    except:
        pygame.display.quit()
        pygame.mixer.music.stop()
        break
