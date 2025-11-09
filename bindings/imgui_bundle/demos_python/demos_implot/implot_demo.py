# This file is a line-by-line transcription of implot_demo.cpp
# (https://github.com/epezent/implot/blob/master/implot_demo.cpp)
import time
from imgui_bundle import imgui, immapp, implot, imgui_ctx, ImVec4, ImVec2, IM_COL32
import numpy as np
from numpy.typing import NDArray
import datetime
from typing import TypeAlias, Any

FloatArray1D: TypeAlias = NDArray[np.floating[Any]]


def make_checkerboard_texture(size: int = 256, tile_size: int = 32) -> NDArray[np.uint8]:
    """Create a checkerboard RGBA texture as a numpy array."""
    img = np.zeros((size, size, 4), dtype=np.uint8)
    for y in range(size):
        for x in range(size):
            if ((x // tile_size) + (y // tile_size)) % 2 == 0:
                color = (255, 255, 255, 255)
            else:
                color = (64, 64, 64, 255)
            img[y, x] = color
    return img


def plot_candlestick(
        label_id: str,
        xs: FloatArray1D,  # x-axis values (timestamps as float)
        opens: FloatArray1D,
        closes: FloatArray1D,
        lows: FloatArray1D,
        highs: FloatArray1D,
        tooltip: bool,
        width_percent: float,
        positive_color: ImVec4 | None = None,
        negative_color: ImVec4 | None = None) -> None:
    """Custom plotter for candlestick charts."""
    from datetime import datetime

    if positive_color is None:
        positive_color = ImVec4(0.0, 1.0, 0.441, 1.0)
    if negative_color is None:
        negative_color = ImVec4(0.853, 0.050, 0.310, 1.0)

    assert opens.shape == closes.shape == lows.shape == highs.shape == xs.shape, "All input arrays must have the same shape."
    assert xs.ndim == 1, "Input arrays must be 1D."

    # get ImGui window DrawList
    draw_list = implot.get_plot_draw_list()
    # calc real value width
    count = xs.shape[0]
    half_width = (xs[1] - xs[0]) * width_percent if count > 1 else width_percent

    # custom tool
    if implot.is_plot_hovered() and tooltip:
        mouse = implot.get_plot_mouse_pos()  # mouse position in plot coordinates, i.e. x is a timestamp
        # round mouse.x to day
        mouse_dt = datetime.fromtimestamp(mouse.x)
        rounded_dt = datetime(mouse_dt.year, mouse_dt.month, mouse_dt.day)
        mouse.x = rounded_dt.timestamp()
        # Draw a transparent gray vertical rect around the hovered day
        tool_l = implot.plot_to_pixels(mouse.x - half_width * 1.5, mouse.y).x
        tool_r = implot.plot_to_pixels(mouse.x + half_width * 1.5, mouse.y).x
        tool_t = implot.get_plot_pos().y
        tool_b = tool_t + implot.get_plot_size().y
        implot.push_plot_clip_rect()
        draw_list.add_rect_filled(ImVec2(tool_l, tool_t), ImVec2(tool_r, tool_b), IM_COL32(128, 128, 128, 64))
        implot.pop_plot_clip_rect()

        # render tool tip (won't be affected by plot clip rect)
        idx = np.searchsorted(xs, mouse.x)
        if 0 < idx < count:
            with imgui_ctx.begin_tooltip():
                dt = datetime.fromtimestamp(float(xs[idx]))
                date_str = dt.strftime("%Y-%m-%d")
                imgui.text(f"Day:   {date_str}")
                imgui.text(f"Open:  ${opens[idx]:.2f}")
                imgui.text(f"Close: ${closes[idx]:.2f}")
                imgui.text(f"Low:   ${lows[idx]:.2f}")
                imgui.text(f"High:  ${highs[idx]:.2f}")

    # begin plot item
    if implot.internal.begin_item(label_id):
        # override legend icon color
        current_item = implot.internal.get_current_item()
        current_item.color = IM_COL32(64, 64, 64, 255)
        # fit data if requested
        if implot.internal.fit_this_frame():
            for i in range(count):
                implot.internal.fit_point(implot.Point(float(xs[i]), float(lows[i])))
                implot.internal.fit_point(implot.Point(float(xs[i]), float(highs[i])))
        # render data
        for i in range(count):
            open_pos = implot.plot_to_pixels(float(xs[i]) - half_width, float(opens[i]))
            close_pos = implot.plot_to_pixels(float(xs[i]) + half_width, float(closes[i]))
            low_pos = implot.plot_to_pixels(float(xs[i]), float(lows[i]))
            high_pos = implot.plot_to_pixels(float(xs[i]), float(highs[i]))
            color = positive_color if opens[i] < closes[i] else negative_color
            color_u32 = imgui.get_color_u32(color)
            draw_list.add_line(low_pos, high_pos, color_u32)
            draw_list.add_rect_filled(open_pos, close_pos, color_u32)

        # end plot item
        implot.internal.end_item()


def demo_custom_plotters_and_tooltips():
    static = demo_custom_plotters_and_tooltips
    imgui.bullet_text("You can create custom plotters or extend ImPlot using implot_internal.h.")
    if not hasattr(static, "initialized"):
        static.nb_days = 218
        static.first_day = datetime.datetime(2019, 1, 1, 0, 0, 0).timestamp()
        static.last_day = static.first_day + static.nb_days * 86400.0
        static.dates = np.array([static.first_day + i * 86400.0 for i in range(0, static.nb_days)])
        static.opens = np.array([1284.7,1319.9,1318.7,1328,1317.6,1321.6,1314.3,1325,1319.3,1323.1,1324.7,1321.3,1323.5,1322,1281.3,1281.95,1311.1,1315,1314,1313.1,1331.9,1334.2,1341.3,1350.6,1349.8,1346.4,1343.4,1344.9,1335.6,1337.9,1342.5,1337,1338.6,1337,1340.4,1324.65,1324.35,1349.5,1371.3,1367.9,1351.3,1357.8,1356.1,1356,1347.6,1339.1,1320.6,1311.8,1314,1312.4,1312.3,1323.5,1319.1,1327.2,1332.1,1320.3,1323.1,1328,1330.9,1338,1333,1335.3,1345.2,1341.1,1332.5,1314,1314.4,1310.7,1314,1313.1,1315,1313.7,1320,1326.5,1329.2,1314.2,1312.3,1309.5,1297.4,1293.7,1277.9,1295.8,1295.2,1290.3,1294.2,1298,1306.4,1299.8,1302.3,1297,1289.6,1302,1300.7,1303.5,1300.5,1303.2,1306,1318.7,1315,1314.5,1304.1,1294.7,1293.7,1291.2,1290.2,1300.4,1284.2,1284.25,1301.8,1295.9,1296.2,1304.4,1323.1,1340.9,1341,1348,1351.4,1351.4,1343.5,1342.3,1349,1357.6,1357.1,1354.7,1361.4,1375.2,1403.5,1414.7,1433.2,1438,1423.6,1424.4,1418,1399.5,1435.5,1421.25,1434.1,1412.4,1409.8,1412.2,1433.4,1418.4,1429,1428.8,1420.6,1441,1460.4,1441.7,1438.4,1431,1439.3,1427.4,1431.9,1439.5,1443.7,1425.6,1457.5,1451.2,1481.1,1486.7,1512.1,1515.9,1509.2,1522.3,1513,1526.6,1533.9,1523,1506.3,1518.4,1512.4,1508.8,1545.4,1537.3,1551.8,1549.4,1536.9,1535.25,1537.95,1535.2,1556,1561.4,1525.6,1516.4,1507,1493.9,1504.9,1506.5,1513.1,1506.5,1509.7,1502,1506.8,1521.5,1529.8,1539.8,1510.9,1511.8,1501.7,1478,1485.4,1505.6,1511.6,1518.6,1498.7,1510.9,1510.8,1498.3,1492,1497.7,1484.8,1494.2,1495.6,1495.6,1487.5,1491.1,1495.1,1506.4])
        static.highs = np.array([1284.75,1320.6,1327,1330.8,1326.8,1321.6,1326,1328,1325.8,1327.1,1326,1326,1323.5,1322.1,1282.7,1282.95,1315.8,1316.3,1314,1333.2,1334.7,1341.7,1353.2,1354.6,1352.2,1346.4,1345.7,1344.9,1340.7,1344.2,1342.7,1342.1,1345.2,1342,1350,1324.95,1330.75,1369.6,1374.3,1368.4,1359.8,1359,1357,1356,1353.4,1340.6,1322.3,1314.1,1316.1,1312.9,1325.7,1323.5,1326.3,1336,1332.1,1330.1,1330.4,1334.7,1341.1,1344.2,1338.8,1348.4,1345.6,1342.8,1334.7,1322.3,1319.3,1314.7,1316.6,1316.4,1315,1325.4,1328.3,1332.2,1329.2,1316.9,1312.3,1309.5,1299.6,1296.9,1277.9,1299.5,1296.2,1298.4,1302.5,1308.7,1306.4,1305.9,1307,1297.2,1301.7,1305,1305.3,1310.2,1307,1308,1319.8,1321.7,1318.7,1316.2,1305.9,1295.8,1293.8,1293.7,1304.2,1302,1285.15,1286.85,1304,1302,1305.2,1323,1344.1,1345.2,1360.1,1355.3,1363.8,1353,1344.7,1353.6,1358,1373.6,1358.2,1369.6,1377.6,1408.9,1425.5,1435.9,1453.7,1438,1426,1439.1,1418,1435,1452.6,1426.65,1437.5,1421.5,1414.1,1433.3,1441.3,1431.4,1433.9,1432.4,1440.8,1462.3,1467,1443.5,1444,1442.9,1447,1437.6,1440.8,1445.7,1447.8,1458.2,1461.9,1481.8,1486.8,1522.7,1521.3,1521.1,1531.5,1546.1,1534.9,1537.7,1538.6,1523.6,1518.8,1518.4,1514.6,1540.3,1565,1554.5,1556.6,1559.8,1541.9,1542.9,1540.05,1558.9,1566.2,1561.9,1536.2,1523.8,1509.1,1506.2,1532.2,1516.6,1519.7,1515,1519.5,1512.1,1524.5,1534.4,1543.3,1543.3,1542.8,1519.5,1507.2,1493.5,1511.4,1525.8,1522.2,1518.8,1515.3,1518,1522.3,1508,1501.5,1503,1495.5,1501.1,1497.9,1498.7,1492.1,1499.4,1506.9,1520.9])
        static.lows  = np.array([1282.85,1315,1318.7,1309.6,1317.6,1312.9,1312.4,1319.1,1319,1321,1318.1,1321.3,1319.9,1312,1280.5,1276.15,1308,1309.9,1308.5,1312.3,1329.3,1333.1,1340.2,1347,1345.9,1338,1340.8,1335,1332,1337.9,1333,1336.8,1333.2,1329.9,1340.4,1323.85,1324.05,1349,1366.3,1351.2,1349.1,1352.4,1350.7,1344.3,1338.9,1316.3,1308.4,1306.9,1309.6,1306.7,1312.3,1315.4,1319,1327.2,1317.2,1320,1323,1328,1323,1327.8,1331.7,1335.3,1336.6,1331.8,1311.4,1310,1309.5,1308,1310.6,1302.8,1306.6,1313.7,1320,1322.8,1311,1312.1,1303.6,1293.9,1293.5,1291,1277.9,1294.1,1286,1289.1,1293.5,1296.9,1298,1299.6,1292.9,1285.1,1288.5,1296.3,1297.2,1298.4,1298.6,1302,1300.3,1312,1310.8,1301.9,1292,1291.1,1286.3,1289.2,1289.9,1297.4,1283.65,1283.25,1292.9,1295.9,1290.8,1304.2,1322.7,1336.1,1341,1343.5,1345.8,1340.3,1335.1,1341.5,1347.6,1352.8,1348.2,1353.7,1356.5,1373.3,1398,1414.7,1427,1416.4,1412.7,1420.1,1396.4,1398.8,1426.6,1412.85,1400.7,1406,1399.8,1404.4,1415.5,1417.2,1421.9,1415,1413.7,1428.1,1434,1435.7,1427.5,1429.4,1423.9,1425.6,1427.5,1434.8,1422.3,1412.1,1442.5,1448.8,1468.2,1484.3,1501.6,1506.2,1498.6,1488.9,1504.5,1518.3,1513.9,1503.3,1503,1506.5,1502.1,1503,1534.8,1535.3,1541.4,1528.6,1525.6,1535.25,1528.15,1528,1542.6,1514.3,1510.7,1505.5,1492.1,1492.9,1496.8,1493.1,1503.4,1500.9,1490.7,1496.3,1505.3,1505.3,1517.9,1507.4,1507.1,1493.3,1470.5,1465,1480.5,1501.7,1501.4,1493.3,1492.1,1505.1,1495.7,1478,1487.1,1480.8,1480.6,1487,1488.3,1484.8,1484,1490.7,1490.4,1503.1])
        static.closes = np.array([1283.35,1315.3,1326.1,1317.4,1321.5,1317.4,1323.5,1319.2,1321.3,1323.3,1319.7,1325.1,1323.6,1313.8,1282.05,1279.05,1314.2,1315.2,1310.8,1329.1,1334.5,1340.2,1340.5,1350,1347.1,1344.3,1344.6,1339.7,1339.4,1343.7,1337,1338.9,1340.1,1338.7,1346.8,1324.25,1329.55,1369.6,1372.5,1352.4,1357.6,1354.2,1353.4,1346,1341,1323.8,1311.9,1309.1,1312.2,1310.7,1324.3,1315.7,1322.4,1333.8,1319.4,1327.1,1325.8,1330.9,1325.8,1331.6,1336.5,1346.7,1339.2,1334.7,1313.3,1316.5,1312.4,1313.4,1313.3,1312.2,1313.7,1319.9,1326.3,1331.9,1311.3,1313.4,1309.4,1295.2,1294.7,1294.1,1277.9,1295.8,1291.2,1297.4,1297.7,1306.8,1299.4,1303.6,1302.2,1289.9,1299.2,1301.8,1303.6,1299.5,1303.2,1305.3,1319.5,1313.6,1315.1,1303.5,1293,1294.6,1290.4,1291.4,1302.7,1301,1284.15,1284.95,1294.3,1297.9,1304.1,1322.6,1339.3,1340.1,1344.9,1354,1357.4,1340.7,1342.7,1348.2,1355.1,1355.9,1354.2,1362.1,1360.1,1408.3,1411.2,1429.5,1430.1,1426.8,1423.4,1425.1,1400.8,1419.8,1432.9,1423.55,1412.1,1412.2,1412.8,1424.9,1419.3,1424.8,1426.1,1423.6,1435.9,1440.8,1439.4,1439.7,1434.5,1436.5,1427.5,1432.2,1433.3,1441.8,1437.8,1432.4,1457.5,1476.5,1484.2,1519.6,1509.5,1508.5,1517.2,1514.1,1527.8,1531.2,1523.6,1511.6,1515.7,1515.7,1508.5,1537.6,1537.2,1551.8,1549.1,1536.9,1529.4,1538.05,1535.15,1555.9,1560.4,1525.5,1515.5,1511.1,1499.2,1503.2,1507.4,1499.5,1511.5,1513.4,1515.8,1506.2,1515.1,1531.5,1540.2,1512.3,1515.2,1506.4,1472.9,1489,1507.9,1513.8,1512.9,1504.4,1503.9,1512.8,1500.9,1488.7,1497.6,1483.5,1494,1498.3,1494.1,1488.1,1487.5,1495.7,1504.7,1505.3])
        static.tooltip = True
        static.positive_color = [0.0, 1.0, 0.441, 1.0]
        static.negative_color = [0.853, 0.050, 0.310, 1.0]

        static.initialized = True

    _, static.tooltip = imgui.checkbox("Show Tooltips", static.tooltip)
    imgui.same_line()
    _, static.positive_color = imgui.color_edit4("Positive Color", static.positive_color, imgui.ColorEditFlags_.no_inputs)
    imgui.same_line()
    _, static.negative_color = imgui.color_edit4("Negative Color", static.negative_color, imgui.ColorEditFlags_.no_inputs)

    implot.get_style().use_local_time = False

    if implot.begin_plot("Candlestick Chart", ImVec2(-1, 0)):
        implot.setup_axes("", "", 0, implot.AxisFlags_.auto_fit | implot.AxisFlags_.range_fit)
        implot.setup_axes_limits(static.first_day, static.last_day, 1250, 1600)
        implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.time)
        implot.setup_axis_limits_constraints(implot.ImAxis_.x1, static.first_day, static.last_day)
        implot.setup_axis_zoom_constraints(implot.ImAxis_.x1, 60 * 60 * 24 * 14, static.last_day - static.first_day)
        implot.setup_axis_format(implot.ImAxis_.y1, "$%.0f")
        plot_candlestick("GOOGL",
                         static.dates,
                         static.opens, static.closes, static.lows, static.highs,
                         tooltip=static.tooltip,
                         width_percent=0.38,
                         positive_color=ImVec4(*static.positive_color),
                         negative_color=ImVec4(*static.negative_color))
        implot.end_plot()


class ScrollingBuffer:
    """Simulates a scrolling buffer for real-time plotting."""
    def __init__(self, max_size=2000):
        self.max_size = max_size
        self.offset = 0
        self.data = np.empty((max_size, 2), dtype=np.float32)
        self.size = 0

    def add_point(self, x, y):
        if self.size < self.max_size:
            self.data[self.size] = [x, y]
            self.size += 1
        else:
            self.data[self.offset] = [x, y]
            self.offset = (self.offset + 1) % self.max_size

    def get_data(self):
        """Returns the data as contiguous 1D arrays for plotting."""
        data = self.data[:self.size] if self.size < self.max_size else np.roll(self.data, -self.offset, axis=0)
        return np.ascontiguousarray(data[:, 0]), np.ascontiguousarray(data[:, 1])


#-----------------------------------------------------------------------------
# [SECTION] Demo Functions
#-----------------------------------------------------------------------------

def demo_help():
    """Displays help information similar to the ImPlot C++ demo."""

    imgui.text("ABOUT THIS DEMO:")
    imgui.bullet_text("Sections below are demonstrating many aspects of the library.")
    imgui.bullet_text("The \"Tools\" menu above gives access to: Style Editors (ImPlot/ImGui)\n"
                      "and Metrics (general purpose Dear ImGui debugging tool).")

    imgui.separator()

    imgui.text("PROGRAMMER GUIDE:")
    imgui.bullet_text("See the ShowDemoWindow() code in implot_demo.cpp. <- you are here!")
    imgui.bullet_text("If you see visual artifacts, do one of the following:")

    imgui.indent()
    imgui.bullet_text("Handle ImGuiBackendFlags_RendererHasVtxOffset for 16-bit indices in your backend.")
    imgui.bullet_text("Or, enable 32-bit indices in imconfig.h.")
    imgui.bullet_text("Your current configuration is:")

    imgui.indent()

    io = imgui.get_io()
    backend_flag = "True" if io.backend_flags & imgui.BackendFlags_.renderer_has_vtx_offset else "False"
    imgui.bullet_text(f"ImGuiBackendFlags_RendererHasVtxOffset: {backend_flag}")

    imgui.unindent()
    imgui.unindent()

    imgui.separator()

    imgui.text("USER GUIDE:")
    implot.show_user_guide()  # Assuming `show_user_guide()` exists in `imgui`


# -----------------------------------------------------------------------------

def demo_config():
    static = demo_config

    if not hasattr(static, "now"):
        static.now = time.time()

    imgui.show_font_selector("Font")
    imgui.show_style_selector("ImGui Style")
    implot.show_style_selector("ImPlot Style")
    implot.show_colormap_selector("ImPlot Colormap")
    implot.show_input_map_selector("Input Map")

    imgui.separator()

    style = implot.get_style()
    _, style.use_local_time = imgui.checkbox("Use Local Time", style.use_local_time)
    _, style.use_iso8601 = imgui.checkbox("Use ISO 8601", style.use_iso8601)
    _, style.use24_hour_clock = imgui.checkbox("Use 24 Hour Clock", style.use24_hour_clock)

    imgui.separator()

    if implot.begin_plot("Preview"):
        implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.time)
        implot.setup_axis_limits(implot.ImAxis_.x1, static.now, static.now + 24 * 3600)

        for i in range(10):
            x = np.array([static.now, static.now + 24 * 3600], np.float32)
            y = np.array([0, i / 9.0], np.float32)

            with imgui_ctx.push_id(str(i)):
                implot.plot_line("##Line", x, y)

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_line_plots():
    static = demo_line_plots

    if not hasattr(static, "xs1"):
        static.xs1 = np.linspace(0, 1, 1001, dtype=np.float32)
        static.ys1 = np.zeros(1001, dtype=np.float32)

    # Update `ys1` dynamically
    t = imgui.get_time() / 10
    static.ys1[:] = 0.5 + 0.5 * np.sin(50 * (static.xs1 + t))

    if not hasattr(static, "xs2"):
        static.xs2 = np.linspace(0, 1, 20, dtype=np.float64)
        static.ys2 = static.xs2 ** 2

    if implot.begin_plot("Line Plots"):
        implot.setup_axes("x", "y")
        implot.plot_line("f(x)", static.xs1, static.ys1)
        implot.set_next_marker_style(implot.Marker_.circle)
        implot.plot_line("g(x)", static.xs2, static.ys2, flags=implot.LineFlags_.segments)
        implot.end_plot()


