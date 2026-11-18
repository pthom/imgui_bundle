---
title: Grokking
voice: en-US-AndrewMultilingualNeural
defaults:
  over: 1
  delay_after_interaction: 8
---
# Grokking

## Teaser

[[Hide everything: the narration alone]]
```cues
set_value("view", "none")
set_value("clock", 0)
set_value("step", 1000)
set_value("knobs", False)
set_value("pca", False)
```
In this lesson, we will watch a neural network learn a concept. This form of learning is called *grokking*.


[[Show the first figure: it zooms or fades into view occupying the full stage (animation come with the look)]]
```cues
set_value("view", "accuracy")
set_value("step", 1000)
```

[[Rename the labels to "Training Set" and "Hidden Set"]]
When we train a network we use two distinct measures:

[[Highlight the blue line - and make it blink a bit]]
```cues
set_value("accent_line", "seen")
```
- Its accuracy on the examples it was trained on (the training set). It rises fast: the network learns them quickly.

[[Highlight the green line - and make it blink a bit]]
```cues
set_value("accent_line", "hidden")
```
- Its accuracy on the examples it has never seen.

[[Shade the zone where no generalization happens, and play the training up to its end]]
```cues
set_value("zone", "memorizing")
set_value("step", 0)
animate("step", 300, over=5)
```
For a long time, it stays at zero: the network cannot generalize what it learned.

[[Shade the zone where it generalizes, and play the training to the end; then clear the accents]]
```cues
set_value("zone", "grokking")
animate("step", 1000, over=6)
set_value("accent_line", "none", at="even on examples")
set_value("zone", "none", at="even on examples")
```
Then, suddenly, it starts to generalize. Soon it makes no mistake at all, even on examples it has never seen.

How can we explain that the network suddenly *groks* (understands) something about those unknown examples?

[[Back to the two figures; the second one replays the training from chaos to the circle]]
```cues
set_value("view", "curves")
set_value("focus", "clock")
animate("step", 0, over=1, at="The second")
animate("step", 1000, over=8, at="from chaos")
highlight("clock", at="a circle")
```
The second picture shows how the network organizes what it knows, inside its weights. During the training, it goes from chaos to a circle. The network has found a structure.

The answer is in that structure. Nobody taught this network a rule: it found one by itself. Let us go back to the beginning, and watch it happen.

## Adding on a clock

```cues
set_value("view", "full")
set_value("focus", "table")
set_value("step", 0)
set_value("table_view", "split")
```
Here is the task. Take two numbers between zero and fifty-two, and add them. When the sum passes fifty-two, wrap around, as the hand of a clock does: on a clock with fifty-three hours, forty plus twenty is seven.
[[a clock widget: the learner picks two hours, the hand turns, the sum appears. To build; until then, the table.]]

```cues
highlight("table_view", at="The table")
```
The table shows every sum: the row is the first number, the column the second. Two thousand eight hundred and nine sums in all.

Half of them, chosen at random, are shown to the network during its training: the blue cells. The other half is hidden from it: the red cells. That half is the test.

Why fifty-three? It is a prime number, so no shortcut exists: no half table, no simple pattern. The network has to find the rule by itself.

### More: modular arithmetic
Addition modulo 53 is the arithmetic of a clock with 53 hours: $(a + b) \bmod 53$. The same arithmetic, with 12 hours, tells you that nine hours after five o'clock, it is two o'clock.

