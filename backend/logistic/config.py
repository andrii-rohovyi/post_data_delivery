import sys

MAX_WEIGHT = sys.maxsize
SOLUTION_CALCULATION_MAX_TIME = 1

# average speed for different modes in seconds
MODE_TO_SPEED = {
    'driving': 50 / (60 * 60),
    'walking': 4 * 1.6 / (60 * 60),
    'bicycling': 12 * 1.6 / (60 * 60)
}

# since we're using ORS on the backend side and google on frontend side we must convert one to another
MODE_CONVERTER = {
	'driving': 'driving-car',
	'bicycling': 'cycling-regular',
	'walking': 'foot-walking'
}
