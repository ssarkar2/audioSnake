import pygame, random, sys
from pygame.locals import *
import pyaudio, wave
import struct, math
from numpy.fft import fft
from numpy import array

#audio stuff

SHORT_NORMALIZE = (1.0/32768.0)
def get_rms(shorts):

    # RMS amplitude is defined as the square root of the
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into
    # a string of 16-bit samples...

    # we will get one short out for each
    # two chars in the string.
    #count = len(block)/2
    #format = "%dh"%(count)
    #shorts = struct.unpack( format, block )
    #print len(shorts)

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
    # sample is a signed short in +/- 32768.
    # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=chunk)
print 'a2'
wf = wave.open('record_snake.wav', 'wb')
wf.setnchannels(1)
sample_width = p.get_sample_size(FORMAT)
wf.setsampwidth(sample_width)
wf.setframerate(RATE)

def collide(x1, x2, y1, y2, w1, w2, h1, h2):
	if x1+w1>x2 and x1<x2+w2 and y1+h1>y2 and y1<y2+h2:return True
	else:return False

def die(screen, score):
	f=pygame.font.SysFont('Arial', 30);t=f.render('Your score was: '+str(score), True, (0, 0, 0));screen.blit(t, (10, 270));pygame.display.update();pygame.time.wait(2000);sys.exit(0)
xs = [290, 290, 290, 290, 290];
ys = [290, 270, 250, 230, 210];
dirs = 0;
score = 0;
applepos = (random.randint(0, 590), random.randint(0, 590));
pygame.init();
s=pygame.display.set_mode((600, 600));
pygame.display.set_caption('Snake');
appleimage = pygame.Surface((10, 10));
appleimage.fill((0, 255, 0));
img = pygame.Surface((20, 20));
img.fill((255, 0, 0));
f = pygame.font.SysFont('Arial', 20);
clock = pygame.time.Clock()
prevturn = 0
ii = 0
while True:
	#clock.tick(2)
    if(pygame.time.get_ticks() % 50 == 0):
       ii+=1
       data = stream.read(chunk)
       count = len(data)/2
       format = "%dh"%(count)
       shorts = struct.unpack( format, data )
       rmsdata = get_rms(shorts)

       datafftabs = abs(fft(shorts))
       maxid = 5
       maxval = datafftabs[5]
       for i in range(2,int(len(datafftabs)/2)):
        #print datafftabs[i]
        if (datafftabs[i] >= maxval):
            maxid = i
            maxval = datafftabs[i]

       if(rmsdata > 0.02):
        if  prevturn == 0:
            if (maxid < 10):  #modify threshold if needed
                dirs -= 1
            else:
                dirs += 1
        dirs%=4
        prevturn = 1
       else:
        prevturn = 0

       wf.writeframes(data)

    if(pygame.time.get_ticks() % 200 == 0):
	   i = len(xs)-1
	   while i >= 2:
		  if collide(xs[0], xs[i], ys[0], ys[i], 20, 20, 20, 20):die(s, score)
		  i-= 1
	   if collide(xs[0], applepos[0], ys[0], applepos[1], 20, 10, 20, 10):score+=1;xs.append(700);ys.append(700);applepos=(random.randint(0,590),random.randint(0,590))
	   if xs[0] < 0 or xs[0] > 580 or ys[0] < 0 or ys[0] > 580: die(s, score)
	   i = len(xs)-1
	   while i >= 1:
		  xs[i] = xs[i-1];ys[i] = ys[i-1];i -= 1
	   if dirs==0:ys[0] += 20
	   elif dirs==1:xs[0] += 20
	   elif dirs==2:ys[0] -= 20
	   elif dirs==3:xs[0] -= 20
	   s.fill((255, 255, 255))
	   for i in range(0, len(xs)):
		  s.blit(img, (xs[i], ys[i]))
	   s.blit(appleimage, applepos);t=f.render(str(score), True, (0, 0, 0));s.blit(t, (10, 10));pygame.display.update()
