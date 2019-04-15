from math import sin, pi, ceil, floor
from array import array
from random import random
import numpy as np
import wave
import pygame
from scipy.signal import butter, lfilter
from pygame.locals import *
import pyaudio


''' Initialization of sampling rate and maximum value for 16-bit clipping '''
sampleRate = 44100
MAX_VAL = 32767


''' Initialization of stream to hear sythesized tones '''
p = pyaudio.PyAudio()
stream = p.open(format = pyaudio.paInt16,
                rate = sampleRate,
                channels = 1,
                input = False,
                output = True)


''' Pygame initialization '''
pygame.init()
pygame.mixer.init(sampleRate,-16,1,4096)
pygame.display.set_mode((300, 300))


''' Extracting notes, keys, and tones information from txt file '''
hold=[]
note=[]
tone=[]
lap='C:/path/note_freq.txt'
desk='C:/path/note_freq.txt'
with open(desk) as f:
    d=f.readlines()
    for i in d:
        i=i.strip('\n')
        i=i.strip('\t')
        hold.append(i) 

for i in hold:
    j=i.split(',')
    note.append(j[0])
    tone.append(float(j[1]))


''' Creating lookup dictonary for a note (ex: C4) and tone (ex: 440 Hz) pair '''
note_tone_table={}
for i, j in zip(note, tone):
	note_tone_table[i]=j


''' Gathering keys on my laptop '''
row1=[pygame.K_F1,pygame.K_F2,pygame.K_F3,pygame.K_F4,pygame.K_F5,pygame.K_F6,pygame.K_F7,pygame.K_F8,pygame.K_F9,pygame.K_F10,pygame.K_F11,\
      pygame.K_F12,pygame.K_SYSREQ,pygame.K_BREAK,pygame.K_INSERT,pygame.K_DELETE]
row2=[pygame.K_BACKQUOTE,pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9,pygame.K_0,\
      pygame.K_MINUS,pygame.K_EQUALS,pygame.K_BACKSPACE,pygame.K_HOME]
row3=[pygame.K_TAB,pygame.K_q,pygame.K_w,pygame.K_e,pygame.K_r,pygame.K_t,pygame.K_y,pygame.K_u,pygame.K_i,pygame.K_o,\
      pygame.K_p,pygame.K_LEFTBRACKET,pygame.K_RIGHTBRACKET,pygame.K_BACKSLASH,pygame.K_PAGEUP]
row4=[pygame.K_CAPSLOCK,pygame.K_a,pygame.K_s,pygame.K_d,pygame.K_f,pygame.K_g,pygame.K_h,pygame.K_j,pygame.K_k,pygame.K_l,\
      pygame.K_SEMICOLON, pygame.K_QUOTE,pygame.K_RETURN,pygame.K_PAGEDOWN]
row5=[pygame.K_LSHIFT,pygame.K_z,pygame.K_x,pygame.K_c,pygame.K_v,pygame.K_b,pygame.K_n,pygame.K_m,\
      pygame.K_COMMA,pygame.K_PERIOD,pygame.K_SLASH,pygame.K_RSHIFT,pygame.K_END]
row6=[pygame.K_LCTRL,pygame.K_LMETA,pygame.K_LSUPER,pygame.K_LALT,pygame.K_SPACE,pygame.K_RALT,\
      pygame.K_RMETA,pygame.K_RCTRL,pygame.K_UP,pygame.K_DOWN,pygame.K_RIGHT,pygame.K_LEFT]
all_keys = row1+row2+row3+row4+row5+row6




def play_guitar(frequency, duration=3):
    N = int(ceil(sampleRate/frequency))                     # Generate length of delay line buffer
    samples = []                                            # Initialize list to hold samples after applying moving average low pass filter and removing first values
                                                            # Hold samples after application of Karplus-Strong Algorithm

    buf = [random() - 0.5 for i in range(N)]                # Generate white noise buffer with length N
                                                            # Maintain that these values are from -1 to 1 rather 0 to 1; offset with - 0.5 so that +0.5 is the new 0.0
    
    for i in range(sampleRate*duration):
        sample = buf[0]                                     # Hold the first value in delay line
        lpfOut = 0.996*0.5*(buf[1]+buf[0])                  # Apply a low pass filter (moving average to first two values
        buf.append(lpfOut)                                  # Add the newly calculated number to the end of the delay line
        buf.pop(0)                                          # Take out the white noise first value

        samples.append(sample)                              # Holds the newly low pass filtered values to play a tone


    temp = [int(x*MAX_VAL) for x in samples]              # Scale those values with MAX_VAL for 16-bit 
    data = array('h', temp).tostring()                    # Convert this array of values to string for playing aloud in the next step

    pygame.sndarray.make_sound(pygame.mixer.Sound(data)).play() # Play the newly synthesized tone
    #stream.write(data)                                     # See above note in the stream initialization
    return data
    

