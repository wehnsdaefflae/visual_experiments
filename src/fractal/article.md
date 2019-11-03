##### improving value noise


###### image

minecraft map zooming out image


###### abstract

Simplex noise (source) is the de facto standard noise procedure used in various generative 
design tasks. It's hardware friendly implementation, scalability into higher dimensions, and organic 
appearance make a versatile tool that can be used as part of a plethora of tried and tested 
digital art workflows to add an organic touch to designs. Despite its well earned 
success, however, it has some limitations that, once noticed, show up in all kinds of works 
where it has been used.

Due to the recent renaissance of MineCraft, it seems fitting to use 
it as a showcase for this limitation. It is important to note, that what I call 
\enquote{limitation} was in fact never intented to be overcome by noise algorithms themselves.
Solid arguments can be brought forward that this is in fact not to be solved by the noise function
itself but rather by a clever combilation and recombination of different approaches (as it is the 
case with many other limitations of individual noise functions). Nonetheless I feel that to 
extend the concept of noise might be an endeavour worth pursuing.


###### problem with regular noise functions

symptom
show minecraft (image), where biome variation muddies out on a large enough map

explanation
variations only at one frequency, this
means no variation at higher or lower levels of detail

frequencies can be combined, but this combination must be predefined
therefore there are always levels without detail


###### related work

it's fracking value noise

problem of value noise is that maxima are in regular intervalls. 
this leads to recogniseable grid patterns

one way to overcome is perlin noise and its improvement simplex noise.
both dealing with gradients rather than scalar values.

this paper proposes a way to overcome the shortcomings of value noise without gradients.
this makes it easier, for example, to integrate structure into noise, 
so as to generate smooth transitions between random structures and manually designed ones.


###### image

16 = 2 * 8
an embedded cross in a 16x16x16 noise cube 


###### conditions for solution

runtime feasible

can be used like traditional noise

introduces new frequencies "on the fly" while maintaining value consistency over different scales

wrappable


###### solution

noise canvas

zoom in or out

fill gaps noisily

brownian bridging affords itself, problem: only defined in one dimension

approach: implement n-dimensional brownian bridging

requires: space-filling curve (?)


###### applications

continuous map generation at various scales at the same time without loss in variation

in general: restriction of random generation and skewing or biasing noise towards manually designed structure



###### problems

lattice structure can be recognised, remedy: overlaying and offsetting different noise tiles at the expense of increasing a constant

zooming in works nice. zooming out generates artefacts: regions of high frequency at regions of previously generated structures

slower than simplex noise. runtime is O(2^d)