### Code
![[grok_train.py#Data#code]]

## Learning by heart

```cues
set_value("table_view", "answers")
set_value("focus", "table")
animate("step", 100, over=8, at="Watch the table")
```
The network is shown half of the sums: the grey cells. The other half, in red, stays hidden: that is the test. Watch the table while it trains. Within a hundred steps, every grey cell turns blue.

```cues
highlight("step", at="still red")
pause("Drag the step slider between 100 and 250: nothing changes on the hidden half. Then press Continue.")
```
But the hidden half is still red. The network has learned its half by heart, and has no idea about the rest.

### More: overfitting
A model that fits its training data, but not new data, is said to overfit. Usually, training stops here.

### Code
The training step: the loss, its gradient, and AdamW, which also shrinks every weight a little at each step.
![[grok_train.py#Step#code]]

## Grokking

```cues
set_value("focus", "table")
animate("step", 700, over=12, at="Nothing changes")
```
Nothing changes in the training: the same steps continue, on the same half. And then, slowly at first, the red cells turn green. By step seven hundred, the network answers every sum it has never seen.

```cues
set_value("focus", "clock", at="Look inside")
highlight("clock", at="Look inside")
animate("step", 1000, over=4, at="a circle")
```
Look inside. The 53 numbers, as the network represents them, now sit on a circle: a clock. The network adds by turning hands. There are several such clocks, one per frequency: pick another one below the plot.

### More: the clock explanation
On the plane of frequency $k$, the number $n$ sits at the angle $2 \pi k n / 53$. Adding $a$ and $b$ is adding
angles: $\cos(a + b) = \cos a \cos b - \sin a \sin b$. The network found this trick by itself, pushed by the weight
decay: a memorized table costs large weights, a clock costs small ones (Nanda et al., 2023).

## Experiments

[[The whole stage, with the weight decay and the seed under the table; back on the recorded run]]
```cues
use_recorded()
set_value("knobs", True)
set_value("view", "full")
set_value("table_view", "answers")
set_value("focus", "accuracy")
set_value("step", 1000)
```
Now it is your turn. Above the figures, two knobs: the weight decay, and the seed of the random start. The Train button trains a new network, live, in a few seconds.

[[The first challenge: without the weight decay, no grokking. The voice waits for the training to end.]]
```cues
challenge("Set the weight decay to zero, press Train, and wait for the end of the training.", until="weight_decay == 0 and step >= 1000", hint="The weight decay slider is under the table; Train starts the training.", hint_after=30)
```
Look at the hidden set. Without the weight decay, the network memorizes just as fast, and never groks: the green curve stays at zero. The decay is what pushes the network from the table to the clocks: a memorized table costs large weights, a clock costs small ones.

Try another seed, with the decay back to one. The clocks change frequency; the story does not.

## Looking inside

[[The clock figure, back on the recorded run at its end: the clock of frequency 21]]
```cues
use_recorded()
set_value("knobs", False)
set_value("view", "curves")
set_value("focus", "clock")
set_value("step", 1000)
set_value("pca", False)
set_value("clock", 0)
```
One last question: how did we draw these clocks? Inside the network, each number is a list of thirty-two values. That makes a point in a space of thirty-two dimensions, and nobody can see thirty-two dimensions.

So we look at a shadow. Hold a teapot under a lamp: its shadow on the table is flat, it has two dimensions. Some shadows tell more than others. From the side, you see the spout and the handle. From above, only a round lid.

[[The PCA chip pulses, then the PCA view replaces the clock]]
```cues
highlight("pca", at="principal component")
set_value("pca", True, at="Here is")
```
A classic tool chooses the shadow for us: the principal component analysis, or PCA. It turns the object until its shadow is as wide as possible, because the widest shadow keeps most of the differences between the points. Here is the PCA of our network.

No clock: the numbers look scattered. The network did not build one clock, but four, all about the same size. The widest shadow mixes two of them, like two drawings traced on the same sheet.

[[Back to the clock of frequency 21; the frequency chips pulse]]
```cues
set_value("pca", False, at="Four of them")
highlight("clock", at="Four of them")
```
So we ask a sharper question. For a number k, is there a plane where each number n sits at the hour k times n? The Fourier transform answers it for every k at once. Four of them have a clock: twenty-one, nine, seventeen and seven.

[[The training replays: the colors find their places]]
```cues
set_value("step", 0, at="During the training")
animate("step", 1000, over=8, at="find their places")
```
Each color is an hour on that clock. During the training, the colors find their places around the circle. That is grokking, seen from the inside.

### More: the PCA and the Fourier planes
A PCA keeps the directions where the 53 embeddings vary the most. Here, the first components carry about 11 % of the variance each: several clocks share it, and the first plane of the PCA mixes the clocks of frequencies 21 and 9.

The plane of frequency $k$ is spanned by two directions of the 32-dimensional space: $\sum_n \cos(2 \pi k n / 53)\, e_n$ and $\sum_n \sin(2 \pi k n / 53)\, e_n$, where $e_n$ is the embedding of the number $n$. The frequencies with the most energy in the Fourier transform of the embeddings, along $n$, give the four clocks.

### Code
![[grok_train.py#Clocks#code]]
