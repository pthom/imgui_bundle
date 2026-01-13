# Plan: Document Async Notebook Feature for imgui_bundle
Comprehensive documentation for the immapp.nb and hello_imgui.nb async notebook API, showcasing interactive GUI development in Jupyter notebooks.

# Steps

## Update imgui_python_intro.md - Add async notebook section

* Expand the current "Jupyter notebooks" bullet (line 107) with async capabilities
* Add new section "## Interactive Development in Jupyter Notebooks" after line 111
* Include 3-cell quick start example showing immapp.nb.start(), variable update, and immapp.nb.stop()
* Add comparison: blocking mode (screenshot after) vs async mode (live updates)
* Create 2-3 screenshots/GIFs: (a) GUI window + notebook side-by-side, (b) real-time variable update in action
* Link to detailed notebook examples and API reference

## Create imgui_jupyter_async.md - Comprehensive async guide

* Section 1: Why async notebook GUIs? (problem statement, comparison with Qt %gui qt)
* Section 2: Quick Start with code examples for all 3 signatures (gui_function, SimpleRunnerParams, RunnerParams)
* Section 3: Real-world examples - (a) Live data visualization with variable injection, (b) ML training dashboard with hyperparameter tuning, (c) Performance monitoring demo from sandbox_async_performance.py
* Section 4: Advanced usage - run_async() for custom workflows, performance tuning with FPS settings
* Section 5: API reference table with start(), stop(), is_running(), and run()
Include comparison table: Qt vs imgui_bundle (setup, code complexity, performance)

## Create demo notebook demo_ml_training.ipynb - ML training showcase

* Cell 1: Simple neural network setup (PyTorch/NumPy-based, no heavy dependencies)
* Cell 2: GUI with live controls (learning rate, dropout, batch size sliders + pause/resume buttons)
* Cell 3: Training loop with async def train_model() showing real-time loss plot updates
* Cell 4: Demonstrate mid-training hyperparameter adjustment and immediate effect
* Cell 5: Cleanup with immapp.nb.stop()
* Use ImPlot for loss curves, show both training and validation metrics

## Create visual assets in images

* Record GIF: 10-second demo showing notebook cell execution while GUI updates live
* Screenshot: Jupyter notebook + imgui window side-by-side showing variable sync
* Screenshot: ML training dashboard with loss curves and sliders
* Comparison diagram: Code complexity (Qt 70 lines vs imgui_bundle 10 lines)
* Performance chart: From sandbox_async_performance.py showing Python loop iterations/sec alongside GUI FPS

## Update immapp_notebook.adoc - Add async API docs

* Add new section after current blocking mode description
* Document immapp.nb.start(), immapp.nb.stop(), immapp.nb.is_running(), and immapp.nb.run()
* Include all 3 overload signatures with parameter descriptions
* Add note about automatic FPS optimizations (early_return mode, 60 FPS cap)
* Link to test_immapp_nb.ipynb for comprehensive examples

## Add "Interactive Notebooks" section to main README or index

* Brief intro to async notebook capabilities (2-3 sentences)
* Link to imgui_jupyter_async.md guide
* Link to demo_ml_training.ipynb
* Highlight key benefit: "Modify variables in real-time while GUI runs"

# Further Considerations
* Video tutorial? - 5-minute YouTube screencast showing installation → first async GUI → ML training demo. Could significantly boost adoption, but requires recording/editing effort. Alternative: rely on GIFs for now, add video later if there's demand.

* Comparison with other frameworks? - Add comparison section covering Dear PyGui (no notebook support), Panel/Streamlit (web-based, different paradigm), ipywidgets (retained mode). This helps position imgui_bundle's unique value, but may lengthen documentation. Option A: Add as appendix in detailed guide. Option B: Keep focused only on Qt comparison.

* PyTorch/TensorFlow dependency for ML demo? - ML training example needs a framework. Option A: Use lightweight NumPy-only neural net (no dependencies, simpler). Option B: Use PyTorch/TensorFlow (more realistic, but adds dependencies). Option C: Make two versions - basic and advanced. Recommendation: Start with NumPy-only version to keep demo accessible.