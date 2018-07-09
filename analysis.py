import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
import numpy as np

def spectrogram_from_file(filename, save_path=None):
	win_len = 256
	sample_rate, samples = None, None
	try:
		sample_rate, samples = wavfile.read(filename)
	except:
		print('failed to read audio file:', filename)
		return None, None, None
	# in some cases sound generation may have failed or produced an unusable tiny file
	if len(samples) < win_len:
		return None, None, None
	# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html
	frequencies, times, spectrogram = signal.spectrogram(
		samples, sample_rate, nperseg=win_len, nfft=win_len, scaling='spectrum')\
	# save spectrogram figure
	if save_path is not None:
		plt.imshow(spectrogram)
		plt.ylabel('Frequency')
		plt.xlabel('Time')
		plt.savefig(save_path)
	return times, frequencies, spectrogram

def sound_similarity(spec1, spec2):
	assert(spec1.shape[0] == spec2.shape[0]), \
		'sound_similarity requires both spectrums have the same number of frequencies'
	# spectrograms may different lengths
	l = min(spec1.shape[1], spec2.shape[1])
	# we do not want to reward empty sounds therefore we add to the divisor 
	# the count of entries where both spectrums are zero
	#nz = np.count_nonzero((spec1[:,:l] + spec2[:,:l])<1e-8)
	dist = np.sum(np.square(spec1[:,:l] - spec2[:,:l]))
	#norm_dist = dist / spec2.size
	return spec2.size / dist
