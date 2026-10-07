"""Grokking on addition modulo 53: the model, its training, and the recording of the training path.

The model and the training follow David Louapre's notebook (an embedding, one hidden layer, AdamW with weight decay),
in numpy. Run this file once, on the desktop: it trains in a few seconds, and writes `grokking_data.npz`, the path
the lesson scrubs through (accuracies, the table of right and wrong answers, the embeddings' projection, at every
checkpoint). The explorable `grokking.py` reads that file; it does not train.
"""
import time
from pathlib import Path

import numpy as np

P = 53             # the modulus: the numbers are 0..52, as hours on a clock of 53
D_EMBED = 32       # each number is encoded as a vector of 32 values
HIDDEN = 64        # the hidden layer
LR, WEIGHT_DECAY = 1e-2, 1.0
STEPS = 1000       # full-batch gradient steps (the network groks around step 600 with this seed)
CHECKPOINT_EVERY = 5
SEED = 42
TRAIN_FRACTION = 0.5
CLOCKS = 4         # the recorded clock views: the strongest frequencies of the final embeddings


r"""::md Data
### The task
Every pair $(a, b)$ of numbers below 53, and the answer $(a + b) \bmod 53$: a table of 53 x 53 = 2809 sums. Half of the
pairs, chosen at random, are shown to the network during training. The other half is never shown: it is the test.
::code
"""
def make_data(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """All the pairs with their answers, and a mask of the pairs used for training."""
    pairs = np.array([[a, b, (a + b) % P] for a in range(P) for b in range(P)])
    train_mask = np.zeros(len(pairs), dtype=bool)
    train_mask[rng.permutation(len(pairs))[: int(len(pairs) * TRAIN_FRACTION)]] = True
    return pairs, train_mask
# ::endcode


r"""::md Model
### The network
Each of the two numbers is turned into a vector of 32 values (its *embedding*: a table of 53 vectors, learned). The
two vectors, put side by side, go through one hidden layer of 64 units, then a last layer gives 53 scores, one per
possible answer. The highest score is the network's answer.
::code
"""
def init_params(rng: np.random.Generator) -> dict[str, np.ndarray]:
    def xavier(shape: tuple[int, int]) -> np.ndarray:
        return rng.normal(0, np.sqrt(2.0 / sum(shape)), shape).astype(np.float32)
    return {"E": xavier((P, D_EMBED)), "W1": xavier((2 * D_EMBED, HIDDEN)), "b1": np.zeros(HIDDEN, np.float32),
            "W2": xavier((HIDDEN, P)), "b2": np.zeros(P, np.float32)}


def forward(params: dict[str, np.ndarray], pairs: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The scores of every answer, for every pair (and the intermediate values, for the gradients)."""
    e = np.concatenate([params["E"][pairs[:, 0]], params["E"][pairs[:, 1]]], axis=1)
    h_pre = e @ params["W1"] + params["b1"]
    h = np.maximum(h_pre, 0)
    return e, h_pre, h, h @ params["W2"] + params["b2"]
# ::endcode


r"""::md Step
### One step of training
The loss says how far the scores are from the right answers (cross-entropy). Its gradient says how to change every
weight to lower it; AdamW applies that change, and also shrinks every weight a little at each step (the *weight
decay*). Without the decay, the network memorizes and never groks.
::code
"""
class Trainer:
    def __init__(self, params: dict[str, np.ndarray], lr: float = LR, weight_decay: float = WEIGHT_DECAY) -> None:
        self.params = params
        self.lr, self.weight_decay = lr, weight_decay
        self.m = {k: np.zeros_like(v) for k, v in params.items()}
        self.v = {k: np.zeros_like(v) for k, v in params.items()}
        self.t = 0

    def step(self, pairs: np.ndarray) -> None:
        p = self.params
        e, h_pre, h, logits = forward(p, pairs)
        z = logits - logits.max(1, keepdims=True)
        prob = np.exp(z)
        prob /= prob.sum(1, keepdims=True)
        prob[np.arange(len(pairs)), pairs[:, 2]] -= 1      # the gradient of the cross-entropy, for every score
        g_logits = prob / len(pairs)
        g = {"W2": h.T @ g_logits, "b2": g_logits.sum(0)}
        g_h = (g_logits @ p["W2"].T) * (h_pre > 0)
        g["W1"], g["b1"] = e.T @ g_h, g_h.sum(0)
        g_e = g_h @ p["W1"].T
        g["E"] = np.zeros_like(p["E"])
        np.add.at(g["E"], pairs[:, 0], g_e[:, :D_EMBED])
        np.add.at(g["E"], pairs[:, 1], g_e[:, D_EMBED:])
        self.t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        for k in p:                                          # AdamW
            p[k] *= 1 - self.lr * self.weight_decay
            self.m[k] = b1 * self.m[k] + (1 - b1) * g[k]
            self.v[k] = b2 * self.v[k] + (1 - b2) * g[k] ** 2
            p[k] -= self.lr * (self.m[k] / (1 - b1**self.t)) / (np.sqrt(self.v[k] / (1 - b2**self.t)) + eps)
# ::endcode


def losses(params: dict[str, np.ndarray], pairs: np.ndarray) -> np.ndarray:
    """The cross-entropy of every pair: how far the scores are from its right answer"""
    logits = forward(params, pairs)[3]
    z = logits - logits.max(1, keepdims=True)
    log_prob = z - np.log(np.exp(z).sum(1, keepdims=True))
    return np.asarray(-log_prob[np.arange(len(pairs)), pairs[:, 2]])


r"""::md Clocks
### The clocks inside the network
After training, the 53 embeddings are not scattered at random: for a few frequencies $k$, they lie on a circle when
projected on the plane of $\cos(2 \pi k n / 53)$ and $\sin(2 \pi k n / 53)$, in the order of the multiples of $k$.
Each such plane is a clock, whose hand turns by $k$ hours for each unit added: the network adds by turning hands
(Nanda et al., 2023).
::code
"""
def clock_frequencies(embeddings: np.ndarray, count: int) -> np.ndarray:
    """The frequencies with the most energy in the embeddings (the Fourier transform along the 53 numbers)"""
    spectrum = np.fft.rfft(embeddings - embeddings.mean(0), axis=0)
    power = (np.abs(spectrum) ** 2).sum(1)
    power[0] = 0
    return np.asarray(np.argsort(power)[::-1][:count])


def clock_axes(embeddings: np.ndarray, k: int) -> np.ndarray:
    """Two unit directions of the embedding space: the plane of frequency k"""
    angles = 2 * np.pi * k * np.arange(P) / P
    axes = np.stack([np.cos(angles) @ embeddings, np.sin(angles) @ embeddings])
    return np.asarray(axes / np.linalg.norm(axes, axis=1, keepdims=True))
# ::endcode


def record_path(out: Path) -> None:
    """Train, and save what the lesson shows at every checkpoint."""
    rng = np.random.default_rng(SEED)
    pairs, train_mask = make_data(rng)
    trainer = Trainer(init_params(rng))
    steps, train_acc, test_acc, train_loss, test_loss, correct, embeddings = [], [], [], [], [], [], []
    t0 = time.perf_counter()
    for step in range(STEPS + 1):
        if step % CHECKPOINT_EVERY == 0:
            right = forward(trainer.params, pairs)[3].argmax(1) == pairs[:, 2]
            loss = losses(trainer.params, pairs)
            steps.append(step)
            train_acc.append(right[train_mask].mean())
            test_acc.append(right[~train_mask].mean())
            train_loss.append(loss[train_mask].mean())
            test_loss.append(loss[~train_mask].mean())
            correct.append(right.reshape(P, P))
            embeddings.append(trainer.params["E"].copy())
        if step < STEPS:
            trainer.step(pairs[train_mask])
    print(f"trained {STEPS} steps in {time.perf_counter() - t0:.1f} s; final test accuracy {test_acc[-1]:.0%}")

    # The clock views: the planes of the final embeddings' strongest frequencies, the same at every checkpoint
    final = embeddings[-1] - embeddings[-1].mean(0)
    frequencies = clock_frequencies(final, CLOCKS)
    axes = np.array([clock_axes(final, int(k)) for k in frequencies])                     # (CLOCKS, 2, D_EMBED)
    clocks = np.array([[(e - e.mean(0)) @ a.T for a in axes] for e in embeddings], np.float32)  # (steps, CLOCKS, P, 2)
    print(f"clocks: frequencies {frequencies.tolist()}")

    np.savez_compressed(out, steps=np.array(steps), train_acc=np.array(train_acc, np.float32),
                        test_acc=np.array(test_acc, np.float32), train_loss=np.array(train_loss, np.float32),
                        test_loss=np.array(test_loss, np.float32), correct=np.array(correct, np.uint8),
                        train_mask=train_mask.reshape(P, P), clock_frequencies=frequencies, clocks=clocks,
                        clock_axes=axes.astype(np.float32))
    print(f"wrote {out} ({out.stat().st_size // 1024} KB, {len(steps)} checkpoints)")


if __name__ == "__main__":
    record_path(Path(__file__).parent / "grokking_data.npz")
