import numpy as np
from matplotlib import pyplot as plt
from scipy import signal
from datetime import datetime as dt
import statsmodels.api as sm

#y1 = [7, 1, 9, 0, 3, 12, 9, 4, 5, 2, 1, 9, 6, 4, 1, 0, 11, 3, 5, 6]
#y2 = [0, 3, 12, 9, 4, 5, 2, 1, 9, 6, 4, 1]

y1 = np.array([2, 22, 14, 8, 0, 4, 8, 16, 26, 6, 12, 14, 16, 2, 6])
y2 = np.array([2, 4, 8, 13, 3, 6])
#y2 = np.array([4, 8, 16, 26, 6, 12])
y1n = y1 / np.std(y1)
y2n = y2 / np.std(y2)
y1l = y1 / np.linalg.norm(y1)
y2l = y2 / np.linalg.norm(y2)

spv = 5
sph = 3

# 1. Sliding correlations
title = "Sliding correlations"
time_before = dt.now()
xcorr = np.zeros(len(y1) - len(y2))
for i in range(len(y1) - len(y2)):
    xcorr[i] = np.corrcoef(y1[i:i+len(y2)], y2)[0][1]
time_elapsed = dt.now() - time_before
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 1)
plt.plot(xcorr)
plt.title(title)

# 2. Sliding correlations, mean removed
title = "Sliding correlations, mean removed"
time_before = dt.now()
xcorr = np.zeros(len(y1) - len(y2))
for i in range(len(y1) - len(y2)):
    xcorr[i] = np.corrcoef(y1[i:i+len(y2)] - np.mean(y1), y2 - np.mean(y2))[0][1]
time_elapsed = dt.now() - time_before
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 2)
plt.plot(xcorr)
plt.title(title)

# 3. SSC
title = "SSC"
time_before = dt.now()
xcorr = signal.correlate(y1, y2, mode="full")
lags = signal.correlation_lags(len(y1), len(y2), mode="full")
time_elapsed = dt.now() - time_before
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 3)
plt.plot(lags, xcorr)
plt.title(title)

# 4. SSC, mean removed
title = "SSC, mean removed"
time_before = dt.now()
xcorr = signal.correlate(y1-np.mean(y1), y2-np.mean(y2), mode="full")
lags = signal.correlation_lags(len(y1), len(y2), mode="full")
time_elapsed = dt.now() - time_before
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 4)
plt.plot(lags, xcorr)
plt.title(title)

# 5. SSC normalized (÷SD)
title = "SSC normalized (÷SD)"
time_before = dt.now()
xcorr = signal.correlate(y1n, y2n, mode="full")
lags = signal.correlation_lags(len(y1), len(y2), mode="full")
time_elapsed = dt.now() - time_before
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 5)
plt.plot(lags, xcorr)
plt.title(title)

# 6. SSC normalized (÷SD, ÷len)
title = "SSC normalized (÷SD, ÷len)"
time_before = dt.now()
xcorr = signal.correlate(y1n, y2n, 'full') / min(len(y1), len(y2))
lags = signal.correlation_lags(len(y1), len(y2), mode="full")
time_elapsed = dt.now() - time_before
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 6)
plt.plot(lags, xcorr)
plt.title(title)

# 7. SSC, division by sqrt(max(corr_y1_y1) * max(corr_y2_y2))
title = "SSC, division by sqrt(max(corr_y1_y1) * max(corr_y2_y2))"
corr_y1_y1 = signal.correlate(y1, y1, "full")
corr_y2_y2 = signal.correlate(y2, y2, "full")
corr_y1_y2 = signal.correlate(y1, y2, "full")
xcorr = 1/np.sqrt(np.max(corr_y1_y1) * np.max(corr_y2_y2)) * corr_y1_y2
lags = signal.correlation_lags(len(y1), len(y2), mode="full")
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 7)
plt.plot(lags, xcorr)
plt.title(title)

# 8. SSC, division by sqrt(sum(abs(y1)^2) * sum(abs(y2)^2))
title = "SSC, division by sqrt(sum(abs(y1)^2) * sum(abs(y2)^2))"
xcorr = signal.correlate(y1, y2, mode="full") / np.sqrt(np.sum(np.abs(y1)**2)*np.sum(np.abs(y2)**2))
lags = signal.correlation_lags(len(y1), len(y2), mode="full")
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 8)
plt.plot(lags, xcorr)
plt.title(title)

