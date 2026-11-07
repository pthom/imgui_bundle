# How it works

This page is a file, `medical_imaging_help.md`, beside the program. The program shows its sections as the intros of the tabs and as the help of the widgets, the (i) buttons. Below, the page embeds the code it explains, taken live from `medical_imaging.py`: the prose and the code stay in their own files, and the page shows them together. This is *narrative programming*, a feature of [RichMd](https://github.com/pthom/imgui_rich_md), the markdown library of Dear ImGui Bundle ([its presentation](https://github.com/pthom/imgui_rich_md/blob/main/docs/narrative_programming/narrative_programming.md)).

## Chest CT

A real chest scan: scroll through its slices, change their contrast, click an organ to measure it in 3D.

A CT scan (computed tomography) measures, slice after slice, how much each small cube of the body absorbs X-rays. Change the contrast of the slices as radiologists do, and click an organ: the app outlines it on every slice, measures its volume, and shows it in 3D.

The same steps, at a larger scale and with stronger methods, start many research tools: following a nodule over time, measuring a lung before surgery, planning an operation in 3D, preparing data to train a model. This demo shows them simply, with no learning. For research and teaching, not for diagnosis.

The scan is LIDC-IDRI-0001, from the LIDC-IDRI collection (Armato et al., 2015), published by The Cancer Imaging Archive under the CC BY 3.0 license. It is made lighter for the web: one slice in two, 5 mm apart, from the kidneys up, at half resolution (1.4 mm per pixel).

### Slices and views

The slices go from the kidneys (slice 0) to the neck (slice 58), 5 mm apart. The arrows step one slice at a time, which is easier with a finger.

- *Original, in HU*: the slice, its grays set by the window. On a desktop, hover a pixel to read its value in Hounsfield units; zoom in far, and each pixel shows its value.
- *Window and segmentation*: the same slice, with the region in blue and its seed as a yellow cross.

The two views zoom and pan together: the mouse wheel zooms, a drag pans. They show the slice as radiologists look at it: the patient's right on the image's left, the front at the top.

The switch above them shows both views, or one alone, larger, or the region in 3D. A phone shows one at a time.

### Window

A CT gives values from -1000 (air) to more than +2000 (dense bone), while a screen shows 256 levels of gray, and the eye tells fewer apart. A *window* shows one part of that range: what lies below it is black, what lies above it is white.

The presets are the radiologists' usual ones:

| Preset | Level | Width | Shows |
|---|---|---|---|
| Lung | -600 | 1500 | the lung tissue and its vessels |
| Mediastinum | 40 | 400 | the heart, the vessels, the fat, the lymph nodes |
| Bone | 400 | 1800 | the bones and their structure |
| Full range | 500 | 3000 | everything, with little contrast |

[Windowing, on Radiopaedia](https://radiopaedia.org/articles/windowing-ct)

### Level and width

The *level* is the center of the window, the *width* its span, both in Hounsfield units (HU).

The Hounsfield scale measures how much a tissue absorbs X-rays, relative to water: water is 0 HU and air -1000 HU. Fat is about -100 HU, soft tissues and blood +20 to +80 HU, bone +300 to +2000 HU. [The Hounsfield scale, on Wikipedia](https://en.wikipedia.org/wiki/Hounsfield_scale)

### Histogram

How many pixels of the slice have each value, in HU, on a logarithmic scale. Its peaks are the air of the lungs (near -850 HU), the fat (near -100 HU), and the soft tissues and blood (0 to +60 HU). The gray ramp is the window: drag its yellow bounds to change it. The region's pixels are in blue.

### Segmentation

Click a structure in either view: a region grows from that point, the *seed*. It takes the neighboring pixels whose values lie within the tolerance of the seed's value, then their neighbors, and so on. From one slice to the next, it goes on where the region of the slice before touches it.

This is *region growing*, one of the simplest segmentation methods. Real tools add constraints on the shape, or use trained models. [Region growing, on Wikipedia](https://en.wikipedia.org/wiki/Region_growing)

### Examples

Three seeds to try, each with its tolerance:
- *Right lung*, *Left lung*: the air of the lungs, -900 HU or so, with a tolerance of 300 HU. The two lungs meet through the airways, so a region may spill a little into the other lung.
- *Nodule*: a small round mass of the left lung, against its back wall, with a tolerance of 100 HU. With 300 HU, the region leaks into the chest wall: try it.

### Tolerance

The region takes the pixels within this many HU of the seed's value. Too small, and it stops at the slightest change; too large, and it leaks into the next organ.

### Measures

- *Area*: the region's pixels on this slice, times the area of a pixel (1.4 x 1.4 mm).
- *Volume*: the region's voxels on all the slices, times the volume of a voxel (1.4 x 1.4 x 5 mm, about 10 mm³).

With slices 5 mm apart, a small structure is measured coarsely: the nodule spans three slices.

### In 3D

Points of the region's surface, at most 6000, shaded by the way they face the light. The yellow plane is the current slice. Right-drag to rotate (two fingers on a phone), left-drag to move, the wheel zooms; a double click with the right button resets the rotation.

## Retina

The blood vessels of a retina, found and measured by classic image processing: tune each step, see its effect.

A fundus photograph shows the back of the eye through the pupil: the retina, its blood vessels, the optic disc (the bright spot at the left, where the optic nerve leaves) and the macula (the darker center, which gives the sharp vision). The vessels' width, branching and course help study diabetes, high blood pressure and other diseases. Here, classic image processing finds them, with no learning.

The photograph: "Fundus photograph of normal left eye", by Mikael Häggström, on Wikimedia Commons, in the public domain (CC0).

### Green channel

The vessels absorb green light more than the retina around them: they contrast most in the green channel of the photograph. The red channel is too bright, the blue one too dark and noisy.

### CLAHE

*Contrast Limited Adaptive Histogram Equalization* raises the contrast in each small tile of the image, so that the faint vessels of a dark area show as well as those of a bright one. The clip limits the gain: higher shows fainter vessels, and more noise. [CLAHE, on Wikipedia](https://en.wikipedia.org/wiki/Adaptive_histogram_equalization)

### Top-hat

A *black top-hat* keeps the dark details thinner than its size, and drops the slow changes of the background's brightness: what stays is mostly the vessels. A larger size keeps the wider vessels; too large, and other dark shapes come in. [Top-hat transform, on Wikipedia](https://en.wikipedia.org/wiki/Top-hat_transform)

### Threshold

The pixels of the top-hat above this value are taken as vessels. Lower finds finer vessels, and more noise.

### Min. area

The groups of vessel pixels smaller than this many pixels are dropped: they are noise, mostly.

### Stages

What the second view shows: each stage of the pipeline, in order, the vessels over the photograph (*Overlay*), or their measures (*Measure*).

### Measure

The vessels' map becomes lines one pixel wide, its *skeleton*, cut at each branching into segments. Click a vessel: its segment shows in yellow, with its measures. The largest segments carry a number.

- *Width*: across the vessel, the top-hat's profile; the width is the span where it stays above half of its peak (the *full width at half maximum*), the median along the segment.
- *Length*: along the skeleton.
- *Position*: from the center of the optic disc, in disc diameters, and the quadrant: superior or inferior, temporal (toward the macula) or nasal.

The scale comes from the optic disc, the yellow circle: its diameter, about 100 pixels on this photograph, is taken as 1.8 mm, a typical value (it varies from about 1.5 to 2.2 mm between people). So the µm and the mm are rough: a clinical measure needs a calibrated camera and validated software. Here, they show the method.

### Vessels' share

The share of the field of view (the lit disc) that the vessels take. It depends on every setting: two photographs compare only with the same settings and the same camera.

## The code

The steps above, as the program does them. Each block below comes from `medical_imaging.py`, live.

### The window

The slice's values become grays: the window's bottom is black, its top white.

![[medical_imaging.py#Window]]

### Region growing

Each slice is cut into its connected groups of pixels within the tolerance (OpenCV's connected components). The seed's group starts the region; on the next slice, the groups that touch the region carry it on.

![[medical_imaging.py#Region growing]]

### The surface in 3D

A voxel of the region is on its surface when one of its six neighbors is outside. The region, blurred, gives the direction of the surface at each point, and the light its shade.

![[medical_imaging.py#Surface points]]

### The vessels

The pipeline of the Retina tab, in a few OpenCV calls.

![[medical_imaging.py#Vessels]]

### The skeleton

The vessels' map, peeled layer after layer until each vessel is a line one pixel wide: Zhang and Suen's thinning, in numpy.

![[medical_imaging.py#Skeleton]]

### The width at half height

Across the vessel, at each point of its skeleton: the profile of the top-hat, and the span where it stays above half of its peak.

![[medical_imaging.py#Width]]
