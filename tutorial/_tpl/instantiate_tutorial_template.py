import os


TPL_DIR = os.path.dirname(__file__)
TUTORIAL_DIR = os.path.realpath(os.path.join(TPL_DIR, ".."))

print(TUTORIAL_DIR)


def _process(tutorial_name: str):
    print(f"Creating tutorial {tutorial_name}...")

    # Copy TPL_DIR/tpl.jpg to name.jpg
    import shutil
    shutil.copyfile(f"{TPL_DIR}/tpl.jpg",f"{TUTORIAL_DIR}/{tutorial_name}.jpg")
    shutil.copyfile(f"{TPL_DIR}/tpl.cpp",f"{TUTORIAL_DIR}/{tutorial_name}.cpp")
    shutil.copyfile(f"{TPL_DIR}/tpl.py",f"{TUTORIAL_DIR}/{tutorial_name}.py")

    # Read content of TPL_DIR/tpl.md
    with open(f"{TPL_DIR}/tpl_md", "r") as f:
        tpl_md = f.read()
    basename = os.path.basename(tutorial_name)
    tpl_md = tpl_md.replace("tpl", basename)
    # Write content to TUTORIAL_DIR/name.md
    with open(f"{TUTORIAL_DIR}/{tutorial_name}.md", "w") as f:
        f.write(tpl_md)


def cli():
    import sys
    tutorial_name = sys.argv[1]
    _process(tutorial_name)


if __name__ == "__main__":
    cli()

