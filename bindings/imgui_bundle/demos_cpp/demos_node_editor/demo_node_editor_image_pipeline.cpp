// Node editor: an image pipeline
//
// An image flows through a graph of filters, and each node shows its result. Change a parameter, and the nodes
// downstream follow at once. The patterns of imgui-node-editor (https://github.com/thedmd/imgui-node-editor) for a
// real app: typed pins, links refused with a reason, a node created by dropping a link in empty space, menus, a group.
#if defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR) && defined(IMGUI_BUNDLE_WITH_IMPLOT) && defined(IMMVISION_HAS_OPENCV)
#define IMGUI_DEFINE_MATH_OPERATORS
#include "imgui-node-editor/imgui_node_editor.h"
#include "imgui_node_editor_immapp/node_editor_default_context.h"  // DisableUserInputThisFrame
#include "imgui_rich_md/rich_md.h"
#include "immapp/immapp.h"
#include "immapp/immapp_widgets.h"  // ShowResizablePlotInNodeEditor_Em
#include "immvision/immvision.h"
#include "implot/implot.h"
#include "hello_imgui/hello_imgui.h"
#include "demo_utils/api_demos.h"  // DemosAssetsFolder
#include "imgui.h"

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

#include <algorithm>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace ed = ax::NodeEditor;

namespace
{

const float IMAGE_WIDTH_EM = 12.0f;  // the width of the images in the nodes: it also gives the nodes their width
const ImVec2 HISTOGRAM_SIZE_EM(12.0f, 6.0f);  // the initial size of the histogram of a Levels node (resizable)
const float PIN_RADIUS_EM = 0.45f;  // the radius of a pin's icon
const float LINK_THICKNESS = 3.0f;  // the thickness of the links (they follow the zoom)
const std::vector<const char*> IMAGES = {"images/house.jpg", "images/tennis.jpg"};  // from the demos' assets

// The gestures, in markdown ("  \n" ends a line)
const char* HELP =
    "**Link** two pins: drag from one to the other; drop a link in empty space to add a node there  \n"
    "**Delete**: select, then <kbd>Delete</kbd>  ·  **Menus**: right-click  ·  **Pan**: right-drag  ·  "
    "**Zoom**: the wheel  ·  **See the whole graph**: <kbd>F</kbd>  ·  **Zoom in an image**: the wheel over it";

// A note of the graph: how to look at the images (ImmVision)
const char* TIPS = R"(**About the images**

* Zoom with the wheel, and pan by dragging: all the images follow
* Zoom in far enough, and the values of the pixels show
* The button at the bottom right of an image opens more options)";


// =====================================================================================================================
// 1. The types of the pins
// =====================================================================================================================
// Each pin carries a type of image. A link is accepted when the input can take the output's type: a gray image can go
// where a color image is expected (it is converted), but not the reverse.
enum class PinType { Color, Gray };

const char* TypeName(PinType type) { return type == PinType::Color ? "a color image" : "a gray image"; }

ImVec4 TypeColor(PinType type)
{
    return type == PinType::Color ? ImVec4(0.95f, 0.6f, 0.25f, 1.0f) : ImVec4(0.7f, 0.78f, 0.85f, 1.0f);
}

bool Accepts(PinType inputType, PinType outputType)
{
    return inputType == PinType::Color || outputType == PinType::Gray;
}


// =====================================================================================================================
// 2. The nodes: one class per filter
// =====================================================================================================================
// The editor draws the graph, but the app owns it: its nodes, pins and links, each with an id that stays the same from
// one frame to the next (here, a counter gives new ones).
uintptr_t NewId()
{
    static uintptr_t lastId = 0;
    return ++lastId;
}

struct InputSpec
{
    const char* name;
    PinType type;
};

struct Node;

struct Pin
{
    std::string name;
    PinType type;
    ed::PinKind kind;  // an input (on the left of its node) or an output (on the right)
    Node* node;
    ed::PinId id = ed::PinId(NewId());
};

// A filter: its pins, its parameters, and what it computes. Each subclass gives its TITLE, DOC, INPUTS and OUTPUT.
struct Node
{
    std::string title;
    std::string doc;  // what it does, under its title (markdown, with math between $ signs)
    ed::NodeId id = ed::NodeId(NewId());
    std::vector<std::unique_ptr<Pin>> inputs;  // the pins are owned by pointers: the links point to them
    std::unique_ptr<Pin> output;
    // The state of the evaluation (see section 3)
    cv::Mat image;  // the last result (empty: none)
    std::string error;  // why there is no result
    int version = 0;  // increases with each new result
    std::vector<int> inputsVersions;  // the versions of the inputs that gave the last result
    bool paramsChanged = true;  // set by the widgets of the parameters
    int computedFrame = -1;  // the frame of the last result (its output links then show the data flowing)
    ImmVision::ImageParams imageParams;  // how the node shows its image

