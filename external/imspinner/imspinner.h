#ifndef _IMSPINNER_H_
#define _IMSPINNER_H_

/*
 * The MIT License (MIT)
 * 
 * Copyright (c) 2021-2022 Dalerank
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 * 
 */


// <Patches on the original source>
#include "imgui.h"
#include "imgui_internal.h"
#include <algorithm>

#include <functional>
#include <array>
size_t min_patched(size_t a, int b)
{
    if ((int) a < b)
        return a;
    else
        return (size_t)b;
}
// </Patches on the original source>


namespace ImSpinner
{
#define DECLPROP(name,type,def) struct name { type value = def; operator type() { return value; } };
    enum SpinnerTypeT {
      e_st_rainbow = 0,
      e_st_angle,
      e_st_dots,
      e_st_ang,

      e_st_count
    };

    using float_ptr = float *;

    DECLPROP (SpinnerType, SpinnerTypeT, e_st_rainbow)
    DECLPROP (Radius, float, 16.f)
    DECLPROP (Speed, float, 1.f)
    DECLPROP (Thickness, float, 1.f)
    DECLPROP (Color, ImColor, 0xffffffff)
    DECLPROP (BgColor, ImColor, 0xffffffff)
    DECLPROP (Angle, float, IM_PI)
    DECLPROP (FloatPtr, float_ptr, nullptr)
    DECLPROP (Dots, int, 0)
    DECLPROP (MiddleDots, int, 0)
    DECLPROP (MinThickness, float, 0.f)
#undef DECLPROP

