// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "imgui_internal.h"
#include "ImGuizmoPure/ImGuizmoPure.h"

void truc()
{

}

namespace IMGUIZMO_NAMESPACE
{
    MatrixComponents DecomposeMatrixToComponents(const Matrix16 &matrix)
    {
        MatrixComponents r;
        DecomposeMatrixToComponents(matrix.values, r.Translation.values, r.Rotation.values, r.Scale.values);
        return r;
    }

    Matrix16 RecomposeMatrixFromComponents(const MatrixComponents& matrixComponents)
    {
        Matrix16 r;
        RecomposeMatrixFromComponents(
            matrixComponents.Translation.values, matrixComponents.Rotation.values, matrixComponents.Scale.values,
            r.values
            );
        return r;
    }

    void DrawCubes(const Matrix16& view, const Matrix16& projection, const std::vector<Matrix16> & matrices)
    {
        std::vector<float> matrices_continuous_guts;
        matrices_continuous_guts.reserve(16 * matrices.size());
        for (auto m: matrices)
            for(size_t i = 0; i < 16; ++i)
                matrices_continuous_guts.push_back(m.values[i]);

        DrawCubes(view.values, projection.values, matrices_continuous_guts.data(), (int)matrices.size());
    }

    void DrawGrid(const Matrix16& view, const Matrix16& projection, const Matrix16& matrix, const float gridSize)
    {
        DrawGrid(view.values, projection.values, matrix.values, gridSize);
    }

    bool Manipulate(
        const Matrix16& view,
        const Matrix16& projection,
        OPERATION operation,
        MODE mode,
        Matrix16& object_matrix,
        Matrix16* delta_matrix,
        std::optional<Matrix3> snap,
        std::optional<Matrix6> local_bounds,
        std::optional<Matrix3> bounds_snap
    )
    {
        bool changed = Manipulate(
            view.values,
            projection.values,
            operation,
            mode,
            object_matrix.values,
            delta_matrix ? delta_matrix->values : NULL,
            snap ? snap->values : NULL,
            local_bounds ? local_bounds->values : NULL,
            bounds_snap ? bounds_snap-> values : NULL
            );
        return changed;
    }

    void ViewManipulate(Matrix16& view, float length, ImVec2 position, ImVec2 size, ImU32 backgroundColor)
    {
        ViewManipulate(view.values, length, position, size, backgroundColor);
    }

    // use this version if you did not call Manipulate before and you are just using ViewManipulate
    void ViewManipulate(
        Matrix16& view,
        const Matrix16& projection,
        OPERATION operation,
        MODE mode,
        Matrix16& matrix,
        float length,
        ImVec2 position,
        ImVec2 size,
        ImU32 backgroundColor)
    {
        ViewManipulate(view.values, projection.values, operation, mode, matrix.values, length, position, size, backgroundColor);
    }


}
