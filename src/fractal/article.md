##### embedding structure in noise

###### image

16 = 2 * 8
an embedded cross in a 16x16x16 noise cube 


###### related work

perlin noise

simplex noise


###### problem with regular noise functions

variations only at one frequency, this
means no variation at higher or lower levels of detail

frequencies can be combined, but this combination must be predefined
therefore there are always levels without detail

this shows in games like minecraft, where biome variation muddies out on a large enough map

(image)


###### conditions for solution

runtime feasible

can be used like traditional noise

introduces new frequencies "on the fly" while maintaining value consistency over different scales


###### solution

noise canvas

zoom in or out

fill gaps noisily

brownian bridging affords itself, problem: only defined in one dimension

approach: implement n-dimensional brownian bridging

requires: space-filling curve (?)