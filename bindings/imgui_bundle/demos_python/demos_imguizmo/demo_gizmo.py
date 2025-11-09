# Demo ImGuizmo (only the 3D gizmo)
# See equivalent python program: demos_cpp/demos_imguizmo/demo_guizmo_pure.cpp

"""
Note: there was a breaking change on ImGuizmo Python API in Nov 2024:
Added classes Matrix3/6/16, modifiable by manipulate and view_manipulate
See [changes in demo_gizmo.py](https://github.com/pthom/imgui_bundle/commit/a455607381eeaa65e05cfa7eac39f68e516b1ec4)
to see how to adapt to the new API

Basically:
- use `gizmo.Matrix3` / `Matrix6` / `Matrix16` instead of `np.array`
- `gizmo.manipulate` and `view_manipulate` will modify the matrices they receive
- if using glm, you will to need to convert to Matrix16, see `glm_mat4x4_to_float_list` in demo_gizmo.py
"""

from typing import List, Tuple
import math

from imgui_bundle import imgui, imguizmo, hello_imgui, ImVec2, immapp
from imgui_bundle.demos_python.demo_utils.api_demos import GuiFunction

try:
    import glm  # pip install PyGLM
except ModuleNotFoundError:
    print(
        "\nThis demo require PyGLM, please install it with this command:\n\n\tpip install PyGLM\n"
    )
    exit(1)


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
The following functions from the C++ example need not to be ported, we use glm instead
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


@immapp.static(statics=None)  # type: ignore
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


def glm_mat4x4_to_float_list(mat: glm.mat4x4) -> List[float]:
    return mat[0].to_list() + mat[1].to_list() + mat[2].to_list() + mat[3].to_list() # type: ignore


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
            radians = glm.radians(fov)  # The gui is in degree, we need radians for glm
            cameraProjection_glm = glm.perspective(radians, io.display_size.x / io.display_size.y, 0.1, 100.0)
            cameraProjection = Matrix16(glm_mat4x4_to_float_list(cameraProjection_glm))
        else:
            viewHeight = viewWidth * io.display_size.y / io.display_size.x
            cameraProjection_glm = glm.ortho(-viewWidth, viewWidth, -viewHeight, viewHeight, 1000.0, -1000.0)
            cameraProjection = Matrix16(glm_mat4x4_to_float_list(cameraProjection_glm))

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
            eye = glm.vec3(
                math.cos(camYAngle) * math.cos(camXAngle) * camDistance,
                math.sin(camXAngle) * camDistance,
                math.sin(camYAngle) * math.cos(camXAngle) * camDistance,
            )
            at = glm.vec3(0.0, 0.0, 0.0)
            up = glm.vec3(0.0, 1.0, 0.0)
            cameraView_glm: glm.mat4x4 = glm.lookAt(eye, at, up)
            cameraView = Matrix16(glm_mat4x4_to_float_list(cameraView_glm))
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
                if gizmo.is_over(gizmo.OPERATION.translate)  # type: ignore
                else ""
            )
            imgui.same_line()
            imgui.text(
                "Over rotate gizmo" if gizmo.is_over(gizmo.OPERATION.rotate) else ""  # type: ignore
            )
            imgui.same_line()
            imgui.text(
                "Over scale gizmo" if gizmo.is_over(gizmo.OPERATION.scale) else ""  # type: ignore
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