    Node(const char* title_, const char* doc_, const std::vector<InputSpec>& inputSpecs, PinType outputType)
        : title(title_), doc(doc_)
    {
        for (const InputSpec& spec : inputSpecs)
            inputs.push_back(std::make_unique<Pin>(Pin{spec.name, spec.type, ed::PinKind::Input, this}));
        output = std::make_unique<Pin>(Pin{"out", outputType, ed::PinKind::Output, this});
        imageParams.ImageDisplaySize = ImmVision::Size((int)HelloImGui::EmSize(IMAGE_WIDTH_EM), 0);
        // The image and its options button: zoom and pan are with the mouse
        imageParams.ShowZoomButtons = imageParams.ShowImageInfo = imageParams.ShowPixelInfo = false;
        imageParams.ZoomKey = "images";  // the images with the same zoom key zoom and pan together
        imageParams.ShowOptionsInTooltip = true;  // the options in a popup: inline, they would widen the node
    }
    virtual ~Node() = default;

    // Draws the widgets of the parameters, and returns true when one of them changed
    virtual bool DrawParams() { return false; }
    virtual cv::Mat Compute(const std::vector<cv::Mat>& inputs) = 0;
};

struct ImageFile : Node
{
    static inline const char* TITLE = "Image";
    static inline const char* DOC = "An image of the demos' assets";
    static inline const std::vector<InputSpec> INPUTS = {};
    static constexpr PinType OUTPUT = PinType::Color;
    int index = 0;
    ImageFile() : Node(TITLE, DOC, INPUTS, OUTPUT) {}

    bool DrawParams() override
    {
        ImGui::SetNextItemWidth(HelloImGui::EmSize(IMAGE_WIDTH_EM));
        // Its popup opens from inside the node
        return ImGui::Combo("##file", &index, IMAGES.data(), (int)IMAGES.size());
    }
    cv::Mat Compute(const std::vector<cv::Mat>&) override
    {
        return ImmVision::ImRead(DemosAssetsFolder() + "/" + IMAGES[index]).to_cv_mat().clone();  // in RGB order
    }
};

struct Grayscale : Node
{
    static inline const char* TITLE = "Grayscale";
    static inline const char* DOC = R"(The luminance: $0.3\,r + 0.59\,g + 0.11\,b$)";
    static inline const std::vector<InputSpec> INPUTS = {{"in", PinType::Color}};
    static constexpr PinType OUTPUT = PinType::Gray;
    Grayscale() : Node(TITLE, DOC, INPUTS, OUTPUT) {}

    cv::Mat Compute(const std::vector<cv::Mat>& inputs) override
    {
        cv::Mat r;
        cv::cvtColor(inputs[0], r, cv::COLOR_RGB2GRAY);
        return r;
    }
};

struct Blur : Node
{
    static inline const char* TITLE = "Blur";
    static inline const char* DOC =
        "A [Gaussian blur](https://en.wikipedia.org/wiki/Gaussian_blur): fewer, smoother edges downstream";
    static inline const std::vector<InputSpec> INPUTS = {{"in", PinType::Gray}};
    static constexpr PinType OUTPUT = PinType::Gray;
    float sigma = 1.5f;
    Blur() : Node(TITLE, DOC, INPUTS, OUTPUT) {}

    bool DrawParams() override
    {
        ImGui::SetNextItemWidth(HelloImGui::EmSize(IMAGE_WIDTH_EM));
        bool changed = ImGui::SliderFloat("##sigma", &sigma, 0.1f, 10.0f, "sigma = %.1f");
        ImGui::SetItemTooltip("The standard deviation of the Gaussian, in pixels: the larger, the blurrier");
        return changed;
    }
    cv::Mat Compute(const std::vector<cv::Mat>& inputs) override
    {
        cv::Mat r;
        cv::GaussianBlur(inputs[0], r, cv::Size(0, 0), sigma);
        return r;
    }
};

struct Edges : Node
{
    static inline const char* TITLE = "Edges";
    static inline const char* DOC = "The [Canny edge detector](https://en.wikipedia.org/wiki/Canny_edge_detector)";
    static inline const std::vector<InputSpec> INPUTS = {{"in", PinType::Gray}};
    static constexpr PinType OUTPUT = PinType::Gray;
    float low = 40.0f, high = 100.0f;
    Edges() : Node(TITLE, DOC, INPUTS, OUTPUT) {}

    bool DrawParams() override
    {
        ImGui::SetNextItemWidth(HelloImGui::EmSize(IMAGE_WIDTH_EM));
        bool changedLow = ImGui::SliderFloat("##low", &low, 0.0f, 300.0f, "low = %.0f");
        ImGui::SetItemTooltip("A pixel whose gradient is below this threshold is never an edge");
        ImGui::SetNextItemWidth(HelloImGui::EmSize(IMAGE_WIDTH_EM));
        bool changedHigh = ImGui::SliderFloat("##high", &high, 0.0f, 300.0f, "high = %.0f");
        ImGui::SetItemTooltip("A pixel whose gradient is above this threshold is always an edge; between the two, "
                              "only when it touches an edge");
        return changedLow || changedHigh;
    }
    cv::Mat Compute(const std::vector<cv::Mat>& inputs) override
    {
        cv::Mat r;
        cv::Canny(inputs[0], r, low, high);
        return r;
    }
};

