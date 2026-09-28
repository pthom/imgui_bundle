"""ImGuizmo: a 3D gizmo on a cube

Move, rotate and scale cubes with a gizmo, as in a 3D editor. Pick the operation and the mode (local or world) in the
editor panel, drag the gizmo's handles, and turn the view with the cube at the top right corner. The gizmo is
[ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo); the camera matrices are a few lines of plain Python.

Note: there was a breaking change on ImGuizmo Python API in Nov 2024:
Added classes Matrix3/6/16, modifiable by manipulate and view_manipulate
See [changes in demo_gizmo.py](https://github.com/pthom/imgui_bundle/commit/a455607381eeaa65e05cfa7eac39f68e516b1ec4)
to see how to adapt to the new API

Basically:
- use `gizmo.Matrix3` / `Matrix6` / `Matrix16` instead of `np.array`
- `gizmo.manipulate` and `view_manipulate` will modify the matrices they receive
- if using glm, convert its matrices to Matrix16 (16 floats, column by column: `mat[0].to_list() + ...`)
"""
# See equivalent C++ program: demos_cpp/demos_imguizmo/demo_guizmo_pure.cpp

from typing import Callable, List, Tuple
import math

from imgui_bundle import imgui, imguizmo, hello_imgui, ImVec2, immapp

GuiFunction = Callable[[], None]


gizmo = imguizmo.im_guizmo

Matrix3 = gizmo.Matrix3
Matrix6 = gizmo.Matrix6
Matrix16 = gizmo.Matrix16

useWindow = True
gizmoCount = 1
camDistance = 8.0
mCurrentGizmoOperation = gizmo.OPERATION.translate

# fmt: off
gObjectMatrix: List[Matrix16] = [
    Matrix16([
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0]
    ),
    Matrix16([
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        2.0, 0.0, 0.0, 1.0
    ]),
    Matrix16([
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        2.0, 0.0, 2.0, 1.0
    ]),
    Matrix16([
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 2.0, 1.0
    ]),
]
# fmt: on

identityMatrix = Matrix16(
    [1.0, 0.0, 0.0, 0.0,
     0.0, 1.0, 0.0, 0.0,
     0.0, 0.0, 1.0, 0.0,
     0.0, 0.0, 0.0, 1.0])

"""
Of the helpers of the C++ example, only these three are ported (below): Perspective, LookAt, OrthoGraphic
    void Frustum(float left, float right, float bottom, float top, float znear, float zfar, Matrix16& m16)
    void Perspective(float fovyInDegrees, float aspectRatio, float znear, float zfar, Matrix16& m16)
    void Cross(const Matrix3& a, const Matrix3& b, Matrix3& r)
    float Dot(const Matrix3& a, const Matrix3& b)
    void Normalize(const Matrix3& a, Matrix3& r)
    void LookAt(const Matrix3& eye, const Matrix3& at, const Matrix3& up, Matrix16& m16)
    void OrthoGraphic(const float l, float r, float b, const float t, float zn, const float zf, Matrix16& m16)
    inline void rotationY(const float angle, Matrix16& m16)
"""


# This function does not exist in the C++ example, but we need to add it to support
# editing Matrix3 (aka numpy array)
def input_matrix3(label: str, matrix3: Matrix3) -> Tuple[bool, Matrix3]:
    mat_values = matrix3.values.tolist()
    changed, new_values = imgui.input_float3(label, mat_values)
    if changed:
        matrix3 = Matrix3(new_values)
    return changed, matrix3


# This function does not exist in the C++ example, but we need to add it to support
# editing Matrix3 (aka numpy array)
def input_only_first_value_matrix3(
    label: str, matrix3: Matrix3
) -> Tuple[bool, Matrix3]:
    value = float(matrix3.values[0])
    changed, new_value = imgui.input_float(label, value)
    if changed:
        matrix3.values[0] = new_value
    return changed, matrix3


