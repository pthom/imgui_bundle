"""Sandbox for testing markdown with online images.

Tests:
- URL image (PNG from the web)
- URL image (JPEG)
- Broken URL (should show placeholder)
- Local asset image (existing behavior)
- Mixed: text, URL images, local images, code blocks
"""
from imgui_bundle import immapp, imgui_md
import logging
logging.getLogger("imgui_md_image_loader").setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)



def gui():
    imgui_md.render_unindented("""
    # Markdown Online Images Test

    ## 1. PNG from URL
    ![litgen logo](https://pthom.github.io/litgen/litgen_book/_static/litgen_logo_big.png)

    ## 2. JPEG from URL
    ![photo](https://picsum.photos/id/1018/300/200)

    ## 3. GIF from URL (stbi renders first frame)
    ![gif](https://upload.wikimedia.org/wikipedia/commons/2/2c/Rotating_earth_%28large%29.gif)

    ## 4. Broken URL (should show placeholder)
    ![broken](https://this.url.does.not.exist.example.com/image.png)

    ## 5. Local asset image
    ![local](images/world.png)

    ## 6.1 HTML img tag with explicit width
    <img src="https://picsum.photos/id/1018/300/200" width="150">

    ## 6.2 HTML img tag with explicit height
    <img src="https://pthom.github.io/litgen/litgen_book/_static/litgen_logo_big.png" height="100">


    ## 7. HTML img tag with both dimensions
    <img src="https://picsum.photos/id/237/300/200" width="100" height="80">

    ## 8. HTML img tag - local asset with size
    <img src="images/world.png" width="64" height="64">

    ## 9. Mixed content
    Some text with an inline reference to the logo above.

    > A blockquote with an image:
    > ![small](https://picsum.photos/id/237/150/100)

    ```python
    # Code blocks should still work
    print("Hello from markdown!")
    ```
    """)


def main():
    immapp.run(gui, with_markdown=True, window_size=(800, 900), window_title="Markdown Image Test")


if __name__ == "__main__":
    main()