struct Threshold : Node
{
    static inline const char* TITLE = "Threshold";
    static inline const char* DOC = "White where the image is brighter than the level, black elsewhere";
    static inline const std::vector<InputSpec> INPUTS = {{"in", PinType::Gray}};
    static constexpr PinType OUTPUT = PinType::Gray;
    int level = 128;
    Threshold() : Node(TITLE, DOC, INPUTS, OUTPUT) {}

    bool DrawParams() override
    {
        ImGui::SetNextItemWidth(HelloImGui::EmSize(IMAGE_WIDTH_EM));
        return ImGui::SliderInt("##level", &level, 0, 255, "level = %d");
    }
    cv::Mat Compute(const std::vector<cv::Mat>& inputs) override
    {
        cv::Mat r;
        cv::threshold(inputs[0], r, level, 255, cv::THRESH_BINARY);
        return r;
    }
};

struct Dilate : Node
{
    static inline const char* TITLE = "Dilate";
    static inline const char* DOC =
        "[Dilation](https://en.wikipedia.org/wiki/Dilation_(morphology)): the white areas grow";
    static inline const std::vector<InputSpec> INPUTS = {{"in", PinType::Gray}};
    static constexpr PinType OUTPUT = PinType::Gray;
    int size = 3;
    Dilate() : Node(TITLE, DOC, INPUTS, OUTPUT) {}

    bool DrawParams() override
    {
        ImGui::SetNextItemWidth(HelloImGui::EmSize(IMAGE_WIDTH_EM));
        bool changed = ImGui::SliderInt("##size", &size, 1, 9, "size = %d");
        ImGui::SetItemTooltip("The size of the disk that dilates the image, in pixels (1: no change)");
        return changed;
    }
    cv::Mat Compute(const std::vector<cv::Mat>& inputs) override
    {
        cv::Mat kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(size, size));
        cv::Mat r;
        cv::dilate(inputs[0], r, kernel);
        return r;
    }
};

struct Colorize : Node
{
    static inline const char* TITLE = "Colorize";
    static inline const char* DOC = R"(Paints the gray image: $g \cdot c$)";
    static inline const std::vector<InputSpec> INPUTS = {{"in", PinType::Gray}};
    static constexpr PinType OUTPUT = PinType::Color;
    ImVec4 color = ImVec4(0.3f, 0.85f, 1.0f, 1.0f);
    Colorize() : Node(TITLE, DOC, INPUTS, OUTPUT) {}

    bool DrawParams() override
    {
        ImGui::SetNextItemWidth(HelloImGui::EmSize(IMAGE_WIDTH_EM));
        // A color picker: its popup opens from inside the node
        return ImGui::ColorEdit4("##color", &color.x, ImGuiColorEditFlags_NoAlpha);
    }
    cv::Mat Compute(const std::vector<cv::Mat>& inputs) override
    {
        cv::Mat rgb, r;
        cv::cvtColor(inputs[0], rgb, cv::COLOR_GRAY2RGB);
        cv::multiply(rgb, cv::Scalar(color.x, color.y, color.z), r);
        return r;
    }
};

const ImVec4 CHANNEL_COLORS[3] = {ImVec4(1.0f, 0.3f, 0.3f, 1.0f), ImVec4(0.3f, 1.0f, 0.3f, 1.0f), ImVec4(0.35f, 0.5f, 1.0f, 1.0f)};

struct Levels : Node
{
    static inline const char* TITLE = "Levels";
    static inline const char* DOC = "Drag the black and white points on the histogram";
    static inline const std::vector<InputSpec> INPUTS = {{"in", PinType::Color}};
    static constexpr PinType OUTPUT = PinType::Color;
    double black = 20.0, white = 235.0;
    float gamma = 1.0f;
    ImVec2 histogramSizeEm = HISTOGRAM_SIZE_EM;
    std::vector<std::vector<double>> histograms;  // of the input image, one per channel
    Levels() : Node(TITLE, DOC, INPUTS, OUTPUT) {}

