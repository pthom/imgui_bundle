# Setup env
cf https://pyodide.org/en/stable/development/building-from-sources.html:

> To build on MacOS with Homebrew, you need:
>    brew install coreutils cmake autoconf automake libtool libffi ccache
> It is also recommended installing the GNU patch and GNU sed:
>    brew install gpatch gnu-sed
> and re-defining them as patch and sed (in the PATH)

# Clone and build
```
git clone https://github.com/pyodide/pyodide.git
git submodule update --init --recursive
pip install -r requirements.txt
make
```

pandas ipython requests imgui_bundle opencv-python typing-extensions pydantic munch numpy matplotlib future scikit-learn --install

PYODIDE_PACKAGES="pandas,ipython,requests,opencv-python,typing-extensions,pydantic,munch,numpy,matplotlib,future,scikit-learn" make

PYODIDE_PACKAGES="pandas,ipython,requests" make