@immapp.static(statics=None)
def EditTransform(
    cameraView: Matrix16,  # may be modified
    cameraProjection: Matrix16,
    objectMatrix: Matrix16,  # may be modified
    editTransformDecomposition: bool,
) -> None:
    statics = EditTransform.statics
    global mCurrentGizmoOperation

    statics = EditTransform
    if not hasattr(statics, "initialized"):
        statics.mCurrentGizmoMode = gizmo.MODE.local
        statics.useSnap = False
        statics.snap = Matrix3([1.0, 1.0, 1.0])
        statics.bounds = Matrix6([-0.5, -0.5, -0.5, 0.5, 0.5, 0.5])
        statics.boundsSnap = Matrix3([0.1, 0.1, 0.1])
        statics.boundSizing = False
        statics.boundSizingSnap = False
        statics.gizmoWindowFlags = 0
        statics.initialized = True

    if editTransformDecomposition:
        if imgui.is_key_pressed(imgui.Key.t):
            mCurrentGizmoOperation = gizmo.OPERATION.translate
        if imgui.is_key_pressed(imgui.Key.e):
            mCurrentGizmoOperation = gizmo.OPERATION.rotate
        if imgui.is_key_pressed(imgui.Key.s):
            mCurrentGizmoOperation = gizmo.OPERATION.scale
        if imgui.radio_button(
            "Translate", mCurrentGizmoOperation == gizmo.OPERATION.translate
        ):
            mCurrentGizmoOperation = gizmo.OPERATION.translate
        imgui.same_line()
        if imgui.radio_button(
            "Rotate", mCurrentGizmoOperation == gizmo.OPERATION.rotate
        ):
            mCurrentGizmoOperation = gizmo.OPERATION.rotate
        imgui.same_line()
        if imgui.radio_button("Scale", mCurrentGizmoOperation == gizmo.OPERATION.scale):
            mCurrentGizmoOperation = gizmo.OPERATION.scale
        if imgui.radio_button(
            "Universal", mCurrentGizmoOperation == gizmo.OPERATION.universal
        ):
            mCurrentGizmoOperation = gizmo.OPERATION.universal

        matrixComponents = gizmo.decompose_matrix_to_components(objectMatrix)
        edited = False
        edit_one, matrixComponents.translation = input_matrix3(
            "Tr", matrixComponents.translation
        )
        edited |= edit_one
        edit_one, matrixComponents.rotation = input_matrix3(
            "Rt", matrixComponents.rotation
        )
        edited |= edit_one
        edit_one, matrixComponents.scale = input_matrix3("Sc", matrixComponents.scale)
        edited |= edit_one

        if edited:
            recomposed = gizmo.recompose_matrix_from_components(matrixComponents).values
            for i in range(16):
                objectMatrix.values[i] = recomposed[i]

        if mCurrentGizmoOperation != gizmo.OPERATION.scale:
            if imgui.radio_button(
                "Local", statics.mCurrentGizmoMode == gizmo.MODE.local
            ):
                statics.mCurrentGizmoMode = gizmo.MODE.local
            imgui.same_line()
            if imgui.radio_button(
                "World", statics.mCurrentGizmoMode == gizmo.MODE.world
            ):
                statics.mCurrentGizmoMode = gizmo.MODE.world

        if imgui.is_key_pressed(imgui.Key.s):
            statics.useSnap = not statics.useSnap
        _, statics.useSnap = imgui.checkbox("##UseSnap", statics.useSnap)
        imgui.same_line()

        if mCurrentGizmoOperation == gizmo.OPERATION.translate:
            _, statics.snap = input_matrix3("Snap", statics.snap)
        elif mCurrentGizmoOperation == gizmo.OPERATION.rotate:
            _, statics.snap = input_only_first_value_matrix3("Angle Snap", statics.snap)
        elif mCurrentGizmoOperation == gizmo.OPERATION.scale:
            _, statics.snap = input_only_first_value_matrix3("Scale Snap", statics.snap)

        _, statics.boundSizing = imgui.checkbox("Bound Sizing", statics.boundSizing)
        if statics.boundSizing:
            imgui.push_id(3)
            _, statics.boundSizingSnap = imgui.checkbox(
                "##BoundSizing", statics.boundSizingSnap
            )
            imgui.same_line()
            _, statics.boundsSnap = input_matrix3("Snap", statics.boundsSnap)
            imgui.pop_id()

    io = imgui.get_io()
    viewManipulateRight = io.display_size.x
    viewManipulateTop = 0.0

    if useWindow:
        imgui.set_next_window_size(ImVec2(800, 400), imgui.Cond_.appearing)
        imgui.set_next_window_pos(ImVec2(400, 20), imgui.Cond_.appearing)
        imgui.push_style_color(
            imgui.Col_.window_bg, imgui.ImColor(0.35, 0.3, 0.3).value
        )
        imgui.begin("Gizmo", None, statics.gizmoWindowFlags)
        gizmo.set_drawlist()
        windowWidth = imgui.get_window_width()
        windowHeight = imgui.get_window_height()
        gizmo.set_rect(
            imgui.get_window_pos().x,
            imgui.get_window_pos().y,
            windowWidth,
            windowHeight,
        )
        viewManipulateRight = imgui.get_window_pos().x + windowWidth
        viewManipulateTop = imgui.get_window_pos().y
        window = imgui.internal.get_current_window()
        if imgui.is_window_hovered() and imgui.is_mouse_hovering_rect(
            window.inner_rect.min, window.inner_rect.max
        ):
            statics.gizmoWindowFlags = imgui.WindowFlags_.no_move
        else:
            statics.gizmoWindowFlags = 0
    else:
        gizmo.set_rect(0, 0, io.display_size.x, io.display_size.y)

    gizmo.draw_grid(cameraView, cameraProjection, identityMatrix, 100.0)

    gizmo.draw_cubes(cameraView, cameraProjection, gObjectMatrix[:gizmoCount])

    gizmo.manipulate(
        cameraView,
        cameraProjection,
        mCurrentGizmoOperation,
        statics.mCurrentGizmoMode,
        objectMatrix,
        None,
        statics.snap if statics.useSnap else None,
        statics.bounds if statics.boundSizing else None,
        statics.boundsSnap if statics.boundSizingSnap else None,
    )

    gizmo.view_manipulate(
        cameraView,
        camDistance,
        ImVec2(viewManipulateRight - 128, viewManipulateTop),
        ImVec2(128, 128),
        0x10101010,
    )

    if useWindow:
        imgui.end()
        imgui.pop_style_color()


