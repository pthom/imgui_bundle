"""A tiny neural network in numpy: two inputs, one hidden layer, one output (a probability).

Its explanation lives next to its code, in ::md sections (narrative programming, see imgui_rich_md).
neural_spiral.py places them in its story: ![[tiny_nn.py#Network]] for the prose of a section,
![[tiny_nn.py#Network#code]] for its code. This file does not depend on ImGui.
"""
from dataclasses import dataclass
import numpy as np


r"""::md Network
### The network
A point $x = (x_1, x_2)$ goes through $H$ hidden units, then one output unit:
$$p = \sigma(\tanh(x W_1 + b_1) W_2 + b_2)$$
Each hidden unit draws a line in the plane, where $x W_1 + b_1 = 0$, and tells on which side of it the point is:
$\tanh$ goes smoothly from $-1$ to $1$ across the line. The output unit weighs these answers, and the sigmoid
$\sigma(s) = 1 / (1 + e^{-s})$ turns their sum into $p$, the probability that the point is of class 1.
Learning is choosing the weights $W_1, b_1, W_2, b_2$. They start at random.
::code
"""
@dataclass
class Network:
    w1: np.ndarray  # (2, H)
    b1: np.ndarray  # (H,)
    w2: np.ndarray  # (H,)
    b2: float


def random_network(hidden: int, rng: np.random.Generator) -> Network:
    return Network(rng.normal(0, 1, (2, hidden)), rng.normal(0, 0.5, hidden),
                   rng.normal(0, 1 / np.sqrt(hidden), hidden), 0.0)


def forward(net: Network, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """n points x (n, 2) -> the answers of the hidden units h (n, H), the probabilities p (n,)"""
    h = np.tanh(x @ net.w1 + net.b1)
    p = 1 / (1 + np.exp(-(h @ net.w2 + net.b2)))
    return h, p
# ::endcode


r"""::md Loss
### How wrong is it: the loss
For a point of class $y$ (0 or 1), the network is right when it gives a high probability to $y$. The loss is the
mean of $-\log$ of that probability, the cross-entropy:
$$L = -\frac{1}{n} \sum_i \left( y_i \log p_i + (1 - y_i) \log(1 - p_i) \right)$$
It is 0 when the network is sure and right, and grows without limit when it is sure and wrong.
::code
"""
def loss(p: np.ndarray, y: np.ndarray) -> float:
    p = np.clip(p, 1e-7, 1 - 1e-7)  # log(0) is -infinity
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
# ::endcode


r"""::md Gradients
### Learning: the gradients
To lower the loss, each weight moves the way that lowers it the fastest: against its gradient, the derivative of $L$
with respect to that weight. The chain rule gives them all, from the output back to the input (backpropagation).
With $s = h W_2 + b_2$ the output before the sigmoid, $a = x W_1 + b_1$ the hidden units before $\tanh$, and
$\delta_s$, $\delta_a$ the derivatives of $L$ with respect to them:
$$\delta_s = \frac{p - y}{n} \qquad \delta_a = (\delta_s W_2^T) \odot (1 - h^2)$$
$$\frac{\partial L}{\partial W_2} = h^T \delta_s \qquad \frac{\partial L}{\partial W_1} = x^T \delta_a$$
The gradients of the biases are the sums of $\delta_s$ and $\delta_a$ over the points. $\delta_s$ is short because
the sigmoid and the cross-entropy simplify each other, and $1 - h^2$ is the derivative of $\tanh$.
::code
"""
def gradients(net: Network, x: np.ndarray, y: np.ndarray) -> Network:
    """The derivatives of the loss, one per weight: a Network of their own"""
    h, p = forward(net, x)
    ds = (p - y) / len(y)
    da = np.outer(ds, net.w2) * (1 - h * h)
    return Network(w1=x.T @ da, b1=da.sum(axis=0), w2=h.T @ ds, b2=float(ds.sum()))
# ::endcode


r"""::md Step
### One step downhill
Each weight moves against its gradient, by a step proportional to the learning rate $\eta$:
$W \leftarrow W - \eta \, \partial L / \partial W$. Training repeats this step, with all the points each time.
::code
"""
def step(net: Network, x: np.ndarray, y: np.ndarray, rate: float) -> None:
    grad = gradients(net, x, y)
    net.w1 -= rate * grad.w1
    net.b1 -= rate * grad.b1
    net.w2 -= rate * grad.w2
    net.b2 -= rate * grad.b2
# ::endcode
