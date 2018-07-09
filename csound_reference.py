# note we work with mono sound
header = '''
sr = 44100\n
ksmps = 32\n
nchnls = 1\n
0dbfs = 1\n
'''

# http://write.flossmanuals.net/csound/d-function-tables/
wavetables = ['giSine', 'giSaw', 'giSquare', 'giTri', 'giImp']
wavetable_declarations = '''
giSine    ftgen     0, 0, 2^10, 10, 1\n
giSaw     ftgen     0, 0, 2^10, 10, 1, 1/2, 1/3, 1/4, 1/5, 1/6, 1/7, 1/8, 1/9\n
giSquare  ftgen     0, 0, 2^10, 10, 1, 0, 1/3, 0, 1/5, 0, 1/7, 0, 1/9\n
giTri     ftgen     0, 0, 2^10, 10, 1, 0, -1/9, 0, 1/25, 0, -1/49, 0, 1/81\n
giImp     ftgen     0, 0, 2^10, 10, 1, 1, 1, 1, 1, 1, 1, 1, 1\n
'''

class OpTag:
	OSC = 0
	RAND = 1
	ENV = 2
	DELAY = 3
	FILTER = 4
	REVERB = 5
	MATH = 6
	def __init__(self, value):
		self.value = value

# from CSound FLOSS manual
# see http://floss.booktype.pro/csound/overview/
opcodes = [
	# OSCILLATORS AND PHASORS
	OpTag(OpTag.OSC),
	# Standard Oscillators
	'ares oscil  xamp:[0,1], xcps:f, ifn:w, iphs:[0,1]',
	'kres oscil  kamp:[0,1], kcps:f, ifn:w, iphs:[0,1]',
	'ares oscili xamp:[0,1], xcps:f, ifn:w, iphs:[0,1]',
	'kres oscili kamp:[0,1], kcps:f, ifn:w, iphs:[0,1]',
	'ares poscil aamp:[0,1], acps:f, ifn:w, iphs:[0,1]',
	'ares poscil aamp:[0,1], kcps:f, ifn:w, iphs:[0,1]',
	'ares poscil kamp:[0,1], acps:f, ifn:w, iphs:[0,1]',
	'ares poscil kamp:[0,1], kcps:f, ifn:w, iphs:[0,1]',
	'ires poscil kamp:[0,1], kcps:f, ifn:w, iphs:[0,1]',
	'kres poscil kamp:[0,1], kcps:f, ifn:w, iphs:[0,1]',

	# Dynamic Sprectrum Oscillators
	'ares buzz xamp:[0,1], xcps:f, knh:(1,2,3,4,5,6), ifn:w, iphs:[0,1]',
	'ares gbuzz xamp:[0,1], xcps:f, knh:(1,2,3,4,5,6), klh:[-4,4], kmul:[0,1], ifn:w, iphs:[0,1]',
	'ares mpulse kamp:[0,1], kintvl:fr',
	'ares vco xamp:[0,1], xcps:f, iwave:w, kpw:[0,1]',
	'ares vco2 kamp:[0,1], kcps:f, imode:(0,2,4,6,10,12), kpw:[0,1], kphs:[0,1]',

	# Phasors
	'ares phasor xcps:f, iphs:[0,1]',
	'kres phasor kcps:f, iphs:[0,1]',

	# RANDOM AND NOISE GENERATORS
	OpTag(OpTag.RAND),
	'ares rand xamp:[0,1]',
	'kres rand xamp:[0,1]',
	'ares randi xamp:[0,1], xcps:f',
	'kres randi kamp:[0,1], kcps:f',
	'ares randh xamp:[0,1], xcps:f',
	'kres randh kamp:[0,1], kcps:f',

	# ENVELOPES
	OpTag(OpTag.ENV),
	# Simple Standard Envelopes
	'ares linen xamp:[0,1], irise:t, idur:t, idec:t',
	'kres linen kamp:[0,1], irise:t, idur:t, idec:t',
	'ares adsr iatt:t, idec:t, islev:[0,1], irel:t, idel:t',
	'kres adsr iatt:t, idec:t, islev:[0,1], irel:t, idel:t',
	'ares madsr iatt:t, idec:t, islev:[0,1], irel:t, idel:t',
	'kres madsr iatt:t, idec:t, islev:[0,1], irel:t, idel:t',

	# Envelopes By Linear And Exponential Generators 
	# as we do not handle optional arguments we use explicit overloads
	'ares linseg ia:[0,1], idur1:t, ib:[0,1], idur2:t, ic:[0,1]',
	'kres linseg ia:[0,1], idur1:t, ib:[0,1], idur2:t, ic:[0,1]',
	'ares linseg ia:[0,1], idur1:t, ib:[0,1], idur2:t, ic:[0,1], idur3:t, id:[0,1]',
	'kres linseg ia:[0,1], idur1:t, ib:[0,1], idur2:t, ic:[0,1], idur3:t, id:[0,1]',
	'ares linseg ia:[0,1], idur1:t, ib:[0,1], idur2:t, ic:[0,1], idur3:t, id:[0,1], idur4:t, ie:[0,1]',
	'kres linseg ia:[0,1], idur1:t, ib:[0,1], idur2:t, ic:[0,1], idur3:t, id:[0,1], idur4:t, ie:[0,1]',
	'ares linseg ia:[0,1], idur1:t, ib:[0,1], idur2:t, ic:[0,1], idur3:t, id:[0,1], idur4:t, ie:[0,1], idur5:t, if:[0,1]',
	'kres linseg ia:[0,1], idur1:t, ib:[0,1], idur2:t, ic:[0,1], idur3:t, id:[0,1], idur4:t, ie:[0,1], idur5:t, if:[0,1]',
	'ares linseg ia:[0,1], idur1:t, ib:[0,1], idur2:t, ic:[0,1], idur3:t, id:[0,1], idur4:t, ie:[0,1], idur5:t, if:[0,1], idur6:t, ig:[0,1]',
	'kres linseg ia:[0,1], idur1:t, ib:[0,1], idur2:t, ic:[0,1], idur3:t, id:[0,1], idur4:t, ie:[0,1], idur5:t, if:[0,1], idur6:t, ig:[0,1]',
	# Zero is illegal for exponentials
	'ares expseg ia:[.05,1], idur1:t, ib:[.05,1], idur2:t, ic:[.05,1]',
	'kres expseg ia:[.05,1], idur1:t, ib:[.05,1], idur2:t, ic:[.05,1]',
	'ares expseg ia:[.05,1], idur1:t, ib:[.05,1], idur2:t, ic:[.05,1], idur3:t, id:[.05,1]',
	'kres expseg ia:[.05,1], idur1:t, ib:[.05,1], idur2:t, ic:[.05,1], idur3:t, id:[.05,1]',
	'ares expseg ia:[.05,1], idur1:t, ib:[.05,1], idur2:t, ic:[.05,1], idur3:t, id:[.05,1], idur4:t, ie:[.05,1]',
	'kres expseg ia:[.05,1], idur1:t, ib:[.05,1], idur2:t, ic:[.05,1], idur3:t, id:[.05,1], idur4:t, ie:[.05,1]',
	'ares expseg ia:[.05,1], idur1:t, ib:[.05,1], idur2:t, ic:[.05,1], idur3:t, id:[.05,1], idur4:t, ie:[.05,1], idur5:t, if:[.05,1]',
	'kres expseg ia:[.05,1], idur1:t, ib:[.05,1], idur2:t, ic:[.05,1], idur3:t, id:[.05,1], idur4:t, ie:[.05,1], idur5:t, if:[.05,1]',
	'ares expseg ia:[.05,1], idur1:t, ib:[.05,1], idur2:t, ic:[.05,1], idur3:t, id:[.05,1], idur4:t, ie:[.05,1], idur5:t, if:[.05,1], idur6:t, ig:[0,1]',
	'kres expseg ia:[.05,1], idur1:t, ib:[.05,1], idur2:t, ic:[.05,1], idur3:t, id:[.05,1], idur4:t, ie:[.05,1], idur5:t, if:[.05,1], idur6:t, ig:[0,1]',

	# DELAYS
	OpTag(OpTag.DELAY),
	# Audio Delays
	'ares delay asig, idlt:[0,1]',
	# Control Signal Delays
	'kr delayk ksig, idel:t, imode:(0,1,2)',

	# FILTERS
	OpTag(OpTag.FILTER),
	# Low Pass Filters
	'ares tone asig, khp:f',
	'ares tonex asig, khp:f, inumlayer:(2,4,6)',
	'ares tonex asig, ahp:f, inumlayer:(2,4,6)',
	'ares butterlp asig, kfreq:f',
	'ares butterlp asig, afreq:f',

	# High Pass Filters
	'ares atone asig, khp:f',
	'ares atonex asig, khp:f, inumlayer:(2,4,6)',
	'ares atonex asig, ahp:f, inumlayer:(2,4,6)',
	'ares butterhp asig, kfreq:f',
	'ares butterhp asig, afreq:f',

	# Band Pass And Resonant Filters
	'ares reson asig, xcf:f, xbw:fd, iscl:(0,1,2)',
	'ares resonx asig, xcf:f, xbw:fd, inumlayer:(2,4,6), iscl:(0,1,2)',
	'ares resony asig, kbf:f, kbw:fd, inum:(2,4,6), ksep:(1,2,3), isepmode:(0,1), iscl:(0,1,2)',
	'ares resonr asig, xcf:f, xbw:fd, iscl:(0,1,2)',
	'ares resonz asig, xcf:f, xbw:fd, iscl:(0,1,2)',
	'ares butterbp asig, xfreq:f, xband:fd',

	# Band Reject Filters
	'ares areson asig, kcf:f, kbw:fd, iscl:(0,1,2)',
	'ares areson asig, acf:f, kbw:fd, iscl:(0,1,2)',
	'ares areson asig, kcf:f, abw:fd, iscl:(0,1,2)',
	'ares areson asig, acf:f, abw:fd, iscl:(0,1,2)',
	'ares butterbp asig, xfreq:f, xband:fd',

	# REVERB
	OpTag(OpTag.REVERB),
	# note: we use constants to feed time params 
	# as the system as it is does not guarantee value ranges except for constants
	'ares reverb asig, irvt:t',
	'ares nreverb asig, itime:t, ihdif:[0,1]',

	# MATH
	OpTag(OpTag.MATH),
	'ares mac ksig1:[0,1], asig1',
	'ares mac ksig1:[0,1], asig1, ksig2:[0,1], asig2',
	'ares mac ksig1:[0,1], asig1, ksig2:[0,1], asig2, ksig3:[0,1], asig3',
	'ares mac ksig1:[0,1], asig1, ksig2:[0,1], asig2, ksig3:[0,1], asig3, ksig4:[0,1], asig4',
	'ares mac ksig1:[0,1], asig1, ksig2:[0,1], asig2, ksig3:[0,1], asig3, ksig4:[0,1], asig4, ksig5:[0,1], asig5',

	'ares maca asig1, asig2',
	'ares maca asig1, asig2, asig3',
	'ares maca asig1, asig2, asig3, asig4',
	'ares maca asig1, asig2, asig3, asig4, asig5',

	'ares product asig1, asig2',
	'ares product asig1, asig2, asig3',
	'ares product asig1, asig2, asig3, asig4',
	'ares product asig1, asig2, asig3, asig4, asig5',

	'ares sum asig1',
	'ares sum asig1, asig2',
	'ares sum asig1, asig2, asig3',
	'ares sum asig1, asig2, asig3, asig4',
	'ares sum asig1, asig2, asig3, asig4, asig5',

	# RATE CONVERSION
	#OpTag(OpTag.RESAMP),
	#'kres downsamp asig',
	#'ares upsamp ksig',
	#'ares interp ksig',
	]