#-----------------------------------------------------------------------------

def random_range(min_val, max_val, size=1):
    return np.random.uniform(min_val, max_val, size)


def demo_filled_line_plots():
    static = demo_filled_line_plots

    if not hasattr(static, "xs1"):
        np.random.seed(0)
        static.xs1 = np.arange(101, dtype=np.float64)
        static.ys1 = random_range(400.0, 450.0, 101)
        static.ys2 = random_range(275.0, 350.0, 101)
        static.ys3 = random_range(150.0, 225.0, 101)

    if not hasattr(static, "show_lines"):
        static.show_lines = True
        static.show_fills = True
        static.fill_ref = 0.0
        static.shade_mode = 0
        static.flags = 0

    _, static.show_lines = imgui.checkbox("Lines", static.show_lines)
    imgui.same_line()
    _, static.show_fills = imgui.checkbox("Fills", static.show_fills)

    if static.show_fills:
        imgui.same_line()
        if imgui.radio_button("To -INF", static.shade_mode == 0):
            static.shade_mode = 0
        imgui.same_line()
        if imgui.radio_button("To +INF", static.shade_mode == 1):
            static.shade_mode = 1
        imgui.same_line()
        if imgui.radio_button("To Ref", static.shade_mode == 2):
            static.shade_mode = 2

        if static.shade_mode == 2:
            imgui.same_line()
            imgui.set_next_item_width(100)
            _, static.fill_ref = imgui.drag_float("##Ref", static.fill_ref, 1, -100, 500)

    if implot.begin_plot("Stock Prices"):
        implot.setup_axes("Days", "Price")
        implot.setup_axes_limits(0, 100, 0, 500)

        if static.show_fills:
            implot.push_style_var(implot.StyleVar_.fill_alpha, 0.25)
            ref_value = -np.inf if static.shade_mode == 0 else np.inf if static.shade_mode == 1 else static.fill_ref
            implot.plot_shaded("Stock 1", static.xs1, static.ys1, ref_value, static.flags)
            implot.plot_shaded("Stock 2", static.xs1, static.ys2, ref_value, static.flags)
            implot.plot_shaded("Stock 3", static.xs1, static.ys3, ref_value, static.flags)
            implot.pop_style_var()

        if static.show_lines:
            implot.plot_line("Stock 1", static.xs1, static.ys1)
            implot.plot_line("Stock 2", static.xs1, static.ys2)
            implot.plot_line("Stock 3", static.xs1, static.ys3)

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_shaded_plots():
    static = demo_shaded_plots

    if not hasattr(static, "xs"):
        np.random.seed(0)
        static.xs = np.linspace(0, 1, 1001, dtype=np.float64)
        static.ys = 0.25 + 0.25 * np.sin(25 * static.xs) * np.sin(5 * static.xs) + random_range(-0.01, 0.01, 1001)
        static.ys1 = static.ys + random_range(0.1, 0.12, 1001)
        static.ys2 = static.ys - random_range(0.1, 0.12, 1001)
        static.ys3 = 0.75 + 0.2 * np.sin(25 * static.xs)
        static.ys4 = 0.75 + 0.1 * np.cos(25 * static.xs)

    if not hasattr(static, "alpha"):
        static.alpha = 0.25

    _, static.alpha = imgui.drag_float("Alpha", static.alpha, 0.01, 0, 1)

    if implot.begin_plot("Shaded Plots"):
        implot.push_style_var(implot.StyleVar_.fill_alpha, static.alpha)
        implot.plot_shaded("Uncertain Data", static.xs, static.ys1, static.ys2)
        implot.plot_line("Uncertain Data", static.xs, static.ys)
        implot.plot_shaded("Overlapping", static.xs, static.ys3, static.ys4)
        implot.plot_line("Overlapping", static.xs, static.ys3)
        implot.plot_line("Overlapping", static.xs, static.ys4)
        implot.pop_style_var()
        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_scatter_plots():
    static = demo_scatter_plots

    if not hasattr(static, "xs1"):
        np.random.seed(0)
        static.xs1 = np.linspace(0, 0.99, 100, dtype=np.float64)
        static.ys1 = static.xs1 + 0.1 * np.random.rand(100)

        static.xs2 = 0.25 + 0.2 * np.random.rand(50)
        static.ys2 = 0.75 + 0.2 * np.random.rand(50)

    if implot.begin_plot("Scatter Plot"):
        implot.plot_scatter("Data 1", static.xs1, static.ys1)

        implot.push_style_var(implot.StyleVar_.fill_alpha, 0.25)
        implot.set_next_marker_style(
            implot.Marker_.square,
            size=6,
            fill=implot.get_colormap_color(1),
            weight=implot.AUTO,
            outline=implot.get_colormap_color(1))
        implot.plot_scatter("Data 2", static.xs2, static.ys2)
        implot.pop_style_var()

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_stairstep_plots():
    static = demo_stairstep_plots

    if not hasattr(static, "ys1"):
        static.ys1 = 0.75 + 0.2 * np.sin(10 * np.arange(21) * 0.05)
        static.ys2 = 0.25 + 0.2 * np.sin(10 * np.arange(21) * 0.05)

    if not hasattr(static, "flags"):
        static.flags = 0

    _, static.flags = imgui.checkbox_flags("Shaded", static.flags, implot.StairsFlags_.shaded)

    if implot.begin_plot("Stairstep Plot"):
        implot.setup_axes("x", "f(x)")
        implot.setup_axes_limits(0, 1, 0, 1)

        implot.push_style_color(implot.Col_.line, [0.5, 0.5, 0.5, 1.0])
        implot.plot_line("##1", static.ys1, xscale=0.05)
        implot.plot_line("##2", static.ys2, xscale=0.05)
        implot.pop_style_color()

        implot.set_next_marker_style(implot.Marker_.circle)
        implot.set_next_fill_style(implot.AUTO_COL, 0.25)
        implot.plot_stairs("Post Step (default)", static.ys1, xscale=0.05, flags=static.flags)

        implot.set_next_marker_style(implot.Marker_.circle)
        implot.set_next_fill_style(implot.AUTO_COL, 0.25)
        implot.plot_stairs("Pre Step", static.ys2, xscale=0.05, flags=static.flags | implot.StairsFlags_.pre_step)

        implot.end_plot()


