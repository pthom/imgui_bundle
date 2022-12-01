#include "imgui_internal.h"
#include "ImGuizmoStl.h"


namespace IMGUIZMO_NAMESPACE
{
    Matrix16& my_16() // py::return_value_policy::reference
    {
        static Matrix16 r;
        return r;
    }
    Matrix6 my_6() // py::return_value_policy::reference
    {
        static Matrix6 r;
        return r;
    }
    Matrix3& my_3() // py::return_value_policy::reference
    {
        static Matrix3 r;
        return r;
    }

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

    IMGUI_API void DrawCubes(const Matrix16& view, const Matrix16& projection, const std::vector<Matrix16> & matrices)
    {
        std::vector<float> matrices_continuous_guts;
        matrices_continuous_guts.reserve(16 * matrices.size());
        for (auto m: matrices)
            for(size_t i = 0; i < 16; ++i)
                matrices_continuous_guts.push_back(m.values[i]);

        DrawCubes(view.values, projection.values, matrices_continuous_guts.data(), (int)matrices.size());
    }

    IMGUI_API void DrawGrid(const Matrix16& view, const Matrix16& projection, const Matrix16& matrix, const float gridSize)
    {
        DrawGrid(view.values, projection.values, matrix.values, gridSize);
    }

    IMGUI_API bool Manipulate(
        const Matrix16& view,
        const Matrix16& projection,
        OPERATION operation,
        MODE mode,
        Matrix16& matrix,
        std::optional<Matrix16> deltaMatrix,
        std::optional<Matrix3> snap,
        std::optional<Matrix6> localBounds,
        std::optional<Matrix3> boundsSnap
    )
    {
        bool r = Manipulate(
            view.values,
            projection.values,
            operation,
            mode,
            matrix.values,
            deltaMatrix ? deltaMatrix->values : NULL,
            snap ? snap->values : NULL,
            localBounds ? localBounds->values : NULL,
            boundsSnap ? boundsSnap-> values : NULL
            );
        return r;
    }

    IMGUI_API void ViewManipulate(Matrix16& view, float length, ImVec2 position, ImVec2 size, ImU32 backgroundColor)
    {
        ViewManipulate(view.values, length, position, size, backgroundColor);
    }

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
        ImU32 backgroundColor)
    {
        ViewManipulate(view.values, projection.values, operation, mode, matrix.values, length, position, size, backgroundColor);
    }


}