def play_violin(frequency, duration=5):

    b,a=butter(2, (frequency)/(0.5*sampleRate), btype='low')    # Generate low pass filter coefficients for later use below
    

    M = sampleRate/frequency - 0.5                              # Length of delay line buffer
    L = int(ceil(M))                                            # Length of wavetable
                                                                # Maintain that it is a int type for later use in the generation of the delay line
    delta = M - floor(M)                                        # Fractional delay value to create the alpha in the allpass factor
    alpha = (1-delta)/(1+delta)                                 # Allpass factor of the all pass filter below

    N = sampleRate * duration                                   # Length of the samples that will be outputed

    buf = [random() - 0.5 for i in range(L)]                    # Generate white noise buffer with length N
                                                                # Maintain that these values are from -1 to 1 rather 0 to 1; offset with - 0.5 so that +0.5 is the new 0.0

                                                                # Linear interpolation of delay line buffer
    kr = 0                                                      # Read pointer initialization
    kw = kr + int(floor(M))                                     # Write pointer initialization
    y1 = np.zeros(N)                                            # New buffer to hold newly interpolated data
    prev_kr_data = 0                                            # Initilization to store previous data at kr and kw
    prev_kw_data = 0

    for n in range(N):
        apfOut = prev_kr_data + alpha * (buf[kr-1]-prev_kw_data) # Pass delay line through all pass filter with factor alpha
        avgOut = b[2] * apfOut + b[1] * prev_kw_data             # Low pass filter weighting for present data (apfOut) and past data (pre_kw_data)
                                                                 # Similar to the moving average for guitar plucking sound effect
        y1[n] = avgOut                                           # The average output is now added to the new data buffer
        
        buf[kw-1] = avgOut                                       # At index kw-1 in the delay line, the value is the average output

        prev_kr_data = buf[kr-1]                                 # The previous data at kr will be the value at kr-1 in the delay line
        prev_kw_data = apfOut                                    # The previous data at kw will be the all pass filtered output
        
        kr = (kr % (L)) +1                                       # Update read and write pointers
        kw =  (kw % (L))+1

    temp = np.array([(x*MAX_VAL) for x in y1[300:44100-200]])    # Scale those values with MAX_VAL for 16-bit
                                                                 # Cut out a few samples at the beginning and end of the buffer to avoid too much noise
                                                                 # Original intention to reduce noise using fft, fftfreq, and ifft
                                                                 # But this creates a perfect tone of a piano defeating the purpose of interpolation
                                                                    ##    print np.array(temp)
                                                                    ##    n = np.size(temp)
                                                                    ##    temp_fft=np.fft.fft(temp)
                                                                    ##    sampleFreq=np.fft.fftfreq(n,0.01)
                                                                    ##    print np.mean(abs(temp))
                                                                    ##    p = np.where(sampleFreq < np.mean(abs(temp))*100)
                                                                    ##    freqs = sampleFreq[p]
                                                                    ##    power = np.absolute(sig_fft)[p]
                                                                    ##    freq = freqs[power.argmax()]
                                                                    ##    temp_fft[np.absolute(sampleFreq)>freq]=0
                                                                    ##    temp = np.fft.ifft(temp_fft)
        
    data = array('f', temp).tostring()                           # Convert this array of values to string for playing aloud in the next step      
    pygame.sndarray.make_sound(pygame.mixer.Sound(data)).play()  # Play the newly synthesized tone
    return y1

running = True
while running:

    events = pygame.event.get()                                     # Get status of event going on (ex: key pressed)
    keys = pygame.key.get_pressed()                                 # Get list of keys pressed in a single event
    
    for event in events:
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:               # Quit the program when ESC key is pressed
                running = False
                pygame.quit()
                raise KeyboardInterrupt
        
        for i,j in zip(all_keys, note):
            
            if event.type == pygame.KEYDOWN and event==i:     # If a certain key is pressed, play the instrument
               print keys
               
               play_violin(note_tone_table[j])
               #play_guitar(note_tone_table[j])
          
                
        if event.type == pygame.KEYUP:                              # Once the key is released, stop playing that tone
            pygame.sndarray.make_sound(pygame.mixer.Sound('')).play()

stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()



