from os import wait
from PIL import Image
from math import floor
import sys
from time import sleep
import serial

# max height of the ascii image in ascii characters
MAX_HEIGHT = 10

# Aspect ratio of the Consolas font
FONT_ASPECT = 0.493

# File name
file = "lunch.gif"

# Serial port 
port = '/dev/ttyS3'

RAMP = " .:-=+*#%@"


im = Image.open(file)

print("Found gif file")

width, height = im.size

print("Gif width:", width)
print("Gif height:", height)

# Sets the number of pixels for the box to be represented by an ascii character
mod_pixel_y = height/MAX_HEIGHT
if mod_pixel_y  < 1:
    mod_pixel_y = 1
mod_pixel_x = mod_pixel_y * FONT_ASPECT
if mod_pixel_x < 1:
    mod_pixel_x = 1
    mod_pixel_y = mod_pixel_x / FONT_ASPECT

# list of frames containing a list of intensities
# Intensity values are stored in the transmission according to the following example:
#       ----------
#       | 1 2 3 4 | - > [1, 2, 3, 4, 5, 6, 7 ,8]
#       | 5 6 7 8 | 
#       ----------
Transmision = [[]]

# Loops through each frame of .gif
for frame in range(0, im.n_frames):
    Transmision.append([])

    print("Converting frame", frame)
    im.seek(frame)

    # loops through each box to be represented by a single ascii character
    for y in range(0, floor(height/mod_pixel_y)):
        for x in range(0, floor(width/mod_pixel_x)):
            box = (round(x*mod_pixel_x), round(y*mod_pixel_y), round((x+1)*mod_pixel_x), round((y+1)*mod_pixel_y))
            region = im.crop(box) # creates box
            r_grey = region.convert('L') # convert to grayscale
            r_width, r_height = region.size

            # caculates average intensity
            total = 0
            for i in range(0, r_width):
                for j in range(0, r_height):
                    total += r_grey.getpixel((i,j))

            mean = total / (r_width * r_height)
            Transmision[frame].append(round(mean))

im.close()

with serial.Serial(port, 115200) as ser:
    print("Printing X width: ", floor(width/mod_pixel_x))
    print(ser.write(floor(width/mod_pixel_x).to_bytes(2, "little")), "Bytes Written")
    ser.flush()
    ser.read_until(b'f')
    print("Connected")
    print("Printing Y width: ", floor(height/mod_pixel_y))
    print(ser.write(floor(height/mod_pixel_y).to_bytes(2,"little")), "Bytes Written")
    ser.flush()
    ser.read_until(b'f')
    print(ser.write(im.n_frames.to_bytes(2,"little")), "Bytes Written")
    ser.flush()
    ser.read_until(b'f')
    print("Settings Transfered")


    for frame in range(0, im.n_frames):
        for pix in range(0, len(Transmision[frame])):
            #print(RAMP[floor(Transmision[frame][pix]/(255/len(RAMP)))], end='')
            ser.write(Transmision[frame][pix].to_bytes(1,"little"))
            if pix % floor(width/mod_pixel_x) == (floor(width/mod_pixel_x) - 1):
                print(ser.read_until(b'\0').decode('UTF-8'),end='')
                ser.flush()
                #print("\n\r", end='')
        #for i in range(0, floor(height/mod_pixel_y)):
            #print('\033[F',end='')
