# Build instructions for Pyodide

You will need a **Linux** system to build Pyodide.

cf https://pyodide.org/en/stable/development/building-from-sources.html#using-make


* Clone the Pyodide repository
```bash
git clone https://github.com/pyodide/pyodide.git
cd pyodide
git submodule update --init --recursive
```

* Create conda environment (pyodide-env)
```bash
conda env create -f environment.yml
conda activate pyodide-env
pip install -r requirements.txt
```

* Build minimal packages
This will download, compile and install emsdk, cpython, and some minimal pyodide packages.
```bash
make
```

* Build packages that are needed (apart from imgui_bundle)
```
pyodide build-recipes numpy pandas ipython requests opencv-python typing-extensions pydantic munch numpy matplotlib future scikit-learn --install
```

* Build imgui_bundle
```bash
pyodide build-recipes imgui_bundle --install
```