    bool DrawParams() override
    {
        bool changed = false;
        auto plotHistogram = [&]() {
            ImPlot::SetupAxes("", "", ImPlotAxisFlags_NoTickLabels, ImPlotAxisFlags_NoDecorations);
            // The square root of the counts: a few very frequent values (a white sky) would flatten the others
            std::vector<std::vector<double>> heights;
            double top = 1.0;
            for (const auto& histogram : histograms)
            {
                std::vector<double> h(256);
                for (int i = 0; i < 256; i++)
                    h[i] = std::sqrt(histogram[i]);
                top = std::max(top, *std::max_element(h.begin(), h.end()));
                heights.push_back(h);
            }
            ImPlot::SetupAxesLimits(0, 255, 0, top * 1.05, ImPlotCond_Always);
            std::vector<double> x(256);
            for (int i = 0; i < 256; i++)
                x[i] = (double)i;
            const char* names[3] = {"R", "G", "B"};
            for (size_t c = 0; c < heights.size(); c++)
            {
                ImPlotSpec fill;
                fill.FillColor = CHANNEL_COLORS[c];
                fill.FillAlpha = 0.3f;
                ImPlot::PlotShaded(names[c], x.data(), heights[c].data(), 256, 0, fill);
                ImPlotSpec line;
                line.LineColor = CHANNEL_COLORS[c];
                ImPlot::PlotLine(names[c], x.data(), heights[c].data(), 256, line);
            }
            // Two vertical lines that the user drags. The plot keeps the mouse: dragging does not move the node.
            bool changedBlack = ImPlot::DragLineX(0, &black, ImVec4(0.2f, 0.2f, 0.2f, 1.0f), 3);
            bool changedWhite = ImPlot::DragLineX(1, &white, ImVec4(1.0f, 1.0f, 1.0f, 1.0f), 3);
            black = std::clamp(black, 0.0, white - 1);
            white = std::clamp(white, black + 1, 255.0);
            changed = changed || changedBlack || changedWhite;
        };
        // A plot inside a node, with a handle at its bottom right corner to resize it
        ImPlotFlags flags = ImPlotFlags_NoLegend | ImPlotFlags_NoMenus | ImPlotFlags_NoBoxSelect;
        histogramSizeEm = ImmApp::ShowResizablePlotInNodeEditor_Em("##histogram", histogramSizeEm, plotHistogram, flags);
        ImGui::SetNextItemWidth(HelloImGui::EmSize(IMAGE_WIDTH_EM));
        bool changedGamma = ImGui::SliderFloat("##gamma", &gamma, 0.2f, 3.0f, "gamma = %.2f");
        ImGui::SetItemTooltip("Above 1, the midtones get brighter");
        return changed || changedGamma;
    }
    cv::Mat Compute(const std::vector<cv::Mat>& inputs) override
    {
        const cv::Mat& in = inputs[0];
        histograms.assign(3, std::vector<double>(256, 0.0));
        for (int y = 0; y < in.rows; y++)
            for (int x = 0; x < in.cols; x++)
            {
                const cv::Vec3b& pixel = in.at<cv::Vec3b>(y, x);
                for (int c = 0; c < 3; c++)
                    histograms[c][pixel[c]] += 1.0;
            }
        cv::Mat lut(1, 256, CV_8U);
        for (int i = 0; i < 256; i++)
        {
            double v = std::clamp((i - black) / (white - black), 0.0, 1.0);
            lut.at<uchar>(i) = (uchar)(std::pow(v, 1.0 / gamma) * 255.0);
        }
        cv::Mat r;
        cv::LUT(in, lut, r);
        return r;
    }
};

struct Blend : Node
{
    static inline const char* TITLE = "Blend";
    static inline const char* DOC = "Mix: $(1-t)\\,a + t\\,b$  \nAdd: $a + t\\,b$";
    static inline const std::vector<InputSpec> INPUTS = {{"a", PinType::Color}, {"b", PinType::Color}};
    static constexpr PinType OUTPUT = PinType::Color;
    static inline const std::vector<const char*> MODES = {"Mix", "Add"};
    int mode = 1;
    float t = 1.0f;
    Blend() : Node(TITLE, DOC, INPUTS, OUTPUT) {}

    bool DrawParams() override
    {
        ImGui::SetNextItemWidth(HelloImGui::EmSize(IMAGE_WIDTH_EM));
        bool changedMode = ImGui::Combo("##mode", &mode, MODES.data(), (int)MODES.size());
        ImGui::SetNextItemWidth(HelloImGui::EmSize(IMAGE_WIDTH_EM));
        bool changedT = ImGui::SliderFloat("##t", &t, 0.0f, 1.0f, "t = %.2f");
        return changedMode || changedT;
    }
    cv::Mat Compute(const std::vector<cv::Mat>& inputs) override
    {
        const cv::Mat& a = inputs[0];
        cv::Mat b, r;
        cv::resize(inputs[1], b, a.size());  // b takes the size of a
        if (std::string(MODES[mode]) == "Mix")
            cv::addWeighted(a, 1.0 - t, b, t, 0.0, r);
        else
            cv::addWeighted(a, 1.0, b, t, 0.0, r);  // saturates at 255
        return r;
    }
};

// The classes of node, for the "Add a node" menu: their title, the types of their pins, and how to create one
struct NodeClass
{
    const char* title;
    std::vector<InputSpec> inputs;
    PinType output;
    std::function<std::unique_ptr<Node>()> make;
};

template <typename T>
NodeClass ClassOf()
{
    return NodeClass{T::TITLE, T::INPUTS, T::OUTPUT, [] { return std::make_unique<T>(); }};
}

const std::vector<NodeClass>& NodeClasses()
{
    static const std::vector<NodeClass> classes = {
        ClassOf<ImageFile>(), ClassOf<Grayscale>(), ClassOf<Blur>(), ClassOf<Edges>(), ClassOf<Threshold>(),
        ClassOf<Dilate>(), ClassOf<Colorize>(), ClassOf<Levels>(), ClassOf<Blend>()};
    return classes;
}


