// Nanobind type casters for ImmVision types:
//   ImageBuffer <-> numpy.ndarray (zero-copy)
//   Point       <-> tuple(int, int)
//   Point2d     <-> tuple(float, float)
//   Size        <-> tuple(int, int)
//   Matrix33d   <-> list[list[float]]  (3x3)
#pragma once

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/vector.h>
#include "immvision/immvision_types.h"

namespace nb = nanobind;

// =========================================================================
// Helpers: ImageDepth <-> numpy dtype
// =========================================================================

namespace immvision_nb_detail {

struct DtypeMapping {
    ImmVision::ImageDepth depth;
    nanobind::dlpack::dtype dtype;
};

inline const std::vector<DtypeMapping>& dtype_mappings() {
    static std::vector<DtypeMapping> mappings = {
        {ImmVision::ImageDepth::uint8,   nanobind::dtype<uint8_t>()},
        {ImmVision::ImageDepth::int8,    nanobind::dtype<int8_t>()},
        {ImmVision::ImageDepth::uint16,  nanobind::dtype<uint16_t>()},
        {ImmVision::ImageDepth::int16,   nanobind::dtype<int16_t>()},
        {ImmVision::ImageDepth::int32,   nanobind::dtype<int32_t>()},
        {ImmVision::ImageDepth::float32, nanobind::dtype<float>()},
        {ImmVision::ImageDepth::float64, nanobind::dtype<double>()},
    };
    return mappings;
}

inline nanobind::dlpack::dtype image_depth_to_dtype(ImmVision::ImageDepth d) {
    for (const auto& m : dtype_mappings())
        if (m.depth == d) return m.dtype;
    throw std::runtime_error("image_depth_to_dtype: unknown depth");
}

inline ImmVision::ImageDepth dtype_to_image_depth(const nanobind::dlpack::dtype& dt) {
    for (const auto& m : dtype_mappings())
        if (m.dtype.code == dt.code && m.dtype.bits == dt.bits) return m.depth;
    throw std::runtime_error("dtype_to_image_depth: unsupported numpy dtype");
}

} // namespace immvision_nb_detail


// =========================================================================
// Type casters
// =========================================================================

NAMESPACE_BEGIN(NB_NAMESPACE)
NAMESPACE_BEGIN(detail)


// ---- ImageBuffer <-> numpy.ndarray (zero-copy) ----
template <>
struct type_caster<ImmVision::ImageBuffer>
{
    NB_TYPE_CASTER(ImmVision::ImageBuffer, const_name("numpy.ndarray"))

    bool from_python(handle src, uint8_t flags, cleanup_list *cleanup) noexcept
    {
        if (!isinstance<ndarray<>>(src))
            return false;
        try
        {
            auto a = nanobind::cast<ndarray<>>(src);

            if (a.ndim() < 2 || a.ndim() > 3)
                return false;

            // Reject non-contiguous arrays
            // nanobind strides are in number of elements
            {
                bool contiguous = true;
                if (a.ndim() == 3) {
                    contiguous = (a.stride(2) == 1)
                              && (a.stride(1) == (int64_t)a.shape(2))
                              && (a.stride(0) == (int64_t)(a.shape(2) * a.shape(1)));
                } else {
                    contiguous = (a.stride(1) == 1)
                              && (a.stride(0) == (int64_t)a.shape(1));
                }
                if (!contiguous) {
                    PyErr_SetString(PyExc_TypeError,
                        "immvision: ImageBuffer requires a contiguous numpy array. "
                        "Use np.ascontiguousarray() to convert.");
                    return false;
                }
            }

            value.height   = (int)a.shape(0);
            value.width    = (int)a.shape(1);
            value.channels = a.ndim() == 3 ? (int)a.shape(2) : 1;
            try {
                value.depth = immvision_nb_detail::dtype_to_image_depth(a.dtype());
            } catch (const std::exception& e) {
                PyErr_Format(PyExc_TypeError,
                    "immvision: unsupported dtype (code=%d, bits=%d): %s",
                    (int)a.dtype().code, (int)a.dtype().bits, e.what());
                return false;
            }
            value.data     = (void*)a.data();
            // a.stride(0) is in elements; step is in bytes
            size_t elem_bytes = a.dtype().bits / 8;
            value.step     = (size_t)a.stride(0) * elem_bytes;

            // Keep the Python ndarray alive via _ref_keeper
            nanobind::object capsule_owner = nanobind::capsule(src.ptr(), [](void* p) noexcept {
                Py_XDECREF(reinterpret_cast<PyObject*>(p));
            });
            Py_INCREF(src.ptr());

            auto ref = std::make_shared<nanobind::object>(std::move(capsule_owner));
            value._ref_keeper = ref;

            return true;
        }
        catch (const std::exception& e)
        {
            PyErr_Format(PyExc_TypeError, "immvision ImageBuffer from_python: %s", e.what());
            return false;
        }
        catch (...)
        {
            PyErr_SetString(PyExc_TypeError, "immvision ImageBuffer from_python: unknown error");
            return false;
        }
    }

