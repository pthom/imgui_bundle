#include "immapp/visual_prog/functions_composition.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include "hello_imgui/hello_imgui.h"

#include <fplus/fplus.hpp>
#include <string>


namespace VisualProg
{
    namespace ed = ax::NodeEditor;

    ///////////////////////////////////////////////////////////////////////////
    //          _FunctionNode
    ///////////////////////////////////////////////////////////////////////////

    class _FunctionNode;

    class _FunctionsCompositionGraphPimpl;

    class _FunctionNode
    {
        friend class _FunctionsCompositionGraphPimpl;

        // members
        FunctionWithGuiPtr _function;
        _FunctionNode* _nextFunctionNode = nullptr;
        AnyDataWithGuiPtr _inputDataWithGui;
        AnyDataWithGuiPtr _outputDataWithGui;

        ed::NodeId _nodeId;
        ed::PinId _pinInput;
        ed::PinId _pinOutput;
        ed::LinkId _linkId;

    public:

        explicit _FunctionNode(FunctionWithGuiPtr function)
        {
            auto& self = *this;
            self._function = function;
            self._inputDataWithGui = function->InputGui;
            self._outputDataWithGui = function->OutputGui;

            static int counter = 0;
            self._nodeId = ed::NodeId(counter++);
            self._pinInput = ed::PinId(counter++);
            self._pinOutput = ed::PinId(counter++);
            self._linkId = ed::LinkId(counter++);
        }

        void DrawNode(int idx)
        {
            auto& self = *this;
            assert(self._function);

            ed::BeginNode(self._nodeId);
            auto position = ed::GetNodePosition(self._nodeId);
            if ((position.x == 0.f) && (position.y == 0.f))
            {
                float width_between_nodes = 200;
                position = ImVec2(idx * width_between_nodes + 1, 0);
                ed::SetNodePosition(self._nodeId, position);
            }

            ImGui::Text("%s", self._function->Name().c_str());

            ImGui::PushID(self._function.get());
            bool params_changed = self._function->GuiParams();
            if (params_changed)
            {
                if (self._inputDataWithGui->Get().has_value() && self._function)
                {
                    auto r = self._function->f(self._inputDataWithGui->Get());
                    self._outputDataWithGui->Set(r);
                    if (self._nextFunctionNode)
                        self._nextFunctionNode->SetInput(r);
                }
            }
            ImGui::PopID();

            bool draw_input = (idx != 0);
            if (draw_input)
            {
                ed::BeginPin(self._pinInput, ed::PinKind::Input);
                ImGui::Text(ICON_FA_CIRCLE);
                ed::EndPin();
            }

            bool draw_input_set_data = (idx == 0);
            if (draw_input_set_data)
            {
                auto new_value = self._inputDataWithGui->GuiSetInput();
                if (new_value.has_value())
                    self.SetInput(new_value);
            }

            // draw output
            {
                if (! self._outputDataWithGui->Get().has_value())
                    ImGui::Text("None");
                else
                {
                    ImGui::PushID(&self._outputDataWithGui);
                    ImGui::BeginGroup();
                    self._outputDataWithGui->GuiData(self._function->Name());
                    ImGui::EndGroup();
                    ImGui::PopID();
                }
                ImGui::SameLine();
                ed::BeginPin(self._pinOutput, ed::PinKind::Output);
                ImGui::Text(ICON_FA_CIRCLE);
                ed::EndPin();
            }

            ed::EndNode();
        }

        void DrawLink()
        {
            auto& self = *this;
            if (!self._nextFunctionNode)
                return;
            ed::Link(self._linkId, self._pinOutput, self._nextFunctionNode->_pinInput);
        }

        void SetInput(const std::any& input_data)
        {
            auto& self = *this;
            self._inputDataWithGui->Set(input_data);
            if (self._function)
            {
                auto r = self._function->f(input_data);
                self._outputDataWithGui->Set(r);

                if (self._nextFunctionNode)
                    self._nextFunctionNode->SetInput(r);
            }
        }
    };


    ///////////////////////////////////////////////////////////////////////////
    //          _InputWithGui
    ///////////////////////////////////////////////////////////////////////////


    struct _InputWithGui: public FunctionWithGui
    {
        std::any f(const std::any& x) override { return x; }
        bool GuiParams() override { return false; }
        std::string Name() override { return "Input"; }
    };




    ///////////////////////////////////////////////////////////////////////////
    //          _FunctionsCompositionGraphPimpl
    ///////////////////////////////////////////////////////////////////////////

    class _FunctionsCompositionGraphPimpl
    {
        std::vector<_FunctionNode> _functionNodes;

    public:
        explicit _FunctionsCompositionGraphPimpl(const std::vector<FunctionWithGuiPtr>& functions)
        {
            assert(functions.size() > 0);
            const auto& f0 = functions[0];

            auto& self = *this;

            auto input_fake_function = std::make_shared<_InputWithGui>();
            input_fake_function->InputGui = f0->InputGui;
            input_fake_function->OutputGui = f0->InputGui;
            auto input_node = _FunctionNode(input_fake_function);
            self._functionNodes.push_back(input_node);

            for(const auto& f: functions)
                self._functionNodes.push_back(_FunctionNode(f));

            for (size_t i = 0; i < self._functionNodes.size() - 1; ++i)
            {
                auto& f0 = self._functionNodes[i];
                auto& f1 = self._functionNodes[i + 1];
                f0._nextFunctionNode = &f1;
            }
        }

        void SetInput(const std::any& input)
        {
            auto& self = *this;
            self._functionNodes[0].SetInput(input);
        }

        void Draw()
        {
            auto& self = *this;
            ImGui::PushID(&self);

            ed::Begin("FunctionsCompositionGraph");
            // draw function nodes
            for(size_t i = 0; i < self._functionNodes.size(); ++i)
                self._functionNodes[i].DrawNode(i);
            // Note: those loops shall not be merged
            for(size_t i = 0; i < self._functionNodes.size(); ++i)
                self._functionNodes[i].DrawLink();
            ed::End();

            ImGui::PopID();
        }
    };


    ///////////////////////////////////////////////////////////////////////////
    //          FunctionsCompositionGraph
    ///////////////////////////////////////////////////////////////////////////

    FunctionsCompositionGraph::~FunctionsCompositionGraph() = default;

    FunctionsCompositionGraph::FunctionsCompositionGraph(const std::vector<FunctionWithGuiPtr>& functions)
    {
        _impl = std::make_unique<_FunctionsCompositionGraphPimpl>(functions);
    }

    void FunctionsCompositionGraph::SetInput(const std::any& input)
    {
        using T = AnyDataWithGuiPtr;
        _impl->SetInput(input);
    }

    void FunctionsCompositionGraph::Draw()
    {
        _impl->Draw();
    }

} // namespace VisualProg