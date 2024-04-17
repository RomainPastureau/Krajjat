import numpy as np
from matplotlib import pyplot as plt
from krajjat.classes.audio import Audio
from datetime import datetime as dt
from find_delay import resample

#############################
### BASIC TEST RESAMPLING ###
#############################
rf = 4
timestamps = np.linspace(0, 100, 1001)
array = np.sin(timestamps)

new_array = resample(array, 10, rf, 19, 0.5, "cubic", 2)
new_timestamps = np.linspace(0, 100, 100*rf+1)
plt.plot(timestamps, array)
plt.plot(new_timestamps, new_array)
plt.show()


################################################
### TEST RESAMPLING WITH WINDOWS AND OVERLAP ###
################################################