    namespace detail {
      bool SpinnerBegin(const char *label, float radius, ImVec2 &pos, ImVec2 &size, ImVec2 &centre) {
        ImGuiWindow *window = ImGui::GetCurrentWindow();
        if (window->SkipItems)
          return false;

        ImGuiContext &g = *GImGui;
        const ImGuiStyle &style = g.Style;
        const ImGuiID id = window->GetID(label);

        pos = window->DC.CursorPos;
        size = ImVec2((radius) * 2, (radius + style.FramePadding.y) * 2);

        const ImRect bb(pos, ImVec2(pos.x + size.x, pos.y + size.y));
        ImGui::ItemSize(bb, style.FramePadding.y);

        centre = bb.GetCenter();
        if (!ImGui::ItemAdd(bb, id))
          return false;

        return true;
      }

#define IMPLRPOP(basetype,type) basetype m_##type; \
                                void set##type(const basetype& v) { m_##type = v;} \
                                void set(type h) { m_##type = h.value;} \
                                template<typename First, typename... Args> \
                                void set(const type& h, const Args&... args) { set##type(h.value); this->template set<Args...>(args...); }
      struct SpinnerConfig {
        SpinnerConfig() {}

        template<typename none = void> void set() {}

        template<typename... Args>
        SpinnerConfig(const Args&... args) { this->template set<Args...>(args...); }

        IMPLRPOP(SpinnerTypeT, SpinnerType)
        IMPLRPOP(float, Radius)
        IMPLRPOP(float, Speed)
        IMPLRPOP(float, Thickness)
        IMPLRPOP(ImColor, Color)
        IMPLRPOP(ImColor, BgColor)
        IMPLRPOP(float, Angle)
        IMPLRPOP(float_ptr, FloatPtr)
        IMPLRPOP(int, Dots)
        IMPLRPOP(int, MiddleDots)
        IMPLRPOP(float, MinThickness)
      };
#undef IMPLRPOP
    }

#define SPINNER_HEADER(pos, size, centre) ImVec2 pos, size, centre; if (!detail::SpinnerBegin(label, radius, pos, size, centre)) { return; }; ImGuiWindow *window = ImGui::GetCurrentWindow();

    void SpinnerRainbow(const char *label, float radius, float thickness, const ImColor &color, float speed)
    {
        SPINNER_HEADER(pos, size, centre);

        // Render
        window->DrawList->PathClear();
        const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
        float start = ImAbs(ImSin((float)ImGui::GetTime() * 1.8f) * (num_segments - 5));

        const float a_min = IM_PI * 2.0f * ((float)start) / (float)num_segments;
        const float a_max = IM_PI * 2.0f * ((float)num_segments - 3) / (float)num_segments;

        for (size_t i = 0; i < num_segments; i++)
        {
            const float a = a_min + ((float)i / (float)num_segments) * (a_max - a_min);
            window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a + (float)ImGui::GetTime() * speed) * radius,
                                         centre.y + ImSin(a + (float)ImGui::GetTime() * speed) * radius));
        }
        window->DrawList->PathStroke(color, false, thickness);
    }

    void SpinnerAng(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), const ImColor &bg = ImColor(0xffffff80), float speed = 2.8f, float angle = IM_PI)
    {
        SPINNER_HEADER(pos, size, centre);

        // Render
        window->DrawList->PathClear();
        const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
        float start = (float)ImGui::GetTime()* speed;
        const float bg_angle_offset = IM_PI * 2.f / num_segments;
        for (size_t i = 0; i <= num_segments; i++)
        {
            const float a = start + (i * bg_angle_offset);
            window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius));
        }
        window->DrawList->PathStroke(bg, false, thickness);

        window->DrawList->PathClear();
        const float angle_offset = angle / num_segments;
        for (size_t i = 0; i < num_segments; i++)
        {
            const float a = start + (i * angle_offset);
            window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius));
        }
        window->DrawList->PathStroke(color, false, thickness);
    }
    /*auto is_between = [] (float start, float end, float mid){
    end = (end - start) < 0.0f ? (end - start + IM_PI) : end - start;
    mid = (mid - start) < 0.0f ? (mid - start + IM_PI) : mid - start;
    return (mid < end);
    };*/

    void SpinnerClock(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), const ImColor &bg = ImColor(0xffffff80), float speed = 2.8f)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      window->DrawList->PathClear();
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      float start = (float)ImGui::GetTime()* speed;
      const float bg_angle_offset = IM_PI * 2.f / num_segments;
      for (size_t i = 0; i <= num_segments; i++)
      {
        const float a = start + (i * bg_angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius));
      }
      window->DrawList->PathStroke(bg, false, thickness);

      window->DrawList->AddLine(centre, ImVec2(centre.x + ImCos(start) * radius, centre.y + ImSin(start) * radius), color, thickness * 2);
      window->DrawList->AddLine(centre, ImVec2(centre.x + ImCos(start * 0.5f) * radius / 2.f, centre.y + ImSin(start * 0.5f) * radius / 2.f), color, thickness * 2);
    }

    void SpinnerPulsar(const char *label, float radius, float thickness, const ImColor &bg = 0xffffff80, float speed = 2.8f, bool sequence = true)
    {
      SPINNER_HEADER(pos, size, centre);

      ImGuiStorage* storage = window->DC.StateStorage;
      const ImGuiID radiusbId = window->GetID("##radiusb");
      float radius_b = storage->GetFloat(radiusbId, 0.8f);

      // Render
      window->DrawList->PathClear();
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      float start = (float)ImGui::GetTime() * speed;
      const float bg_angle_offset = IM_PI * 2.f / num_segments;

      float start_r = ImFmod(start, IM_PI / 2.f);
      float radius_k = ImSin(start_r);
      float radius1 = radius_k * radius;
      for (size_t i = 0; i <= num_segments; i++)
      {
        const float a = start + (i * bg_angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius1, centre.y + ImSin(a) * radius1));
      }
      window->DrawList->PathStroke(bg, false, thickness);

      if (sequence)
      {
        radius_b -= (0.005f * speed);
        radius_b = ImMax(radius_k, ImMax(0.8f, radius_b));
      } 
      else 
      {
        radius_b = (1 - radius_k);
      }
      storage->SetFloat(radiusbId, radius_b);
      
      float radius_tb = sequence ? ImMax(radius_k, radius_b) * radius : (radius_b * radius);
      window->DrawList->PathClear();
      for (size_t i = 0; i <= num_segments; i++)
      {
        const float a = start + (i * bg_angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius_tb, centre.y + ImSin(a) * radius_tb));
      }
      window->DrawList->PathStroke(bg, false, thickness);
    }

    void SpinnerDoubleFadePulsar(const char *label, float radius, float thickness, const ImColor &bg = 0xffffff80, float speed = 2.8f)
    {
      (void) thickness;
      SPINNER_HEADER(pos, size, centre);

      ImGuiStorage* storage = window->DC.StateStorage;
      const ImGuiID radiusbId = window->GetID("##radiusb");
      float radius_b = storage->GetFloat(radiusbId, 0.8f);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      float start = (float)ImGui::GetTime() * speed;
      const float bg_angle_offset = IM_PI * 2.f / num_segments;

      float start_r = ImFmod(start, IM_PI / 2.f);
      float radius_k = ImSin(start_r);
      float radius1 = radius_k * radius;
      ImColor c = bg;
      c.Value.w = ImMin(0.1f, radius_k);
      window->DrawList->AddCircleFilled(centre, radius1, c, num_segments);

      radius_b = (1 - radius_k);
      storage->SetFloat(radiusbId, radius_b);

      float radius_tb = radius_b * radius;
      c = bg;
      c.Value.w = ImMin(0.3f, radius_b);
      window->DrawList->AddCircleFilled(centre, radius_tb, c, num_segments);
    }

    void SpinnerTwinPulsar(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, int rings = 2)
    {
      SPINNER_HEADER(pos, size, centre);

      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      const float bg_angle_offset = IM_PI * 2.f / num_segments;
      const float koeff = IM_PI / (2 * (float)rings);
      float start = (float)ImGui::GetTime() * speed;

      for (int num_ring = 0; num_ring < rings; ++num_ring)
      {
        window->DrawList->PathClear();
        float start_r = ImFmod(start + (num_ring * koeff), IM_PI / 2.f);
        float radius_k = ImSin(start_r);
        float radius1 = radius_k * radius;
        ImColor c = color;
        if (radius_k > 0.5f)
        {
          c.Value.w = 2.f - (radius_k * 2.f);
        }

        for (size_t i = 0; i <= num_segments; i++)
        {
          const float a = start + (i * bg_angle_offset);
          window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius1, centre.y + ImSin(a) * radius1));
        }
        window->DrawList->PathStroke(c, false, thickness);
      }
    }

    void SpinnerFadePulsar(const char *label, float radius, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, int rings = 2)
    {
      SPINNER_HEADER(pos, size, centre);

      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      const float bg_angle_offset = IM_PI * 2.f / num_segments;
      const float koeff = IM_PI / (2 * (float)rings);
      float start = (float)ImGui::GetTime() * speed;

      for (int num_ring = 0; num_ring < rings; ++num_ring)
      {
        float start_r = ImFmod(start + (num_ring * koeff), IM_PI / 2.f);
        float radius_k = ImSin(start_r);
        float radius1 = radius_k * radius;
        ImColor c = color;
        if (radius_k > 0.5f)
        {
          c.Value.w = 2.f - (radius_k * 2.f);
        }

        c.Value.w = (radius_k > 0.5f) ? (2.f - (radius_k * 2.f)) : c.Value.w;
        window->DrawList->AddCircleFilled(centre, radius1, c, num_segments);
      }
    }

    void SpinnerDots(const char *label, float *nextdot, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t dots = 12, size_t mdots = 6, float minth = -1.f)
    {
        SPINNER_HEADER(pos, size, centre);

        // Render
        float start = (float)ImGui::GetTime() * speed;
        const float bg_angle_offset = IM_PI * 2.f / dots;
        dots = min_patched(dots, 32);

        float def_nextdot = 0;
        float &ref_nextdot = nextdot ? *nextdot : def_nextdot;
        if (ref_nextdot < 0.f)
          ref_nextdot = (float)dots;

        auto thcorrect = [&thickness, &ref_nextdot, &mdots, &minth] (int i) {
            const float nth = minth < 0.f ? thickness / 2.f : minth;
            return ImMax(nth, ImSin(((i - ref_nextdot) / mdots) * IM_PI) * thickness);
        };

        for (size_t i = 0; i <= dots; i++)
        {
            float a = start + (i * bg_angle_offset);
            a = ImFmod(a, 2 * IM_PI);
            float th = minth < 0 ? thickness / 2.f : minth;

            if (ref_nextdot + mdots < dots) {
                if (i > ref_nextdot && i < ref_nextdot + mdots)
                    th = thcorrect(i);
            } else {
                if ((i > ref_nextdot && i < dots) || (i < ((int)(ref_nextdot + mdots)) % dots))
                    th = thcorrect(i);
            }

            window->DrawList->AddCircleFilled(ImVec2(centre.x + ImCos(-a) * radius, centre.y + ImSin(-a) * radius), th, color, 8);
        }
    }

    void SpinnerVDots(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t dots = 12, size_t mdots = 6)
    {
        SPINNER_HEADER(pos, size, centre);

        // Render
        float start = (float)ImGui::GetTime() * speed;
        const float bg_angle_offset = IM_PI * 2.f / dots;
        dots = min_patched(dots, 32);

        for (size_t i = 0; i <= dots; i++)
        {
            float a = start + (i * bg_angle_offset);
            a = ImFmod(a, 2 * IM_PI);
            window->DrawList->AddCircleFilled(ImVec2(centre.x + ImCos(-a) * radius, centre.y + ImSin(-a) * radius), thickness / 2, color, 8);
        }

        window->DrawList->PathClear();
        const float d_ang = (mdots / (float)dots) * 2 * IM_PI;
        const float angle_offset = (d_ang) / dots;
        for (size_t i = 0; i < dots; i++)
        {
            const float a = start + (i * angle_offset);
            window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius));
        }
        window->DrawList->PathStroke(color, false, thickness);
    }

    void SpinnerBounceDots(const char *label, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t dots = 3)
    {
      ImGuiWindow *window = ImGui::GetCurrentWindow();
      if (window->SkipItems)
        return;

      ImGuiContext &g = *GImGui;
      const ImGuiStyle &style = g.Style;
      const ImGuiID id = window->GetID(label);

      const float nextItemKoeff = 2.5f;
      const float heightKoeff = 2.f;
      const float heightSpeed = 0.8f;
      ImVec2 pos = window->DC.CursorPos;
      ImVec2 size( (thickness * nextItemKoeff) * dots + style.FramePadding.x, thickness * 4 * heightKoeff + style.FramePadding.y);

      const ImRect bb(pos, ImVec2(pos.x + size.x, pos.y + size.y));
      ImGui::ItemSize(bb, style.FramePadding.y);
      if (!ImGui::ItemAdd(bb, id))
        return;

      const ImVec2 centre = bb.GetCenter();

      // Render
      float start = (float)ImGui::GetTime() * speed;

      const float offset = IM_PI / dots;
      for (size_t i = 0; i < dots; i++)
      {
        float a = start + (IM_PI - i * offset);
        float sina = ImSin(a * heightSpeed);
        float y = centre.y + sina * thickness * heightKoeff;
        if (y > centre.y)
          y = centre.y;
        window->DrawList->AddCircleFilled(ImVec2(pos.x + style.FramePadding.x  + i * (thickness * nextItemKoeff), y), thickness, color, 8);
      }
    }

    void SpinnerFadeDots(const char *label, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t dots = 3)
    {
      ImGuiWindow *window = ImGui::GetCurrentWindow();
      if (window->SkipItems)
        return;

      ImGuiContext &g = *GImGui;
      const ImGuiStyle &style = g.Style;
      const ImGuiID id = window->GetID(label);

      const float nextItemKoeff = 2.5f;
      const float heightKoeff = 2.f;
      const float heightSpeed = 0.8f;
      ImVec2 pos = window->DC.CursorPos;
      ImVec2 size( (thickness * nextItemKoeff) * dots + style.FramePadding.x, thickness * 4 * heightKoeff + style.FramePadding.y);

      const ImRect bb(pos, ImVec2(pos.x + size.x, pos.y + size.y));
      ImGui::ItemSize(bb, style.FramePadding.y);
      if (!ImGui::ItemAdd(bb, id))
        return;

      const ImVec2 centre = bb.GetCenter();

      // Render
      float start = (float)ImGui::GetTime() * speed;

      const float offset = IM_PI / dots;
      for (size_t i = 0; i < dots; i++)
      {
        float a = start + (IM_PI - i * offset);
        ImColor c = color;
        c.Value.w = ImMax(0.1f, ImSin(a * heightSpeed));
        window->DrawList->AddCircleFilled(ImVec2(pos.x + style.FramePadding.x  + i * (thickness * nextItemKoeff), centre.y), thickness, c, 8);
      }
    }

    void SpinnerScaleDots(const char *label, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t dots = 3)
    {
      ImGuiWindow *window = ImGui::GetCurrentWindow();
      if (window->SkipItems)
        return;

      ImGuiContext &g = *GImGui;
      const ImGuiStyle &style = g.Style;
      const ImGuiID id = window->GetID(label);

      const float nextItemKoeff = 2.5f;
      const float heightKoeff = 2.f;
      const float heightSpeed = 0.8f;
      ImVec2 pos = window->DC.CursorPos;
      ImVec2 size( (thickness * nextItemKoeff) * dots + style.FramePadding.x, thickness * 4 * heightKoeff + style.FramePadding.y);

      const ImRect bb(pos, ImVec2(pos.x + size.x, pos.y + size.y));
      ImGui::ItemSize(bb, style.FramePadding.y);
      if (!ImGui::ItemAdd(bb, id))
        return;

      const ImVec2 centre = bb.GetCenter();

      // Render
      float start = (float)ImGui::GetTime() * speed;

      const float offset = IM_PI / dots;
      for (size_t i = 0; i < dots; i++)
      {
        const float a = start + (IM_PI - i * offset);
        const float th = thickness * ImSin(a * heightSpeed);
        ImColor fade_color = color;
        fade_color.Value.w = 0.1f;
        window->DrawList->AddCircleFilled(ImVec2(pos.x + style.FramePadding.x  + i * (thickness * nextItemKoeff), centre.y), thickness, fade_color, 8);
        window->DrawList->AddCircleFilled(ImVec2(pos.x + style.FramePadding.x  + i * (thickness * nextItemKoeff), centre.y), th, color, 8);
      }
    }

    void SpinnerMovingDots(const char *label, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t dots = 3)
    {
      ImGuiWindow *window = ImGui::GetCurrentWindow();
      if (window->SkipItems)
        return;

      ImGuiContext &g = *GImGui;
      const ImGuiStyle &style = g.Style;
      const ImGuiID id = window->GetID(label);

      const float nextItemKoeff = 2.5f;
      const float heightKoeff = 2.f;
      const float heightSpeed = 0.8f;
      ImVec2 pos = window->DC.CursorPos;
      ImVec2 size( (thickness * nextItemKoeff) * dots + style.FramePadding.x, thickness * 4 * heightKoeff + style.FramePadding.y);

      const ImRect bb(pos, ImVec2(pos.x + size.x, pos.y + size.y));
      ImGui::ItemSize(bb, style.FramePadding.y);
      if (!ImGui::ItemAdd(bb, id))
        return;

      const ImVec2 centre = bb.GetCenter();

      // Render
      float start = ImFmod((float)ImGui::GetTime() * speed, size.x);

      float offset = 0;
      for (size_t i = 0; i < dots; i++)
      {
        const float a = start + (i * IM_PI / dots);
        float th = thickness;
        offset =  ImFmod(start + i * (size.x / dots), size.x);
        if (offset < thickness)
        {
          th = offset;
        }
        if (offset > size.x - thickness)
          th = size.x - offset;
        
        window->DrawList->AddCircleFilled(ImVec2(pos.x + style.FramePadding.x + offset, centre.y), th, color, 8);
      }
    }

    void SpinnerRotateDots(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, int dots = 2)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      ImGuiStorage* storage = window->DC.StateStorage;
      const ImGuiID velocityId = window->GetID("##velocity");
      const ImGuiID vtimeId = window->GetID("##velocitytime");

      float velocity = storage->GetFloat(velocityId, 0.f);
      float vtime = storage->GetFloat(vtimeId, 0.f);
     
      float dtime = ImFmod((float)vtime, IM_PI);
      float start = (vtime += velocity);
      if (dtime > 0.f && dtime < IM_PI / 2.f)
      {
        velocity += 0.001f * speed;
      }
      else if (dtime > IM_PI * 0.9f && dtime < IM_PI)
      {
        velocity -= 0.01f * speed;
      }
      if (velocity > 0.1f) velocity = 0.1f;
      if (velocity < 0.01f) velocity = 0.01f;

      storage->SetFloat(velocityId, velocity);
      storage->SetFloat(vtimeId, vtime);

      window->DrawList->AddCircleFilled(centre, thickness, color, 8);

      const float angle_offset = (2 * IM_PI) / dots;
      for (int i = 0; i < dots; i++)
      {
        const float a = start + (i * angle_offset);
        window->DrawList->AddCircleFilled(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius), thickness, color, 8);
      }
    }

    void SpinnerTwinAng(const char *label, float radius1, float radius2, float thickness, const ImColor &color1 = ImColor(0xffffffff), const ImColor &color2 = ImColor(0xff0000ff), float speed = 2.8f)
    {
      const float radius = ImMax(radius1, radius2);
      SPINNER_HEADER(pos, size, centre);

      // Render
      window->DrawList->PathClear();
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) * 2;
      const float start = ImFmod((float)ImGui::GetTime() * speed, IM_PI * 2.f);
      const float aoffset = ImFmod((float)ImGui::GetTime(), 1.5f * IM_PI);
      const float bofsset = (aoffset > IM_PI) ? IM_PI : aoffset;

      const float angle_offset = IM_PI * 2.f / num_segments;
      for (size_t i = 0; i <= 2 * num_segments; i++)
      {
        const float a = start + (i * angle_offset);
        if (i * angle_offset > 2 * bofsset)
          break;
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius1, centre.y + ImSin(a) * radius1));
      }
      window->DrawList->PathStroke(color1, false, thickness);

      window->DrawList->PathClear();
      for (size_t i = 0; i < num_segments / 2; i++)
      {
        const float a = start + (i * angle_offset);
        if (i * angle_offset > bofsset)
          break;
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius2, centre.y + ImSin(a) * radius2));
      }
      window->DrawList->PathStroke(color2, false, thickness);
    }

    void SpinnerFilling(const char *label, float radius, float thickness, const ImColor &color1 = ImColor(0xffffffff), const ImColor &color2 = ImColor(0xff0000ff), float speed = 2.8f)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const float start = ImFmod((float)ImGui::GetTime() * speed, IM_PI * 2.f);
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) * 2;
      window->DrawList->PathClear();
      const float angle_offset = IM_PI * 2.f / num_segments;
      for (size_t i = 0; i <= 2 * num_segments; i++)
      {
        const float a = (i * angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius));
      }
      window->DrawList->PathStroke(color1, false, thickness);

      window->DrawList->PathClear();
      for (size_t i = 0; i < 2 * num_segments / 2; i++)
      {
        const float a = (i * angle_offset);
        if (a > start)
          break;
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius));
      }
      window->DrawList->PathStroke(color2, false, thickness);
    }

    void SpinnerTopup(const char *label, float radius1, float radius2, const ImColor &color = ImColor(0xff0000ff), const ImColor &fg = ImColor(0xffffffff), const ImColor &bg = ImColor(0xffffffff), float speed = 2.8f)
    {
      const float radius = ImMax(radius1, radius2);
      SPINNER_HEADER(pos, size, centre);

      // Render
      const float start = ImFmod((float)ImGui::GetTime() * speed, IM_PI);
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) * 2;
      window->DrawList->AddCircleFilled(centre, radius1, bg, num_segments);

      window->DrawList->PathClear();
      const float abegin = (IM_PI * 0.5f) - start;
      const float aend = (IM_PI * 0.5f) + start;
      const float angle_offset = (aend - abegin) / num_segments;
      window->DrawList->PathArcTo(centre, radius1, abegin, aend, num_segments * 2);
      window->DrawList->PathFillConvex(color);

      window->DrawList->AddCircleFilled(centre, radius2, fg, num_segments);
    }

    void SpinnerTwinAng180(const char *label, float radius1, float radius2, float thickness, const ImColor &color1 = ImColor(0xffffffff), const ImColor &color2 = ImColor(0xff0000ff), float speed = 2.8f)
    {
      const float radius = ImMax(radius1, radius2);
      SPINNER_HEADER(pos, size, centre);

      // Render
      window->DrawList->PathClear();
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) * 4;
      const float start = ImFmod((float)ImGui::GetTime()* speed, IM_PI * 2.f);
      const float aoffset = ImFmod((float)ImGui::GetTime(), 2.f * IM_PI);
      const float bofsset = (aoffset > IM_PI) ? IM_PI : aoffset;

      const float angle_offset = IM_PI * 2.f / num_segments;
      window->DrawList->PathClear();
      float ared_min = 0, ared = 0;
      if (aoffset > IM_PI)
        ared_min = aoffset - IM_PI;

      for (size_t i = 0; i <= num_segments / 2 + 1; i++)
      {
        ared = start + (i * angle_offset);

        if (i * angle_offset < ared_min)
          continue;

        if (i * angle_offset > bofsset)
          break;

        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(ared) * radius2, centre.y + ImSin(ared) * radius2));
      }
      window->DrawList->PathStroke(color2, false, thickness);

      for (size_t i = 0; i <= 2 * num_segments + 1; i++)
      {
        const float a = ared + ared_min + (i * angle_offset);
        if (i * angle_offset < ared_min)
          continue;

        if (i * angle_offset > bofsset)
          break;
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius1, centre.y + ImSin(a) * radius1));
      }
      window->DrawList->PathStroke(color1, false, thickness);
    }

    void SpinnerTwinAng360(const char *label, float radius1, float radius2, float thickness, const ImColor &color1 = ImColor(0xffffffff), const ImColor &color2 = ImColor(0xff0000ff), float speed1 = 2.8f, float speed2 = 2.5f)
    {
      const float radius = ImMax(radius1, radius2);
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) * 2;
      const float start1 = ImFmod((float)ImGui::GetTime() * speed1, IM_PI * 2.f);
      const float start2 = ImFmod((float)ImGui::GetTime() * speed2, IM_PI * 2.f);
      const float aoffset = ImFmod((float)ImGui::GetTime(), 2.f * IM_PI);
      const float bofsset = (aoffset > IM_PI) ? IM_PI : aoffset;

      const float angle_offset = IM_PI * 2.f / num_segments;
      window->DrawList->PathClear();
      float ared_min = 0, ared = 0;
      if (aoffset > IM_PI)
        ared_min = aoffset - IM_PI;

      for (size_t i = 0; i <= num_segments + 1; i++)
      {
        ared = start1 + (i * angle_offset);

        if (i * angle_offset < ared_min * 2)
          continue;

        if (i * angle_offset > bofsset * 2.f)
          break;

        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(ared) * radius2, centre.y + ImSin(ared) * radius2));
      }
      window->DrawList->PathStroke(color2, false, thickness);

      window->DrawList->PathClear();
      for (size_t i = 0; i <= num_segments + 1; i++)
      {
        ared = start2 + (i * angle_offset);

        if (i * angle_offset < ared_min * 2)
          continue;

        if (i * angle_offset > bofsset * 2.f)
          break;

        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(-ared) * radius1, centre.y + ImSin(-ared) * radius1));
      }
      window->DrawList->PathStroke(color1, false, thickness);
    }

    void SpinnerIncDots(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t dots = 6)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      float start = (float)ImGui::GetTime() * speed;
      float astart = ImFmod(start, IM_PI / dots);
      start -= astart;
      const float bg_angle_offset = IM_PI / dots;
      dots = ImMin<size_t>(dots, 32);

      for (size_t i = 0; i <= dots; i++)
      {
        float a = start + (i * bg_angle_offset);
        ImColor c = color;
        c.Value.w = ImMax(0.1f, i / (float)dots);
        window->DrawList->AddCircleFilled(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius), thickness, c, 8);
      }
    }

    void SpinnerIncFullDots(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t dots = 4)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      dots = ImMin<size_t>(dots, 32);
      float start = (float)ImGui::GetTime() * speed;
      float astart = ImFmod(start, IM_PI / dots);
      start -= astart;
      const float bg_angle_offset = IM_PI / dots;

      for (size_t i = 0; i < dots * 2; i++)
      {
        float a = start + (i * bg_angle_offset);
        ImColor c = color;
        c.Value.w = 0.1f;
        window->DrawList->AddCircleFilled(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius), thickness, c, 8);
      }

      for (size_t i = 0; i < dots; i++)
      {
        float a = start + (i * bg_angle_offset);
        ImColor c = color;
        c.Value.w = ImMax(0.1f, i / (float)dots);
        window->DrawList->AddCircleFilled(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius), thickness, c, 8);
      }
    }

    void SpinnerFadeBars(const char *label, float w, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t bars = 3, bool scale = false)
    {
      float radius = (w * 0.5f) * bars;
      SPINNER_HEADER(pos, size, centre);

      ImGuiContext &g = *GImGui;
      const ImGuiStyle &style = g.Style;
      const float nextItemKoeff = 1.5f;
      const float yOffsetKoeftt = 0.8f;
      const float heightSpeed = 0.8f;

      // Render
      float start = (float)ImGui::GetTime() * speed;

      const float offset = IM_PI / bars;
      for (size_t i = 0; i < bars; i++)
      {
        float a = start + (IM_PI - i * offset);
        ImColor c = color;
        c.Value.w = ImMax(0.1f, ImSin(a * heightSpeed));
        float h = (scale ? (0.6f + 0.4f * c.Value.w) : 1.f) * size.y / 2;
        window->DrawList->AddRectFilled(ImVec2(pos.x + style.FramePadding.x + i * (w * nextItemKoeff) - w / 2, centre.y - h * yOffsetKoeftt),
                                        ImVec2(pos.x + style.FramePadding.x + i * (w * nextItemKoeff) + w / 2, centre.y + h * yOffsetKoeftt), c);
      }
    }

    void SpinnerBarsRotateFade(const char *label, float rmin, float rmax , float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t bars = 6)
    {
      float radius = rmax;
      SPINNER_HEADER(pos, size, centre);

      // Render
      float start = (float)ImGui::GetTime() * speed;
      float astart = ImFmod(start, IM_PI / bars);
      start -= astart;
      const float bg_angle_offset = IM_PI / bars;
      bars = ImMin<size_t>(bars, 32);

      for (size_t i = 0; i <= bars; i++)
      {
        float a = start + (i * bg_angle_offset);
        ImColor c = color;
        c.Value.w = ImMax(0.1f, i / (float)bars);
        window->DrawList->AddLine(ImVec2(centre.x + ImCos(a) * rmin, centre.y + ImSin(a) * rmin), ImVec2(centre.x + ImCos(a) * rmax, centre.y + ImSin(a) * rmax), c, thickness);
      }
    }

    void SpinnerBarsScaleMiddle(const char *label, float w, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t bars = 3)
    {
      float radius = (w) * bars;
      SPINNER_HEADER(pos, size, centre);

      ImGuiContext &g = *GImGui;
      const ImGuiStyle &style = g.Style;
      const float nextItemKoeff = 1.5f;
      const float yOffsetKoeftt = 0.8f;
      const float heightSpeed = 0.8f;

      // Render
      float start = (float)ImGui::GetTime() * speed;

      const float offset = IM_PI / bars;
      for (size_t i = 0; i < bars; i++)
      {
        float a = start + (IM_PI - i * offset);
        float h = (0.4f + 0.6f * ImMax(0.1f, ImSin(a * heightSpeed))) * (size.y / 2);
        window->DrawList->AddRectFilled(ImVec2(centre.x + style.FramePadding.x + i * (w * nextItemKoeff) - w / 2, centre.y - h * yOffsetKoeftt),
                                        ImVec2(centre.x + style.FramePadding.x + i * (w * nextItemKoeff) + w / 2, centre.y + h * yOffsetKoeftt), color);
        if (i == 0)
          continue;

        window->DrawList->AddRectFilled(ImVec2(centre.x + style.FramePadding.x - i * (w * nextItemKoeff) - w / 2, centre.y - h * yOffsetKoeftt),
                                        ImVec2(centre.x + style.FramePadding.x - i * (w * nextItemKoeff) + w / 2, centre.y + h * yOffsetKoeftt), color);
      }
    }

    void SpinnerAngTwin(const char *label, float radius1, float radius2, float thickness, const ImColor &color = ImColor(0xffffffff), const ImColor &bg = ImColor(0xffffff80), float speed = 2.8f, float angle = IM_PI, size_t arcs = 1)
    {
      float radius = ImMax(radius1, radius2);
      SPINNER_HEADER(pos, size, centre);

      // Render
      window->DrawList->PathClear();
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      float start = (float)ImGui::GetTime()* speed;
      const float bg_angle_offset = IM_PI * 2.f / num_segments;

      for (size_t i = 0; i <= num_segments; i++)
      {
        const float a = start + (i * bg_angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius1, centre.y + ImSin(a) * radius1));
      }
      window->DrawList->PathStroke(bg, false, thickness);

      const float angle_offset = angle / num_segments;
      for (size_t arc_num = 0; arc_num < arcs; ++arc_num)
      {
          window->DrawList->PathClear();
          float arc_start = 2 * IM_PI / arcs;
          for (size_t i = 0; i < num_segments; i++)
          {
            const float a = arc_start * arc_num + start + (i * angle_offset);
            window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius2, centre.y + ImSin(a) * radius2));
          }
          window->DrawList->PathStroke(color, false, thickness);
      }
    }

    void SpinnerArcRotation(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t arcs = 4)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) / 2;
      float start = (float)ImGui::GetTime()* speed;

      float arc_angle = 2.f * IM_PI / (float)arcs;
      const float angle_offset = arc_angle / num_segments;
      for (size_t arc_num = 0; arc_num < arcs; ++arc_num)
      {
        window->DrawList->PathClear();
        ImColor c = color;
        c.Value.w = ImMax(0.1f, arc_num / (float)arcs);
        for (size_t i = 0; i <= num_segments; i++)
        {
          const float a = start + arc_angle * arc_num + (i * angle_offset);
          window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius));
        }
        window->DrawList->PathStroke(c, false, thickness);
      }
    }

    void SpinnerArcFade(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t arcs = 4)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) / 2;
      float start = ImFmod((float)ImGui::GetTime()* speed, IM_PI * 4.f);

      float arc_angle = 2.f * IM_PI / (float)arcs;
      const float angle_offset = arc_angle / num_segments;
      for (size_t arc_num = 0; arc_num < arcs; ++arc_num)
      {
        window->DrawList->PathClear();
        for (size_t i = 0; i <= num_segments + 1; i++)
        {
          const float a = arc_angle * arc_num + (i * angle_offset) - IM_PI / 2.f - IM_PI / 4.f;
          window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius));
        }
        const float a = arc_angle * arc_num;
        ImColor c = color;
        if (start < IM_PI * 2.f) {
          c.Value.w = 0.f;
          if (start > a && start < (a + arc_angle))
          {
            c.Value.w = 1.f - (start - a) / (float)arc_angle;
          }
          else if (start < a)
          {
            c.Value.w = 1.f;
          }
          c.Value.w = ImMax(0.05f, 1.f - c.Value.w);
        } else {
          const float startk = start - IM_PI * 2.f;
          c.Value.w = 0.f;
          if (startk > a && startk < (a + arc_angle))
          {
            c.Value.w = 1.f - (startk - a) / (float)arc_angle;
          }
          else if (startk < a)
          {
            c.Value.w = 1.f;
          }
          c.Value.w = ImMax(0.05f, c.Value.w);
        }
       
        window->DrawList->PathStroke(c, false, thickness);
      }
    }

    void SpinnerFilledArcFade(const char *label, float radius, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t arcs = 4)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) / 2;
      float start = ImFmod((float)ImGui::GetTime()* speed, IM_PI * 4.f);

      float arc_angle = 2.f * IM_PI / (float)arcs;
      const float angle_offset = arc_angle / num_segments;
      for (size_t arc_num = 0; arc_num < arcs; ++arc_num)
      {
        const float b = arc_angle * arc_num - IM_PI / 2.f - IM_PI / 4.f;
        const float e = arc_angle * arc_num + arc_angle - IM_PI / 2.f - IM_PI / 4.f;
        const float a = arc_angle * arc_num;
        ImColor c = color;
        if (start < IM_PI * 2.f) {
          c.Value.w = 0.f;
          if (start > a && start < (a + arc_angle))
          {
            c.Value.w = 1.f - (start - a) / (float)arc_angle;
          }
          else if (start < a)
          {
            c.Value.w = 1.f;
          }
          c.Value.w = ImMax(0.f, 1.f - c.Value.w);
        }
        else
        {
          const float startk = start - IM_PI * 2.f;
          c.Value.w = 0.f;
          if (startk > a && startk < (a + arc_angle))
          {
            c.Value.w = 1.f - (startk - a) / (float)arc_angle;
          }
          else if (startk < a)
          {
            c.Value.w = 1.f;
          }
        }

        window->DrawList->PathClear();
        window->DrawList->PathLineTo(centre);
        for (size_t i = 0; i <= num_segments + 1; i++)
        {
          const float ar = arc_angle * arc_num + (i * angle_offset) - IM_PI / 2.f - IM_PI / 4.f;
          window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(ar) * radius, centre.y + ImSin(ar) * radius));
        }
        window->DrawList->PathFillConvex(c);
      }
    }

    void SpinnerFilledArcColor(const char *label, float radius, const ImColor &color = ImColor(0xffff0000), const ImColor &bg = ImColor(0xffffffff), float speed = 2.8f, size_t arcs = 4)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) / 2;
      float start = ImFmod((float)ImGui::GetTime()* speed, IM_PI * 2.f);

      float arc_angle = 2.f * IM_PI / (float)arcs;
      const float angle_offset = arc_angle / num_segments;

      window->DrawList->AddCircleFilled(centre, radius, bg, num_segments * 2);

      for (size_t arc_num = 0; arc_num < arcs; ++arc_num)
      {
        const float b = arc_angle * arc_num - IM_PI / 2.f;
        const float e = arc_angle * arc_num + arc_angle - IM_PI / 2.f;
        const float a = arc_angle * arc_num;

        ImColor c = color;
        c.Value.w = 0.f;
        if (start > a && start < (a + arc_angle))
        {
          c.Value.w = 1.f - (start - a) / (float)arc_angle;
        }
        else if (start < a)
        {
          c.Value.w = 1.f;
        }
        c.Value.w = ImMax(0.f, 1.f - c.Value.w);
        
        window->DrawList->PathClear();
        window->DrawList->PathLineTo(centre);
        for (size_t i = 0; i < num_segments + 1; i++)
        {
          const float ar = arc_angle * arc_num + (i * angle_offset) - IM_PI / 2.f;
          window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(ar) * radius, centre.y + ImSin(ar) * radius));
        }
        window->DrawList->PathFillConvex(c);
      }
    }

    void SpinnerTwinBall(const char *label, float radius1, float radius2, float thickness, float b_thickness, const ImColor &ball = ImColor(0xffffffff), const ImColor &bg = ImColor(0xffffff80), float speed = 2.8f, size_t balls = 2)
    {
      float radius = ImMax(radius1, radius2);
      SPINNER_HEADER(pos, size, centre);

      // Render
      window->DrawList->PathClear();
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      float start = (float)ImGui::GetTime()* speed;
      const float bg_angle_offset = IM_PI * 2.f / num_segments;

      for (size_t i = 0; i <= num_segments; i++)
      {
        const float a = start + (i * bg_angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius1, centre.y + ImSin(a) * radius1));
      }
      window->DrawList->PathStroke(bg, false, thickness);

      for (size_t b_num = 0; b_num < balls; ++b_num)
      {
        float b_start = 2 * IM_PI / balls;
        const float a = b_start * b_num + start;
        window->DrawList->AddCircleFilled(ImVec2(centre.x + ImCos(a) * radius2, centre.y + ImSin(a) * radius2), b_thickness, ball);
      }
    }

    void SpinnerBounceBall(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      ImGuiStorage* storage = window->DC.StateStorage;
      const ImGuiID vtimeId = window->GetID("##vtime");
      const ImGuiID hmaxId = window->GetID("##hmax");

      float vtime = storage->GetFloat(vtimeId, 0.f);
      float hmax = storage->GetFloat(hmaxId, 1.f);

      vtime += 0.05f;
      hmax += 0.01f;
      float maxht = ImMax(ImSin(ImFmod((float)hmax, IM_PI)), 0.7f) * radius;

      float start = ImFmod((float)ImGui::GetTime() * speed, IM_PI);

      storage->SetFloat(vtimeId, vtime);
      storage->SetFloat(hmaxId, hmax);

      window->DrawList->AddCircleFilled(ImVec2(centre.x, centre.y + radius - ImSin(start) * 2.f * maxht), thickness, color, 8);
    }

    void SpinnerIncScaleDots(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t dots = 6)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      float start = (float)ImGui::GetTime() * speed;
      float astart = ImFmod(start, IM_PI / dots);
      start -= astart;
      const float bg_angle_offset = IM_PI / dots;
      dots = min_patched(dots, 32);

      for (size_t i = 0; i <= dots; i++)
      {
        float a = start + (i * bg_angle_offset);
        float th = thickness * ImMax(0.1f, i / (float)dots);
        window->DrawList->AddCircleFilled(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius), th, color, 8);
      }
    }

    void SpinnerAngTriple(const char *label, float radius1, float radius2, float radius3, float thickness, const ImColor &c1 = ImColor(0xffffffff), const ImColor &c2 = ImColor(0xffffff80), const ImColor &c3 = ImColor(0xffffffff), float speed = 2.8f, float angle = IM_PI)
    {
      float radius = ImMax(ImMax(radius1, radius2), radius3);
      SPINNER_HEADER(pos, size, centre);

      // Render
      float start1 = (float)ImGui::GetTime() * speed;
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) * 2;
      const float angle_offset = angle / num_segments;
      window->DrawList->PathClear();
      for (size_t i = 0; i < num_segments; i++)
      {
        const float a = start1 + (i * angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius1, centre.y + ImSin(a) * radius1));
      }
      window->DrawList->PathStroke(c1, false, thickness);

      float start2 = (float)ImGui::GetTime() * 1.2f * speed;
      window->DrawList->PathClear();
      for (size_t i = 0; i < num_segments; i++)
      {
        const float a = start2 + (i * angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(-a) * radius2, centre.y + ImSin(-a) * radius2));
      }
      window->DrawList->PathStroke(c2, false, thickness);

      float start3 = (float)ImGui::GetTime() * 0.9f * speed;
      window->DrawList->PathClear();
      for (size_t i = 0; i < num_segments; i++)
      {
        const float a = start3 + (i * angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius3, centre.y + ImSin(a) * radius3));
      }
      window->DrawList->PathStroke(c3, false, thickness);
    }

    void SpinnerAngEclipse(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, float angle = IM_PI)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      float start = (float)ImGui::GetTime()* speed;

      const float angle_offset = angle / num_segments;
      const float th = thickness / num_segments;
      for (size_t i = 0; i < num_segments; i++)
      {
        const float a = start + (i * angle_offset);
        const float a1 = start + ((i+1) * angle_offset);
        window->DrawList->AddLine(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius),
                                  ImVec2(centre.x + ImCos(a1) * radius, centre.y + ImSin(a1) * radius),
                                  color,
                                  th * i);
      }
    }

    void SpinnerIngYang(const char *label, float radius, float thickness, bool reverse, float yang_detlta_r, const ImColor &colorI = ImColor(0xffffffff), const ImColor &colorY = ImColor(0xffffffff), float speed = 2.8f, float angle = IM_PI * 0.7f)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      float startI = (float)ImGui::GetTime() * speed;
      float startY = (float)ImGui::GetTime() * (speed + (yang_detlta_r > 0.f ? ImClamp(yang_detlta_r * 0.5f, 0.5f, 2.f) : 0.f));

      const float angle_offset = angle / num_segments;
      const float th = thickness / num_segments;
      for (size_t i = 0; i < num_segments; i++)
      {
        const float a = startI + (i * angle_offset);
        const float a1 = startI + ((i + 1) * angle_offset);
        window->DrawList->AddLine(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius),
                                  ImVec2(centre.x + ImCos(a1) * radius, centre.y + ImSin(a1) * radius),
                                  colorI,
                                  th * i);
      }
      const float ai_end = startI + (num_segments * angle_offset);
      ImVec2 circle_i_center{centre.x + ImCos(ai_end) * radius, centre.y + ImSin(ai_end) * radius};
      window->DrawList->AddCircleFilled(circle_i_center, thickness / 2.f, colorI, num_segments);

      const float rv = reverse ? -1.f : 1.f;
      const float yang_radius = (radius - yang_detlta_r);
      for (size_t i = 0; i < num_segments; i++)
      {
        const float a = startY + IM_PI + (i * angle_offset);
        const float a1 = startY + IM_PI + ((i+1) * angle_offset);
        window->DrawList->AddLine(ImVec2(centre.x + ImCos(a * rv) * yang_radius, centre.y + ImSin(a * rv) * yang_radius),
                                  ImVec2(centre.x + ImCos(a1 * rv) * yang_radius, centre.y + ImSin(a1 * rv) * yang_radius),
                                  colorY,
                                  th * i);
      }
      const float ay_end = startY + IM_PI + (num_segments * angle_offset);
      ImVec2 circle_y_center{centre.x + ImCos(ay_end * rv) * yang_radius, centre.y + ImSin(ay_end * rv) * yang_radius};
      window->DrawList->AddCircleFilled(circle_y_center, thickness / 2.f, colorY, num_segments);
    }


    void SpinnerGooeyBalls(const char *label, float radius, const ImColor &color, float speed)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      const float start = ImFmod((float)ImGui::GetTime() * speed, IM_PI);

      const float radius1 = (0.3f + 0.3f * ImSin(start)) * radius;
      const float radius2 = radius - radius1;

      window->DrawList->AddCircleFilled(ImVec2(centre.x - radius + radius1, centre.y), radius1, color, num_segments);
      window->DrawList->AddCircleFilled(ImVec2(centre.x - radius + radius1 * 1.2f + radius2, centre.y), radius2, color, num_segments);
    }

    void SpinnerRotateGooeyBalls(const char *label, float radius, float thickness, const ImColor &color, float speed, int balls)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      const float start = ImFmod((float)ImGui::GetTime(), IM_PI);
      const float rstart = ImFmod((float)ImGui::GetTime() * speed, IM_PI * 2);

      const float radius1 = (0.2f + 0.3f * ImSin(start)) * radius;
      const float angle_offset = IM_PI * 2.f / balls;

      for (int i = 0; i <= balls; i++)
      {
        const float a = rstart + (i * angle_offset);
        window->DrawList->AddCircleFilled(ImVec2(centre.x + ImCos(a) * radius1, centre.y + ImSin(a) * radius1), thickness, color, num_segments);
      }
    }

    void SpinnerMoonLine(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), const ImColor &bg = ImColor(0xff000000), float speed = 2.8f, float angle = IM_PI)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      float start = (float)ImGui::GetTime()* speed;

      const float angle_offset = (angle * 0.5f) / num_segments;
      const float th = thickness / num_segments;

      window->DrawList->AddCircleFilled(centre, radius, bg, num_segments);

      auto draw_gradient = [&] (auto b, auto e, auto th) {
        for (size_t i = 0; i < num_segments; i++)
        {
          window->DrawList->AddLine(ImVec2(centre.x + ImCos(start + b(i)) * radius, centre.y + ImSin(start + b(i)) * radius),
                                    ImVec2(centre.x + ImCos(start + e(i)) * radius, centre.y + ImSin(start + e(i)) * radius),
                                    color,
                                    th(i));
        }

      };

      draw_gradient([&] (auto i) { return (num_segments + i) * angle_offset; },
                    [&] (auto i) { return (num_segments + i + 1) * angle_offset; },
                    [&] (auto i) { return thickness - th * i; });

      draw_gradient([&] (auto i) { return (i) * angle_offset; },
                    [&] (auto i) { return (i + 1) * angle_offset; },
                    [&] (auto i) { return th * i; });

      draw_gradient([&] (auto i) { return (num_segments + i) * angle_offset; },
                    [&] (auto i) { return (num_segments + i + 1) * angle_offset; },
                    [&] (auto i) { return thickness - th * i; });

      const float b_angle_offset = (2.f * IM_PI - angle) / num_segments; 
      draw_gradient([&] (auto i) { return num_segments * angle_offset * 2.f + (i * b_angle_offset); },
                    [&] (auto i) { return num_segments * angle_offset * 2.f + ((i + 1) * b_angle_offset); },
                    [] (auto) { return 1.f; });
    }

    void SpinnerCircleDrop(const char *label, float radius, float thickness, float thickness_drop, const ImColor &color = ImColor(0xffffffff), const ImColor &bg = ImColor(0xffffff80), float speed = 2.8f, float angle = IM_PI)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      window->DrawList->PathClear();
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      float start = (float)ImGui::GetTime() * speed;
      const float bg_angle_offset = IM_PI * 2.f / num_segments;

      const float angle_offset = angle / num_segments;
      const float th = thickness_drop / num_segments;
      const float drop_radius_th = thickness_drop / num_segments;
      for (size_t i = 0; i < num_segments; i++)
      {
        const float a = start + (i * angle_offset);
        const float a1 = start + ((i + 1) * angle_offset);
        const float s_drop_radius = radius - thickness / 2.f - (drop_radius_th * i);
        window->DrawList->AddLine(ImVec2(centre.x + ImCos(a) * s_drop_radius, centre.y + ImSin(a) * s_drop_radius),
                                  ImVec2(centre.x + ImCos(a1) * s_drop_radius, centre.y + ImSin(a1) * s_drop_radius),
                                  color,
                                  th * 2.f * i);
      }
      const float ai_end = start + (num_segments * angle_offset);
      const float f_drop_radius = radius - thickness / 2.f - thickness_drop;
      ImVec2 circle_i_center{centre.x + ImCos(ai_end) * f_drop_radius, centre.y + ImSin(ai_end) * f_drop_radius};
      window->DrawList->AddCircleFilled(circle_i_center, thickness_drop, color, num_segments);

      for (size_t i = 0; i <= num_segments; i++)
      {
        const float a = (i * bg_angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius));
      }
      window->DrawList->PathStroke(bg, false, thickness);
    }

    void SpinnerSurroundedIndicator(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), const ImColor &bg = ImColor(0xffffff80), float speed = 2.8f)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      window->DrawList->PathClear();
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);

      ImColor c = color;
      float lerp_koeff = (ImSin((float)ImGui::GetTime() * speed) + 1.f) * 0.5f;
      c.Value.w = ImMax(0.1f, ImMin(lerp_koeff, 1.f));
      window->DrawList->AddCircleFilled(centre, thickness, bg, num_segments);
      window->DrawList->AddCircleFilled(centre, thickness, c, num_segments);

      auto PathArc = [&] {
        const float bg_angle_offset = IM_PI * 2.f / num_segments;
        for (size_t i = 0; i <= num_segments; i++) {
          window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(i * bg_angle_offset) * radius, centre.y + ImSin(i * bg_angle_offset) * radius));
        }
      };
      PathArc();
      window->DrawList->PathStroke(bg, false, thickness);

      PathArc();
      lerp_koeff = (ImSin((float)ImGui::GetTime() * speed * 1.6f) + 1.f) * 0.5f;
      c.Value.w = 1.f - ImMax(0.1f, ImMin(lerp_koeff, 1.f));;
      window->DrawList->PathStroke(c, false, thickness);
    }

    void SpinnerTrianglesSeletor(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), const ImColor &bg = ImColor(0xffffff80), float speed = 2.8f, size_t bars = 8)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      window->DrawList->PathClear();
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);

      ImColor c = color;
      float lerp_koeff = (ImSin((float)ImGui::GetTime() * speed) + 1.f) * 0.5f;
      c.Value.w = ImMax(0.1f, ImMin(lerp_koeff, 1.f));
      float dr = radius - thickness - 3;
      window->DrawList->AddCircleFilled(centre, dr, bg, num_segments);
      window->DrawList->AddCircleFilled(centre, dr, c, num_segments);

      // Render
      float start = (float)ImGui::GetTime() * speed;
      float astart = ImFmod(start, IM_PI * 2 / bars);
      start -= astart;
      const float angle_offset = IM_PI * 2 / bars;
      const float angle_offset_t = angle_offset * 0.3f;
      bars = ImMin<size_t>(bars, 32);

      const float rmin = radius - thickness;
      auto get_points = [&] (auto left, auto right) -> std::array<ImVec2, 4> {
        return {
          ImVec2(centre.x + ImCos(left) * rmin, centre.y + ImSin(left) * rmin),
          ImVec2(centre.x + ImCos(left) * radius, centre.y + ImSin(left) * radius),
          ImVec2(centre.x + ImCos(right) * radius, centre.y + ImSin(right) * radius),
          ImVec2(centre.x + ImCos(right) * rmin, centre.y + ImSin(right) * rmin)
        };
      };

      auto draw_sectors = [&] (auto s, auto color_func) {
        for (size_t i = 0; i <= bars; i++) {
          float left = s + (i * angle_offset) - angle_offset_t;
          float right = s + (i * angle_offset) + angle_offset_t;
          auto points = get_points(left, right);
          window->DrawList->AddConvexPolyFilled(points.data(), 4, color_func(i));
        }
      };

      draw_sectors(0, [&] (auto) { ImColor rc = bg; rc.Value.w = 0.1f; return rc; });
      draw_sectors(start, [&] (auto i) { ImColor rc = bg; rc.Value.w = (i / (float)bars) - 0.5f; return rc; });
    }

    template<SpinnerTypeT Type, typename... Args>
    void Spinner(const char *label, const Args&... args)
    {
      struct SpinnerDraw { SpinnerTypeT type; void (*func)(const char *, const detail::SpinnerConfig &); }

      spinner_draw_funcs[e_st_count] = {
        { e_st_rainbow, [] (const char *label, const detail::SpinnerConfig &c) { SpinnerRainbow(label, c.m_Radius, c.m_Thickness, c.m_Color, c.m_Speed); } },
        { e_st_angle, [] (const char *label, const detail::SpinnerConfig &c) { SpinnerAng(label, c.m_Radius, c.m_Thickness, c.m_Color, c.m_BgColor, c.m_Speed, c.m_Angle); } },
        { e_st_dots, [] (const char *label, const detail::SpinnerConfig &c) { SpinnerDots(label, c.m_FloatPtr, c.m_Radius, c.m_Thickness, c.m_Color, c.m_Speed, c.m_Dots, c.m_MiddleDots, c.m_MinThickness); } },
        { e_st_ang, [] (const char *label, const detail::SpinnerConfig &c) { SpinnerAng(label, c.m_Radius, c.m_Thickness, c.m_Color, c.m_BgColor, c.m_Speed, c.m_Angle); } }
      };

      detail::SpinnerConfig config(SpinnerType{Type}, args...);
      if (config.m_SpinnerType < sizeof(spinner_draw_funcs))
      {
        spinner_draw_funcs[config.m_SpinnerType].func(label, config);
      }
    }

    void SpinnerFlowingGradient(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), const ImColor &bg = ImColor(0xff000000), float speed = 2.8f, float angle = IM_PI)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius);
      float start = (float)ImGui::GetTime()* speed;

      const float angle_offset = (angle * 0.5f) / num_segments;
      const float bg_angle_offset = (IM_PI * 2.f) / num_segments;
      const float th = thickness / num_segments;

      for (size_t i = 0; i <= num_segments; i++)
      {
        const float a = (i * bg_angle_offset);
        window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a) * radius, centre.y + ImSin(a) * radius));
      }
      window->DrawList->PathStroke(bg, false, thickness);

      auto draw_gradient = [&] (auto b, auto e, auto c) {
        for (size_t i = 0; i < num_segments; i++)
        {
          window->DrawList->AddLine(ImVec2(centre.x + ImCos(start + b(i)) * radius, centre.y + ImSin(start + b(i)) * radius),
                                    ImVec2(centre.x + ImCos(start + e(i)) * radius, centre.y + ImSin(start + e(i)) * radius),
                                    c(i),
                                    thickness);
        }
      };

      draw_gradient([&] (auto i) { return (i) * angle_offset; },
                    [&] (auto i) { return (i + 1) * angle_offset; },
                    [&] (auto i) { ImColor rc = color; rc.Value.w = (i / (float)num_segments); return rc; });

      draw_gradient([&] (auto i) { return (num_segments + i) * angle_offset; },
                    [&] (auto i) { return (num_segments + i + 1) * angle_offset; },
                    [&] (auto i) { ImColor rc = color; rc.Value.w = 1.f - (i / (float)num_segments); return rc; });
    }

    void SpinnerRotateSegments(const char *label, float radius, float thickness, const ImColor &color = ImColor(0xffffffff), float speed = 2.8f, size_t arcs = 4, size_t layers = 1)
    {
      SPINNER_HEADER(pos, size, centre);

      // Render
      const size_t num_segments = window->DrawList->_CalcCircleAutoSegmentCount(radius) / 2;
      float start = (float)ImGui::GetTime()* speed;

      float arc_angle = 2.f * IM_PI / (float)arcs;
      const float angle_offset = arc_angle / num_segments;
      float r = radius;
      float reverse = 1.f;
      for (size_t layer = 0; layer < layers; layer++)
      {
        for (size_t arc_num = 0; arc_num < arcs; ++arc_num)
        {
          window->DrawList->PathClear();
          for (size_t i = 2; i <= num_segments - 2; i++)
          {
            const float a = start * (1 + 0.1 * layer) + arc_angle * arc_num + (i * angle_offset);
            window->DrawList->PathLineTo(ImVec2(centre.x + ImCos(a * reverse) * r, centre.y + ImSin(a * reverse) * r));
          }
          window->DrawList->PathStroke(color, false, thickness);
        }

        r -= (thickness + 1);
        reverse *= -1.f;
      }
    }

