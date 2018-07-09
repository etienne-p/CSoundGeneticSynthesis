import os, subprocess
from csound_reference import header, wavetable_declarations

def lerp(a, b, t):
	return a + (b - a) * t

def clip(x, a, b):
	return min(max(a, x), b)

def clean_dir(dirpath):
	for filename in os.listdir(dirpath):
		filepath = os.path.join(dirpath, filename)
		os.remove(filepath)

def render_audio(instr, dur, filename, sync=True):
	# file contents
	orc = '\n'.join([header, wavetable_declarations, instr])
	sco = 'i1 0 ' + str(dur)
	# write temporary orc and sco files
	with open(filename + '.orc', 'w') as f:
		f.write(orc)
	with open(filename + '.sco', 'w') as f:
		f.write(sco)
	# render audio with CSound
	args = ['csound', '-W', '-o', filename + '.wav', filename + '.orc', filename + '.sco']
	if sync:
		return subprocess.call(args)
	return subprocess.Popen(args)

def wait_for_processes_completion(processes):
	while True:
		all_done = True
		for p in processes:
			if p.poll() is None:
				all_done = False
				break
		if all_done:
			return
