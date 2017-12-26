      # Apply a low pass filter (moving average to first two values
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