def demo_bar_plots():
    static = demo_bar_plots

    if not hasattr(static, "data"):
        static.data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.int8)

    if implot.begin_plot("Bar Plot"):
        implot.plot_bars("Vertical", static.data, bar_size=0.7, shift=1)
        implot.plot_bars("Horizontal", static.data, bar_size=0.4, shift=1, flags=implot.BarsFlags_.horizontal)
        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_bar_groups():
    static = demo_bar_groups

    if not hasattr(static, "data"):
        static.data = np.array([
            83, 67, 23, 89, 83, 78, 91, 82, 85, 90,  # midterm
            80, 62, 56, 99, 55, 78, 88, 78, 90, 100, # final
            80, 69, 52, 92, 72, 78, 75, 76, 89, 95   # course
        ], dtype=np.int8)

        static.ilabels = ["Midterm Exam", "Final Exam", "Course Grade"]
        static.glabels = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10"]
        static.positions = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

        static.items = 3
        static.groups = 10
        static.size = 0.67
        static.flags = 0
        static.horz = False

    _, static.flags = imgui.checkbox_flags("Stacked", static.flags, implot.BarGroupsFlags_.stacked)
    imgui.same_line()
    _, static.horz = imgui.checkbox("Horizontal", static.horz)

    _, static.items = imgui.slider_int("Items", static.items, 1, 3)
    _, static.size = imgui.slider_float("Size", static.size, 0, 1)

    if implot.begin_plot("Bar Group"):
        implot.setup_legend(implot.Location_.east, implot.LegendFlags_.outside)

        if static.horz:
            implot.setup_axes("Score", "Student", implot.AxisFlags_.auto_fit, implot.AxisFlags_.auto_fit)
            implot.setup_axis_ticks(
                axis=implot.ImAxis_.y1,
                values=static.positions,
                labels=static.glabels,
                keep_default=False
            )
            implot.plot_bar_groups(
                label_ids=static.ilabels,
                values=static.data,
                group_size=static.groups,
                shift=0,
                flags=static.flags | implot.BarGroupsFlags_.horizontal)
        else:
            implot.setup_axes("Student", "Score", implot.AxisFlags_.auto_fit, implot.AxisFlags_.auto_fit)
            implot.setup_axis_ticks(
                axis=implot.ImAxis_.x1,
                values=static.positions,
                labels=static.glabels,
                keep_default=False
            )
            implot.plot_bar_groups(
                label_ids=static.ilabels,
                values=static.data,
                group_size=static.groups,
                shift=0,
                flags=static.flags)

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_bar_stacks():
    static = demo_bar_stacks

    if not hasattr(static, "liars"):
        static.liars = -1

    if static.liars == -1:
        liars_data = np.array([4282515870, 4282609140, 4287357182, 4294630301, 4294945280, 4294921472], np.uint32)
        static.liars = implot.add_colormap("Liars", liars_data)

    if not hasattr(static, "diverging"):
        static.diverging = True

    _, static.diverging = imgui.checkbox("Diverging", static.diverging)

    politicians = ["Trump", "Bachman", "Cruz", "Gingrich", "Palin", "Santorum", "Walker", "Perry", "Ryan", "McCain",
                     "Rubio", "Romney", "Rand Paul", "Christie", "Biden", "Kasich", "Sanders", "J Bush", "H Clinton",
                     "Obama"]
    data_reg = np.array([18,26,7,14,10,8,6,11,4,4,3,8,6,8,6,5,0,3,1,2,    # Pants on Fire
    43,36,30,21,30,27,25,17,11,22,15,16,16,17,12,12,14,6,13,12,  # False
    16,13,28,22,15,21,15,18,30,17,24,18,13,10,14,15,17,22,14,12, # Mostly False
    17,10,13,25,12,22,19,26,23,17,22,27,20,26,29,17,18,22,21,27, # Half True
    5,7,16,10,10,12,23,13,17,20,22,16,23,19,20,26,36,29,27,26,   # Mostly True
    1,8,6,8,23,10,12,15,15,20,14,15,22,20,19,25,15,18,24,21])     # True

    labels_reg = ["Pants on Fire","False","Mostly False","Half True","Mostly True","True"]

    data_div = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,                             # Pants on Fire (dummy, to order legend logically)
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,                                         # False         (dummy, to order legend logically)
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,                                         # Mostly False  (dummy, to order legend logically)
    -16,-13,-28,-22,-15,-21,-15,-18,-30,-17,-24,-18,-13,-10,-14,-15,-17,-22,-14,-12, # Mostly False
    -43,-36,-30,-21,-30,-27,-25,-17,-11,-22,-15,-16,-16,-17,-12,-12,-14,-6,-13,-12,  # False
    -18,-26,-7,-14,-10,-8,-6,-11,-4,-4,-3,-8,-6,-8,-6,-5,0,-3,-1,-2,                 # Pants on Fire
    17,10,13,25,12,22,19,26,23,17,22,27,20,26,29,17,18,22,21,27,                     # Half True
    5,7,16,10,10,12,23,13,17,20,22,16,23,19,20,26,36,29,27,26,                       # Mostly True
    1,8,6,8,23,10,12,15,15,20,14,15,22,20,19,25,15,18,24,21])                         # True
    labels_div = ["Pants on Fire","False","Mostly False","Mostly False","False","Pants on Fire","Half True","Mostly True","True"]

    implot.push_colormap(static.liars)
    if implot.begin_plot("PolitiFact: Who Lies More?", ImVec2(-1, 400), implot.Flags_.no_mouse_text):
        implot.setup_legend(implot.Location_.south, implot.LegendFlags_.outside | implot.LegendFlags_.horizontal)
        implot.setup_axes("", "", implot.AxisFlags_.auto_fit | implot.AxisFlags_.no_decorations, implot.AxisFlags_.auto_fit | implot.AxisFlags_.invert)
        implot.setup_axis_ticks(implot.ImAxis_.y1,
                                v_min=0, v_max=19, n_ticks=20,
                                labels=politicians, keep_default=False)
        if static.diverging:
            implot.plot_bar_groups(
                label_ids=labels_div,
                values=data_div,
                group_size=0.75,
                shift=0,
                flags=implot.BarGroupsFlags_.stacked | implot.BarGroupsFlags_.horizontal)
        else:
            implot.plot_bar_groups(
                label_ids=labels_reg,
                values=data_reg,
                group_size=0.75,
                shift=0,
                flags=implot.BarGroupsFlags_.stacked | implot.BarGroupsFlags_.horizontal)
        implot.end_plot()

    implot.pop_colormap()


def demo_error_bars():
    static = demo_error_bars

    if not hasattr(static, "xs"):
        static.xs = np.array([1, 2, 3, 4, 5], dtype=np.float64)
        static.bar = np.array([1, 2, 5, 3, 4], dtype=np.float64)
        static.lin1 = np.array([8, 8, 9, 7, 8], dtype=np.float64)
        static.lin2 = np.array([6, 7, 6, 9, 6], dtype=np.float64)
        static.err1 = np.array([0.2, 0.4, 0.2, 0.6, 0.4], dtype=np.float64)
        static.err2 = np.array([0.4, 0.2, 0.4, 0.8, 0.6], dtype=np.float64)
        static.err3 = np.array([0.09, 0.14, 0.09, 0.12, 0.16], dtype=np.float64)
        static.err4 = np.array([0.02, 0.08, 0.15, 0.05, 0.2], dtype=np.float64)

    if implot.begin_plot("##ErrorBars"):
        implot.setup_axes_limits(0, 6, 0, 10)

        implot.plot_bars("Bar", static.xs, static.bar, bar_size=0.5)
        implot.plot_error_bars("Bar", static.xs, static.bar, static.err1)

        implot.set_next_error_bar_style(implot.get_colormap_color(1), 0)
        implot.plot_error_bars("Line", static.xs, static.lin1, static.err1, static.err2)

        implot.set_next_marker_style(implot.Marker_.square)
        implot.plot_line("Line", static.xs, static.lin1)

        implot.push_style_color(implot.Col_.error_bar, implot.get_colormap_color(2))
        implot.plot_error_bars("Scatter", static.xs, static.lin2, static.err2)
        implot.plot_error_bars("Scatter", static.xs, static.lin2, static.err3, static.err4,
                               flags=implot.ErrorBarsFlags_.horizontal)
        implot.pop_style_color()

        implot.plot_scatter("Scatter", static.xs, static.lin2)

        implot.end_plot()


def demo_stem_plots():
    static = demo_stem_plots

    if not hasattr(static, "xs"):
        static.xs = np.linspace(0, 1, 51, dtype=np.float64)
        static.ys1 = 1.0 + 0.5 * np.sin(25 * static.xs) * np.cos(2 * static.xs)
        static.ys2 = 0.5 + 0.25 * np.sin(10 * static.xs) * np.sin(static.xs)

    if implot.begin_plot("Stem Plots"):
        implot.setup_axis_limits(implot.ImAxis_.x1, 0, 1.0)
        implot.setup_axis_limits(implot.ImAxis_.y1, 0, 1.6)
        implot.plot_stems("Stems 1", static.xs, static.ys1)
        implot.set_next_marker_style(implot.Marker_.circle)
        implot.plot_stems("Stems 2", static.xs, static.ys2)
        implot.end_plot()


#-----------------------------------------------------------------------------
# Demo_InfiniteLines
#-----------------------------------------------------------------------------

def demo_infinite_lines():
    static = demo_infinite_lines
    if not hasattr(static, "vals"):
        static.vals = np.array([0.25, 0.5, 0.75], dtype=np.float64)

    if implot.begin_plot("##Infinite"):
        implot.setup_axes("", "", implot.AxisFlags_.no_initial_fit, implot.AxisFlags_.no_initial_fit)
        implot.plot_inf_lines("Vertical", static.vals)
        implot.plot_inf_lines("Horizontal", static.vals, flags=implot.InfLinesFlags_.horizontal)
        implot.end_plot()


