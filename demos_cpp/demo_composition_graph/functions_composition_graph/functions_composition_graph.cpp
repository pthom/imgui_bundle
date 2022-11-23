#include "functions_composition_graph/functions_composition_graph.h"
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
    using _FunctionNodePtr = std::shared_ptr<_FunctionNode>;

    class _FunctionsCompositionGraphPimpl;

    class _FunctionNode
    {
        friend class _FunctionsCompositionGraphPimpl;

        // members
        FunctionWithGuiPtr _function;
        _FunctionNodePtr _nextFunctionNode;
        AnyDataWithGuiPtr _inputData;
        AnyDataWithGuiPtr _outputData;

        ed::NodeId _nodeId;
        ed::PinId _pinInput;
        ed::PinId _pinOutput;
        ed::LinkId _linkId;

    public:

        explicit _FunctionNode(FunctionWithGuiPtr function, _FunctionNodePtr nextFunctionNode = nullptr)
        {
            auto& self = *this;
            self._function = function;
            self._nextFunctionNode = nextFunctionNode;
            self._inputData = nullptr;
            self._outputData = nullptr;

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
                if (self._inputData && self._function)
                {
                    self._outputData = self._function->f(self._inputData);
                    if (self._nextFunctionNode)
                        self._nextFunctionNode->SetInput(self._outputData);
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
                auto new_value = self._inputData->GuiSetInput();
                if (new_value)
                    self.SetInput(new_value);
            }

            // draw output
            {
                if (! self._outputData)
                    ImGui::Text("None");
                else
                {
                    ImGui::PushID(self._outputData.get());
                    ImGui::BeginGroup();
                    self._outputData->GuiData(self._function->Name());
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

        void SetInput(AnyDataWithGuiPtr input_data)
        {
            auto& self = *this;
            self._inputData = input_data;
            if (self._function)
            {
                self._outputData = self._function->f(input_data);

                if (self._nextFunctionNode)
                    self._nextFunctionNode->SetInput(self._outputData);
            }
        }
    };


    ///////////////////////////////////////////////////////////////////////////
    //          _InputWithGui & _OutputWithGui
    ///////////////////////////////////////////////////////////////////////////

    struct IdentityFunctionWithGui: public FunctionWithGui
    {
        AnyDataWithGuiPtr f(const AnyDataWithGuiPtr& x) override { return x; }
        bool GuiParams() override { return false; }
    };

    struct _InputWithGui: public IdentityFunctionWithGui { std::string Name() override { return "Input"; } };
    struct _OutputWithGui: public IdentityFunctionWithGui { std::string Name() override { return "Output"; } };


    ///////////////////////////////////////////////////////////////////////////
    //          _FunctionsCompositionGraphPimpl
    ///////////////////////////////////////////////////////////////////////////

    class _FunctionsCompositionGraphPimpl
    {
        std::vector<_FunctionNodePtr> _functionNodes;

    public:
        explicit _FunctionsCompositionGraphPimpl(const std::vector<FunctionWithGuiPtr>& functions)
        {
            auto& self = *this;

            auto input_fake_function = std::make_shared<_InputWithGui>();
            auto input_node = std::make_shared<_FunctionNode>(input_fake_function);
            self._functionNodes.push_back(input_node);

            for(const auto& f: functions)
            {
                auto functionNode = std::make_shared<_FunctionNode>(f);
                self._functionNodes.push_back(functionNode);
            }

            for (const auto& f_pair:  fplus::overlapping_pairs(self._functionNodes))
                f_pair.first->_nextFunctionNode = f_pair.second;
        }

        void SetInput(AnyDataWithGuiPtr inputData)
        {
            auto& self = *this;
            self._functionNodes[0]->SetInput(inputData);
        }

        void Draw()
        {
            auto& self = *this;
            ImGui::PushID(&self);

            ed::Begin("FunctionsCompositionGraph");
            // draw function nodes
            for(size_t i = 0; i < self._functionNodes.size(); ++i)
                self._functionNodes[i]->DrawNode(i);
            // Note: those loops shall not be merged
            for(size_t i = 0; i < self._functionNodes.size(); ++i)
                self._functionNodes[i]->DrawLink();
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

    void FunctionsCompositionGraph::SetInput(AnyDataWithGuiPtr&& input)
    {
        using T = AnyDataWithGuiPtr;
        _impl->SetInput(std::forward<T>(input));
    }

    void FunctionsCompositionGraph::Draw()
    {
        _impl->Draw();
    }

} // namespace VisualProg