// =====================================================================================================================
// 3. The graph, and its evaluation
// =====================================================================================================================
struct Link
{
    Pin* start;  // an output
    Pin* end;  // an input
    ed::LinkId id = ed::LinkId(NewId());
};

// A frame behind some nodes, with a title: dragging it moves the nodes inside
struct Group
{
    std::string title;
    ImVec2 sizeEm;
    ed::NodeId id = ed::NodeId(NewId());
};

// A node without pins, that shows a text (markdown)
struct Note
{
    std::string text;
    float widthEm;
    ed::NodeId id = ed::NodeId(NewId());
};

struct Graph
{
    std::vector<std::unique_ptr<Node>> nodes;  // owned by pointers: the pins point to their node
    std::vector<Link> links;
    std::vector<Group> groups;
    std::vector<Note> notes;

    // Adds a node at a position in the editor's coordinates (pixels at zoom 1)
    Node* AddNode(std::unique_ptr<Node> node, ImVec2 position)
    {
        ed::SetNodePosition(node->id, position);  // the editor keeps the positions: we only give the first one
        nodes.push_back(std::move(node));
        return nodes.back().get();
    }

    void AddGroup(const Group& group, ImVec2 position)
    {
        groups.push_back(group);
        ed::SetNodePosition(group.id, position);
    }

    void AddNote(const Note& note, ImVec2 position)
    {
        notes.push_back(note);
        ed::SetNodePosition(note.id, position);
    }

    void Connect(Pin* output, Pin* input)
    {
        std::erase_if(links, [input](const Link& link) { return link.end == input; });  // an input receives one link at most
        links.push_back(Link{output, input});
    }

    const Link* LinkTo(const Pin* input) const
    {
        for (const Link& link : links)
            if (link.end == input)
                return &link;
        return nullptr;
    }

    // Removes a node and its links, a group, or a note
    void Remove(ed::NodeId nodeId)
    {
        std::erase_if(groups, [nodeId](const Group& group) { return group.id == nodeId; });
        std::erase_if(notes, [nodeId](const Note& note) { return note.id == nodeId; });
        std::erase_if(links, [nodeId](const Link& link) {
            return link.start->node->id == nodeId || link.end->node->id == nodeId;
        });
        std::erase_if(nodes, [nodeId](const std::unique_ptr<Node>& node) { return node->id == nodeId; });
    }

    Pin* FindPin(ed::PinId pinId)
    {
        for (auto& node : nodes)
        {
            for (auto& pin : node->inputs)
                if (pin->id == pinId)
                    return pin.get();
            if (node->output->id == pinId)
                return node->output.get();
        }
        return nullptr;
    }

    // True if `node` is `other`, or feeds it through links
    bool Feeds(const Node* node, const Node* other) const
    {
        if (node == other)
            return true;
        for (const Link& link : links)
            if (link.end->node == other && Feeds(node, link.start->node))
                return true;
        return false;
    }
};

// Computes the node's image again if its parameters, or the images it receives, changed.
// Its sources are evaluated first (a pull). A version number tells whether an image changed: this is cheaper than
// comparing the images, and it follows the new links too.
void Evaluate(Graph& graph, Node& node)
{
    std::vector<Node*> sources;
    for (auto& pin : node.inputs)
    {
        const Link* link = graph.LinkTo(pin.get());
        if (link != nullptr)
            Evaluate(graph, *link->start->node);
        sources.push_back(link != nullptr ? link->start->node : nullptr);
    }
    std::vector<int> versions;
    for (Node* source : sources)
        versions.push_back(source != nullptr ? source->version : -1);
    if (!node.paramsChanged && versions == node.inputsVersions)
        return;

    node.paramsChanged = false;
    node.inputsVersions = versions;
    node.version++;
    node.computedFrame = ImGui::GetFrameCount();
    node.imageParams.RefreshImage = true;  // ImmVision keeps a texture of each image: it must know of a new one
    std::string missing;
    for (size_t i = 0; i < sources.size(); i++)
        if (sources[i] == nullptr || sources[i]->image.empty())
            missing += (missing.empty() ? "" : ", ") + node.inputs[i]->name;
    if (!missing.empty())
    {
        node.image = cv::Mat();
        node.error = "Waiting for an image on: " + missing;
        return;
    }
    std::vector<cv::Mat> inputs;
    for (size_t i = 0; i < sources.size(); i++)
    {
        cv::Mat image = sources[i]->image;
        if (node.inputs[i]->type == PinType::Color && image.channels() == 1)  // a gray image where a color one is expected
            cv::cvtColor(image, image, cv::COLOR_GRAY2RGB);
        inputs.push_back(image);
    }
    node.image = node.Compute(inputs);
    node.error = "";
}

