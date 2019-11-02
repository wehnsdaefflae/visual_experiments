##### embedding structure in value noise

###### image

16 = 2 * 8
an embedded cross in a 16x16x16 noise cube 


###### related work

perlin noise

simplex noise

it's fracking Value noise

###### problem with regular noise functions

symptom
show minecraft (image), where biome variation muddies out on a large enough map

explanation
variations only at one frequency, this
means no variation at higher or lower levels of detail

frequencies can be combined, but this combination must be predefined
therefore there are always levels without detail


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