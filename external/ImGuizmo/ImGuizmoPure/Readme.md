# ImGuizmoStl: STL interfaces to ImGuizmo

Goal: provide usable interfaces for python bindings, for example using vectors instead of count + naked pointers.

As an example, here is how [ImCurveEdit.h](../ImGuizmo/ImCurveEdit.h) can be adapted:

Original code:
```cpp
namespace ImCurveEdit
{
   struct Delegate
   {
       ...
      virtual size_t GetPointCount(size_t curveIndex) = 0;   // This is a vector in disguise
      virtual ImVec2* GetPoints(size_t curveIndex) = 0;
      ...
   };

   int Edit(Delegate& delegate, const ImVec2& size, unsigned int id, const ImRect* clippingRect = NULL,
            ImVector<EditPoint>* selectedPoints = NULL // This is an output only
            );
}
```


Adapter code:
```cpp
#include <tuple>
#include "ImGuizmo/ImCurveEdit.h"

namespace ImCurveEdit
{
   struct DelegatePure: public Delegate
   {
       ...
      virtual std::vector<ImVec2>& GetPointsList() = 0; // Use a vector (more adapted to python bindings)
      ...
   };

   // Using a tuple makes it possible to easily capture the output in python
   //    e.g.
   // ```python
   // ret, selected_points = im_curve_edit.edit(delegate, size, id_, clipping_rect)
   // ```
   std::tuple<int, std::vector<EditPoint>> Edit(
       DelegateCpp& delegate, const ImVec2& size, unsigned int id, const ImRect* clippingRect = NULL,
       * selectedPoints = NULL);
}
```