#ifdef IMSPINNER_DEMO
    void demoSpinners() {

      static int hue = 0;
      static float nextdot = 0, nextdot2;
      
      nextdot -= 0.07f;

      static float velocity = 1.f;
      ImGui::SliderFloat("Speed", &velocity, 0.0f, 10.0f, "velocity = %.3f");

      ImSpinner::Spinner<e_st_rainbow>("Spinner", Radius{16.f}, Thickness{2.f}, Color{ImColor::HSV(++hue * 0.005f, 0.8f, 0.8f)}, Speed{8 * velocity}); ImGui::SameLine();
      ImSpinner::Spinner<e_st_angle>("SpinnerAng", Radius{16.f}, Thickness{2.f}, Color{ImColor(255, 255, 255)}, BgColor{ImColor(255, 255, 255, 128)}, Speed{8 * velocity}, Angle{IM_PI}); ImGui::SameLine();
      ImSpinner::Spinner<e_st_dots>("SpinnerDots", FloatPtr{&nextdot}, Radius{16}, Thickness{4}, Color{ImColor(255, 255, 255)}, Speed{1 * velocity}, Dots{12}, MiddleDots{6}, MinThickness{-1.f}); ImGui::SameLine();
      ImSpinner::Spinner<e_st_ang>("SpinnerAngNoBg", Radius{16.f}, Thickness{2.f}, Color{ImColor(255, 255, 255)}, BgColor{ImColor(255, 255, 255, 0)}, Speed{6 * velocity}, Angle{IM_PI}); ImGui::SameLine();
      ImSpinner::Spinner<e_st_ang>("SpinnerAng270", Radius{16.f}, Thickness{2.f}, Color{ImColor(255, 255, 255)}, BgColor{ImColor(255, 255, 255, 128)}, Speed{6 * velocity}, Angle{270.f / 360.f * 2 * IM_PI});

      ImGui::SameLine();
      ImSpinner::SpinnerAng("SpinnerAng270NoBg", 16, 6, ImColor(255, 255, 255), ImColor(255, 255, 255, 0), 6 * velocity, 270.f / 360.f * 2 * IM_PI );

      ImGui::SameLine();
      ImSpinner::SpinnerVDots("SpinnerVDots", 16, 4, ImColor(255, 255, 255), 2.7f * velocity);

      ImGui::SameLine(); ImGui::Dummy({10, 0}); ImGui::SameLine();
      ImSpinner::SpinnerBounceBall("SpinnerBounceBall", 16, 6, ImColor(255, 255, 255), 4 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerAngEclipse("SpinnerAng", 16, 5, ImColor(255, 255, 255), 6 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerIngYang("SpinnerIngYang", 16, 5, false, 0, ImColor(255, 255, 255), ImColor(255, 0, 0), 4 * velocity, IM_PI * 0.8f);

      // Next Line
      ImSpinner::SpinnerBounceDots("SpinnerBounceDots", 6, ImColor(255, 255, 255), 6 * velocity, 3);

      ImGui::SameLine();
      ImSpinner::SpinnerFadeDots("SpinnerFadeDots", 6, ImColor(255, 255, 255), 8 * velocity, 3);

      ImGui::SameLine();
      ImSpinner::SpinnerScaleDots("SpinnerMovingDots", 6, ImColor(255, 255, 255), 7 * velocity, 3);

      ImGui::SameLine();
      ImSpinner::SpinnerMovingDots("SpinnerMovingDots", 6, ImColor(255, 255, 255), 30 * velocity, 3);

      ImGui::SameLine(); ImGui::Dummy({10, 0}); ImGui::SameLine();
      ImSpinner::SpinnerRotateDots("SpinnerRotateDots", 16, 6, ImColor(255, 255, 255), 4 * velocity, 2);

      ImGui::SameLine(); ImGui::Dummy({10, 0}); ImGui::SameLine();
      ImSpinner::SpinnerTwinAng("SpinnerTwinAng", 16, 16, 6, ImColor(255, 255, 255), ImColor(255, 0, 0), 4 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerClock("SpinnerClock", 16, 2, ImColor(255, 0, 0), ImColor(255, 255, 255), 4 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerIngYang("SpinnerIngYangR", 16, 5, true, 0.1f, ImColor(255, 255, 255), ImColor(255, 0, 0), 4 * velocity, IM_PI * 0.8f);

      // next line
      ImSpinner::SpinnerTwinAng180("SpinnerTwinAng", 16, 12, 4, ImColor(255, 255, 255), ImColor(255, 0, 0), 4 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerTwinAng360("SpinnerTwinAng360", 16, 11, 4, ImColor(255, 255, 255), ImColor(255, 0, 0), 4 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerIncDots("SpinnerIncDots", 16, 4, ImColor(255, 255, 255), 5.6f, 6);

      ImGui::SameLine();
      nextdot2 -= 0.2f * velocity;
      ImSpinner::SpinnerDots("SpinnerDots", &nextdot2, 16, 4, ImColor(255, 255, 255), 0.3f, 12, 6, 0.f);

      ImGui::SameLine();
      ImSpinner::SpinnerIncScaleDots("SpinnerIncScaleDots", 16, 4, ImColor(255, 255, 255), 6.6f, 6);

      ImGui::SameLine();
      ImSpinner::SpinnerAng("SpinnerAng90", 16, 6, ImColor(255, 255, 255), ImColor(255, 255, 255, 128), 8.f * velocity, IM_PI / 2.f);

      ImGui::SameLine();
      ImSpinner::SpinnerAng("SpinnerAng90", 16, 6, ImColor(255, 255, 255), ImColor(255, 255, 255, 0), 8.5f * velocity, IM_PI / 2.f);

      ImGui::SameLine();
      ImSpinner::SpinnerFadeBars("SpinnerFadeBars", 10, ImColor(255, 255, 255), 4.8f * velocity, 3);

      ImGui::SameLine(); ImGui::Dummy({10, 0}); ImGui::SameLine();
      ImSpinner::SpinnerPulsar("SpinnerPulsar", 16, 2, ImColor(255, 255, 255), 1 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerIngYang("SpinnerIngYangR2", 16, 5, true, 3.f, ImColor(255, 255, 255), ImColor(255, 0, 0), 4 * velocity, IM_PI * 0.8f);

      // Next line
      ImSpinner::SpinnerBarsRotateFade("SpinnerBarsRotateFade", 8, 18, 4, ImColor(255, 255, 255), 7.6f, 6);

      ImGui::SameLine();
      ImSpinner::SpinnerFadeBars("SpinnerFadeScaleBars", 10, ImColor(255, 255, 255), 6.8f, 3, true);

      ImGui::SameLine(); ImGui::Dummy({10, 0}); ImGui::SameLine();
      ImSpinner::SpinnerBarsScaleMiddle("SpinnerBarsScaleMiddle", 6, ImColor(255, 255, 255), 8.8f, 3);

      ImGui::SameLine(); ImGui::Dummy({10, 0}); ImGui::SameLine();
      ImSpinner::SpinnerAngTwin("SpinnerAngTwin1", 16, 13, 2, ImColor(255, 0, 0), ImColor(255, 255, 255), 6 * velocity, IM_PI / 2.f);

      ImGui::SameLine();
      ImSpinner::SpinnerAngTwin("SpinnerAngTwin2", 13, 16, 2, ImColor(255, 0, 0), ImColor(255, 255, 255), 6 * velocity, IM_PI / 2.f);

      ImGui::SameLine();
      ImSpinner::SpinnerAngTwin("SpinnerAngTwin3", 13, 16, 2, ImColor(255, 0, 0), ImColor(255, 255, 255), 6 * velocity, IM_PI / 2.f, 2);

      ImGui::SameLine();
      ImSpinner::SpinnerAngTwin("SpinnerAngTwin4", 16, 13, 2, ImColor(255, 0, 0), ImColor(255, 255, 255), 6 * velocity, IM_PI / 2.f, 2);

      ImGui::SameLine(); 
      ImSpinner::SpinnerTwinPulsar("SpinnerTwinPulsar", 16, 2, ImColor(255, 255, 255), 0.5f * velocity, 2);

      ImGui::SameLine();
      ImSpinner::SpinnerAngTwin("SpinnerAngTwin4", 14, 13, 3, ImColor(255, 0, 0), ImColor(0, 0, 0, 0), 5 * velocity, IM_PI / 1.5f, 2);

      // next line
      ImSpinner::SpinnerTwinBall("SpinnerTwinBall", 16, 11, 2, 2.5f, ImColor(255, 0, 0), ImColor(255, 255, 255), 6 * velocity, 2);

      ImGui::SameLine();
      ImSpinner::SpinnerTwinBall("SpinnerTwinBall2", 15, 19, 2, 2.f, ImColor(255, 0, 0), ImColor(255, 255, 255), 6 * velocity, 3);

      ImGui::SameLine();
      ImSpinner::SpinnerTwinBall("SpinnerTwinBall2", 16, 16, 2, 5.f, ImColor(255, 0, 0), ImColor(255, 255, 255), 5 * velocity, 1);

      ImGui::SameLine();
      ImSpinner::SpinnerAngTriple("SpinnerAngTriple", 16, 13, 10, 1.3f, ImColor(255, 255, 255), ImColor(255, 0, 0), ImColor(255, 255, 255), 5 * velocity, 1.5f * IM_PI);

      ImGui::SameLine();
      ImSpinner::SpinnerIncFullDots("SpinnerIncFullDots", 16, 4, ImColor(255, 255, 255), 5.6f, 4);

      ImGui::SameLine();
      ImSpinner::SpinnerGooeyBalls("SpinnerGooeyBalls", 16, ImColor(255, 255, 255), 2.f);

      ImGui::SameLine();
      ImSpinner::SpinnerRotateGooeyBalls("SpinnerRotateGooeyBalls2", 16, 5, ImColor(255, 255, 255), 6.f, 2);

      ImGui::SameLine();
      ImSpinner::SpinnerRotateGooeyBalls("SpinnerRotateGooeyBalls3", 16, 5, ImColor(255, 255, 255), 6.f, 3);

      ImGui::SameLine();
      ImSpinner::SpinnerMoonLine("SpinnerMoonLine", 16, 3, ImColor(200, 80, 0), ImColor(80, 80, 80), 5 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerArcRotation("SpinnerArcRotation", 13, 5, ImColor(255, 255, 255), 3 * velocity, 4);

      // Next line
      ImSpinner::SpinnerArcFade("SpinnerArcFade", 13, 5, ImColor(255, 255, 255), 3 * velocity, 4);

      ImGui::SameLine();
      ImSpinner::SpinnerFilling("SpinnerFilling", 16, 6, ImColor(255, 255, 255), ImColor(255, 0, 0), 4 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerTopup("SpinnerTopup", 16, 12, ImColor(255, 0, 0), ImColor(80, 80, 80), ImColor(255, 255, 255), 1 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerFadePulsar("SpinnerFadePulsar", 16, ImColor(255, 255, 255), 1.5f * velocity, 1);

      ImGui::SameLine();
      ImSpinner::SpinnerFadePulsar("SpinnerFadePulsar2", 16, ImColor(255, 255, 255), 0.9f * velocity, 2);

      ImGui::SameLine();
      ImSpinner::SpinnerPulsar("SpinnerPulsar", 16, 2, ImColor(255, 255, 255), 1 * velocity, false);

      ImGui::SameLine();
      ImSpinner::SpinnerDoubleFadePulsar("SpinnerDoubleFadePulsar", 16, 2, ImColor(255, 255, 255), 2 * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerFilledArcFade("SpinnerFilledArcFade", 16, ImColor(255, 255, 255), 4 * velocity, 4);

      ImGui::SameLine();
      ImSpinner::SpinnerFilledArcFade("SpinnerFilledArcFade6", 16, ImColor(255, 255, 255), 6 * velocity, 6);

      ImGui::SameLine();
      ImSpinner::SpinnerFilledArcFade("SpinnerFilledArcFade6", 16, ImColor(255, 255, 255), 8 * velocity, 12);

      ImGui::SameLine();
      ImSpinner::SpinnerFilledArcColor("SpinnerFilledArcColor", 16, ImColor(255, 0, 0), ImColor(255, 255, 255), 2.8f * velocity, 4);

      // Next line
      ImSpinner::SpinnerCircleDrop("SpinnerCircleDrop", 16, 1.5f, 4.f, ImColor(255, 0, 0), ImColor(255, 255, 255), 2.8f * velocity, IM_PI);

      ImGui::SameLine();
      ImSpinner::SpinnerSurroundedIndicator("SpinnerSurroundedIndicator", 16, 5, ImColor(0, 0, 0), ImColor(255, 255, 255), 7.8f * velocity);

      ImGui::SameLine();
      ImSpinner::SpinnerTrianglesSeletor("SpinnerTrianglesSeletor", 16, 8, ImColor(0, 0, 0), ImColor(255, 255, 255), 4.8f * velocity, 8);

      ImGui::SameLine();
      ImSpinner::SpinnerFlowingGradient("SpinnerFlowingFradient", 16, 6, ImColor(200, 80, 0), ImColor(80, 80, 80), 5 * velocity, IM_PI * 2.f);

      ImGui::SameLine();
      ImSpinner::SpinnerRotateSegments("SpinnerRotateSegments", 16, 4, ImColor(255, 255, 255), 3 * velocity, 4);

      ImGui::SameLine();
      ImSpinner::SpinnerRotateSegments("SpinnerRotateSegments2", 16, 3, ImColor(255, 255, 255), 2.4 * velocity, 4, 2);

      ImGui::SameLine();
      ImSpinner::SpinnerRotateSegments("SpinnerRotateSegments3", 16, 2, ImColor(255, 255, 255), 2.1 * velocity, 4, 3);
    }
#endif // IMSPINNER_DEMO
}

#endif // _IMSPINNER_H_