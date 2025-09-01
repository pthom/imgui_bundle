// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#pragma once

#include "imgui.h"
#include "ImGuizmo/ImGuizmo.h"

#include <optional>
#include <vector>
#include <array>
#include <tuple>


#ifndef IMGUIZMO_NAMESPACE
#define IMGUIZMO_NAMESPACE ImGuizmo
#endif


namespace IMGUIZMO_NAMESPACE
{
    struct Matrix16
    {
        float values[16]{};
        Matrix16() { for (float & value : values) value = 0.f; }
        explicit Matrix16(const std::array<float, 16>& v) { for (int i = 0; i < 16; ++i) values[i] = v[i]; }
    };
    struct Matrix6
    {
        float values[6]{};
        Matrix6() { for (float & value : values) value = 0.f; }
        explicit Matrix6(const std::array<float, 6>& v) { for (int i = 0; i < 6; ++i) values[i] = v[i]; }
    };
    struct Matrix3
    {
        float values[3]{};
        Matrix3() { for (float & value : values) value = 0.f; }
        explicit Matrix3(const std::array<float, 3>& v) { for (int i = 0; i < 3; ++i) values[i] = v[i]; }
    };

    struct MatrixComponents
    {
        Matrix3 Translation;
        Matrix3 Rotation;
        Matrix3 Scale;
    };

    // helper functions for manualy editing translation/rotation/scale with an input float
    // translation, rotation and scale float points to 3 floats each
    // Angles are in degrees (more suitable for human editing)
    // example:
    // float matrixTranslation[3], matrixRotation[3], matrixScale[3];
    // ImGuizmo::DecomposeMatrixToComponents(gizmoMatrix.m16, matrixTranslation, matrixRotation, matrixScale);
    // ImGui::InputFloat3("Tr", matrixTranslation, 3);
    // ImGui::InputFloat3("Rt", matrixRotation, 3);
    // ImGui::InputFloat3("Sc", matrixScale, 3);
    // ImGuizmo::RecomposeMatrixFromComponents(matrixTranslation, matrixRotation, matrixScale, gizmoMatrix.m16);
    //
    // These functions have some numerical stability issues for now. Use with caution.
    IMGUI_API MatrixComponents DecomposeMatrixToComponents(const Matrix16 &matrix);
    IMGUI_API Matrix16 RecomposeMatrixFromComponents(const MatrixComponents& matrixComponents);

    // Render a cube with face color corresponding to face normal. Usefull for debug/tests
    IMGUI_API void DrawCubes(const Matrix16& view, const Matrix16& projection, const std::vector<Matrix16> & matrices);
    IMGUI_API void DrawGrid(const Matrix16& view, const Matrix16& projection, const Matrix16& matrix, const float gridSize);

    // Manipulate: main API  of ImGuizmo
    // Returns true if the objectMatrix has been modified
    //
    // Mandatory input parameters:
    //   - view: camera view matrix (array of 16 floats)
    //   - projection: camera projection matrix (array of 16 floats)
    //   - operation: operation to perform (translate, rotate, scale)
    //   - mode: in which space the operation is applied (local or world)
    // Input / Output parameter:
    //   - object_matrix: matrix of the object to manipulate (array of 16 floats)
    //     (will be modified when using the gizmo)
    //
    // Optional output parameter:
    //   - delta_matrix: matrix that contains the transformation delta (array of 16 floats)
    //     (useful to retrieve the modification between two frames)
    //     pass a newly created Matrix16, and it will be filled if not None.
    //
    // Optional input parameters:
    //   - snap: if not None, contains the snap value (array of 3 floats)
    //     (for example, if using TRANSLATE and snap={1,1,1}, the object will be snapped to the next integer position)
    //   - local_bounds: if not None, contains the local bounds of the object (array of 6 floats)
    //   - bounds_snap: if not None, contains the snap value for the bounds (array of 3 floats)
    IMGUI_API  bool Manipulate(
        const Matrix16& view,
        const Matrix16& projection,
        OPERATION operation,
        MODE mode,
        Matrix16& object_matrix, // This matrix may be modified!
        Matrix16* delta_matrix = nullptr,
        std::optional<Matrix3> snap = std::nullopt,
        std::optional<Matrix6> local_bounds = std::nullopt,
        std::optional<Matrix3> bounds_snap = std::nullopt
    );

    //
    // Please note that this cubeview is patented by Autodesk : https://patents.google.com/patent/US7782319B2/en
    // It seems to be a defensive patent in the US. I don't think it will bring troubles using it as
    // other software are using the same mechanics. But just in case, you are now warned!
    //
    // ViewManipulate may change the view parameter
    IMGUI_API void ViewManipulate(
        Matrix16& view, // This matrix may be modified!
        float length,
        ImVec2 position,
        ImVec2 size,
        ImU32 backgroundColor);

    // use this version if you did not call Manipulate before, and you are just using ViewManipulate.
    // ViewManipulate may change the view parameter!
    IMGUI_API void ViewManipulate(
        Matrix16& view,
        const Matrix16& projection,
        OPERATION operation,
        MODE mode,
        Matrix16& matrix, // !!!
        float length,
        ImVec2 position,
        ImVec2 size,
        ImU32 backgroundColor);
}
