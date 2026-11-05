# How it works

This page is a file, `gravitational_lensing_help.md`, beside the program. Its first section is the intro of the tab "Explore"; the rest explains the model.

## Explore

A mass in the foreground bends the light of a galaxy behind it: the same galaxy becomes a ring, two images, an arc, or four images.

The left sky is the galaxy as it is, in the *source plane*. The right sky is what a telescope sees, through the lens. Drag the yellow dot to move the galaxy, the blue dot to move the lens, and watch the right sky. The presets set up the classic cases, and the knobs change the galaxy's size and tilt, the lens's strength (its *Einstein radius*) and its kind.

The thin dotted line in the right sky is the *critical curve*: there, the lens magnifies without limit. The dotted line in the left sky is the *caustic*, its image in the source plane. Move the galaxy across the caustic: two images are born, or merge and vanish. Hover a pixel of the right sky: a cross in the left sky shows where its light comes from. Hover the left sky: the pixels that show that point light up on the right.

## The lens equation

A thin lens, at a single distance, bends a ray by an angle that depends only on where the ray crosses the lens plane. For a point mass, the deflection is `theta_E^2 / r`, where `r` is the ray's distance from the mass in the sky and `theta_E` the *Einstein radius*: the radius of the ring made by a source right behind the lens. The light we see at the angle `theta` comes from the source-plane position `beta`:

`beta = theta - theta_E^2 * (theta - L) / |theta - L|^2`

with `L` the lens's position. For a galaxy, modeled as an *isothermal sphere*, the deflection has a constant size, `theta_E`, whatever the distance: the arcs are flatter and longer. The *shear* adds the pull of the lens's neighbors, a stretch of the sky along one axis: the caustic opens into a diamond, and a source inside it shows four times, the Einstein Cross. A second lens adds its own deflection.

## Backward ray mapping

The program does not follow rays from the galaxy. For each pixel of the observed sky it asks where its light comes from, by the lens equation, and reads the galaxy's brightness there. Several pixels can read the same point of the galaxy: those are the multiple images. Lensing keeps the surface brightness (a lensed pixel is as bright as the point it shows) and changes the apparent area: the light that reaches us grows with the area. The bars under "Light" compare the light of the galaxy as it is with the light through the lens, integrated over the sky shown.

The display stretches the brightness as astronomers do (an asinh stretch), so that the faint arms and the bright bulge show together: the "Exposure" knob sets it. The measures use the unstretched light.

## Critical curves and caustics

The mapping from the observed sky to the source plane shrinks or stretches each small patch. Where it shrinks a patch to nothing, a point of the source fills a whole area of the sky: the magnification diverges. These points form the *critical curve*. Its image by the mapping, in the source plane, is the *caustic*. A source on one side of the caustic makes two images fewer than on the other side: crossing it, two images appear together on the critical curve, then separate.

The program finds the critical curve on its grid, where the sign of the mapping's Jacobian changes between neighboring cells, then maps those points to the source plane. For a point mass, the critical curve is the Einstein ring and the caustic is a single point. For a galaxy with shear, the caustic is the diamond with four cusps. For two lenses, the curves join and grow cusps.

## The unit

The angles are in an arbitrary unit. In the real sky, the Einstein radius is 1.75 arcseconds for a ray grazing the Sun (the bending measured in 1919), about one arcsecond for a galaxy lensing a quasar, tens of arcseconds for a cluster of galaxies, and a milliarcsecond for a star lensing another star, far too small to resolve: only the brightening is seen, a *microlensing* event.

## Limits

The model is static, thin and dimensionless: no distances, no redshifts, no time delays between the images, no motion. Near a cusp of the caustic, the magnification measured on the grid depends on its resolution. The galaxy is synthetic.

## Real skies

- The Einstein Cross, Q2237+0305: a quasar seen four times through a galaxy (ESA/Hubble).
- The Cosmic Horseshoe, LRG 3-757: a nearly complete ring around a galaxy (ESA/Hubble).
- Abell 370: the giant arc of a cluster of galaxies, the first one recognized, in 1987 (NASA/ESA).
- Michael Friendly's "Re-Visions" are for Minard; here the reference is Peter Schneider, Jürgen Ehlers and Emilio Falco, *Gravitational Lenses* (Springer, 1992), and the review by Ramesh Narayan and Matthias Bartelmann, *Lectures on Gravitational Lensing* (1996).
