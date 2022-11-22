#pragma once

#include <string_view>
#include <string>
#include <vector>
#include <memory>


namespace VisualProg
{

    // AnyDataWithGui: a data that can be presented visually
    //  Derive this class with your own types (i.e. add your types as members)
    struct AnyDataWithGui
    {
        // Override this by implementing a draw function that presents the data content
        virtual void GuiData(std::string_view function_name) = 0;
    };
    using AnyDataWithGuiPtr = std::shared_ptr<AnyDataWithGui>;


    // FunctionWithGui: any function that can be presented visually, with
    // - a displayed name
    // - a gui in order to modify the internal params
    // - a pure function f: AnyDataWithGui -> AnyDataWithGui
    //  Derive this class with your own functions
    struct FunctionWithGui
    {
        // implement your function by overriding this
        virtual AnyDataWithGuiPtr f(const AnyDataWithGuiPtr& x) = 0;

        // Displayed name of the function
        virtual std::string Name() = 0;

        // override this if you want to provide a gui for the function inner params
        // (i.e. neither input nor output params, but the function internal state)
        // It should return True if the inner params were changed.
        virtual bool GuiParams() { return false; }
    };
    using FunctionWithGuiPtr = std::shared_ptr<FunctionWithGui>;


    class _FunctionsCompositionGraphPimpl; // PImpl encapsulation


    class FunctionsCompositionGraph
    {
        std::unique_ptr<_FunctionsCompositionGraphPimpl> _impl;
    public:
        FunctionsCompositionGraph(const std::vector<FunctionWithGuiPtr>& functions);
        ~FunctionsCompositionGraph();
        void SetInput(AnyDataWithGuiPtr&& input);
        void Draw();
    };
}