    static handle from_cpp(const ImmVision::ImageBuffer &buf, rv_policy policy, cleanup_list *cleanup) noexcept
    {
        try
        {
            if (buf.empty())
                return nanobind::none().release();

            if (policy == rv_policy::automatic)
                policy = rv_policy::copy;
            else if (policy == rv_policy::automatic_reference)
                policy = rv_policy::reference;

            size_t ndim = buf.channels == 1 ? 2 : 3;
            size_t shape[3]  = {(size_t)buf.height, (size_t)buf.width, (size_t)buf.channels};
            // nanobind ndarray strides are in number of elements, not bytes
            int64_t elem_bytes = (int64_t)ImmVision::ImageDepthSize(buf.depth);
            int64_t row_stride_elems = (int64_t)buf.step / elem_bytes;
            int64_t strides[3] = {row_stride_elems, (int64_t)buf.channels, 1};

            auto dt = immvision_nb_detail::image_depth_to_dtype(buf.depth);

            // Heap-allocate an ImageBuffer copy. This copies the _ref_keeper shared_ptr
            // (incrementing its refcount) but NOT the pixel data — zero copy.
            // The capsule will destroy this heap ImageBuffer when Python is done,
            // which decrements the refcount and frees the pixels if no other owner remains.
            auto* heap_buf = new ImmVision::ImageBuffer(buf);
            nanobind::object owner = nanobind::capsule(heap_buf,
                [](void* p) noexcept { delete static_cast<ImmVision::ImageBuffer*>(p); });

            ndarray<> a(heap_buf->data, ndim, shape, owner, strides, dt);

            return ndarray_export(a.handle(), nanobind::numpy::value,
                                  rv_policy::reference, cleanup);
        }
        catch (...)
        {
            return nanobind::none().release();
        }
    }
};


// ---- Point <-> tuple(int, int) ----
template <>
struct type_caster<ImmVision::Point>
{
    NB_TYPE_CASTER(ImmVision::Point, const_name("Tuple[int, int]"))

    bool from_python(handle src, uint8_t flags, cleanup_list *cleanup) noexcept
    {
        try
        {
            auto t = nanobind::cast<std::tuple<int, int>>(src);
            value.x = std::get<0>(t);
            value.y = std::get<1>(t);
            return true;
        }
        catch (...)
        {
            return false;
        }
    }

    static handle from_cpp(const ImmVision::Point &p, rv_policy policy, cleanup_list *cleanup) noexcept
    {
        return nanobind::make_tuple(p.x, p.y).release();
    }
};


// ---- Point2d <-> tuple(float, float) ----
template <>
struct type_caster<ImmVision::Point2d>
{
    NB_TYPE_CASTER(ImmVision::Point2d, const_name("Tuple[float, float]"))

    bool from_python(handle src, uint8_t flags, cleanup_list *cleanup) noexcept
    {
        try
        {
            auto t = nanobind::cast<std::tuple<double, double>>(src);
            value.x = std::get<0>(t);
            value.y = std::get<1>(t);
            return true;
        }
        catch (...)
        {
            return false;
        }
    }

    static handle from_cpp(const ImmVision::Point2d &p, rv_policy policy, cleanup_list *cleanup) noexcept
    {
        return nanobind::make_tuple(p.x, p.y).release();
    }
};


// ---- Size <-> tuple(int, int) ----
template <>
struct type_caster<ImmVision::Size>
{
    NB_TYPE_CASTER(ImmVision::Size, const_name("Tuple[int, int]"))

    bool from_python(handle src, uint8_t flags, cleanup_list *cleanup) noexcept
    {
        try
        {
            auto t = nanobind::cast<std::tuple<int, int>>(src);
            value.width  = std::get<0>(t);
            value.height = std::get<1>(t);
            return true;
        }
        catch (...)
        {
            return false;
        }
    }

    static handle from_cpp(const ImmVision::Size &s, rv_policy policy, cleanup_list *cleanup) noexcept
    {
        return nanobind::make_tuple(s.width, s.height).release();
    }
};


// ---- Matrix33d <-> list[list[float]] (3x3) ----
template <>
struct type_caster<ImmVision::Matrix33d>
{
    NB_TYPE_CASTER(ImmVision::Matrix33d, const_name("List[List[float]]"))

    bool from_python(handle src, uint8_t flags, cleanup_list *cleanup) noexcept
    {
        try
        {
            // Accept list[list[float]] or numpy 3x3 array
            if (isinstance<ndarray<>>(src))
            {
                auto a = nanobind::cast<ndarray<>>(src);
                if (a.ndim() != 2 || a.shape(0) != 3 || a.shape(1) != 3)
                    return false;
                // Cast to double array
                auto arr = nanobind::cast<ndarray<double, nanobind::shape<3, 3>>>(src);
                for (int r = 0; r < 3; r++)
                    for (int c = 0; c < 3; c++)
                        value.m[r][c] = arr(r, c);
                return true;
            }
            else
            {
                auto outer = nanobind::cast<std::vector<std::vector<double>>>(src);
                if (outer.size() != 3)
                    return false;
                for (int r = 0; r < 3; r++)
                {
                    if (outer[r].size() != 3)
                        return false;
                    for (int c = 0; c < 3; c++)
                        value.m[r][c] = outer[r][c];
                }
                return true;
            }
        }
        catch (...)
        {
            return false;
        }
    }

    static handle from_cpp(const ImmVision::Matrix33d &m, rv_policy policy, cleanup_list *cleanup) noexcept
    {
        try
        {
            nanobind::list outer;
            for (int r = 0; r < 3; r++)
            {
                nanobind::list row;
                for (int c = 0; c < 3; c++)
                    row.append(m.m[r][c]);
                outer.append(row);
            }
            return outer.release();
        }
        catch (...)
        {
            return nanobind::none().release();
        }
    }
};


NAMESPACE_END(detail)
NAMESPACE_END(NB_NAMESPACE)
