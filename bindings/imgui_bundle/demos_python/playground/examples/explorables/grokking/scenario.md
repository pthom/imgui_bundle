---
title: Grokking
voice: en-US-AndrewMultilingualNeural
defaults:
  over: 1
  delay_after_interaction: 8
---
# Grokking

## Teaser

```cues
set_value("step", 1000)
set_value("clock", 0)
```
This network learned to add. Nobody told it how.

```cues
highlight("step", at="hidden half")
animate("step", 0, over=4, at="Let's go back")
```
For a long time, it only knew the sums by heart. Then, in a few hundred steps, it found the rule, and the hidden
half of the table turned green. Let's go back to the beginning, and watch it happen.

## Adding on a clock

```cues
set_value("step", 0)
set_value("table_view", "split")
```
Here is the task. Take two numbers between zero and fifty-two, and add them. When the sum passes fifty-two, wrap
around, as the hand of a clock does: on a clock with fifty-three hours, forty plus twenty is seven.
[[a clock widget: the learner picks two hours, the hand turns, the sum appears. To build; until then, the table.]]

```cues
highlight("table_view", at="The table")
```
The table shows every sum: the row is the first number, the column the second. Two thousand eight hundred and nine
sums in all.

Half of them, chosen at random, are shown to the network during its training: the blue cells. The other half is
hidden from it: the red cells. That half is the test.

Why fifty-three? It is a prime number, so no shortcut exists: no half table, no simple pattern. The network has to
find the rule by itself.

### More: modular arithmetic
Addition modulo 53 is the arithmetic of a clock with 53 hours: $(a + b) \bmod 53$. The same arithmetic, with
12 hours, tells you that nine hours after five o'clock, it is two o'clock.

### Code
![[grok_train.py#Data#code]]

## Learning by heart

```cues
set_value("table_view", "answers")
animate("step", 100, over=8, at="Watch the table")
```
The network is shown half of the sums: the blue cells. The other half, in red, stays hidden: that is the test.
Watch the table while it trains. Within a hundred steps, every blue cell is right.

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
animate("step", 700, over=12, at="Nothing changes")
```
Nothing changes in the training: the same steps continue, on the same half. And then, slowly at first, the red
cells turn green. By step seven hundred, the network answers every sum it has never seen.

```cues
highlight("clock", at="Look inside")
animate("step", 1000, over=4, at="a circle")
```
Look inside. The 53 numbers, as the network represents them, now sit on a circle: a clock. The network adds by
turning hands. There are several such clocks, one per frequency: pick another one below the plot.

### More: the clock explanation
On the plane of frequency $k$, the number $n$ sits at the angle $2 \pi k n / 53$. Adding $a$ and $b$ is adding
angles: $\cos(a + b) = \cos a \cos b - \sin a \sin b$. The network found this trick by itself, pushed by the weight
decay: a memorized table costs large weights, a clock costs small ones (Nanda et al., 2023).