Graph InitialGraph()
{
    float em = HelloImGui::EmSize();
    Graph graph;
    graph.AddGroup(Group{"Draw the edges", ImVec2(62, 24)}, ImVec2(15, 27) * em);
    graph.AddNote(Note{TIPS, 17.0f}, ImVec2(38, 1) * em);
    Node* image = graph.AddNode(std::make_unique<ImageFile>(), ImVec2(0, 0) * em);
    Node* levels = graph.AddNode(std::make_unique<Levels>(), ImVec2(17, 0) * em);
    Node* gray = graph.AddNode(std::make_unique<Grayscale>(), ImVec2(16, 30) * em);
    Node* blur = graph.AddNode(std::make_unique<Blur>(), ImVec2(31, 30) * em);
    Node* edges = graph.AddNode(std::make_unique<Edges>(), ImVec2(46, 30) * em);
    Node* dilate = graph.AddNode(std::make_unique<Dilate>(), ImVec2(61, 30) * em);
    Node* colorize = graph.AddNode(std::make_unique<Colorize>(), ImVec2(79, 16) * em);
    Node* blend = graph.AddNode(std::make_unique<Blend>(), ImVec2(96, 4) * em);
    struct Step { Node* source; Node* target; int inputIndex; };
    std::vector<Step> chain = {{image, levels, 0}, {image, gray, 0}, {gray, blur, 0}, {blur, edges, 0},
                               {edges, dilate, 0}, {dilate, colorize, 0}, {levels, blend, 0}, {colorize, blend, 1}};
    for (const Step& step : chain)
        graph.Connect(step.source->output.get(), step.target->inputs[step.inputIndex].get());
    return graph;
}


// =====================================================================================================================
// 4. Drawing the graph
// =====================================================================================================================
// A pin's icon: a circle for a color image, a square for a gray one; filled when linked
void DrawPin(const Pin& pin, bool linked)
{
    ed::BeginPin(pin.id, pin.kind);
    ed::PinPivotAlignment(ImVec2(0.5f, 0.5f));  // the links reach the center of the icon...
    ed::PinPivotSize(ImVec2(0, 0));  // ...and not the edge of the pin's rectangle
    float radius = HelloImGui::EmSize(PIN_RADIUS_EM);
    ImVec2 topLeft = ImGui::GetCursorScreenPos();
    ImGui::Dummy(ImVec2(2 * radius, 2 * radius));  // the space of the pin; the draw list paints it
    ImVec2 center = topLeft + ImVec2(radius, radius);
    ImU32 color = ImGui::GetColorU32(TypeColor(pin.type));
    ImDrawList* drawList = ImGui::GetWindowDrawList();
    if (pin.type == PinType::Color)
    {
        drawList->AddCircle(center, radius, color, 0, 2.0f);
        if (linked)
            drawList->AddCircleFilled(center, radius * 0.6f, color);
    }
    else
    {
        ImVec2 half(radius * 0.85f, radius * 0.85f);
        drawList->AddRect(center - half, center + half, color, 0.0f, 2.0f);
        if (linked)
            drawList->AddRectFilled(center - half * 0.6f, center + half * 0.6f, color);
    }
    ed::EndPin();
    ImGui::SetItemTooltip("%s: %s", pin.name.c_str(), TypeName(pin.type));
}

void DrawNode(const Graph& graph, Node& node)
{
    float width = HelloImGui::EmSize(IMAGE_WIDTH_EM);
    ed::BeginNode(node.id);
    ImGui::PushID((int)node.id.Get());  // the widgets of two nodes of the same kind need different ids
    // The editor wraps the text at the width of the node (see main()). So the node needs an item with a fixed width,
    // first: text alone would give it no width, and it would collapse to one character per line.
    ImGui::Dummy(ImVec2(width, 0));
    RichMd::Render("**" + node.title + "**  \n" + node.doc);

    for (auto& pin : node.inputs)  // the inputs, on the left
    {
        DrawPin(*pin, graph.LinkTo(pin.get()) != nullptr);
        ImGui::SameLine();
        ImGui::Text("%s", pin->name.c_str());
    }

    if (node.DrawParams())
        node.paramsChanged = true;

    if (!node.error.empty())
        ImGui::TextColored(ImVec4(1.0f, 0.55f, 0.3f, 1.0f), "%s", node.error.c_str());
    else if (!node.image.empty())
    {
        ImmVision::Image("##image", node.image, &node.imageParams);  // zoom with the wheel, pan with a drag
        node.imageParams.RefreshImage = false;
        if (ImGui::IsItemHovered())
            DisableUserInputThisFrame();  // the wheel zooms the image, not the graph
    }

    ImGui::BeginHorizontal("output", ImVec2(width, 0));  // the output, on the right
    ImGui::Spring();
    ImGui::Text("%s", node.output->name.c_str());
    bool outputLinked = std::any_of(graph.links.begin(), graph.links.end(),
                                    [&node](const Link& link) { return link.start == node.output.get(); });
    DrawPin(*node.output, outputLinked);
    ImGui::EndHorizontal();

    ImGui::PopID();
    ed::EndNode();
}

void DrawGroup(const Group& group)
{
    ed::PushStyleColor(ed::StyleColor_NodeBg, ImVec4(1.0f, 1.0f, 1.0f, 0.05f));
    ed::PushStyleColor(ed::StyleColor_NodeBorder, ImVec4(1.0f, 1.0f, 1.0f, 0.25f));
    ed::BeginNode(group.id);
    RichMd::Render("**" + group.title + "**");
    ed::Group(group.sizeEm * HelloImGui::EmSize());  // its size at creation; then the user resizes it
    ed::EndNode();
    ed::PopStyleColor(2);
}