# 9. SSC, normalized (linalg)
title = "SSC, normalized (linalg)"
xcorr = np.abs(signal.correlate(y1n, y2n, "full"))
lags = signal.correlation_lags(len(y1), len(y2), mode="full")
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 9)
plt.plot(lags, xcorr)
plt.title(title)

# 10. Statsmodel CCF
title = "Statsmodel CCF"
xcorr = np.abs(sm.tsa.stattools.ccf(y2, y1, adjusted=False))
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 10)
plt.plot(xcorr)
plt.title(title)

# 11. corr_y1_y1
title = "corr_y1_y1"
xcorr = np.abs(signal.correlate(y1, y1, "full"))
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 11)
plt.plot(xcorr)
plt.title(title)

# 12. corr_y2_y2
title = "corr_y2_y2"
xcorr = np.abs(signal.correlate(y2, y2, "full"))
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 12)
plt.plot(xcorr)
plt.title(title)

# 13. corr_y1_y1 n
title = "corr_y1_y1 n"
xcorr = np.abs(signal.correlate(y1n, y1n, "full"))
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 13)
plt.plot(xcorr)
plt.title(title)

# 14. corr_y2_y2 n
title = "corr_y2_y2 n"
xcorr = np.abs(signal.correlate(y2n, y2n, "full"))
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 14)
plt.plot(xcorr)
plt.title(title)

def cross_corr(y1, y2):
    print("Getting normalized y2")
    y2_normalized = (y2 - y2.mean()) / y2.std() / np.sqrt(y2.size)
    print("Getting y1_m")
    y1_m = signal.correlate(y1, np.ones(y2.size), 'valid') ** 2 / y2_normalized.size
    # y1_m = np.convolve(y1, np.ones(y2_normalized.size), 'valid') ** 2 / y2_normalized.size
    print("Getting y1_m2")
    y1_m2 = signal.correlate(y1 ** 2, np.ones(y2.size), "valid")
    # y1_m2 = np.convolve(y1 ** 2, np.ones(y2_normalized.size), 'valid')
    print("Getting cross correlation")
    cross_correlation = signal.correlate(y1, y2_normalized, "valid") / np.sqrt(y1_m2 - y1_m)
    # cross_correlation = np.convolve(y1, y2_normalized, 'valid') / np.sqrt(y1_m2 - y1_m)
    return cross_correlation

# 15. Convolution
title = "Convolution"
xcorr = cross_corr(y1, y2)
print(str(title) + " · " + str(time_elapsed) + " · " + str(np.max(xcorr)) + "\n" + str(xcorr) + "\n")
plt.subplot(spv, sph, 15)
plt.plot(xcorr)
plt.title(title)
plt.show()

print("MAX Y1:", np.max(corr_y1_y1))
print("HALF Y1:", corr_y1_y1[int(len(corr_y1_y1)/2)])
print("MAX Y2:", np.max(corr_y2_y2))
print("HALF Y2:", corr_y2_y2[int(len(corr_y2_y2)/2)])
print("SQRT MAX Y1 * MAX Y2:", np.sqrt(np.max(corr_y1_y1) * np.max(corr_y2_y2)))
print("SQRT HALF Y1 * HALF Y2:", np.sqrt(corr_y1_y1[int(len(corr_y1_y1)/2)] * corr_y2_y2[int(len(corr_y2_y2)/2)]))

xcorr = signal.correlate(y1, y2, mode="full")

print("MAX XCORR:", np.max(xcorr))
print("HALF XCORR:", xcorr[int(len(xcorr)/2)])
print("MAX XCORR / MAX Y1:", np.max(xcorr)/np.max(corr_y1_y1))
print("MAX XCORR / MAX Y2:", np.max(xcorr)/np.max(corr_y2_y2))
print("MAX XCORR / HALF Y1:", np.max(xcorr)/corr_y1_y1[int(len(corr_y1_y1)/2)])
print("MAX XCORR / HALF Y2:", np.max(xcorr)/corr_y2_y2[int(len(corr_y2_y2)/2)])
