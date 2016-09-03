from array import array
import random
import PIL, PIL.Image

POPULATION = 128
GENERATIONS = 128
STYLES = 17
PALETTE = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (0,255,255), (255,0,255), (0,0,0), (255,255,255),
    (255,128,128),(128,255,128),(128,128,255),
    (0,128,255),(128,0,255),(0,255,128),(255,0,128),(128,255,0),(255,128,0)]
NOISE = 60

def make_weights(stuff):
    return[[value] * size for (value, size) in stuff]


WEIGHTS = [
    (2,),
    (1,1,1),
    (),
    (-1,-1,-1,-1,-1),
    (-2,-2,-2,-2,-2,-2,-2),
]

def make_dist_weights(values):
    return[[value] * (i*2+1) for (i,value) in enumerate(values)]

def make_const_dist_weights(dist, values):
    return[[V] * dist for V in values]

WEIGHTS = make_dist_weights((5,4,3,2,1,0,-1,-2,-3,-4,-5))

print(WEIGHTS)

a = array('B', [random.choice(range(STYLES)) for p in range(POPULATION * GENERATIONS)])

for g in range(len(WEIGHTS), GENERATIONS):
    for p in range(POPULATION):
        scores = [0] * STYLES
        for h in range(len(WEIGHTS)):
            for n in range(len(WEIGHTS[h])):
                npos = n - len(WEIGHTS[h]) // 2
                scores[a[(g - h - 1) * POPULATION + ((p + npos) % POPULATION)]] += WEIGHTS[h][n]
        identical = 0
        choice = -1
        best_score = -1000
        for i, s in enumerate(scores):
            s += int(NOISE * random.random())
            if s > best_score:
                identical = 1
                choice = i
                best_score = s
            elif s == best_score:
                identical += 1
                if random.random() * identical < 1:
                    choice = i
        a[g * POPULATION + p] = choice

adjusted_palette = [0] * 256 * 3
for i, color in enumerate(PALETTE):
    for j, component in enumerate(color):
        adjusted_palette[i * 3 + j] = component

image = PIL.Image.frombytes('P', (GENERATIONS, POPULATION), a.tobytes())
image.putpalette(adjusted_palette)

image.save("output.png")