def demo_pie_charts():
    static = demo_pie_charts

    if not hasattr(static, "data1"):
        static.labels1 = ["Frogs", "Hogs", "Dogs", "Logs"]
        static.data1 = [0.15, 0.30, 0.2, 0.05]
        static.flags = 0

    imgui.set_next_item_width(250)
    _, static.data1 = imgui.drag_float4("Values", static.data1, 0.01, 0, 1)

    _, static.flags = imgui.checkbox_flags("Normalize", static.flags, implot.PieChartFlags_.normalize)
    _, static.flags = imgui.checkbox_flags("Ignore Hidden", static.flags, implot.PieChartFlags_.ignore_hidden)

    if implot.begin_plot("##Pie1", size=(250, 250), flags=implot.Flags_.equal | implot.Flags_.no_mouse_text):
        implot.setup_axes("", "", implot.AxisFlags_.no_decorations, implot.AxisFlags_.no_decorations)
        implot.setup_axes_limits(0, 1, 0, 1)
        implot.plot_pie_chart(static.labels1, np.array(static.data1), x=0.5, y=0.5, radius=0.4, label_fmt="%.2f", angle0=90, flags=static.flags)  # type: ignore
        implot.end_plot()

    imgui.same_line()

    if not hasattr(static, "data2"):
        static.labels2 = ["A", "B", "C", "D", "E"]
        static.data2 = np.array([1, 1, 2, 3, 5], dtype=np.int32)

    implot.push_colormap(implot.Colormap_.pastel)
    if implot.begin_plot("##Pie2", size=(250, 250), flags=implot.Flags_.equal | implot.Flags_.no_mouse_text):
        implot.setup_axes("", "", implot.AxisFlags_.no_decorations, implot.AxisFlags_.no_decorations)
        implot.setup_axes_limits(0, 1, 0, 1)
        implot.plot_pie_chart(static.labels2, static.data2, x=0.5, y=0.5, radius=0.4, label_fmt="%.0f", angle0=180, flags=static.flags)
        implot.end_plot()
    implot.pop_colormap()