void DrawNote(const Note& note)
{
    ed::BeginNode(note.id);
    ImGui::Dummy(ImVec2(HelloImGui::EmSize(note.widthEm), 0));  // text alone gives no width to a node (see DrawNode())
    RichMd::Render(note.text);
    ed::EndNode();
}

void DrawLinks(const Graph& graph)
{
    for (const Link& link : graph.links)
    {
        ed::Link(link.id, link.start->id, link.end->id, TypeColor(link.start->type), LINK_THICKNESS);
        if (link.start->node->computedFrame == ImGui::GetFrameCount())
            ed::Flow(link.id);  // a new image runs along the link
    }
}


// =====================================================================================================================
// 5. Letting the user edit the graph
// =====================================================================================================================
// The editor tells what the user wants (a new link, a new node, a deletion); the app decides, and changes its graph.

// Why a link from `output` to `input` is refused ("" if it is accepted)
std::string WhyNot(const Pin& output, const Pin& input, const Graph& graph)
{
    if (output.kind != ed::PinKind::Output || input.kind != ed::PinKind::Input)
        return "A link goes from an output (right) to an input (left)";
    if (graph.Feeds(input.node, output.node))
        return "This link would make a loop";
    if (!Accepts(input.type, output.type))
        return input.node->title + " needs " + TypeName(input.type) + ": add a Grayscale node before it";
    return "";
}

// Whether a new node of this class could be linked to a pin
bool CanLink(const Pin& pin, const NodeClass& nodeClass)
{
    if (pin.kind == ed::PinKind::Output)
        return std::any_of(nodeClass.inputs.begin(), nodeClass.inputs.end(),
                           [&pin](const InputSpec& input) { return Accepts(input.type, pin.type); });
    return Accepts(pin.type, nodeClass.output);
}

struct MenuState
{
    Pin* droppedPin = nullptr;  // the pin of a link dropped in empty space: the new node is linked to it
    ImVec2 position;  // where the add menu opened, in the editor's coordinates
    ed::NodeId nodeId;  // the node whose menu is open
    ed::LinkId linkId;  // the link whose menu is open
};

void OpenAddMenu(MenuState& menu, Pin* droppedPin)
{
    ImGui::OpenPopup("Add a node");
    menu.droppedPin = droppedPin;
    // The mouse in the editor's coordinates, those of the node positions. ImGui::GetMousePos() gives them too, but not
    // in HandleCreations(): once a query returned true, the editor is suspended, and it gives screen coordinates.
    menu.position = ed::GetMousePosOnCanvas();
}

void HandleCreations(Graph& graph, MenuState& menu)
{
    // ed::EndCreate() only when ed::BeginCreate() returned true
    if (ed::BeginCreate(ImVec4(1.0f, 1.0f, 1.0f, 1.0f), 2.0f))
    {
        ed::PinId startId, endId;
        // True while the user drags a link between two pins (the drag may start from an input or from an output)
        if (ed::QueryNewLink(&startId, &endId))
        {
            Pin* start = graph.FindPin(startId);
            Pin* end = graph.FindPin(endId);
            if (start != nullptr && end != nullptr)
            {
                bool startIsInput = (start->kind == ed::PinKind::Input);
                Pin* output = startIsInput ? end : start;
                Pin* input = startIsInput ? start : end;
                std::string reason = WhyNot(*output, *input, graph);
                if (!reason.empty())
                {
                    ed::RejectNewItem(ImVec4(1.0f, 0.3f, 0.3f, 1.0f), 2.0f);  // the link turns red
                    ImGui::SetTooltip("%s", reason.c_str());
                }
                else
                {
                    ImGui::SetTooltip("Release to link");
                    if (ed::AcceptNewItem())  // true when the user releases the mouse
                        graph.Connect(output, input);
                }
            }
        }
        ed::PinId pinId;
        // True while the user drags a link from a pin to empty space
        if (ed::QueryNewNode(&pinId))
        {
            ImGui::SetTooltip("Release to add a node linked to this pin");
            if (ed::AcceptNewItem())
                OpenAddMenu(menu, graph.FindPin(pinId));
        }
        ed::EndCreate();
    }
}

void HandleDeletions(Graph& graph)
{
    if (ed::BeginDelete())
    {
        // The Delete key, and the menus below, send the items to delete here, one by one
        ed::LinkId linkId;
        while (ed::QueryDeletedLink(&linkId))
            if (ed::AcceptDeletedItem())
                std::erase_if(graph.links, [linkId](const Link& link) { return link.id == linkId; });
        ed::NodeId nodeId;
        while (ed::QueryDeletedNode(&nodeId))
            if (ed::AcceptDeletedItem())
                graph.Remove(nodeId);
        ed::EndDelete();
    }
}

