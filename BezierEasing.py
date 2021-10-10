NEWTON_ITERATIONS = 4
NEWTON_MIN_SLOPE = 0.001
SUBDIVISION_PRECISION = 0.0000001
SUBDIVISION_MAX_ITERATIONS = 10

kSplineTableSize = 11
kSampleStepSize = 1.0 / (kSplineTableSize - 1.0)

def A(aA1, aA2):
    return 1.0 - 3.0 * aA2 + 3.0 * aA1
def B(aA1, aA2):
    return 3.0 * aA2 - 6.0 * aA1
def C(aA1):
    return 3.0 * aA1

# Returns x(t) given t, x1, and x2, or y(t) given t, y1, and y2.
def calcBezier(aT, aA1, aA2):
    return ((A(aA1, aA2) * aT + B(aA1, aA2)) * aT + C(aA1)) * aT

# Returns dx/dt given t, x1, and x2, or dy/dt given t, y1, and y2.
def getSlope(aT, aA1, aA2):
    return 3.0 * A(aA1, aA2) * aT * aT + 2.0 * B(aA1, aA2) * aT + C(aA1)

def binarySubdivide(aX, aA, aB, mX1, mX2):
    i = 0;
    while True:
        currentT = aA + (aB - aA) / 2.0
        currentX = calcBezier(currentT, mX1, mX2) - aX
        if currentX > 0.0:
            aB = currentT
        else:
            aA = currentT
        i += 1
        if not(abs(currentX) > SUBDIVISION_PRECISION and i < SUBDIVISION_MAX_ITERATIONS):
            break
    return currentT;

def newtonRaphsonIterate(aX, aGuessT, mX1, mX2):
    for i in range(NEWTON_ITERATIONS):
        currentSlope = getSlope(aGuessT, mX1, mX2)
        if currentSlope == 0.0:
            return aGuessT
        currentX = calcBezier(aGuessT, mX1, mX2) - aX
        aGuessT -= currentX / currentSlope
    return aGuessT

def LinearEasing(x):
    return x;

def bezier(mX1, mY1, mX2, mY2):
    if not(0 <= mX1 and mX1 <= 1 and 0 <= mX2 and mX2 <= 1):
        raise ValueError('bezier x values must be in [0, 1] range')

    if (mX1 == mY1 and mX2 == mY2):
        return LinearEasing

    # Precompute samples table
    sampleValues = []
    for i in range(kSplineTableSize):
        sampleValues.append(calcBezier(i * kSampleStepSize, mX1, mX2))

    def getTForX(aX):
        intervalStart = 0.0
        currentSample = 1
        lastSample = kSplineTableSize - 1

        while currentSample != lastSample and sampleValues[currentSample] <= aX:
            intervalStart += kSampleStepSize
            currentSample += 1
        currentSample -= 1

        # Interpolate to provide an initial guess for t
        dist = (aX - sampleValues[currentSample]) / (sampleValues[currentSample + 1] - sampleValues[currentSample])
        guessForT = intervalStart + dist * kSampleStepSize

        initialSlope = getSlope(guessForT, mX1, mX2)
        if initialSlope >= NEWTON_MIN_SLOPE:
            return newtonRaphsonIterate(aX, guessForT, mX1, mX2)
        elif initialSlope == 0.0:
            return guessForT
        else:
            return binarySubdivide(aX, intervalStart, intervalStart + kSampleStepSize, mX1, mX2)

    def BezierEasing(x):
        if x == 0 or x == 1:
            return x
        return calcBezier(getTForX(x), mY1, mY2) 

    return BezierEasing