# The camera matrices, as OpenGL and ImGuizmo want them: 16 floats, column by column (what glm would give)
def perspective(fovy_degrees: float, aspect: float, znear: float, zfar: float) -> Matrix16:
    f = 1.0 / math.tan(math.radians(fovy_degrees) / 2.0)
    return Matrix16([f / aspect, 0.0, 0.0, 0.0,
                     0.0, f, 0.0, 0.0,
                     0.0, 0.0, (zfar + znear) / (znear - zfar), -1.0,
                     0.0, 0.0, 2.0 * zfar * znear / (znear - zfar), 0.0])


def orthographic(left: float, right: float, bottom: float, top: float, znear: float, zfar: float) -> Matrix16:
    return Matrix16([2.0 / (right - left), 0.0, 0.0, 0.0,
                     0.0, 2.0 / (top - bottom), 0.0, 0.0,
                     0.0, 0.0, -2.0 / (zfar - znear), 0.0,
                     -(right + left) / (right - left), -(top + bottom) / (top - bottom),
                     -(zfar + znear) / (zfar - znear), 1.0])


def look_at(eye: Tuple[float, float, float], at: Tuple[float, float, float],
            up: Tuple[float, float, float]) -> Matrix16:
    def normalized(v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
        return (v[0] / n, v[1] / n, v[2] / n)

    def cross(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> Tuple[float, float, float]:
        return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

    def dot(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    f = normalized((at[0] - eye[0], at[1] - eye[1], at[2] - eye[2]))
    s = normalized(cross(f, up))
    u = cross(s, f)
    return Matrix16([s[0], u[0], -f[0], 0.0,
                     s[1], u[1], -f[1], 0.0,
                     s[2], u[2], -f[2], 0.0,
                     -dot(s, eye), -dot(u, eye), dot(f, eye), 1.0])


# This returns a closure function that will later be invoked to run the app
def make_closure_demo_guizmo() -> GuiFunction:
    lastUsing = 0
    cameraView = Matrix16(
        [1.0, 0.0, 0.0, 0.0,
         0.0, 1.0, 0.0, 0.0,
         0.0, 0.0, 1.0, 0.0,
         0.0, 0.0, 0.0, 1.0]
    )

    cameraProjection = Matrix16()  # Filled with zeros by default

    # Camera projection
    isPerspective = True
    fov = 27.0
    viewWidth = 10.0  # for orthographic
    camYAngle = 165.0 / 180.0 * 3.14159
    camXAngle = 32.0 / 180.0 * 3.14159

    firstFrame = True

    def gui():
        global useWindow, camDistance, gizmoCount, mCurrentGizmoOperation
        nonlocal lastUsing, cameraView, cameraProjection, isPerspective, fov, viewWidth, camYAngle, camXAngle, firstFrame

        io = imgui.get_io()
        if isPerspective:
            cameraProjection = perspective(fov, io.display_size.x / io.display_size.y, 0.1, 100.0)
        else:
            viewHeight = viewWidth * io.display_size.y / io.display_size.x
            cameraProjection = orthographic(-viewWidth, viewWidth, -viewHeight, viewHeight, 1000.0, -1000.0)

        gizmo.set_orthographic(not isPerspective)
        gizmo.begin_frame()

        imgui.set_next_window_pos(ImVec2(1024, 100), imgui.Cond_.appearing)
        imgui.set_next_window_size(ImVec2(256, 256), imgui.Cond_.appearing)

        # create a window and insert the inspector
        imgui.set_next_window_pos(ImVec2(10, 10), imgui.Cond_.appearing)
        imgui.set_next_window_size(ImVec2(320, 340), imgui.Cond_.appearing)
        imgui.begin("Editor")
        if imgui.radio_button("Full view", not useWindow):
            useWindow = False
        imgui.same_line()
        if imgui.radio_button("Window", useWindow):
            useWindow = True

        imgui.text("Camera")
        viewDirty = False
        if imgui.radio_button("Perspective", isPerspective):
            isPerspective = True
        imgui.same_line()
        if imgui.radio_button("Orthographic", not isPerspective):
            isPerspective = False
        if isPerspective:
            _, fov = imgui.slider_float("Fov", fov, 20.0, 110.0)
        else:
            _, viewWidth = imgui.slider_float("Ortho width", viewWidth, 1, 20)

        changed, camDistance = imgui.slider_float("Distance", camDistance, 1.0, 10.0)
        if changed:
            viewDirty = True
        _, gizmoCount = imgui.slider_int("Gizmo count", gizmoCount, 1, 4)

        if viewDirty or firstFrame:
            eye = (
                math.cos(camYAngle) * math.cos(camXAngle) * camDistance,
                math.sin(camXAngle) * camDistance,
                math.sin(camYAngle) * math.cos(camXAngle) * camDistance,
            )
            cameraView = look_at(eye, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
            firstFrame = False

        imgui.text(
            f"X: {io.mouse_pos.x} Y: {io.mouse_pos.y}",
        )
        if gizmo.is_using():
            imgui.text("Using gizmo")
        else:
            imgui.text("Over gizmo" if gizmo.is_over() else "")
            imgui.same_line()
            imgui.text(
                "Over translate gizmo"
                if gizmo.is_over(gizmo.OPERATION.translate)
                else ""
            )
            imgui.same_line()
            imgui.text(
                "Over rotate gizmo" if gizmo.is_over(gizmo.OPERATION.rotate) else ""
            )
            imgui.same_line()
            imgui.text(
                "Over scale gizmo" if gizmo.is_over(gizmo.OPERATION.scale) else ""
            )

        imgui.separator()

        for matId in range(gizmoCount):
            gizmo.push_id(matId)
            EditTransform(cameraView, cameraProjection, gObjectMatrix[matId], lastUsing == matId)
            gizmo.pop_id()

        imgui.end()

    return gui


def main():
    gui = make_closure_demo_guizmo()

    runner_params = immapp.RunnerParams()
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )
    runner_params.imgui_window_params.enable_viewports = True
    runner_params.docking_params.layout_condition = (
        hello_imgui.DockingLayoutCondition.application_start
    )
    runner_params.callbacks.show_gui = gui
    runner_params.app_window_params.window_geometry.size = (1200, 800)

    # Docking Splits
    runner_params.docking_params.docking_splits = [
        hello_imgui.DockingSplit(
            initial_dock_="MainDockSpace",
            new_dock_="EditorDock",
            direction_=imgui.Dir.left,
            ratio_=0.25,
        )
    ]

    runner_params.docking_params.dockable_windows = [
        hello_imgui.DockableWindow(label_="Editor", dock_space_name_="EditorDock"),
        hello_imgui.DockableWindow(label_="Gizmo", dock_space_name_="MainDockSpace"),
    ]

    immapp.run(runner_params)


if __name__ == "__main__":
    main()