void HandleMenus(Graph& graph, MenuState& menu)
{
    if (ed::ShowBackgroundContextMenu())
        OpenAddMenu(menu, nullptr);
    if (ImGui::BeginPopup("Add a node"))
    {
        Pin* pin = menu.droppedPin;
        for (const NodeClass& nodeClass : NodeClasses())
        {
            if (pin != nullptr && !CanLink(*pin, nodeClass))
                continue;
            if (ImGui::MenuItem(nodeClass.title))
            {
                Node* node = graph.AddNode(nodeClass.make(), menu.position);
                if (pin != nullptr && pin->kind == ed::PinKind::Output)
                {
                    for (auto& input : node->inputs)
                        if (Accepts(input->type, pin->type))
                        {
                            graph.Connect(pin, input.get());
                            break;
                        }
                }
                else if (pin != nullptr)
                    graph.Connect(node->output.get(), pin);
            }
        }
        ImGui::EndPopup();
    }

    if (ed::ShowNodeContextMenu(&menu.nodeId))
        ImGui::OpenPopup("Node");
    if (ImGui::BeginPopup("Node"))
    {
        if (ImGui::MenuItem("Delete"))
            ed::DeleteNode(menu.nodeId);  // the node then goes through HandleDeletions()
        ImGui::EndPopup();
    }
    if (ed::ShowLinkContextMenu(&menu.linkId))
        ImGui::OpenPopup("Link");
    if (ImGui::BeginPopup("Link"))
    {
        if (ImGui::MenuItem("Delete"))
            ed::DeleteLink(menu.linkId);
        ImGui::EndPopup();
    }
}


// =====================================================================================================================
// 6. The GUI function
// =====================================================================================================================
struct AppState
{
    ed::EditorContext* editor = nullptr;  // the demo's own editor (see Editor())
    std::unique_ptr<Graph> graph;  // created at the first frame: the node positions need the editor
    MenuState menu;
    int frame = 0;  // since the graph was created
};

AppState& State()
{
    static AppState state;
    return state;
}

// The demo's own editor, with its own config, whatever the app that shows it: an app such as the bundle's explorer
// shows several node editor demos, which need different configs.
ed::EditorContext* Editor()
{
    AppState& state = State();
    if (!state.editor)
    {
        ed::Config config;
        config.SettingsFile = nullptr;  // the demo places its nodes at start: nothing to save
        // Inside a node, text wraps at the width of the node, and separators span it (instead of the width of the
        // window). A node then needs an item with a fixed width: see DrawNode().
        config.ForceWindowContentWidthToNodeWidth = true;
        state.editor = ed::CreateEditor(&config);
    }
    return state.editor;
}

}  // namespace


void gui_demo_node_editor_image_pipeline()
{
    AppState& state = State();
    RichMd::Render(HELP);
    if (ImGui::Button("Reset the graph"))
    {
        state.graph.reset();
        state.frame = 0;
    }
    ed::EditorContext* previousEditor = ed::GetCurrentEditor();
    ed::SetCurrentEditor(Editor());
    ed::Begin("Image pipeline");
    if (!state.graph)
        state.graph = std::make_unique<Graph>(InitialGraph());
    Graph& graph = *state.graph;
    for (auto& node : graph.nodes)
        Evaluate(graph, *node);
    for (const Group& group : graph.groups)  // the groups first: they are behind the nodes
        DrawGroup(group);
    for (const Note& note : graph.notes)
        DrawNote(note);
    for (auto& node : graph.nodes)
        DrawNode(graph, *node);
    DrawLinks(graph);
    HandleCreations(graph, state.menu);
    HandleDeletions(graph);
    HandleMenus(graph, state.menu);
    ed::End();

    // Fit the graph in the view, once the editor knows the size of the nodes: at the third frame (at the second, the
    // fit has no effect). The navigation functions work after ed::End().
    if (state.frame == 2)
        ed::NavigateToContent(0.0f);
    state.frame++;
    ed::SetCurrentEditor(previousEditor);
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    HelloImGui::RunnerParams params;
    params.callbacks.ShowGui = gui_demo_node_editor_image_pipeline;
    params.appWindowParams.windowTitle = "Node editor: an image pipeline";
    params.appWindowParams.windowGeometry.size = {1400, 850};
    params.callbacks.BeforeExit = [] { ed::DestroyEditor(Editor()); };
    ImmApp::AddOnsParams addOns;  // the demo creates its own node editor
    addOns.withLatex = true;  // implies withMarkdown
    addOns.withImplot = true;
    ImmApp::Run(params, addOns);
    return 0;
}
#endif

#else // the node editor, ImPlot and OpenCV are needed
#include "imgui.h"
void gui_demo_node_editor_image_pipeline()
{
    ImGui::TextWrapped("This demo requires imgui-node-editor, ImPlot, and OpenCV (build with -DIMGUI_BUNDLE_DEMOS_WITH_OPENCV=ON)");
}
#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
#include <cstdio>
int main(int, char**) { printf("This demo requires imgui-node-editor, ImPlot, and OpenCV\n"); return 0; }
#endif
#endif
