// This demo show how we can call ImGui::ErrorCheckEndFrameRecover()
// to recover from errors originating when ImGui::End() is not called (for example when an exception is raised)

#include "hello_imgui/hello_imgui.h"
#include "imgui.h"

#include <cmath>
#include <map>
#include <cassert>


struct SliderAdaptativeInterval
{
    float max() const { return pow(10.f, CurrentPower); }

    void SetCurrentValue(float currentValue)
    {
        assert (currentValue >= 0.f);
        if (currentValue == lastValue)
            return;

        float w = max();
        float triggerRatio = 0.1f;
        float triggerMax = w * (1 - triggerRatio);
        float triggerMin = w * (triggerRatio / 5.f);
        if (currentValue > triggerMax)
            CurrentPower++;
        else if (currentValue <  triggerMin)
            CurrentPower--;

        lastValue = currentValue;
    }

    std::string FormatString()
    {
        std::string floatFormat = "%.4g";
        char maxValueFormatted[256];
        snprintf(maxValueFormatted, 256, floatFormat.c_str(), max());

        std::string format = floatFormat + "  (max: " + maxValueFormatted + ")";
        return format;
    }
    int CurrentPower = 1;

private:
    float lastValue = 0.0f;
};


struct SliderAdaptativeIntervalCache
{
    SliderAdaptativeInterval& GetOrCreate(ImGuiID id)
    {
        if (Intervals.find(id) == Intervals.end())
            Intervals[id] = SliderAdaptativeInterval();
        return Intervals.at(id);
    }

    std::map<ImGuiID, SliderAdaptativeInterval> Intervals;
};


bool AdaptativeSliderFloat(const char* label, float* v)
{
    static SliderAdaptativeIntervalCache cache;
    SliderAdaptativeInterval& interval = cache.GetOrCreate(ImGui::GetID(label));

    ImGui::PushID(interval.CurrentPower);

    bool r = ImGui::SliderFloat(label, v, 0.f, interval.max(), interval.FormatString().c_str());
    interval.SetCurrentValue(*v);

    ImGui::PopID();

    return r;
}



void Gui()
{
    ImGui::Text("Hello");

    static float value = 30.f;

    ImGui::SetNextItemWidth(150);
    AdaptativeSliderFloat("Value", &value);
}


int main()
{
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = Gui;
    HelloImGui::Run(runnerParams);
    return 0;
}
