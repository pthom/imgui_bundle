"""
An image from a prompt: calling an AI service

Type a prompt, click **Generate**: a free AI service, [Pollinations](https://pollinations.ai), draws the image. The GUI
stays responsive meanwhile: `immapp.start_download()` makes the request in the background, on the desktop and in the
browser, and the GUI function looks at it at each frame.

The service is free and needs no account. Its images carry a watermark, and it gives a few images to each visitor (it
counts them by IP address), then asks for a pause. It may change. Your prompt goes to this service.
"""
from __future__ import annotations

import time
from urllib.parse import quote

import cv2
import numpy as np
from numpy.typing import NDArray

from imgui_bundle import imgui, immapp, immvision, ImVec2, ImVec4, em_size

# The service: a plain GET, without key, that answers with a JPEG
SERVICE_URL = "https://image.pollinations.ai/prompt/{prompt}?width={width}&height={height}&seed={seed}"
PROMPT = "A lighthouse on a cliff at dusk, watercolor"  # the prompt at start
IMAGE_SIZE = (512, 384)  # the size of the generated images, in pixels
WIDTH_EM = 30.0  # the width of the prompt and of the image on screen
ERROR_COLOR = ImVec4(1.0, 0.55, 0.3, 1.0)

# The free tier: a few images per visitor (by IP address). Past them, the service answers HTTP 402 (it asks for a
# payment), with no explanation: the demo gives one.
QUOTA_NOTE = "A free service: a few images per visitor, then a pause"
QUOTA_EXCEEDED = ("The free images are used up for now: the service gives a few to each visitor (it counts them by IP "
                  "address), then asks for a pause. Retry later.")

Image = NDArray[np.uint8]  # an image: height x width x 3, in RGB order


def image_url(prompt: str, seed: int) -> str:
    """The URL of the image of a prompt. Another seed gives another image for the same prompt."""
    width, height = IMAGE_SIZE
    return SERVICE_URL.format(prompt=quote(prompt, safe=""), width=width, height=height, seed=seed)


def decode(data: bytes) -> Image | None:
    """The image in the bytes (JPEG, PNG...), in RGB order; None if they hold no image"""
    bgr = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    return None if bgr is None else cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)  # type: ignore  # OpenCV decodes in BGR order


class AppState:
    def __init__(self) -> None:
        self.prompt = PROMPT
        self.seed = 1
        self.download: immapp.Download | None = None  # the request in progress
        self.start_time = 0.0  # when it started
        self.image: Image | None = None
        self.error = ""
        self.image_params = immvision.ImageParams()  # how ImmVision shows the image: zoom with the wheel, pan by dragging


state = AppState()


def gui() -> None:
    imgui.text("Prompt")
    _, state.prompt = imgui.input_text_multiline("##prompt", state.prompt, ImVec2(em_size(WIDTH_EM), em_size(4)))
    imgui.set_next_item_width(em_size(10))
    _, state.seed = imgui.slider_int("Seed", state.seed, 1, 1000)
    imgui.same_line()
    imgui.text_disabled("(another seed, another image)")

    # The request: started by the button, it runs in the background
    imgui.begin_disabled(state.download is not None)  # one request at a time
    if imgui.button("Generate"):
        state.download = immapp.start_download(image_url(state.prompt, state.seed))
        state.start_time = time.time()
    imgui.end_disabled()

    # At each frame, look whether the request is done
    if state.download is not None and state.download.done:
        state.error = state.download.error  # empty on success; else the status, and the service's explanation
        if state.download.status in (402, 429):  # 429: Too Many Requests, the usual answer of a rate limit
            state.error = QUOTA_EXCEEDED
        if not state.error:
            image = decode(state.download.data)
            if image is None:
                state.error = "The service answered with something else than an image"
            else:
                state.image = image
                state.image_params.refresh_image = True  # ImmVision keeps a texture of the image: it must know
        state.download = None

    imgui.same_line()
    if state.download is not None:
        imgui.text(f"Generating... {time.time() - state.start_time:.1f} s")
    else:
        imgui.text_disabled(QUOTA_NOTE)
    if state.error:
        imgui.push_style_color(imgui.Col_.text, ERROR_COLOR)
        imgui.text_wrapped(state.error)
        imgui.pop_style_color()

    if state.image is not None:
        state.image_params.image_display_size = (int(em_size(WIDTH_EM)), 0)  # the height follows the image
        immvision.image("##image", state.image, state.image_params)
        state.image_params.refresh_image = False
    else:
        imgui.text_disabled("Click Generate: the image shows here")


def main() -> None:
    immapp.run(gui, window_title="An image from a prompt", window_size=(650, 700))


if __name__ == "__main__":
    main()