def demo_heatmaps():
    static = demo_heatmaps

    if not hasattr(static, "values1"):
        static.values1 = np.array([
            [0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
            [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
            [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
            [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
            [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
            [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
            [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]
        ], dtype=np.float32)
        static.scale_min = 0.0
        static.scale_max = 6.3
        static.xlabels = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
        static.ylabels = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]

    if not hasattr(static, "map"):
        static.map = implot.Colormap_.viridis

    if implot.colormap_button(implot.get_colormap_name(static.map), size=(225, 0), cmap=static.map):
        static.map = (static.map + 1) % implot.get_colormap_count()
        implot.bust_color_cache("##Heatmap1")
        implot.bust_color_cache("##Heatmap2")

    imgui.same_line()
    imgui.label_text("##Colormap Index", "Change Colormap")
    imgui.set_next_item_width(225)
    _, static.scale_min, static.scale_max = imgui.drag_float_range2("Min / Max", static.scale_min, static.scale_max, 0.01, -20, 20)

    if not hasattr(static, "hm_flags"):
        static.hm_flags = 0
    _, static.hm_flags = imgui.checkbox_flags("Column Major", static.hm_flags, implot.HeatmapFlags_.col_major)

    axes_flags = implot.AxisFlags_.lock | implot.AxisFlags_.no_grid_lines | implot.AxisFlags_.no_tick_marks

    implot.push_colormap(static.map)

    if implot.begin_plot("##Heatmap1", size=(225, 225), flags=implot.Flags_.no_legend | implot.Flags_.no_mouse_text):
        implot.setup_axes("", "", axes_flags, axes_flags)
        implot.setup_axis_ticks(implot.ImAxis_.x1, v_min=0 + 1.0 / 14.0, v_max=1 - 1.0 / 14.0, n_ticks=7, labels=static.xlabels, keep_default=False)
        implot.setup_axis_ticks(implot.ImAxis_.y1, v_min=1 - 1.0 / 14.0, v_max=0 + 1.0 / 14.0, n_ticks=7, labels=static.ylabels, keep_default=False)
        implot.plot_heatmap("heat", static.values1, scale_min=static.scale_min, scale_max=static.scale_max, label_fmt="%g",
                            bounds_min=implot.Point(0, 0), bounds_max=implot.Point(1, 1), flags=static.hm_flags)
        implot.end_plot()

    imgui.same_line()
    implot.colormap_scale("##HeatScale", static.scale_min, static.scale_max, size=(60, 225))

    imgui.same_line()

    size = 80
    if not hasattr(static, "values2"):
        np.random.seed(int(imgui.get_time() * 1000000))
        static.values2 = np.random.uniform(0.0, 1.0, size=(size, size))

    if implot.begin_plot("##Heatmap2", size=(225, 225)):
        implot.setup_axes("", "", implot.AxisFlags_.no_decorations, implot.AxisFlags_.no_decorations)
        implot.setup_axes_limits(-1, 1, -1, 1)
        implot.plot_heatmap("heat1", static.values2, scale_min=0, scale_max=1)
        implot.plot_heatmap("heat2", static.values2, scale_min=0, scale_max=1, bounds_min=implot.Point(-1, -1), bounds_max=implot.Point(0, 0))
        implot.end_plot()

    implot.pop_colormap()


#-----------------------------------------------------------------------------

def demo_histogram():
    static = demo_histogram

    if not hasattr(static, "hist_flags"):
        static.hist_flags = implot.HistogramFlags_.density
        static.bins = 50
        static.mu = 5.0
        static.sigma = 2.0
        static.range = False
        static.rmin = -3.0
        static.rmax = 13.0
        static.data = np.random.normal(static.mu, static.sigma, 10000)

    imgui.set_next_item_width(200)
    if imgui.radio_button("Sqrt", static.bins == implot.Bin_.sqrt):
        static.bins = implot.Bin_.sqrt
    imgui.same_line()
    if imgui.radio_button("Sturges", static.bins == implot.Bin_.sturges):
        static.bins = implot.Bin_.sturges
    imgui.same_line()
    if imgui.radio_button("Rice", static.bins == implot.Bin_.rice):
        static.bins = implot.Bin_.rice
    imgui.same_line()
    if imgui.radio_button("Scott", static.bins == implot.Bin_.scott):
        static.bins = implot.Bin_.scott
    imgui.same_line()
    if imgui.radio_button("N Bins", static.bins >= 0):
        static.bins = 50

    if static.bins >= 0:
        imgui.same_line()
        imgui.set_next_item_width(200)
        _, static.bins = imgui.slider_int("##Bins", static.bins, 1, 100)

    _, static.hist_flags = imgui.checkbox_flags("Horizontal", static.hist_flags, implot.HistogramFlags_.horizontal)
    imgui.same_line()
    _, static.hist_flags = imgui.checkbox_flags("Density", static.hist_flags, implot.HistogramFlags_.density)
    imgui.same_line()
    _, static.hist_flags = imgui.checkbox_flags("Cumulative", static.hist_flags, implot.HistogramFlags_.cumulative)

    _, static.range = imgui.checkbox("Range", static.range)

    if static.range:
        imgui.same_line()
        imgui.set_next_item_width(200)
        _, static.rmin, static.rmax = imgui.drag_float_range2("##Range", static.rmin, static.rmax, 0.1, -3, 13)
        imgui.same_line()
        _, static.hist_flags = imgui.checkbox_flags("Exclude Outliers", static.hist_flags, implot.HistogramFlags_.no_outliers)

    x = np.linspace(-3, 13, 100)
    y = np.exp(-((x - static.mu) ** 2) / (2 * static.sigma ** 2)) / (static.sigma * np.sqrt(2 * np.pi))

    if static.hist_flags & implot.HistogramFlags_.cumulative:
        y = np.cumsum(y)
        y /= y[-1]

    if implot.begin_plot("##Histograms"):
        implot.setup_axes("", "", implot.AxisFlags_.auto_fit, implot.AxisFlags_.auto_fit)
        implot.set_next_fill_style(implot.AUTO_COL, 0.5)
        implot.plot_histogram("Empirical", static.data, bins=static.bins, bar_scale=1.0,
                              range=implot.Range(static.rmin, static.rmax) if static.range else implot.Range(), flags=static.hist_flags)

        if (static.hist_flags & implot.HistogramFlags_.density) and not (static.hist_flags & implot.HistogramFlags_.no_outliers):
            if static.hist_flags & implot.HistogramFlags_.horizontal:
                implot.plot_line("Theoretical", y, x)
            else:
                implot.plot_line("Theoretical", x, y)

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_histogram2d():
    static = demo_histogram2d

    if not hasattr(static, "count"):
        static.count = 50000
        static.xybins = [100, 100]
        static.hist_flags = 0
        static.dist1 = np.random.normal(1, 2, 100000)
        static.dist2 = np.random.normal(1, 1, 100000)

    _, static.count = imgui.slider_int("Count", static.count, 100, 100000)
    _, static.xybins = imgui.slider_int2("Bins", static.xybins, 1, 500)
    imgui.same_line()
    _, static.hist_flags = imgui.checkbox_flags("Density", static.hist_flags, implot.HistogramFlags_.density)

    max_count = 0
    flags = implot.AxisFlags_.auto_fit | implot.AxisFlags_.foreground

    implot.push_colormap("Hot")
    if implot.begin_plot("##Hist2D", size=(imgui.get_content_region_avail().x - 100 - imgui.get_style().item_spacing.x, 0)):
        implot.setup_axes("", "", flags, flags)
        implot.setup_axes_limits(-6, 6, -6, 6)
        max_count = implot.plot_histogram_2d(
            "Hist2D",
            xs=static.dist1, ys=static.dist2,
            x_bins=static.xybins[0], y_bins=static.xybins[1],
            range=implot.Rect(-6, 6, -6, 6),
            flags=static.hist_flags)  # type: ignore
        implot.end_plot()

    imgui.same_line()
    implot.colormap_scale("Density" if static.hist_flags & implot.HistogramFlags_.density else "Count", 0, max_count, size=(100, 0))
    implot.pop_colormap()


def demo_digital_plots():
    static = demo_digital_plots

    if not hasattr(static, "paused"):
        static.paused = False
        static.data_digital = [ScrollingBuffer(), ScrollingBuffer()]
        static.data_analog = [ScrollingBuffer(), ScrollingBuffer()]
        static.show_digital = [True, False]
        static.show_analog = [True, False]
        static.t = 0.0

    imgui.bullet_text("Digital plots do not respond to Y drag and zoom, so that")
    imgui.indent()
    imgui.text("you can drag analog plots over the rising/falling digital edge.")
    imgui.unindent()

    _, static.show_digital[0] = imgui.checkbox("digital_0", static.show_digital[0])
    imgui.same_line()
    _, static.show_digital[1] = imgui.checkbox("digital_1", static.show_digital[1])
    imgui.same_line()
    _, static.show_analog[0] = imgui.checkbox("analog_0", static.show_analog[0])
    imgui.same_line()
    _, static.show_analog[1] = imgui.checkbox("analog_1", static.show_analog[1])

    if not static.paused:
        static.t += imgui.get_io().delta_time
        if static.show_digital[0]:
            static.data_digital[0].add_point(static.t, np.sin(2 * static.t) > 0.45)
        if static.show_digital[1]:
            static.data_digital[1].add_point(static.t, np.sin(2 * static.t) < 0.45)
        if static.show_analog[0]:
            static.data_analog[0].add_point(static.t, np.sin(2 * static.t))
        if static.show_analog[1]:
            static.data_analog[1].add_point(static.t, np.cos(2 * static.t))

    if implot.begin_plot("##Digital"):
        implot.setup_axis_limits(implot.ImAxis_.x1, static.t - 10.0, static.t,
                                 implot.Cond_.once if static.paused else implot.Cond_.always)
        implot.setup_axis_limits(implot.ImAxis_.y1, -1, 1)

        for i in range(2):
            if static.show_digital[i] and static.data_digital[i].size > 0:
                implot.plot_digital(f"digital_{i}", *static.data_digital[i].get_data())

        for i in range(2):
            if static.show_analog[i] and static.data_analog[i].size > 0:
                implot.plot_line(f"analog_{i}", *static.data_analog[i].get_data())

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_images():
    static = demo_images

    if not hasattr(static, "bmin"):
        static.bmin = [0.0, 0.0]
        static.bmax = [1.0, 1.0]
        static.uv0 = [0.0, 0.0]
        static.uv1 = [1.0, 1.0]
        static.tint =[1.0, 1.0, 1.0, 1.0]

        # Create textures
        # Step 1: create them as numpy arrays
        checker_img = make_checkerboard_texture()
        # Step 2: convert them to OpenGL textures (using imgui_bundle's immvision)
        from imgui_bundle import immvision
        static.tex_checker = immvision.GlTexture(checker_img)
        # Step 3: create ImTextureRef from the OpenGL texture id
        static.tex_id_checker = imgui.ImTextureRef(static.tex_checker.texture_id)

    imgui.bullet_text("Below we are displaying the font texture, which is the only texture we have\naccess to in this demo.")
    imgui.bullet_text("Use the 'ImTextureID' type as storage to pass pointers or identifiers to your\nown texture data.")
    imgui.bullet_text("See ImGui Wiki page 'Image Loading and Displaying Examples'.")

    _, static.bmin = imgui.slider_float2("Min", static.bmin, -2, 2, "%.1f")
    _, static.bmax = imgui.slider_float2("Max", static.bmax, -2, 2, "%.1f")
    _, static.uv0 = imgui.slider_float2("UV0", static.uv0, -2, 2, "%.1f")
    _, static.uv1 = imgui.slider_float2("UV1", static.uv1, -2, 2, "%.1f")
    _, static.tint = imgui.color_edit4("Tint", static.tint)

    if implot.begin_plot("##image"):
        implot.plot_image("my image", static.tex_id_checker,
                          bounds_min=implot.Point(static.bmin[0], static.bmin[1]),
                          bounds_max=implot.Point(static.bmax[0], static.bmax[1]),
                          uv0=ImVec2(static.uv0[0], static.uv0[1]),
                          uv1=ImVec2(static.uv1[0], static.uv1[1]),
                          tint_col=ImVec4(static.tint[0], static.tint[1], static.tint[2], static.tint[3]))
        implot.end_plot()


class RollingBuffer:
    """Simulates a rolling buffer for real-time plotting with fixed history span."""
    def __init__(self, span=10.0):
        self.span = span
        self.data = []

    def add_point(self, x, y):
        self.data.append((x, y))
        self.data = [(px, py) for px, py in self.data if x - px <= self.span]

    def get_data(self):
        if not self.data:
            return np.array([], dtype=np.float32), np.array([], dtype=np.float32)
        data = np.array(self.data, dtype=np.float32)
        return np.ascontiguousarray(data[:, 0]), np.ascontiguousarray(data[:, 1])


#-----------------------------------------------------------------------------

def demo_markers_and_text():
    static = demo_markers_and_text

    if not hasattr(static, "mk_size"):
        static.mk_size = implot.get_style().marker_size
        static.mk_weight = implot.get_style().marker_weight

    _, static.mk_size = imgui.drag_float("Marker Size", static.mk_size, 0.1, 2.0, 10.0, "%.2f px")
    _, static.mk_weight = imgui.drag_float("Marker Weight", static.mk_weight, 0.05, 0.5, 3.0, "%.2f px")

    if implot.begin_plot("##MarkerStyles", size=(-1, 0), flags=implot.Flags_.canvas_only):
        implot.setup_axes("", "", implot.AxisFlags_.no_decorations, implot.AxisFlags_.no_decorations)
        implot.setup_axes_limits(0, 10, 0, 12)

        xs = [1, 4]
        ys = [10, 11]

        # Filled markers
        for m in range(implot.Marker_.count):
            with imgui_ctx.push_id(str(m)):
                implot.set_next_marker_style(m, static.mk_size, implot.AUTO_COL, static.mk_weight)
                implot.plot_line("##Filled", np.array(xs), np.array(ys))
            ys = [ys[0] - 1, ys[1] - 1]

        xs = [6, 9]
        ys = [10, 11]

        # Open markers
        for m in range(implot.Marker_.count):
            with imgui_ctx.push_id(str(m)):
                implot.set_next_marker_style(m, static.mk_size, [0, 0, 0, 0], static.mk_weight)
                implot.plot_line("##Open", np.array(xs), np.array(ys))
            ys = [ys[0] - 1, ys[1] - 1]

        implot.plot_text("Filled Markers", 2.5, 6.0)
        implot.plot_text("Open Markers", 7.5, 6.0)

        implot.push_style_color(implot.Col_.inlay_text, [1, 0, 1, 1])
        implot.plot_text("Vertical Text", 5.0, 6.0, pix_offset=(0, 0), flags=implot.TextFlags_.vertical)
        implot.pop_style_color()

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_nan_values():
    static = demo_nan_values

    if not hasattr(static, "include_nan"):
        static.include_nan = True
        static.flags = 0

    data1 = np.array([0.0, 0.25, 0.5, 0.75, 1.0], dtype=np.float32)
    data2 = np.array([0.0, 0.25, 0.5, 0.75, 1.0], dtype=np.float32)

    if static.include_nan:
        data1[2] = np.nan  # Insert NaN at index 2

    _, static.include_nan = imgui.checkbox("Include NaN", static.include_nan)
    imgui.same_line()
    _, static.flags = imgui.checkbox_flags("Skip NaN", static.flags, implot.LineFlags_.skip_nan)

    if implot.begin_plot("##NaNValues"):
        implot.set_next_marker_style(implot.Marker_.square)
        implot.plot_line("line", data1, data2, flags=static.flags)
        implot.plot_bars("bars", data1)
        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_log_scale():
    static = demo_log_scale

    if not hasattr(static, "xs"):
        static.xs = np.linspace(0.1, 100, 1001, dtype=np.float64)
        static.ys1 = np.sin(static.xs) + 1
        static.ys2 = np.log(static.xs)
        static.ys3 = np.power(10, static.xs[:21])

    if implot.begin_plot("Log Plot", size=(-1, 0)):
        implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.log10)
        implot.setup_axes_limits(0.1, 100, 0, 10)

        implot.plot_line("f(x) = x", static.xs, static.xs)
        implot.plot_line("f(x) = sin(x)+1", static.xs, static.ys1)
        implot.plot_line("f(x) = log(x)", static.xs, static.ys2)
        implot.plot_line("f(x) = 10^x", static.xs[:21], static.ys3)

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_symmetric_log_scale():
    static = demo_symmetric_log_scale

    if not hasattr(static, "xs"):
        static.xs = np.linspace(-50, 50, 1001, dtype=np.float64)
        static.ys1 = np.sin(static.xs)
        static.ys2 = static.xs * 0.002 - 1

    if implot.begin_plot("SymLog Plot", size=(-1, 0)):
        implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.sym_log)

        implot.plot_line("f(x) = a*x+b", static.xs, static.ys2)
        implot.plot_line("f(x) = sin(x)", static.xs, static.ys1)

        implot.end_plot()


class HugeTimeData:
    """Simulates large time-series data for time-scale plotting."""
    Size = 60 * 60 * 24 * 366  # 1 year of second-resolution data (~500MB)

    def __init__(self, t_min):
        """Generates large synthetic time-series data."""
        self.Ts = np.linspace(t_min, t_min + self.Size, self.Size, dtype=np.float64)
        self.Ys = self.get_y(self.Ts)

    @staticmethod
    def get_y(t):
        """Computes the Y values based on time t."""
        return 0.5 + 0.25 * np.sin(t / (86400 * 12)) + 0.005 * np.sin(t / 3600)


def demo_time_scale():
    static = demo_time_scale

    if not hasattr(static, "t_min"):
        static.t_min = 1609459200  # 01/01/2021 @ 12:00:00am (UTC)
        static.t_max = 1640995200  # 01/01/2022 @ 12:00:00am (UTC)
        static.data = None

    imgui.bullet_text("When `ImPlotAxisFlags_Time` is enabled on the X-Axis, values are interpreted as\n"
                      "UNIX timestamps in seconds and axis labels are formatted as date/time.")
    imgui.bullet_text("By default, labels are in UTC time but can be set to use local time instead.")

    style = implot.get_style()
    _, style.use_local_time = imgui.checkbox("Local Time", style.use_local_time)
    imgui.same_line()
    _, style.use_iso8601 = imgui.checkbox("ISO 8601", style.use_iso8601)
    imgui.same_line()
    _, style.use24_hour_clock = imgui.checkbox("24 Hour Clock", style.use24_hour_clock)

    if static.data is None:
        imgui.same_line()
        if imgui.button("Generate Huge Data (~500MB!)"):
            static.data = HugeTimeData(static.t_min)

    if implot.begin_plot("##Time", size=(-1, 0)):
        implot.setup_axis_scale(implot.ImAxis_.x1, implot.Scale_.time)
        implot.setup_axes_limits(static.t_min, static.t_max, 0, 1)

        if static.data is not None:
            plot_limits = implot.get_plot_limits()

            # Compute downsampling factor
            downsample = max(int(plot_limits.x.size() / 1000) + 1, 1)

            # Compute valid start index
            start = int(plot_limits.x.min - static.t_min)
            start = max(0, min(start, HugeTimeData.Size - 1))

            # Compute valid end index
            end = int(plot_limits.x.max - static.t_min) + 1000
            end = max(0, min(end, HugeTimeData.Size - 1))

            # Ensure valid slice size
            # size = max((end - start) // downsample, 1)

            implot.plot_line("Time Series",
                             np.ascontiguousarray(static.data.Ts[start:end:downsample]),
                             np.ascontiguousarray(static.data.Ys[start:end:downsample]))

        # Plot current time marker
        t_now = time.time()
        y_now = float(HugeTimeData.get_y(t_now))

        implot.plot_scatter("Now", np.array([t_now]), np.array([y_now]))
        implot.annotation(
            x=t_now, y=y_now,
            col=implot.get_last_item_color(),
            pix_offset=(10, 10),
            clamp=False,
            fmt="Now")

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_multiple_axes():
    static = demo_multiple_axes

    if not hasattr(static, "xs"):
        static.xs = np.linspace(0, 100, 1001, dtype=np.float64)
        static.xs2 = static.xs + 10.0
        static.ys1 = np.sin(static.xs) * 3 + 1
        static.ys2 = np.cos(static.xs) * 0.2 + 0.5
        static.ys3 = np.sin(static.xs + 0.5) * 100 + 200

        static.x2_axis = True
        static.y2_axis = True
        static.y3_axis = True

    _, static.x2_axis = imgui.checkbox("X-Axis 2", static.x2_axis)
    imgui.same_line()
    _, static.y2_axis = imgui.checkbox("Y-Axis 2", static.y2_axis)
    imgui.same_line()
    _, static.y3_axis = imgui.checkbox("Y-Axis 3", static.y3_axis)

    imgui.bullet_text("You can drag axes to the opposite side of the plot.")
    imgui.bullet_text("Hover over legend items to see which axis they are plotted on.")

    if implot.begin_plot("Multi-Axis Plot", size=(-1, 0)):
        implot.setup_axes("X-Axis 1", "Y-Axis 1")
        implot.setup_axes_limits(0, 100, 0, 10)

        if static.x2_axis:
            implot.setup_axis(implot.ImAxis_.x2, "X-Axis 2", implot.AxisFlags_.aux_default)
            implot.setup_axis_limits(implot.ImAxis_.x2, 0, 100)

        if static.y2_axis:
            implot.setup_axis(implot.ImAxis_.y2, "Y-Axis 2", implot.AxisFlags_.aux_default)
            implot.setup_axis_limits(implot.ImAxis_.y2, 0, 1)

        if static.y3_axis:
            implot.setup_axis(implot.ImAxis_.y3, "Y-Axis 3", implot.AxisFlags_.aux_default)
            implot.setup_axis_limits(implot.ImAxis_.y3, 0, 300)

        implot.plot_line("f(x) = x", static.xs, static.xs)

        if static.x2_axis:
            implot.set_axes(implot.ImAxis_.x2, implot.ImAxis_.y1)
            implot.plot_line("f(x) = sin(x)*3+1", static.xs2, static.ys1)

        if static.y2_axis:
            implot.set_axes(implot.ImAxis_.x1, implot.ImAxis_.y2)
            implot.plot_line("f(x) = cos(x)*.2+.5", static.xs, static.ys2)

        if static.x2_axis and static.y3_axis:
            implot.set_axes(implot.ImAxis_.x2, implot.ImAxis_.y3)
            implot.plot_line("f(x) = sin(x+.5)*100+200", static.xs2, static.ys3)

        implot.end_plot()


#-----------------------------------------------------------------------------
# Demo_LinkedAxes
#-----------------------------------------------------------------------------
def demo_linked_axes():
    static = demo_linked_axes

    if not hasattr(static, "x_min"):
        static.x_min = implot.BoxedValue(0.0)
        static.x_max = implot.BoxedValue(1.0)
        static.y_min = implot.BoxedValue(0.0)
        static.y_max = implot.BoxedValue(1.0)
        static.linkx = True
        static.linky = True

    _, static.linkx = imgui.checkbox("Link X", static.linkx)
    imgui.same_line()
    _, static.linky = imgui.checkbox("Link Y", static.linky)

    data = np.array([0, 1], dtype=np.float32)

    if implot.begin_aligned_plots("AlignedGroup"):
        if implot.begin_plot("Plot A"):
            if static.linkx:
                implot.setup_axis_links(implot.ImAxis_.x1, static.x_min, static.x_max)
            if static.linky:
                implot.setup_axis_links(implot.ImAxis_.y1, static.y_min, static.y_max)
            implot.plot_line("Line", data)
            implot.end_plot()

        if implot.begin_plot("Plot B"):
            if static.linkx:
                implot.setup_axis_links(implot.ImAxis_.x1, static.x_min, static.x_max)
            if static.linky:
                implot.setup_axis_links(implot.ImAxis_.y1, static.y_min, static.y_max)
            implot.plot_line("Line", data)
            implot.end_plot()

        implot.end_aligned_plots()


def demo_axis_constraints():
    static = demo_axis_constraints

    if not hasattr(static, "constraints"):
        static.constraints = [-10, 10, 1, 20]  # X_min, X_max, Zoom_min, Zoom_max
        static.flags = 0

    _, static.constraints[:2] = imgui.drag_float2("Limits Constraints", static.constraints[:2], 0.01)
    _, static.constraints[2:] = imgui.drag_float2("Zoom Constraints", static.constraints[2:], 0.01)
    _, static.flags = imgui.checkbox_flags("Pan Stretch", static.flags, implot.AxisFlags_.pan_stretch)

    if implot.begin_plot("##AxisConstraints", size=(-1, 0)):
        implot.setup_axes("X", "Y", static.flags, static.flags)
        implot.setup_axes_limits(-1, 1, -1, 1)

        implot.setup_axis_limits_constraints(implot.ImAxis_.x1, static.constraints[0], static.constraints[1])
        implot.setup_axis_zoom_constraints(implot.ImAxis_.x1, static.constraints[2], static.constraints[3])
        implot.setup_axis_limits_constraints(implot.ImAxis_.y1, static.constraints[0], static.constraints[1])
        implot.setup_axis_zoom_constraints(implot.ImAxis_.y1, static.constraints[2], static.constraints[3])

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_equal_axes():
    static = demo_equal_axes

    if not hasattr(static, "xs1"):
        angles = np.linspace(0, 2 * np.pi, 360)
        static.xs1 = np.cos(angles)
        static.ys1 = np.sin(angles)

        static.xs2 = np.array([-1, 0, 1, 0, -1], dtype=np.float32)
        static.ys2 = np.array([0, 1, 0, -1, 0], dtype=np.float32)

    imgui.bullet_text("Equal constraint applies to axis pairs (e.g. X1/Y1, X2/Y2)")

    if implot.begin_plot("##EqualAxes", size=(-1, 0), flags=implot.Flags_.equal):
        implot.setup_axis(implot.ImAxis_.x2, None, implot.AxisFlags_.aux_default)
        implot.setup_axis(implot.ImAxis_.y2, None, implot.AxisFlags_.aux_default)

        implot.plot_line("Circle", static.xs1, static.ys1)

        implot.set_axes(implot.ImAxis_.x2, implot.ImAxis_.y2)
        implot.plot_line("Diamond", static.xs2, static.ys2)

        implot.end_plot()


#-----------------------------------------------------------------------------

def demo_auto_fitting_data():
    static = demo_auto_fitting_data

    if not hasattr(static, "xflags"):
        static.xflags = implot.AxisFlags_.none
        static.yflags = implot.AxisFlags_.auto_fit | implot.AxisFlags_.range_fit
        static.data = 1 + np.sin(np.arange(101) / 10.0)

    imgui.bullet_text("The Y-axis has been configured to auto-fit to only the data visible in X-axis range.")
    imgui.bullet_text("Zoom and pan the X-axis. Disable Stems to see a difference in fit.")
    imgui.bullet_text("If `ImPlotAxisFlags_RangeFit` is disabled, the axis will fit **ALL** data.")

    imgui.text_unformatted("X: ")
    imgui.same_line()
    _, static.xflags = imgui.checkbox_flags("ImPlotAxisFlags_AutoFit##X", static.xflags, implot.AxisFlags_.auto_fit)
    imgui.same_line()
    _, static.xflags = imgui.checkbox_flags("ImPlotAxisFlags_RangeFit##X", static.xflags, implot.AxisFlags_.range_fit)

    imgui.text_unformatted("Y: ")
    imgui.same_line()
    _, static.yflags = imgui.checkbox_flags("ImPlotAxisFlags_AutoFit##Y", static.yflags, implot.AxisFlags_.auto_fit)
    imgui.same_line()
    _, static.yflags = imgui.checkbox_flags("ImPlotAxisFlags_RangeFit##Y", static.yflags, implot.AxisFlags_.range_fit)

    if implot.begin_plot("##DataFitting"):
        implot.setup_axes("X", "Y", static.xflags, static.yflags)
        implot.plot_line("Line", static.data)
        implot.plot_stems("Stems", static.data)
        implot.end_plot()


def demo_subplots_sizing():
    static = demo_subplots_sizing

    if not hasattr(static, "flags"):
        static.flags = implot.SubplotFlags_.share_items | implot.SubplotFlags_.no_legend

    _, static.flags = imgui.checkbox_flags("ImPlotSubplotFlags_NoResize", static.flags, implot.SubplotFlags_.no_resize)
    _, static.flags = imgui.checkbox_flags("ImPlotSubplotFlags_NoTitle", static.flags, implot.SubplotFlags_.no_title)

    if not hasattr(static, "rows"):
        static.rows = 3
        static.cols = 3

    _, static.rows = imgui.slider_int("Rows", static.rows, 1, 5)
    _, static.cols = imgui.slider_int("Cols", static.cols, 1, 5)

    if static.rows < 1 or static.cols < 1:
        imgui.text_colored(ImVec4(1, 0, 0, 1), "Nice try, but the number of rows and columns must be greater than 0!")
        return

    if not hasattr(static, "rratios"):
        static.rratios = [5, 1, 1, 1, 1, 1]
        static.cratios = [5, 1, 1, 1, 1, 1]

    # imgui.drag_scalar_n("Row Ratios", static.rratios, static.rows, 0.01)
    # imgui.drag_scalar_n("Col Ratios", static.cratios, static.cols, 0.01)

    row_col_ratios = implot.SubplotsRowColRatios(static.rratios, static.cratios)
    if implot.begin_subplots(
            title_id="My Subplots",
            rows=static.rows, cols=static.cols,
            size=(-1, 400),
            flags=static.flags,
            row_col_ratios=row_col_ratios):
        id_counter = 0
        for i in range(static.rows * static.cols):
            if implot.begin_plot("", size=(0, 0), flags=implot.Flags_.no_legend):
                implot.setup_axes("", "", implot.AxisFlags_.no_decorations, implot.AxisFlags_.no_decorations)

                # Compute sinewave data
                fi = 0.01 * (i + 1)
                x_values = np.linspace(0, 1000, 1000, dtype=np.float32)
                y_values = np.sin(fi * x_values)

                # Apply colormap based on subplot index
                if static.rows * static.cols > 1:
                    col = implot.sample_colormap(i / float(static.rows * static.cols - 1), implot.Colormap_.jet)
                    implot.set_next_line_style(col)

                # Label and plot line
                label = f"data{id_counter}"
                id_counter += 1
                implot.plot_line(label, x_values, y_values)

                implot.end_plot()
        implot.end_subplots()


def demo_subplot_item_sharing():
    static = demo_subplot_item_sharing

    if not hasattr(static, "flags"):
        static.flags = implot.SubplotFlags_.share_items

    _, static.flags = imgui.checkbox_flags("ImPlotSubplotFlags_ShareItems", static.flags, implot.SubplotFlags_.share_items)
    _, static.flags = imgui.checkbox_flags("ImPlotSubplotFlags_ColMajor", static.flags, implot.SubplotFlags_.col_major)

    imgui.bullet_text("Drag and drop items from the legend onto plots (except for 'common')")

    if not hasattr(static, "rows"):
        static.rows = 2
        static.cols = 3
        static.id = [0, 1, 2, 3, 4, 5]
        static.curj = -1  # Current dataset being dragged

    if implot.begin_subplots("##ItemSharing", static.rows, static.cols, size=(-1, 400), flags=static.flags):
        implot.setup_legend(implot.Location_.south, implot.LegendFlags_.sort | implot.LegendFlags_.horizontal)

        for i in range(static.rows * static.cols):
            if implot.begin_plot(""):
                # Common sinewave plot
                x_values = np.linspace(0, 1000, 1000, dtype=np.float32)
                y_values = np.sin(0.01 * x_values)
                implot.plot_line("common", x_values, y_values)

                for j in range(6):
                    if static.id[j] == i:
                        label = f"data{j}"
                        y_j_values = np.sin((0.01 * (j + 2)) * x_values)
                        implot.plot_line(label, x_values, y_j_values)

                        # Drag source
                        if imgui.begin_drag_drop_source():
                            static.curj = j
                            imgui.set_drag_drop_payload_py_id("MY_DND", 0, 0)
                            implot.item_icon(implot.get_last_item_color())
                            imgui.same_line()
                            imgui.text(label)
                            imgui.end_drag_drop_source()

                # Drop target
                if imgui.begin_drag_drop_target():
                    payload = imgui.accept_drag_drop_payload_py_id("MY_DND")
                    if payload:
                        static.id[static.curj] = i
                    imgui.end_drag_drop_target()

                implot.end_plot()
        implot.end_subplots()


def demo_subplot_axis_linking():
    static = demo_subplot_axis_linking

    if not hasattr(static, "flags"):
        static.flags = implot.SubplotFlags_.link_rows | implot.SubplotFlags_.link_cols

    _, static.flags = imgui.checkbox_flags("ImPlotSubplotFlags_LinkRows", static.flags, implot.SubplotFlags_.link_rows)
    _, static.flags = imgui.checkbox_flags("ImPlotSubplotFlags_LinkCols", static.flags, implot.SubplotFlags_.link_cols)
    _, static.flags = imgui.checkbox_flags("ImPlotSubplotFlags_LinkAllX", static.flags, implot.SubplotFlags_.link_all_x)
    _, static.flags = imgui.checkbox_flags("ImPlotSubplotFlags_LinkAllY", static.flags, implot.SubplotFlags_.link_all_y)

    if not hasattr(static, "rows"):
        static.rows = 2
        static.cols = 2

    if implot.begin_subplots("##AxisLinking", static.rows, static.cols, size=(-1, 400), flags=static.flags):
        for _ in range(static.rows * static.cols):
            if implot.begin_plot(""):
                implot.setup_axes_limits(0, 1000, -1, 1)

                # Generate sine wave data
                x_values = np.linspace(0, 1000, 1000, dtype=np.float32)
                y_values = np.sin(0.01 * x_values)

                implot.plot_line("common", x_values, y_values)

                implot.end_plot()
        implot.end_subplots()


#-----------------------------------------------------------------------------
def demo_drag_points():
    static = demo_drag_points
    imgui.bullet_text("Click and drag each point.")

    if not hasattr(static, "flags"):
        static.flags = implot.DragToolFlags_.none

    _, static.flags = imgui.checkbox_flags("No Cursors", static.flags, implot.DragToolFlags_.no_cursors)
    imgui.same_line()
    _, static.flags = imgui.checkbox_flags("No Fit", static.flags, implot.DragToolFlags_.no_fit)
    imgui.same_line()
    _, static.flags = imgui.checkbox_flags("No Input", static.flags, implot.DragToolFlags_.no_inputs)

    ax_flags = implot.AxisFlags_.no_tick_labels | implot.AxisFlags_.no_tick_marks
    clicked, hovered, held = [False] * 4, [False] * 4, [False] * 4

    if implot.begin_plot("##Bezier", size=(-1, 0), flags=implot.Flags_.canvas_only):
        implot.setup_axes("", "", ax_flags, ax_flags)
        implot.setup_axes_limits(0, 1, 0, 1)

        if not hasattr(static, "P"):
            static.P = [implot.Point(0.05, 0.05), implot.Point(0.2, 0.4), implot.Point(0.8, 0.6), implot.Point(0.95, 0.95)]

        colors = [[0, 0.9, 0, 1], [1, 0.5, 1, 1], [0, 0.5, 1, 1], [0, 0.9, 0, 1]]
        for i in range(4):
            _, static.P[i].x, static.P[i].y, clicked[i], hovered[i], held[i] = implot.drag_point(  # type: ignore
                id_=i, x=static.P[i].x, y=static.P[i].y, col=colors[i], flags=static.flags, held=held[i])

        # Compute Bézier curve
        t_vals = np.linspace(0, 1, 100)
        u = 1 - t_vals
        w1, w2, w3, w4 = u**3, 3 * u**2 * t_vals, 3 * u * t_vals**2, t_vals**3
        b = np.dot(np.column_stack((w1, w2, w3, w4)), [[p.x, p.y] for p in static.P])

        # Ensure 1D contiguous arrays using `.ravel()`
        implot.plot_line("##bez", b[:, 0].ravel(), b[:, 1].ravel())

        implot.end_plot()


def demo_drag_lines():
    static = demo_drag_lines

    imgui.bullet_text("Click and drag the horizontal and vertical lines.")

    if not hasattr(static, "x1"):
        static.x1 = 0.2
        static.x2 = 0.8
        static.y1 = 0.25
        static.y2 = 0.75
        static.f = 0.1
        static.flags = implot.DragToolFlags_.none

    _, static.flags = imgui.checkbox_flags("No Cursors", static.flags, implot.DragToolFlags_.no_cursors)
    imgui.same_line()
    _, static.flags = imgui.checkbox_flags("No Fit", static.flags, implot.DragToolFlags_.no_fit)
    imgui.same_line()
    _, static.flags = imgui.checkbox_flags("No Input", static.flags, implot.DragToolFlags_.no_inputs)


    if implot.begin_plot("##lines", size=(-1, 0)):
        implot.setup_axes_limits(0, 1, 0, 1)

        # Drag lines
        _changed, static.x1, _, _, _ = implot.drag_line_x(0, x=static.x1, col=[1, 1, 1, 1], thickness=1, flags=static.flags)
        _changed, static.x2, _, _, _ = implot.drag_line_x(1, x=static.x2, col=[1, 1, 1, 1], thickness=1, flags=static.flags)
        _changed, static.y1, _, _, _ = implot.drag_line_y(2, static.y1, col=[1, 1, 1, 1], thickness=1, flags=static.flags)
        _changed, static.y2, _, _, _ = implot.drag_line_y(3, static.y2, col=[1, 1, 1, 1], thickness=1, flags=static.flags)

        # Compute curve based on dragged values
        t_vals = np.linspace(-0.5, 0.5, 1000)
        xs = (static.x2 + static.x1) / 2 + np.abs(static.x2 - static.x1) * t_vals
        ys = (static.y1 + static.y2) / 2 + np.abs(static.y2 - static.y1) / 2 * np.sin(static.f * np.arange(1000) / 10)

        # Drag frequency line
        _, static.f, clicked, hovered, held = implot.drag_line_y(120482, static.f, col=[1, 0.5, 1, 1], thickness=1, flags=static.flags)

        implot.set_next_line_style(implot.AUTO_COL, 2.0 if hovered or held else 1.0)
        implot.plot_line("Interactive Data", xs, ys)

        implot.end_plot()


class DemoDragRectState:
    x_data: NDArray[np.float64]
    y_data1: NDArray[np.float64]
    y_data2: NDArray[np.float64]
    y_data3: NDArray[np.float64]
    rect: implot.Rect
    flags: int

    def __init__(self):
        import math
        nb_data = 512
        sampling_freq = 44100
        freq = 500.0
        i = np.arange(-nb_data, 2 * nb_data, 1)
        t = i / sampling_freq
        self.x_data = t
        arg = 2 * math.pi * freq * t
        self.y_data1 = np.sin(arg)
        self.y_data2 = self.y_data1 - 0.6 + np.sin(arg * 2) * 0.4
        self.y_data3 = self.y_data2 - 0.6 + np.sin(arg * 3) * 0.4
        self.rect = implot.Rect(0.0025, 0.0075, -2.7, 1.1)  # type: ignore
        self.flags = implot.DragToolFlags_.none


def demo_drag_rects():
    static = demo_drag_rects
    if not hasattr(static, "state"):
        static.state = DemoDragRectState()
    state = static.state

    imgui.bullet_text("Click and drag the edges, corners, and center of the rect.")
    _, state.flags = imgui.checkbox_flags(
        "NoCursors", state.flags, implot.DragToolFlags_.no_cursors
    )
    imgui.same_line()
    _, state.flags = imgui.checkbox_flags(
        "NoFit", state.flags, implot.DragToolFlags_.no_fit
    )
    imgui.same_line()
    _, state.flags = imgui.checkbox_flags(
        "NoInput", state.flags, implot.DragToolFlags_.no_inputs
    )

    plot_height = immapp.em_size() * 15
    if implot.begin_plot("##Main", ImVec2(-1, plot_height)):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_tick_labels, implot.ImPlotAxisFlags_.no_tick_labels)
        # implot.setup_axes_limits(0, 0.01, -1, 1)
        implot.plot_line("Signal 1", state.x_data, state.y_data1)
        implot.plot_line("Signal 2", state.x_data, state.y_data2)
        implot.plot_line("Signal 3", state.x_data, state.y_data3)
        (
            _,
            state.rect.x.min,
            state.rect.y.min,
            state.rect.x.max,
            state.rect.y.max,
            clicked,
            hovered,
            held,
        ) = implot.drag_rect(
            0,
            state.rect.x.min,
            state.rect.y.min,
            state.rect.x.max,
            state.rect.y.max,
            ImVec4(1, 0, 1, 1),
            state.flags,
        )

        # Example showing how to use implot_internal
        implot.internal.fit_point(implot.Point(0, -3.5))
        implot.internal.fit_point(implot.Point(0, 1.5))

        implot.end_plot()
    if implot.begin_plot("##rect", ImVec2(-1, plot_height), implot.Flags_.canvas_only):
        # implot.setup_axes("", "", implot.ImPlotAxisFlags_.no_decorations, implot.ImPlotAxisFlags_.no_decorations)
        implot.setup_axes_limits(
            state.rect.x.min,
            state.rect.x.max,
            state.rect.y.min,
            state.rect.y.max,
            imgui.Cond_.always,
        )
        implot.plot_line("Signal 1", state.x_data, state.y_data1)
        implot.plot_line("Signal 2", state.x_data, state.y_data2)
        implot.plot_line("Signal 3", state.x_data, state.y_data3)
        implot.end_plot()


def demo_annotations():
    static = demo_annotations
    if not hasattr(static, "clamp"):
        static.clamp = False

    _, static.clamp = imgui.checkbox("Clamp", static.clamp)

    if implot.begin_plot("##Annotations"):
        implot.setup_axes_limits(0, 2, 0, 1)

        px = np.array([0.25, 0.25, 0.75, 0.75], dtype=np.float32)
        py = np.array([0.25, 0.75, 0.75, 0.25], dtype=np.float32)
        implot.plot_scatter("##Points", px, py)

        col = implot.get_last_item_color()
        implot.annotation(0.25, 0.25, col, ImVec2(-15, 15), static.clamp, "BL")
        implot.annotation(0.75, 0.25, col, ImVec2(15, 15), static.clamp, "BR")
        implot.annotation(0.75, 0.75, col, ImVec2(15, -15), static.clamp, "TR")
        implot.annotation(0.25, 0.75, col, ImVec2(-15, -15), static.clamp, "TL")
        implot.annotation(0.5, 0.5, col, ImVec2(0, 0), static.clamp, "Center")

        implot.annotation(1.25, 0.75, ImVec4(0, 1, 0, 1), ImVec2(0, 0), static.clamp)

        bx = np.array([1.2, 1.5, 1.8], dtype=np.float32)
        by = np.array([0.25, 0.5, 0.75], dtype=np.float32)
        implot.plot_bars("##Bars", bx, by, 0.2)
        for i in range(3):
            implot.annotation(
                x=float(bx[i]), y=float(by[i]),
                col=ImVec4(0, 0, 0, 0),
                pix_offset=ImVec2(0, -5),
                clamp=static.clamp,
                fmt="B[%d]=%.2f" % (i, float(by[i]))
            )
        implot.end_plot()


def demo_tags():
    static = demo_tags

    if not hasattr(static, "show"):
        static.show = True
        static.drag_tag = 0.25

    _, static.show = imgui.checkbox("Show Tags", static.show)

    if implot.begin_plot("##Tags"):
        implot.setup_axis(implot.ImAxis_.x2)
        implot.setup_axis(implot.ImAxis_.y2)

        if static.show:
            implot.tag_x(0.25, ImVec4(1, 1, 0, 1))
            implot.tag_y(0.75, ImVec4(1, 1, 0, 1))

            _, static.drag_tag, _, _, _ = implot.drag_line_y(
                id_=0, y=static.drag_tag, col=ImVec4(1, 0, 0, 1), thickness=1, flags=implot.DragToolFlags_.no_fit
            )

            implot.tag_y(static.drag_tag, ImVec4(1, 0, 0, 1), "Drag")

            implot.set_axes(implot.ImAxis_.x2, implot.ImAxis_.y2)
            implot.tag_x(0.5, ImVec4(0, 1, 1, 1), "MyTag")
            implot.tag_y(0.5, ImVec4(0, 1, 1, 1), "Tag: %d" % 42)

        implot.end_plot()


def sparkline(label_id, values, y_min, y_max, offset, color, size):
    implot.push_style_var(implot.StyleVar_.plot_padding, ImVec2(0, 0))
    if implot.begin_plot(label_id, size, implot.Flags_.canvas_only):
        implot.setup_axes("", "", implot.AxisFlags_.no_decorations, implot.AxisFlags_.no_decorations)
        implot.setup_axes_limits(0, len(values) - 1, y_min, y_max, imgui.Cond_.always)
        implot.set_next_line_style(color)
        implot.plot_line("line", values, offset=offset)
        implot.end_plot()
    implot.pop_style_var()


def demo_tables():
    static = demo_tables

    if not hasattr(static, "anim"):
        static.anim = True
        static.offset = 0
        static.flags = (
                imgui.TableFlags_.borders_outer | imgui.TableFlags_.borders_v |
                imgui.TableFlags_.row_bg | imgui.TableFlags_.resizable |
                imgui.TableFlags_.reorderable
        )

    imgui.bullet_text("Plots can be used inside of ImGui tables as another means of creating subplots.")
    _, static.anim = imgui.checkbox("Animate", static.anim)

    if static.anim:
        static.offset = (static.offset + 1) % 100

    if imgui.begin_table("##table", 3, static.flags, (-1, 0)):
        imgui.table_setup_column("Electrode", imgui.TableColumnFlags_.width_fixed, 75.0)
        imgui.table_setup_column("Voltage", imgui.TableColumnFlags_.width_fixed, 75.0)
        imgui.table_setup_column("EMG Signal")
        imgui.table_headers_row()

        implot.push_colormap(implot.Colormap_.cool)

        for row in range(10):
            imgui.table_next_row()

            np.random.seed(row)
            data = np.random.uniform(0.0, 10.0, 100)

            imgui.table_set_column_index(0)
            imgui.text(f"EMG {row}")

            imgui.table_set_column_index(1)
            imgui.text(f"{data[static.offset]:.3f} V")

            imgui.table_set_column_index(2)
            with imgui_ctx.push_id(str(row)):
                sparkline("##spark", data, y_min=0, y_max=11.0, offset=static.offset,
                                 color=implot.get_colormap_color(row), size=(-1, 35))

        implot.pop_colormap()
        imgui.end_table()


def style_seaborn():
    style = implot.get_style()
    style.set_color_(implot.Col_.line, implot.AUTO_COL)
    style.set_color_(implot.Col_.fill, implot.AUTO_COL)
    style.set_color_(implot.Col_.marker_outline, implot.AUTO_COL)
    style.set_color_(implot.Col_.marker_fill, implot.AUTO_COL)

    style.set_color_(implot.Col_.error_bar, ImVec4(0.00, 0.00, 0.00, 1.00))
    style.set_color_(implot.Col_.frame_bg, ImVec4(1.00, 1.00, 1.00, 1.00))
    style.set_color_(implot.Col_.plot_bg, ImVec4(0.92, 0.92, 0.95, 1.00))
    style.set_color_(implot.Col_.plot_border, ImVec4(0.00, 0.00, 0.00, 0.00))
    style.set_color_(implot.Col_.legend_bg, ImVec4(0.92, 0.92, 0.95, 1.00))
    style.set_color_(implot.Col_.legend_border, ImVec4(0.80, 0.81, 0.85, 1.00))
    style.set_color_(implot.Col_.legend_text, ImVec4(0.00, 0.00, 0.00, 1.00))
    style.set_color_(implot.Col_.title_text, ImVec4(0.00, 0.00, 0.00, 1.00))
    style.set_color_(implot.Col_.inlay_text, ImVec4(0.00, 0.00, 0.00, 1.00))
    style.set_color_(implot.Col_.axis_text, ImVec4(0.00, 0.00, 0.00, 1.00))
    style.set_color_(implot.Col_.axis_grid, ImVec4(1.00, 1.00, 1.00, 1.00))
    style.set_color_(implot.Col_.axis_bg_hovered, ImVec4(0.92, 0.92, 0.95, 1.00))
    style.set_color_(implot.Col_.axis_bg_active, ImVec4(0.92, 0.92, 0.95, 0.75))
    style.set_color_(implot.Col_.selection, ImVec4(1.00, 0.65, 0.00, 1.00))
    style.set_color_(implot.Col_.crosshairs, ImVec4(0.23, 0.10, 0.64, 0.50))

    style.line_weight = 1.5
    style.marker = implot.Marker_.none
    style.marker_size = 4
    style.marker_weight = 1
    style.fill_alpha = 1.0
    style.error_bar_size = 5
    style.error_bar_weight = 1.5
    style.digital_bit_height = 8
    style.digital_bit_gap = 4
    style.plot_border_size = 0
    style.minor_alpha = 1.0
    style.major_tick_len = ImVec2(0, 0)
    style.minor_tick_len = ImVec2(0, 0)
    style.major_tick_size = ImVec2(0, 0)
    style.minor_tick_size = ImVec2(0, 0)
    style.major_grid_size = ImVec2(1.2, 1.2)
    style.minor_grid_size = ImVec2(1.2, 1.2)
    style.plot_padding = ImVec2(12, 12)
    style.label_padding = ImVec2(5, 5)
    style.legend_padding = ImVec2(5, 5)
    style.mouse_pos_padding = ImVec2(5, 5)
    style.plot_min_size = ImVec2(300, 225)


def demo_custom_styles():
    # Apply Seaborn style
    import copy
    implot.push_colormap(implot.Colormap_.deep)
    backup_style = copy.copy(implot.get_style())
    style_seaborn()
    if implot.begin_plot("Seaborn Style"):
        implot.setup_axes("x-axis", "y-axis")
        implot.setup_axes_limits(-0.5, 9.5, 0, 10)
        lin = np.array([8, 8, 9, 7, 8, 8, 8, 9, 7, 8], dtype=np.uint32)
        bar = np.array([1, 2, 5, 3, 4, 1, 2, 5, 3, 4], dtype=np.uint32)
        dot = np.array([7, 6, 6, 7, 8, 5, 6, 5, 8, 7], dtype=np.uint32)
        implot.plot_bars("Bars", bar, 0.5)
        implot.plot_line("Line", lin)
        implot.next_colormap_color() # skip green
        implot.plot_scatter("Scatter", dot)
        implot.end_plot()

    # Restore previous style
    implot.set_style(backup_style)
    implot.pop_colormap()


#-----------------------------------------------------------------------------

def demo_custom_rendering():
    if implot.begin_plot("##CustomRend"):
        cntr = implot.plot_to_pixels(implot.Point(0.5, 0.5))
        rmin = implot.plot_to_pixels(implot.Point(0.25, 0.75))
        rmax = implot.plot_to_pixels(implot.Point(0.75, 0.25))

        implot.push_plot_clip_rect()
        draw_list = implot.get_plot_draw_list()
        draw_list.add_circle_filled(cntr, 20, imgui.IM_COL32(255, 255, 0, 255), 20)
        draw_list.add_rect(rmin, rmax, imgui.IM_COL32(128, 0, 255, 255))
        implot.pop_plot_clip_rect()

        implot.end_plot()


def demo_legend_popups():
    static = demo_legend_popups

    imgui.bullet_text("You can implement legend context menus to inject per-item controls and widgets.")
    imgui.bullet_text("Right-click the legend label/icon to edit custom item attributes.")

    if not hasattr(static, "frequency"):
        static.frequency = 0.1
        static.amplitude = 0.5
        static.color = [1.0, 1.0, 0.0]
        static.alpha = 1.0
        static.line = False
        static.thickness = 1.0
        static.markers = False
        static.shaded = False

    vals = static.amplitude * np.sin(static.frequency * np.arange(101, dtype=np.float32))

    if implot.begin_plot("Right Click the Legend"):
        implot.setup_axes_limits(0, 100, -1, 1)

        implot.push_style_var(implot.StyleVar_.fill_alpha, static.alpha)

        if not static.line:
            implot.set_next_fill_style(ImVec4(static.color[0], static.color[1], static.color[2], 1.0))
            implot.plot_bars("Right Click Me", vals)
        else:
            if static.markers:
                implot.set_next_marker_style(implot.Marker_.square)
            implot.set_next_line_style(ImVec4(static.color[0], static.color[1], static.color[2], 1.0), static.thickness)
            implot.plot_line("Right Click Me", vals)
            if static.shaded:
                implot.plot_shaded("Right Click Me", vals)

        implot.pop_style_var()

        # Custom legend context menu
        if implot.begin_legend_popup("Right Click Me"):
            _, static.frequency = imgui.slider_float("Frequency", static.frequency, 0, 1, "%0.2f")
            _, static.amplitude = imgui.slider_float("Amplitude", static.amplitude, 0, 1, "%0.2f")
            imgui.separator()
            _, static.color = imgui.color_edit3("Color", static.color[:3])
            _, static.alpha = imgui.slider_float("Transparency", static.alpha, 0, 1, "%.2f")
            _, static.line = imgui.checkbox("Line Plot", static.line)
            if static.line:
                _, static.thickness = imgui.slider_float("Thickness", static.thickness, 0, 5)
                _, static.markers = imgui.checkbox("Markers", static.markers)
                _, static.shaded = imgui.checkbox("Shaded", static.shaded)
            implot.end_legend_popup()

        implot.end_plot()


def demo_colormap_widgets():
    static = demo_colormap_widgets

    if not hasattr(static, "cmap"):
        static.cmap = implot.Colormap_.viridis
        static.t = 0.5
        static.col = [1.0, 1.0, 1.0, 1.0]  # Placeholder color
        static.scale = [0, 100]
        static.flags = 0

    # Colormap Button
    if implot.colormap_button("Button", size=(0, 0), cmap=static.cmap):
        static.cmap = (static.cmap + 1) % implot.get_colormap_count()

    # Colormap Slider
    imgui.color_button("##Display", static.col, imgui.ColorEditFlags_.no_inputs)
    imgui.same_line()
    # _, static.t, static.col = implot.colormap_slider(
    #     label="Slider",
    #     t=static.t,
    #     out=static.col,
    #     format="%.3f",
    #     cmap=static.cmap)

    # Colormap Icon
    implot.colormap_icon(static.cmap)
    imgui.same_line()
    imgui.text("Icon")

    # Colormap Scale
    implot.colormap_scale("Scale", static.scale[0], static.scale[1], size=(0, 0), format="%g dB", flags=static.flags, cmap=static.cmap)

    # Input for Scale Values
    _, static.scale = imgui.input_float2("Scale", static.scale)

    # Checkbox Flags for Scale Behavior
    _, static.flags = imgui.checkbox_flags("No Label", static.flags, implot.ColormapScaleFlags_.no_label)
    _, static.flags = imgui.checkbox_flags("Opposite", static.flags, implot.ColormapScaleFlags_.opposite)
    _, static.flags = imgui.checkbox_flags("Invert", static.flags, implot.ColormapScaleFlags_.invert)


#-----------------------------------------------------------------------------
# DEMO WINDOW
#-----------------------------------------------------------------------------
def demo_header(label, demo_function):
    static = demo_header
    fn_id = id(demo_function)
    if not hasattr(static, "fn_snippets"):
        static.fn_snippets = {}
    if fn_id not in static.fn_snippets:
        import inspect
        source = inspect.getsource(demo_function)
        snippet_data = immapp.snippets.SnippetData(code=source)
        snippet_data.show_copy_button = True
        snippet_data.max_height_in_lines = 30
        static.fn_snippets[fn_id] = snippet_data

    if imgui.tree_node_ex(label):
        if imgui.tree_node_ex("Source code"):
            snippet_data = static.fn_snippets[fn_id]
            immapp.snippets.show_code_snippet(snippet_data)
            imgui.tree_pop()
        demo_function()
        imgui.tree_pop()


def show_all_demos():
    """Main function to display all ImPlot demos with categorized tabs."""
    imgui.text(f"ImPlot says hello. ({implot.version})")
    imgui.spacing()

    if imgui.begin_tab_bar("ImPlotDemoTabs"):
        if imgui.begin_tab_item_simple("Plots"):
            demo_header("Line Plots", demo_line_plots)
            demo_header("Filled Line Plots", demo_filled_line_plots)
            demo_header("Shaded Plots", demo_shaded_plots)
            demo_header("Scatter Plots", demo_scatter_plots)
            # demo_header("Realtime Plots", demo_realtime_plots)
            demo_header("Stairstep Plots", demo_stairstep_plots)
            demo_header("Bar Plots", demo_bar_plots)
            demo_header("Bar Groups", demo_bar_groups)
            demo_header("Bar Stacks", demo_bar_stacks)
            demo_header("Error Bars", demo_error_bars)
            demo_header("Stem Plots", demo_stem_plots)
            demo_header("Infinite Lines", demo_infinite_lines)
            demo_header("Pie Charts", demo_pie_charts)
            demo_header("Heatmaps", demo_heatmaps)
            demo_header("Histogram", demo_histogram)
            demo_header("Histogram 2D", demo_histogram2d)
            demo_header("Digital Plots", demo_digital_plots)
            demo_header("Images", demo_images)
            demo_header("Markers and Text", demo_markers_and_text)
            demo_header("NaN Values", demo_nan_values)
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Subplots"):
            demo_header("Sizing", demo_subplots_sizing)
            demo_header("Item Sharing", demo_subplot_item_sharing)
            demo_header("Axis Linking", demo_subplot_axis_linking)
            demo_header("Tables", demo_tables)
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Axes"):
            demo_header("Log Scale", demo_log_scale)
            demo_header("Symmetric Log Scale", demo_symmetric_log_scale)
            demo_header("Time Scale", demo_time_scale)
            # demo_header("Custom Scale", demo_custom_scale)
            demo_header("Multiple Axes", demo_multiple_axes)
            # demo_header("Tick Labels", demo_tick_labels)
            demo_header("Linked Axes", demo_linked_axes)
            demo_header("Axis Constraints", demo_axis_constraints)
            demo_header("Equal Axes", demo_equal_axes)
            demo_header("Auto-Fitting Data", demo_auto_fitting_data)
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Tools"):
            # demo_header("Offset and Stride", demo_offset_and_stride)
            demo_header("Drag Points", demo_drag_points)
            demo_header("Drag Lines", demo_drag_lines)
            demo_header("Drag Rects", demo_drag_rects)
            # demo_header("Querying", demo_querying)
            demo_header("Annotations", demo_annotations)
            demo_header("Tags", demo_tags)
            # demo_header("Drag and Drop", demo_drag_and_drop)
            # demo_header("Legend Options", demo_legend_options)
            demo_header("Legend Popups", demo_legend_popups)
            demo_header("Colormap Widgets", demo_colormap_widgets)
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Custom"):
            demo_header("Custom Styles", demo_custom_styles)
            # demo_header("Custom Data and Getters", demo_custom_data_and_getters)
            demo_header("Custom Rendering", demo_custom_rendering)
            demo_header("Custom Plotters and Tooltips", demo_custom_plotters_and_tooltips)
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Config"):
            demo_config()
            imgui.end_tab_item()

        if imgui.begin_tab_item_simple("Help"):
            demo_help()
            imgui.end_tab_item()

        imgui.end_tab_bar()


def show_demo_window():
    """Main ImPlot Demo Window with menu options for various ImPlot and ImGui tools."""
    static = show_demo_window

    if not hasattr(static, "show_implot_metrics"):
        static.show_implot_metrics = False
        static.show_implot_style_editor = False
        static.show_imgui_metrics = False
        static.show_imgui_style_editor = False
        static.show_imgui_demo = False

    # Show Metrics Windows
    if static.show_implot_metrics:
        implot.show_metrics_window()

    # Show ImPlot Style Editor
    if static.show_implot_style_editor:
        imgui.set_next_window_size((415, 762), imgui.Cond_.appearing)
        imgui.begin("Style Editor (ImPlot)", True)
        implot.show_style_editor()
        imgui.end()

    # Show ImGui Style Editor
    if static.show_imgui_style_editor:
        imgui.begin("Style Editor (ImGui)", True)
        imgui.show_style_editor()
        imgui.end()

    # Show ImGui Metrics
    if static.show_imgui_metrics:
        imgui.show_metrics_window()

    # Show ImGui Demo Window
    if static.show_imgui_demo:
        imgui.show_demo_window()

    # Main Demo Window
    imgui.set_next_window_pos((50, 50), imgui.Cond_.first_use_ever)
    imgui.set_next_window_size((600, 750), imgui.Cond_.first_use_ever)
    imgui.begin("ImPlot Demo", True, imgui.WindowFlags_.menu_bar)

    if imgui.begin_menu_bar():
        if imgui.begin_menu("Tools"):
            _, static.show_implot_metrics = imgui.menu_item("Metrics", "", static.show_implot_metrics)
            _, static.show_implot_style_editor = imgui.menu_item("Style Editor", "", static.show_implot_style_editor)
            imgui.separator()
            _, static.show_imgui_metrics = imgui.menu_item("ImGui Metrics", "", static.show_imgui_metrics)
            _, static.show_imgui_style_editor = imgui.menu_item("ImGui Style Editor", "", static.show_imgui_style_editor)
            _, static.show_imgui_demo = imgui.menu_item("ImGui Demo", "", static.show_imgui_demo)
            imgui.end_menu()
        imgui.end_menu_bar()

    #-------------------------------------------------------------------------
    show_all_demos()
    imgui.end()


def main():
    immapp.run(show_demo_window, with_implot=True, with_markdown=True)


if __name__ == "__main__":
    main()
