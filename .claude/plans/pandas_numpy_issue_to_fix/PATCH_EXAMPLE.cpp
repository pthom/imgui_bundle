/*
 * Enhanced C++ binding with better error messages for readonly arrays
 *
 * This demonstrates how to modify one plot_line binding to provide
 * a helpful error message when users pass readonly pandas arrays.
 */

// Add this helper function near the top of the file (after includes)
namespace {
    // Helper to check if an array is writable and provide helpful error
    nb::ndarray<> check_array_writable(nb::handle obj, const char* param_name) {
        // First check if it's even an array
        if (!nb::isinstance<nb::ndarray<>>(obj)) {
            throw std::runtime_error(
                std::string("Parameter '") + param_name +
                "' must be a numpy array"
            );
        }

        // Try to cast to ndarray - this will fail for readonly arrays
        try {
            return nb::cast<nb::ndarray<>>(obj);
        } catch (const nb::cast_error&) {
            // Readonly array - provide helpful error!
            throw std::runtime_error(
                std::string("Parameter '") + param_name +
                "' is a read-only numpy array, commonly from pandas operations like:\n"
                "  df.index.map(lambda ts: ts.timestamp()).to_numpy()\n\n"
                "These arrays are incompatible with ImPlot's nanobind bindings.\n\n"
                "Fix: Create a writable copy:\n"
                "  " + std::string(param_name) + " = np.array(" + std::string(param_name) + ")\n"
            );
        }
    }
}

// Modified plot_line binding (2-array version):
// BEFORE (original generated code around line 976):
m.def("plot_line",
    [](const char * label_id, const nb::ndarray<> & xs, const nb::ndarray<> & ys,
       const std::optional<const ImPlotSpec> & spec = std::nullopt)
    {
        // ... existing code ...
    },
    nb::arg("label_id"), nb::arg("xs"), nb::arg("ys"),
    nb::arg("spec").none() = nb::none()
);

// AFTER (enhanced version with helpful errors):
m.def("plot_line",
    [](const char * label_id, nb::handle xs_obj, nb::handle ys_obj,
       const std::optional<const ImPlotSpec> & spec = std::nullopt)
    {
        // Check arrays with helpful error messages
        nb::ndarray<> xs = check_array_writable(xs_obj, "xs");
        nb::ndarray<> ys = check_array_writable(ys_obj, "ys");

        // Now continue with the existing logic (unchanged)
        auto PlotLine_adapt_c_buffers = [](const char * label_id,
            const nb::ndarray<> & xs, const nb::ndarray<> & ys,
            const ImPlotSpec & spec = ImPlotSpec())
        {
            // Check if the array is 1D and C-contiguous
            if (! (xs.ndim() == 1 && xs.stride(0) == 1))
                throw std::runtime_error("The array must be 1D and contiguous");

            // ... rest of existing code unchanged ...
        };

        // ... rest of existing function unchanged ...
    },
    nb::arg("label_id"), nb::arg("xs"), nb::arg("ys"),
    nb::arg("spec").none() = nb::none(),
    "Plots a standard 2D line plot"
);

/*
 * Benefits:
 * 1. Clear error message identifying readonly arrays
 * 2. Explains the common cause (pandas operations)
 * 3. Shows exact fix with code example
 * 4. Zero performance impact on valid arrays
 * 5. Maintains all existing functionality
 *
 * This pattern should be applied to all array-accepting functions:
 * - plot_scatter
 * - plot_bars
 * - plot_stairs
 * - etc.
 */
