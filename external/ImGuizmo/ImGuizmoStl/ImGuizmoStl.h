#pragma once

#include "ImGuizmo/ImGuizmo.h"
#include "imgui.h"

#include <optional>
#include <vector>

#ifndef IMGUIZMO_NAMESPACE
#define IMGUIZMO_NAMESPACE ImGuizmo
#endif


namespace IMGUIZMO_NAMESPACE
{
    // Matrix16 can be cast to float[16] aka float* (if you really need it)
    struct Matrix16
    {
        float values[16];

        float operator[](size_t i) const { return values[i]; }
        float& operator[](size_t i) { return values[i]; }
    };

    // Matrix3 can be cast to float[3] aka float*
    struct Matrix3
    {
        float values[3];

        float operator[](size_t i) const { return values[i]; }
        float& operator[](size_t i) { return values[i]; }
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
    IMGUI_API void DrawCubes(const Matrix16& view, const Matrix16& projection, const std::vector<const Matrix16> & matrices, int matrixCount);
    IMGUI_API void DrawGrid(const Matrix16& view, const Matrix16& projection, const Matrix16& matrix, const float gridSize);

    IMGUI_API bool Manipulate(
        const Matrix16& view,
        const Matrix16& projection,
        OPERATION operation,
        MODE mode,
        Matrix16& matrix,
        std::optional<Matrix16> deltaMatrix = std::nullopt,
        std::optional<Matrix3> snap = std::nullopt,
        std::optional<Matrix3> localBounds = std::nullopt,
        std::optional<Matrix3> boundsSnap = std::nullopt
    );

    //
    // Please note that this cubeview is patented by Autodesk : https://patents.google.com/patent/US7782319B2/en
    // It seems to be a defensive patent in the US. I don't think it will bring troubles using it as
    // other software are using the same mechanics. But just in case, you are now warned!
    //
    IMGUI_API void ViewManipulate(Matrix16& view, float length, ImVec2 position, ImVec2 size, ImU32 backgroundColor);

    // use this version if you did not call Manipulate before and you are just using ViewManipulate
    IMGUI_API void ViewManipulate(
        Matrix16& view,
        const Matrix16& projection,
        OPERATION operation,
        MODE mode,
        Matrix16& matrix,
        float length,
        ImVec2 position,
        ImVec2 size,
        ImU32 backgroundColor);


}
