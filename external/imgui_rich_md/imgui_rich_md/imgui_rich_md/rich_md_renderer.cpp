/*
 * imgui_md: Markdown for Dear ImGui using MD4C
 * (https://github.com/mekhontsev/imgui_md)
 *
 * Copyright (c) 2021 Dmitry Mekhontsev
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

#include "rich_md_renderer.h"

#include <cassert>
#include <cmath>

namespace RichMd
{


// Small vertical gap between markdown blocks.
// Unlike ImGui::NewLine() which adds a full FontSize (widget-oriented),
// this adds a fraction of FontSize for tighter text layout.
static void add_block_gap(float gap_em)
{
	ImGui::Dummy(ImVec2(0.0f, ImGui::GetFontSize() * gap_em));
}

// A color of the style, or its automatic value
static ImVec4 resolve_color(const ImVec4& color, const ImVec4& automatic)
{
	return (color.w < 0.0f) ? automatic : color;
}


Renderer::Renderer()
{
	m_md.abi_version = 0;

	m_md.flags = MD_FLAG_TABLES | MD_FLAG_UNDERLINE | MD_FLAG_STRIKETHROUGH | MD_FLAG_TASKLISTS;

	m_md.enter_block = [](MD_BLOCKTYPE t, void* d, void* u) {
		return ((Renderer*)u)->block(t, d, true);
	};

	m_md.leave_block = [](MD_BLOCKTYPE t, void* d, void* u) {
		return ((Renderer*)u)->block(t, d, false);
	};

	m_md.enter_span = [](MD_SPANTYPE t, void* d, void* u) {
		return ((Renderer*)u)->span(t, d, true);
	};

	m_md.leave_span = [](MD_SPANTYPE t, void* d, void* u) {
		return ((Renderer*)u)->span(t, d, false);
	};

	m_md.text = [](MD_TEXTTYPE t, const MD_CHAR* text, MD_SIZE size, void* u) {
		return ((Renderer*)u)->text(t, text, text + size);
	};

	m_md.debug_log = nullptr;

	m_md.syntax = nullptr;
}

void Renderer::BLOCK_UL(const MD_BLOCK_UL_DETAIL* d, bool e)
{
	if (e) {
		m_list_stack.push_back(list_info{ 0, d->mark, false, true });
	} else {
		m_list_stack.pop_back();
	}
}

void Renderer::BLOCK_OL(const MD_BLOCK_OL_DETAIL* d, bool e)
{
	if (e) {
		m_list_stack.push_back(list_info{ d->start, d->mark_delimiter, true, true });
	} else {
		m_list_stack.pop_back();
	}
}

void Renderer::BLOCK_LI(const MD_BLOCK_LI_DETAIL* d, bool e)
{
	if (e) {
		// Skip the per-item gap on the first LI of a top-level list:
		// the parent UL/OL's centralized enter-gap already provided
		// one inter-block gap, and emitting another would make
		// P->list transitions visibly larger than list->P. For nested
		// lists the centralized gap was suppressed (we are inside a
		// list), so we still need this gap to break onto a new line.
		bool is_first = m_list_stack.back().first_item_pending;
		m_list_stack.back().first_item_pending = false;
		bool is_top_level = (m_list_stack.size() == 1);
		if (!(is_first && is_top_level))
			add_block_gap(style.blockGap);

		list_info& nfo = m_list_stack.back();
		if (d && d->is_task) {
			render_task_marker(d->task_mark == 'x' || d->task_mark == 'X');
			ImGui::SameLine();
			if (nfo.is_ol)
				++nfo.cur_ol;
		} else if (nfo.is_ol) {
			ImGui::Text("%d%c", nfo.cur_ol++, nfo.delim);
			ImGui::SameLine();
		} else {
			if (nfo.delim == '*') {
				float cx = ImGui::GetCursorPosX();
				cx -= ImGui::GetStyle().FramePadding.x * 2;
				ImGui::SetCursorPosX(cx);
				ImGui::Bullet();
			} else {
				ImGui::Text("%c", nfo.delim);
				ImGui::SameLine();
			}
		}

		ImGui::Indent();
	} else {
		ImGui::Unindent();
	}
}

void Renderer::render_task_marker(bool checked)
{
	// Draw a small bordered square, with a check mark if `checked`.
	// Uses the current font size to scale, stays aligned with the text baseline.
	float h = ImGui::GetFontSize();
	float sz = h * 0.75f;
	ImVec2 cursor = ImGui::GetCursorScreenPos();
	float y_center = cursor.y + h * 0.5f;
	ImVec2 tl(cursor.x, y_center - sz * 0.5f);
	ImVec2 br(cursor.x + sz, y_center + sz * 0.5f);
	ImDrawList* dl = ImGui::GetWindowDrawList();
	ImU32 border = ImGui::GetColorU32(ImGuiCol_Text);
	float rounding = sz * 0.15f;
	float thickness = (sz / 12.0f > 1.0f) ? (sz / 12.0f) : 1.0f;
#if IMGUI_VERSION_NUM < 19276
	dl->AddRect(tl, br, border, rounding, 0, thickness);
#else
	dl->AddRect(tl, br, border, rounding, thickness);
#endif
	if (checked) {
		ImU32 mark = ImGui::GetColorU32(ImGuiCol_CheckMark);
		float pad = sz * 0.22f;
		ImVec2 a(tl.x + pad, tl.y + sz * 0.55f);
		ImVec2 b(tl.x + sz * 0.45f, br.y - pad);
		ImVec2 c(br.x - pad, tl.y + pad);
		float check_thick = (sz / 8.0f > 1.5f) ? (sz / 8.0f) : 1.5f;
		dl->AddLine(a, b, mark, check_thick);
		dl->AddLine(b, c, mark, check_thick);
	}
	// Reserve horizontal space; the caller issues SameLine() after.
	ImGui::Dummy(ImVec2(sz, h));
}

void Renderer::BLOCK_HR(bool e)
{
	if (!e) {
		ImGui::Separator();
	}
}

void Renderer::BLOCK_H(const MD_BLOCK_H_DETAIL* d, bool e)
{
	if (e) {
		m_hlevel = d->level;
		m_heading_text.clear();
	} else {
		m_hlevel = 0;
	}

	set_font(e);

	if (!e) {
		if (d->level <= 2) {
			// Small gap between heading text and the underline separator.
			add_block_gap(style.blockGap);
			ImGui::Separator();
		}
		heading((int)d->level, m_heading_text);
	}
}

void Renderer::heading(int, const std::string&)
{
}

void Renderer::BLOCK_DOC(bool)
{

}

// The same color is used for the admonition label and for the quote's left bar
ImVec4 Renderer::admonition_color(AdmonitionKind kind) const
{
	if (kind == AdmonitionKind::None)
		return ImGui::GetStyle().Colors[ImGuiCol_TextDisabled];
	return style.admonitionColors[(int)kind - 1];
}

static const char* admonition_label(Renderer::AdmonitionKind k)
{
	switch (k) {
	case Renderer::AdmonitionKind::Note:      return "NOTE";
	case Renderer::AdmonitionKind::Tip:       return "TIP";
	case Renderer::AdmonitionKind::Important: return "IMPORTANT";
	case Renderer::AdmonitionKind::Warning:   return "WARNING";
	case Renderer::AdmonitionKind::Caution:   return "CAUTION";
	default: return "";
	}
}

void Renderer::BLOCK_QUOTE(bool e)
{
	if (e) {
		m_quote_depth++;
		ImGui::Indent();
		// The quote frame provides the inter-block gap before its first child,
		// so suppress the dispatcher's gap for that first child. The flag is
		// cleared by the first child's dispatch, so later children still get
		// normal inter-block gaps.
		m_skip_next_block_gap = true;
		// Remember the indented column (X, Y) at quote entry, so we can draw
		// the vertical bar on the left at exit — by then the cursor has
		// moved to the end of the last rendered word.
		m_quote_start.push_back(ImGui::GetCursorScreenPos());
		// Arm admonition scan for the first text event inside this quote.
		m_admonition_scan_pending = true;
		m_admonition_kind = AdmonitionKind::None;
	} else {
		// Draw a vertical bar on the left side of the quote
		if (!m_quote_start.empty()) {
			float start_y = m_quote_start.back().y;
			float indented_x = m_quote_start.back().x;
			m_quote_start.pop_back();
			// cursor.y at exit is the TOP of the last rendered line
			// (render_text() ends with SameLine(0, 0)), so extend by one
			// line height to cover that last line.
			float end_y = ImGui::GetCursorScreenPos().y + ImGui::GetTextLineHeight();
			float bar_x = indented_x - ImGui::GetStyle().IndentSpacing * 0.5f;
			bool is_admonition = (m_admonition_kind != AdmonitionKind::None);
			float thickness = is_admonition ? style.admonitionBarThickness : style.quoteBarThickness;
			ImColor bar_color = is_admonition
				? ImColor(admonition_color(m_admonition_kind))
				: ImColor(resolve_color(style.quoteBar, ImGui::GetStyle().Colors[ImGuiCol_TextDisabled]));
			ImGui::GetWindowDrawList()->AddLine(
				ImVec2(bar_x, start_y), ImVec2(bar_x, end_y),
				bar_color, thickness);
		}
		ImGui::Unindent();
		m_quote_depth--;
		m_admonition_kind = AdmonitionKind::None;
		m_admonition_scan_pending = false;
		m_admonition_skip_next_softbr = false;
	}
}

// Try to match a "[!NOTE]" / "[!TIP]" / ... marker at the start of `str`.
// On match, returns the admonition kind and sets `marker_end` to the byte
// just after the closing ']'. Case-insensitive per GitHub behavior.
static Renderer::AdmonitionKind match_admonition_marker(
	const char* str, const char* str_end, const char*& marker_end)
{
	if (str_end - str < 4 || str[0] != '[' || str[1] != '!')
		return Renderer::AdmonitionKind::None;
	const char* p = str + 2;
	const char* close = p;
	while (close < str_end && *close != ']')
		++close;
	if (close >= str_end)
		return Renderer::AdmonitionKind::None;
	auto eq_ci = [](const char* a, const char* a_end, const char* b) {
		size_t n = (size_t)(a_end - a);
		if (strlen(b) != n) return false;
		for (size_t i = 0; i < n; ++i) {
			char ca = a[i]; if (ca >= 'a' && ca <= 'z') ca = (char)(ca - 'a' + 'A');
			if (ca != b[i]) return false;
		}
		return true;
	};
	Renderer::AdmonitionKind kind = Renderer::AdmonitionKind::None;
	if      (eq_ci(p, close, "NOTE"))      kind = Renderer::AdmonitionKind::Note;
	else if (eq_ci(p, close, "TIP"))       kind = Renderer::AdmonitionKind::Tip;
	else if (eq_ci(p, close, "IMPORTANT")) kind = Renderer::AdmonitionKind::Important;
	else if (eq_ci(p, close, "WARNING"))   kind = Renderer::AdmonitionKind::Warning;
	else if (eq_ci(p, close, "CAUTION"))   kind = Renderer::AdmonitionKind::Caution;
	if (kind == Renderer::AdmonitionKind::None)
		return kind;
	marker_end = close + 1;
	return kind;
}

void Renderer::render_admonition_header(AdmonitionKind kind)
{
	ImVec4 col = admonition_color(kind);
	ImGui::PushStyleColor(ImGuiCol_Text, col);
	// Bold the label: fake it by pushing the strong flag and re-picking the font.
	bool saved_strong = m_is_strong;
	m_is_strong = true;
	set_font(true);
	ImGui::TextUnformatted(admonition_label(kind));
	set_font(false);
	m_is_strong = saved_strong;
	ImGui::PopStyleColor();
	// TextUnformatted already advanced the cursor to the next line;
	// the content starts right below, no extra NewLine needed.
}


void Renderer::BLOCK_CODE(const MD_BLOCK_CODE_DETAIL* detail, bool e)
{
    if (!can_use_child_windows())
        m_is_code = e;
    else
    {
    m_is_code_block = e;

    if (m_is_code_block)
        m_code_block = "";
    else
        render_code_block();

    if (detail->lang.text == NULL)
        m_code_block_language = "";
    else
        m_code_block_language = std::string(detail->lang.text, detail->lang.size);
    }
}

void Renderer::BLOCK_HTML(bool)
{

}

void Renderer::BLOCK_P(bool)
{
	// Inter-block spacing is handled centrally in block() on enter.
}

void Renderer::BLOCK_TABLE(const MD_BLOCK_TABLE_DETAIL* d, bool e)
{
	if (e) {
		// Unique ID per table in this render; labels inside cells may repeat.
		ImGui::PushID(m_table_id_counter++);
		ImGuiTableFlags flags = ImGuiTableFlags_SizingStretchProp
		                      | ImGuiTableFlags_Resizable;
		if (m_table_border)
			flags |= ImGuiTableFlags_BordersInnerV
			       | ImGuiTableFlags_BordersOuterV
			       | ImGuiTableFlags_BordersOuterH
			       | ImGuiTableFlags_BordersInnerH;
		m_table_open = ImGui::BeginTable("##md", d->col_count, flags);
	} else {
		if (m_table_open)
			ImGui::EndTable();
		m_table_open = false;
		ImGui::PopID();
	}
}

void Renderer::BLOCK_THEAD(bool e)
{
	m_is_table_header = e;
	if (m_table_header_highlight) set_font(e);
}

void Renderer::BLOCK_TBODY(bool e)
{
	m_is_table_body = e;
}

void Renderer::BLOCK_TR(bool e)
{
	if (m_table_open && e) ImGui::TableNextRow();
}

// Non-left alignments (CENTER/RIGHT) can't be expressed directly in ImGui
// Tables, so we open a BeginGroup at cell entry, note the drawlist vertex
// count, render content normally, then on exit shift the new vertices by
// the appropriate X offset (cell_width - content_width, halved for center).
// Known limitation: for multi-line wrapped cells, all lines shift by the
// same offset (based on widest line), not per-line like HTML text-align.
static void begin_aligned_cell(MD_ALIGN align, int& vtx_start, float& cell_width)
{
	if (align == MD_ALIGN_DEFAULT || align == MD_ALIGN_LEFT)
		return;
	cell_width = ImGui::GetContentRegionAvail().x;
	vtx_start = ImGui::GetWindowDrawList()->VtxBuffer.Size;
	ImGui::BeginGroup();
}

static void end_aligned_cell(MD_ALIGN align, int vtx_start, float cell_width)
{
	if (align == MD_ALIGN_DEFAULT || align == MD_ALIGN_LEFT)
		return;
	ImGui::EndGroup();
	float content_w = ImGui::GetItemRectSize().x;
	if (content_w >= cell_width)
		return;
	float offset = (align == MD_ALIGN_CENTER)
		? (cell_width - content_w) * 0.5f
		: (cell_width - content_w);
	if (offset <= 0.0f)
		return;
	ImDrawList* dl = ImGui::GetWindowDrawList();
	for (int i = vtx_start; i < dl->VtxBuffer.Size; ++i)
		dl->VtxBuffer[i].pos.x += offset;
}

void Renderer::BLOCK_TH(const MD_BLOCK_TD_DETAIL* d, bool e)
{
	if (!m_table_open) return;
	if (e) {
		ImGui::TableNextColumn();
		m_cell_align = d->align;
		begin_aligned_cell(m_cell_align, m_cell_vtx_start, m_cell_width);
	} else {
		end_aligned_cell(m_cell_align, m_cell_vtx_start, m_cell_width);
		m_cell_align = MD_ALIGN_DEFAULT;
	}
}

void Renderer::BLOCK_TD(const MD_BLOCK_TD_DETAIL* d, bool e)
{
	if (!m_table_open) return;
	if (e) {
		ImGui::TableNextColumn();
		m_cell_align = d->align;
		begin_aligned_cell(m_cell_align, m_cell_vtx_start, m_cell_width);
	} else {
		end_aligned_cell(m_cell_align, m_cell_vtx_start, m_cell_width);
		m_cell_align = MD_ALIGN_DEFAULT;
	}
}

////////////////////////////////////////////////////////////////////////////////
void Renderer::set_href(bool e, const MD_ATTRIBUTE& src)
{
	if (e) {
		m_href.assign(src.text, src.size);
	} else {
		m_href.clear();
	}
}

void Renderer::set_img_src(bool e, const MD_ATTRIBUTE& src)
{
    if (e) {
        m_img_src.assign(src.text, src.size);
    } else {
        m_img_src.clear();
    }
}


void Renderer::set_font(bool e)
{
	if (e) {
		auto sized_font = get_font();
		ImGui::PushFont(sized_font.font, sized_font.size);
	} else {
		ImGui::PopFont();
	}
}

void Renderer::set_color(bool e)
{
	if (e) {
		ImGui::PushStyleColor(ImGuiCol_Text, get_color());
	} else {
		ImGui::PopStyleColor();
	}
}

void Renderer::line(ImColor c, bool under)
{
	ImVec2 mi = ImGui::GetItemRectMin();
	ImVec2 ma = ImGui::GetItemRectMax();

	if (!under) {
		ma.y -= ImGui::GetFontSize() / 2;
	}

	mi.y = ma.y;

	float lineThickness = ImGui::GetFontSize() / 14.5f;
	ImGui::GetWindowDrawList()->AddLine(mi, ma, c, lineThickness);
}

bool Renderer::link_item(const Style& style, const char* url)
{
	const ImGuiStyle& s = ImGui::GetStyle();
	ImVec4 underline;
	bool clicked = false;
	if (ImGui::IsItemHovered(ImGuiHoveredFlags_DelayNormal)) {
		ImGui::SetMouseCursor(ImGuiMouseCursor_Hand);
		if (style.linkTooltip)
			ImGui::SetTooltip("%s", url);
		underline = resolve_color(style.linkUnderlineHovered, s.Colors[ImGuiCol_ButtonHovered]);
		clicked = ImGui::IsMouseClicked(0);
	} else {
		underline = resolve_color(style.linkUnderline, s.Colors[ImGuiCol_Button]);
	}
	line(underline, true);
	return clicked;
}

void Renderer::SPAN_A(const MD_SPAN_A_DETAIL* d, bool e)
{
	set_href(e, d->href);
	set_color(e);
}


void Renderer::SPAN_EM(bool e)
{
	m_is_em = e;
	set_font(e);
}

void Renderer::SPAN_STRONG(bool e)
{
	m_is_strong = e;
	set_font(e);
}


void Renderer::SPAN_IMG(const MD_SPAN_IMG_DETAIL* d, bool e)
{
	m_is_image = e;

	set_img_src(e, d->src);

	if (e) {

		image_info nfo;
		image_status status = get_image(nfo);
		if (status == image_status::loading) {
			draw_loading_spinner();
		} else if (status == image_status::ready) {

			// Images are drawn at the same scale as the text
			const float scale = ImGui::GetStyle().FontScaleMain * ImGui::GetStyle().FontScaleDpi;
			nfo.size.x *= scale;
			nfo.size.y *= scale;

			ImVec2 const csz = ImGui::GetContentRegionAvail();
			if (nfo.size.x > csz.x) {
				const float r = nfo.size.y / nfo.size.x;
				nfo.size.x = csz.x;
				nfo.size.y = csz.x * r;
			}

			ImGui::Image(nfo.texture, nfo.size, nfo.uv0, nfo.uv1);
			// Stay on the same line so consecutive inline images or text continue horizontally
			ImGui::SameLine(0, 0);

			if (ImGui::IsItemHovered()) {

				//if (d->title.size) {
				//	ImGui::SetTooltip("%.*s", (int)d->title.size, d->title.text);
				//}
				ImGui::SetMouseCursor(ImGuiMouseCursor_Hand);

				if (ImGui::IsMouseClicked(0)) {
					open_url();
				}
			}
		}
	}
}

void Renderer::SPAN_CODE(bool)
{

}


void Renderer::EnableLatex()
{
	m_md.flags |= MD_FLAG_LATEXMATHSPANS;
}

void Renderer::set_flag(unsigned flag, bool enable)
{
	if (enable)
		m_md.flags |= flag;
	else
		m_md.flags &= ~flag;
}

void Renderer::SPAN_LATEXMATH(bool e)
{
	if (e) {
		m_is_latex_inline = true;
		m_latex_buffer.clear();
	} else {
		m_is_latex_inline = false;
		render_latex_span(false);
	}
}

void Renderer::SPAN_LATEXMATH_DISPLAY(bool e)
{
	if (e) {
		m_is_latex_display = true;
		m_latex_buffer.clear();
	} else {
		m_is_latex_display = false;
		render_latex_span(true);
	}
}

bool Renderer::get_latex_texture(const std::string&, float, ImU32, bool, latex_texture&) const
{
	return false;  // no LaTeX in this base class
}

// Draws m_latex_buffer: inline, aligned on the text baseline; display, centered on its own line.
// Formulas are rasterized at the framebuffer density and displayed at the logical size (sharp on HiDPI).
void Renderer::render_latex_span(bool display)
{
	float pixel_scale = ImGui::GetIO().DisplayFramebufferScale.y;
	if (pixel_scale <= 0.01f)
		pixel_scale = 1.0f;
	float logical_font_size = ImGui::GetFontSize();
	ImU32 color = ImGui::GetColorU32(ImGuiCol_Text);

	latex_texture tex;
	if (!get_latex_texture(m_latex_buffer, logical_font_size * pixel_scale, color, display, tex)) {
		// Fallback: the formula's source, with its delimiters (in the error color, with the message
		// as a tooltip, when the formula is invalid)
		bool invalid = !tex.error.empty();
		if (invalid)
			ImGui::PushStyleColor(ImGuiCol_Text, resolve_color(style.errorColor, admonition_color(AdmonitionKind::Caution)));
		if (display) {
			ImGui::NewLine();
			std::string fallback = "$$" + m_latex_buffer + "$$";
			ImGui::TextUnformatted(fallback.c_str());
		} else {
			std::string fallback = "$" + m_latex_buffer + "$";
			ImGui::TextUnformatted(fallback.c_str());
		}
		if (invalid) {
			ImGui::PopStyleColor();
			if (ImGui::IsItemHovered())
				ImGui::SetTooltip("%s", tex.error.c_str());
		}
		if (display)
			ImGui::NewLine();
		else
			ImGui::SameLine(0.0f, 0.0f);
		return;
	}
	if (tex.texture._TexData == nullptr && tex.texture._TexID == ImTextureID_Invalid)
		return;

	float logical_w = tex.size_px.x / pixel_scale;
	float logical_h = tex.size_px.y / pixel_scale;
	if (display) {
		// Display math: centered on its own line
		ImGui::NewLine();
		float avail = ImGui::GetContentRegionAvail().x;
		float pad_x = (avail - logical_w) * 0.5f;
		if (pad_x > 0.0f)
			ImGui::SetCursorPosX(ImGui::GetCursorPosX() + pad_x);
		ImGui::Image(tex.texture, ImVec2(logical_w, logical_h));
		ImGui::NewLine();
	} else {
		// Inline math: the formula's baseline on the text baseline. ImGui::Text() draws from
		// cursor.y with the baseline at cursor.y + ascent, so the image top goes at
		// cursor.y + ascent - baseline.
		float logical_baseline = tex.baseline_px / pixel_scale;
		ImFontBaked* baked = ImGui::GetFontBaked();
		float text_ascent = baked ? baked->Ascent : logical_font_size * 0.8f;
		float saved_y = ImGui::GetCursorPosY();
		ImGui::SetCursorPosY(saved_y + text_ascent - logical_baseline);
		ImGui::Image(tex.texture, ImVec2(logical_w, logical_h));
		ImGui::SameLine(0.0f, 0.0f);
		// Restore Y so the following inline content lands on the original line
		ImGui::SetCursorPosY(saved_y);
	}
}

void Renderer::SPAN_WIKILINK(const MD_SPAN_WIKILINK_DETAIL* d, bool e)
{
	// Rendered as a link whose href is the target; the click goes to open_wikilink()
	m_is_wikilink = e;
	set_href(e, d->target);
	set_color(e);
}

void Renderer::open_wikilink() const
{
}

void Renderer::SPAN_U(bool e)
{
	m_is_underline = e;
}

void Renderer::SPAN_DEL(bool e)
{
	m_is_strikethrough = e;
}

void Renderer::render_text(const char* str, const char* str_end)
{
	const ImGuiStyle& s = ImGui::GetStyle();
	bool is_lf = false;

	// <sub>/<sup>: render with a smaller font, offset vertically within
	// the current line so the baseline roughly matches GitHub's look.
	bool pushed_small_font = false;
	float base_font_size = get_font().size;
	float sub_sup_y_offset = 0.0f;
	if (m_is_sub || m_is_sup) {
		auto f = get_font();
		float small = f.size * style.subSupScale;
		ImGui::PushFont(f.font, small);
		pushed_small_font = true;
		sub_sup_y_offset = m_is_sup ? 0.0f : (base_font_size - small);
	}
	const float size = ImGui::GetFontSize();

	// Mid-word break avoidance: if a new span begins mid-line and the
	// remaining width on the current line cannot fit even its first
	// word (including any leading blanks that were emitted between
	// adjacent spans), drop to a fresh line so the wrap uses the full
	// content width. Without this, ImGui's "force 1 char to fit"
	// fallback in CalcWordWrapPosition splits inside the first word
	// (e.g. "D" / "ear ImGui Bundle", or "browser u" / "sing ...").
	if (!m_is_image && !m_is_table_header && str < str_end) {
		float wl = ImGui::GetContentRegionAvail().x;
		const char* word_start = str;
		while (word_start < str_end
		       && (*word_start == ' ' || *word_start == '\t'))
			++word_start;
		const char* word_end = word_start;
		while (word_end < str_end && *word_end != ' '
		       && *word_end != '\n' && *word_end != '\t') {
			++word_end;
		}
		if (word_end > word_start) {
			// Width to fit = any leading blanks + first word.
			ImVec2 chunk_sz = ImGui::CalcTextSize(str, word_end);
			const bool not_at_line_start =
				ImGui::GetCursorPosX() > ImGui::GetCursorStartPos().x + 1.0f;
			if (chunk_sz.x > wl && not_at_line_start) {
				ImGui::NewLine();
				// The leading blanks were inter-span spacing on the
				// previous line; drop them now that we've broken.
				str = word_start;
			}
		}
	}

	while (!m_is_image && str < str_end) {

		const char* te = str_end;

		if (!m_is_table_header) {
			// Inside a BeginTable cell, ContentRegionAvail.x is the cell
			// width; outside a table, it's the window content width.
			float wl = ImGui::GetContentRegionAvail().x;
			te = ImGui::GetFont()->CalcWordWrapPosition(
				size, str, str_end, wl);
			if (te == str) ++te;
		}

		// Vertical offset for sub/sup while keeping the surrounding
		// line's Y intact (restored after the text is drawn).
		float saved_y = 0.0f;
		bool adjusted_y = false;
		if (sub_sup_y_offset != 0.0f) {
			saved_y = ImGui::GetCursorPosY();
			ImGui::SetCursorPosY(saved_y + sub_sup_y_offset);
			adjusted_y = true;
		}

		// <mark>: draw a highlight rectangle behind the text using
		// drawlist channels so the background stays under the glyphs.
		ImDrawList* dl = ImGui::GetWindowDrawList();
		bool mark_split = m_is_mark;
		if (mark_split) {
			dl->ChannelsSplit(2);
			dl->ChannelsSetCurrent(1);
		}

		if (m_is_error)
			ImGui::PushStyleColor(ImGuiCol_Text, resolve_color(style.errorColor, admonition_color(AdmonitionKind::Caution)));
		ImGui::TextUnformatted(str, te);
		if (m_is_error) {
			ImGui::PopStyleColor();
			if (!m_error_title.empty() && ImGui::IsItemHovered())
				ImGui::SetTooltip("%s", m_error_title.c_str());
		}

		if (mark_split) {
			dl->ChannelsSetCurrent(0);
			ImVec2 mi = ImGui::GetItemRectMin();
			ImVec2 ma = ImGui::GetItemRectMax();
			mi.x -= 2.0f; ma.x += 2.0f;
			dl->AddRectFilled(mi, ma, ImGui::GetColorU32(style.markBackground), 2.0f);
			dl->ChannelsMerge();
		}
		// <kbd>: draw a thin rounded border around the glyph run.
		if (m_is_kbd) {
			ImVec2 mi = ImGui::GetItemRectMin();
			ImVec2 ma = ImGui::GetItemRectMax();
			mi.x -= 3.0f; ma.x += 3.0f;
			ImU32 border = ImGui::GetColorU32(resolve_color(style.kbdBorder, s.Colors[ImGuiCol_Border]));
#if IMGUI_VERSION_NUM < 19276
			dl->AddRect(mi, ma, border, 3.0f, 0, 1.0f);
#else
			dl->AddRect(mi, ma, border, 3.0f, 1.0f);
#endif
		}

		// Restore Y so the next span sits on the original line.
		if (adjusted_y) {
			float cur_x = ImGui::GetCursorPosX();
			ImGui::SetCursorPos(ImVec2(cur_x, saved_y));
		}

		if (te > str && *(te - 1) == '\n') {
			is_lf = true;
		}

		if (!m_href.empty()) {
			if (link_item(style, m_href.c_str())) {
				if (m_is_wikilink)
					open_wikilink();
				else
					open_url();
			}
		}
		if (m_is_underline) {
			line(s.Colors[ImGuiCol_Text], true);
		}
		if (m_is_strikethrough) {
			line(s.Colors[ImGuiCol_Text], false);
		}

		str = te;

		while (str < str_end && *str == ' ')++str;
	}

	if (pushed_small_font)
		ImGui::PopFont();

	if (!is_lf)
    {
        ImGui::SameLine(0.0f, 0.0f);
    }
}


bool Renderer::render_entity(const char* str, const char* str_end)
{
	const size_t sz = str_end - str;
	if (strncmp(str, "&nbsp;", sz) == 0) {
		ImGui::TextUnformatted(""); ImGui::SameLine();
		return true;
	}
	return false;
}

static bool skip_spaces(const std::string& d, size_t& p)
{
	for (; p < d.length(); ++p) {
		if (d[p] != ' ' && d[p] != '\t') {
			break;
		}
	}
	return p < d.length();
}

static std::string get_div_class(const char* str, const char* str_end)
{
	if (str_end <= str)return "";

	std::string d(str, str_end - str);
	if (d.back() == '>')d.pop_back();

	const char attr[] = "class";
	size_t p = d.find(attr);
	if (p == std::string::npos)return "";
	p += sizeof(attr)-1;

	if (!skip_spaces(d, p))return "";

	if (d[p] != '=')return "";
	++p;

	if (!skip_spaces(d, p))return "";

	bool has_q = false;

	if (d[p] == '"' || d[p] == '\'') {
		has_q = true;
		++p;
	}
	if (p == d.length())return "";

	if (!has_q) {
		if (!skip_spaces(d, p))return "";
	}

	size_t pe;
	for (pe = p; pe < d.length(); ++pe) {

		const char c = d[pe];

		if (has_q) {
			if (c == '"' || c == '\'') {
				break;
			}
		} else {
			if (c == ' ' || c == '\t') {
				break;
			}
		}
	}

	return d.substr(p, pe - p);

}

// Helper: extract an attribute value from an HTML tag string
// e.g. extract_html_attr("<img src=\"foo.png\" width=\"200\">", "src") -> "foo.png"
static std::string extract_html_attr(const std::string& tag, const char* name)
{
	std::string needle = std::string(name) + "=";
	auto pos = tag.find(needle);
	if (pos == std::string::npos) return "";
	pos += needle.size();
	if (pos >= tag.size()) return "";
	char quote = tag[pos];
	if (quote == '"' || quote == '\'') {
		auto end = tag.find(quote, pos + 1);
		if (end == std::string::npos) return "";
		return tag.substr(pos + 1, end - pos - 1);
	}
	// No quotes: read until space or >
	auto end = tag.find_first_of(" \t\n>", pos);
	if (end == std::string::npos) end = tag.size();
	return tag.substr(pos, end - pos);
}

static int extract_html_int_attr(const std::string& tag, const char* name, int defaultValue)
{
	std::string val = extract_html_attr(tag, name);
	if (val.empty()) return defaultValue;
	try { return std::stoi(val); }
	catch (...) { return defaultValue; }
}

static bool details_hidden(const std::vector<bool>& stack);  // defined below

bool Renderer::check_html(const char* str, const char* str_end)
{
	const size_t sz = str_end - str;

	if (strncmp(str, "<br>", sz) == 0) {
		ImGui::NewLine();
		return true;
	}
	if (strncmp(str, "<hr>", sz) == 0) {
		ImGui::Separator();
		return true;
	}
	if (strncmp(str, "<u>", sz) == 0) {
		m_is_underline = true;
		return true;
	}
	if (strncmp(str, "</u>", sz) == 0) {
		m_is_underline = false;
		return true;
	}

	// Inline HTML spans with built-in rendering. The text between the
	// opening and closing tags arrives as normal MD_TEXT_NORMAL events;
	// render_text() inspects these flags and adjusts accordingly.
	if (strncmp(str, "<sub>",   sz) == 0) { m_is_sub  = true;  return true; }
	if (strncmp(str, "</sub>",  sz) == 0) { m_is_sub  = false; return true; }
	if (strncmp(str, "<sup>",   sz) == 0) { m_is_sup  = true;  return true; }
	if (strncmp(str, "</sup>",  sz) == 0) { m_is_sup  = false; return true; }
	if (strncmp(str, "<kbd>",   sz) == 0) { m_is_kbd  = true;  return true; }
	if (strncmp(str, "</kbd>",  sz) == 0) { m_is_kbd  = false; return true; }
	if (strncmp(str, "<mark>",  sz) == 0) { m_is_mark = true;  return true; }
	if (strncmp(str, "</mark>", sz) == 0) { m_is_mark = false; return true; }
	// <md-error title="reason">: text in the error color, the reason as a tooltip (failed @import)
	if (sz > 9 && strncmp(str, "<md-error", 9) == 0) {
		m_is_error = true;
		m_error_title.clear();
		const char* t = strstr(str, "title=\"");
		if (t && t < str_end) {
			t += 7;
			const char* e = (const char*)memchr(t, '"', str_end - t);
			if (e) m_error_title.assign(t, e);
		}
		return true;
	}
	if (strncmp(str, "</md-error>", sz) == 0) { m_is_error = false; return true; }

	// <details> / </details>: open a CollapsingHeader whose label comes
	// from the inner <summary>...</summary> line. When collapsed, all
	// subsequent rendering is suppressed until the matching </details>.
	// Requires the standard CommonMark pattern with blank lines:
	//   <details>
	//   <summary>Label</summary>
	//
	//   Markdown content here…
	//
	//   </details>
	auto starts_with = [&](const char* prefix) {
		size_t n = strlen(prefix);
		return sz >= n && strncmp(str, prefix, n) == 0;
	};

	// <pre>...</pre>: block-level preformatted monospace text.
	// md4c treats <pre> as a CommonMark type-1 HTML block, delivering the
	// content through MD_TEXT_HTML events that include the tags themselves.
	// Buffer across chunks in case md4c splits on newlines.
	auto render_pre = [&](const char* s, const char* e) {
		// Skip one optional leading '\n' right after <pre>.
		if (s < e && *s == '\n') ++s;
		// When hidden by a collapsed <details>, consume but don't render.
		for (bool open : m_details_open_stack)
			if (!open) return;
		// m_is_code makes subclass get_font() return the monospace code font.
		m_is_code = true;
		auto f = get_font();
		if (f.font) ImGui::PushFont(f.font, f.size);
		while (s < e) {
			const char* eol = s;
			while (eol < e && *eol != '\n') ++eol;
			if (eol > s)
				ImGui::TextUnformatted(s, eol);
			else
				ImGui::NewLine();
			s = (eol < e) ? eol + 1 : e;
		}
		if (f.font) ImGui::PopFont();
		m_is_code = false;
	};
	auto find_close_pre = [&](const char* s, const char* e) -> const char* {
		for (const char* q = s; q + 6 <= e; ++q)
			if (strncmp(q, "</pre>", 6) == 0) return q;
		return nullptr;
	};
	if (m_in_pre) {
		const char* close = find_close_pre(str, str_end);
		if (close) {
			m_pre_buffer.append(str, close);
			render_pre(m_pre_buffer.data(), m_pre_buffer.data() + m_pre_buffer.size());
			m_pre_buffer.clear();
			m_in_pre = false;
		} else {
			m_pre_buffer.append(str, str_end);
		}
		return true;
	}
	if (starts_with("<pre>") || starts_with("<pre ")) {
		const char* gt = (const char*)memchr(str, '>', str_end - str);
		const char* content_start = gt ? gt + 1 : str_end;
		const char* close = find_close_pre(content_start, str_end);
		if (close) {
			render_pre(content_start, close);
		} else {
			m_pre_buffer.assign(content_start, str_end);
			m_in_pre = true;
		}
		return true;
	}
	if (starts_with("<details>") || starts_with("<details ")) {
		m_details_awaiting_summary = true;
		// Check for the `open` attribute (boolean HTML attribute: `<details open>`
		// or `<details open="open">`). Simple substring check between the tag
		// start and the closing '>'.
		const char* tag_end = (const char*)memchr(str, '>', str_end - str);
		if (!tag_end) tag_end = str_end;
		bool has_open_attr = false;
		for (const char* q = str; q + 4 <= tag_end; ++q) {
			if ((q == str || q[-1] == ' ' || q[-1] == '\t') &&
			    strncmp(q, "open", 4) == 0 &&
			    (q + 4 == tag_end || q[4] == ' ' || q[4] == '\t' || q[4] == '=' || q[4] == '>')) {
				has_open_attr = true;
				break;
			}
		}
		m_details_awaiting_open_default = has_open_attr;
		// Swallow the stray "\n" chunk md4c emits between <details> and
		// <summary> so the CollapsingHeader sits flush with the content
		// above it.
		m_details_suppress_next_raw_html = true;
		return true;
	}
	if (starts_with("<summary>")) {
		// Find "</summary>" on the same chunk.
		const char* p = str + strlen("<summary>");
		const char* close = nullptr;
		for (const char* q = p; q + 10 <= str_end; ++q) {
			if (strncmp(q, "</summary>", 10) == 0) { close = q; break; }
		}
		std::string raw_label = (close != nullptr)
			? std::string(p, close)
			: std::string(p, str_end);
		// Decode the common HTML entities so `<summary>&lt;pre&gt;</summary>`
		// displays as `<pre>` in the collapsing header.
		std::string label;
		label.reserve(raw_label.size());
		for (size_t i = 0; i < raw_label.size(); ) {
			if (raw_label[i] == '&') {
				if (raw_label.compare(i, 4, "&lt;")   == 0) { label += '<';  i += 4; continue; }
				if (raw_label.compare(i, 4, "&gt;")   == 0) { label += '>';  i += 4; continue; }
				if (raw_label.compare(i, 5, "&amp;")  == 0) { label += '&';  i += 5; continue; }
				if (raw_label.compare(i, 6, "&quot;") == 0) { label += '"';  i += 6; continue; }
				if (raw_label.compare(i, 6, "&apos;") == 0) { label += '\''; i += 6; continue; }
				if (raw_label.compare(i, 5, "&#39;")  == 0) { label += '\''; i += 5; continue; }
			}
			label += raw_label[i++];
		}
		if (!m_details_awaiting_summary) {
			// Orphan <summary> (not inside a <details>) — just show the label.
			ImGui::TextUnformatted(label.c_str());
			return true;
		}
		// If any ancestor <details> is collapsed, suppress this nested header
		// entirely. Still push to the stack (as closed) so the matching
		// </details> pops correctly.
		bool any_ancestor_closed = false;
		for (bool open : m_details_open_stack)
			if (!open) { any_ancestor_closed = true; break; }
		if (any_ancestor_closed) {
			m_details_id_counter++;  // consume the id anyway: the ids of the following headers must not depend on what is open
			m_details_open_stack.push_back(false);
			m_details_awaiting_summary = false;
			m_details_awaiting_open_default = false;
			return true;
		}
		ImGui::PushID(m_details_id_counter++);
		// Honour the `open` attribute on <details open>: pre-open the
		// CollapsingHeader once (user can still collapse it afterwards).
		if (m_details_awaiting_open_default)
			ImGui::SetNextItemOpen(true, ImGuiCond_Once);
		bool open = ImGui::CollapsingHeader(label.c_str());
		ImGui::PopID();
		m_details_open_stack.push_back(open);
		if (open)
			ImGui::Indent();
		m_details_awaiting_summary = false;
		m_details_awaiting_open_default = false;
		// Eat the trailing "\n" chunk md4c emits right after </summary>;
		// rendering it would advance the cursor by a full line and
		// produce a visibly oversized gap before the body content.
		m_details_suppress_next_raw_html = true;
		return true;
	}
	if (starts_with("</details>")) {
		if (!m_details_open_stack.empty()) {
			bool was_open = m_details_open_stack.back();
			m_details_open_stack.pop_back();
			if (was_open)
				ImGui::Unindent();
		}
		m_details_awaiting_summary = false;
		// Eat the trailing "\n" chunk md4c emits right after this tag
		// so content below sits flush with the collapsible.
		m_details_suppress_next_raw_html = true;
		return true;
	}

	// <img src="..." width="..." height="...">
	if (sz >= 4 && strncmp(str, "<img", 4) == 0) {
		// Consume but don't render when hidden by a collapsed <details>.
		for (bool open : m_details_open_stack)
			if (!open) return true;
		std::string tag(str, str_end);
		std::string src = extract_html_attr(tag, "src");
		if (src.empty()) return false;

		int width = extract_html_int_attr(tag, "width", 0);
		int height = extract_html_int_attr(tag, "height", 0);

		m_img_src = src;
		image_info nfo;
		image_status status = get_image(nfo);
		if (status == image_status::loading) {
			draw_loading_spinner();
		} else if (status == image_status::ready) {
			const float scale = ImGui::GetStyle().FontScaleMain * ImGui::GetStyle().FontScaleDpi;
			float natural_w = nfo.size.x * scale;
			float natural_h = nfo.size.y * scale;

			if (width > 0 && height > 0) {
				nfo.size.x = (float)width;
				nfo.size.y = (float)height;
			} else if (width > 0) {
				nfo.size.x = (float)width;
				nfo.size.y = natural_h * ((float)width / natural_w);
			} else if (height > 0) {
				nfo.size.x = natural_w * ((float)height / natural_h);
				nfo.size.y = (float)height;
			} else {
				nfo.size.x = natural_w;
				nfo.size.y = natural_h;
			}

			// Clamp to available width
			ImVec2 const csz = ImGui::GetContentRegionAvail();
			if (nfo.size.x > csz.x) {
				float r = nfo.size.y / nfo.size.x;
				nfo.size.x = csz.x;
				nfo.size.y = csz.x * r;
			}

			ImGui::Image(nfo.texture, nfo.size, nfo.uv0, nfo.uv1);
			// Stay on the same line so consecutive inline images or text continue horizontally
			ImGui::SameLine(0, 0);
		}
		m_img_src.clear();
		return true;
	}

	if (strncmp(str, "<center>", sz) == 0) {
		if (details_hidden(m_details_open_stack))
			return true;
		if (!m_in_center) {
			m_in_center = true;
			begin_aligned_cell(MD_ALIGN_CENTER, m_center_vtx_start, m_center_width);
		}
		return true;
	}
	if (strncmp(str, "</center>", sz) == 0) {
		if (details_hidden(m_details_open_stack))
			return true;
		if (m_in_center) {
			m_in_center = false;
			end_aligned_cell(MD_ALIGN_CENTER, m_center_vtx_start, m_center_width);
		}
		return true;
	}

	const size_t div_sz = 4;
	if (strncmp(str, "<div", sz > div_sz ? div_sz : sz) == 0) {
		m_div_stack.emplace_back(get_div_class(str + div_sz, str_end));
		html_div(m_div_stack.back(), true);
		return true;
	}
	if (strncmp(str, "</div>", sz) == 0) {
		if (m_div_stack.empty())return false;
		html_div(m_div_stack.back(), false);
		m_div_stack.pop_back();
		return true;
	}
	return false;
}


void Renderer::html_div(const std::string& dclass, bool e)
{
	//Example:
#if 0
	if (dclass == "red") {
		if (e) {
			ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(255, 0, 0, 255));
		} else {
			ImGui::PopStyleColor();
		}
	}
#endif
    (void)dclass; (void)e;
}

void Renderer::render_code_block()
{
    m_is_code = true;
    push_code_style();

    const char* begin = m_code_block.data();
    const char *end = m_code_block.data() + m_code_block.size();
    render_text(begin, end);

    pop_code_style();
    m_is_code = false;
}

void Renderer::push_code_style()
{
	auto code_font = get_font();
	ImGui::PushFont(code_font.font, code_font.size);

    // Automatic: the text color, a little more blue
    auto automatic = ImGui::GetStyle().Colors[ImGuiCol_Text];
    automatic.z *= 1.15f;
    ImGui::PushStyleColor(ImGuiCol_Text, resolve_color(style.codeColor, automatic));

}
void Renderer::pop_code_style()
{
    ImGui::PopStyleColor();
    ImGui::PopFont();
}


void Renderer::render_inline_code(const char *str, const char *str_end)
{
    m_is_code = true;
    push_code_style();
    render_text(str, str_end);
    pop_code_style();
    m_is_code = false;
}

// True when we're inside a <details> that the user has collapsed.
// Used to suppress all drawing between <summary>…</summary> and
// </details>, while still letting check_html() see the </details>
// tag so it can close the stack.
static bool details_hidden(const std::vector<bool>& stack)
{
	for (bool open : stack)
		if (!open) return true;
	return false;
}

int Renderer::text(MD_TEXTTYPE type, const char* str, const char* str_end)
{
	// Even while hidden we keep processing raw HTML so </details>
	// can pop the stack; everything else is discarded.
	if (details_hidden(m_details_open_stack) && type != MD_TEXT_HTML)
		return 0;

	switch (type) {
	case MD_TEXT_NORMAL:
		if (m_hlevel > 0)
			m_heading_text.append(str, str_end);
		if (m_admonition_scan_pending) {
			m_admonition_scan_pending = false;
			const char* marker_end = nullptr;
			AdmonitionKind kind = match_admonition_marker(str, str_end, marker_end);
			if (kind != AdmonitionKind::None) {
				m_admonition_kind = kind;
				render_admonition_header(kind);
				m_admonition_skip_next_softbr = true;
				// Render any trailing content on the marker's own line
				// (skip leading whitespace).
				while (marker_end < str_end && (*marker_end == ' ' || *marker_end == '\t'))
					++marker_end;
				if (marker_end < str_end)
					render_text(marker_end, str_end);
				break;
			}
		}
		render_text(str, str_end);
		break;
	case MD_TEXT_CODE:
        if (m_is_code_block)
            m_code_block += std::string(str, str_end);
        else
            render_inline_code(str, str_end);
		break;
	case MD_TEXT_NULLCHAR:
		break;
	case MD_TEXT_BR:
		ImGui::NewLine();
		break;
	case MD_TEXT_SOFTBR:
		if (m_admonition_skip_next_softbr) {
			m_admonition_skip_next_softbr = false;
			break;
		}
		soft_break();
		break;
	case MD_TEXT_ENTITY:
		if (!render_entity(str, str_end)) {
			render_text(str, str_end);
		};
		break;
	case MD_TEXT_HTML:
		if (!check_html(str, str_end)) {
			// Drop stray raw-HTML chunks (typically "\n") that
			// md4c emits between recognized tags inside/around a
			// <details> block — drawing them would widen the
			// collapsible's vertical spacing.
			if (m_details_suppress_next_raw_html) {
				m_details_suppress_next_raw_html = false;
			} else if (!details_hidden(m_details_open_stack)) {
				render_text(str, str_end);
			}
		} else {
			// Recognized tag: clear any pending suppression since
			// the tag itself was already handled and any flag it
			// set should take precedence on the following chunk.
		}
		break;
	case MD_TEXT_LATEXMATH:
		if (m_is_latex_inline || m_is_latex_display) {
			m_latex_buffer.append(str, str_end - str);
		} else {
			render_text(str, str_end);
		}
		break;
	default:
		break;
	}

	return 0;
}

int Renderer::block(MD_BLOCKTYPE type, void* d, bool e)
{
	// Suppress block rendering while inside a collapsed <details>.
	// BLOCK_HTML pairs still arrive (the tags themselves land as
	// MD_TEXT_HTML in text(), which is allowed through), so we just
	// drop any other block work here.
	if (details_hidden(m_details_open_stack))
		return 0;

	// Centralized inter-block spacing: on enter of any top-level
	// "paragraph-class" block, call add_block_gap() -- unless the flag
	// m_skip_next_block_gap tells us to suppress it (true at the very
	// first block, and for the first child of a quote). Blocks nested
	// inside a list are skipped; LI handles its own spacing.
	if (e) {
		bool is_separator_eligible = false;
		switch (type) {
		case MD_BLOCK_P:
		case MD_BLOCK_H:
		case MD_BLOCK_QUOTE:
		case MD_BLOCK_HR:
		case MD_BLOCK_CODE:
		case MD_BLOCK_HTML:
		case MD_BLOCK_TABLE:
		case MD_BLOCK_UL:
		case MD_BLOCK_OL:
			is_separator_eligible = m_list_stack.empty();
			break;
		default:
			break;
		}
		if (is_separator_eligible) {
			if (m_skip_next_block_gap)
				m_skip_next_block_gap = false;
			else {
				add_block_gap(style.blockGap);
				// Extra breathing room above headers, decaying with depth:
				// H1 gets the most, H6 none. Light scheme: 0.15 em per step.
				if (type == MD_BLOCK_H) {
					int level = ((MD_BLOCK_H_DETAIL*)d)->level;
					int steps = 7 - level;
					if (steps > 0)
						ImGui::Dummy(ImVec2(0.0f, ImGui::GetFontSize() * style.headerGapStep * (float)steps));
				}
			}
		}
	}

	switch (type)
	{
	case MD_BLOCK_DOC:
		BLOCK_DOC(e);
		break;
	case MD_BLOCK_QUOTE:
		BLOCK_QUOTE(e);
		break;
	case MD_BLOCK_UL:
		BLOCK_UL((MD_BLOCK_UL_DETAIL*)d, e);
		break;
	case MD_BLOCK_OL:
		BLOCK_OL((MD_BLOCK_OL_DETAIL*)d, e);
		break;
	case MD_BLOCK_LI:
		BLOCK_LI((MD_BLOCK_LI_DETAIL*)d, e);
		break;
	case MD_BLOCK_HR:
		BLOCK_HR(e);
		break;
	case MD_BLOCK_H:
		BLOCK_H((MD_BLOCK_H_DETAIL*)d, e);
		break;
	case MD_BLOCK_CODE:
		BLOCK_CODE((MD_BLOCK_CODE_DETAIL*)d, e);
		break;
	case MD_BLOCK_HTML:
		BLOCK_HTML(e);
		break;
	case MD_BLOCK_P:
		BLOCK_P(e);
		break;
	case MD_BLOCK_TABLE:
		BLOCK_TABLE((MD_BLOCK_TABLE_DETAIL*)d, e);
		break;
	case MD_BLOCK_THEAD:
		BLOCK_THEAD(e);
		break;
	case MD_BLOCK_TBODY:
		BLOCK_TBODY(e);
		break;
	case MD_BLOCK_TR:
		BLOCK_TR(e);
		break;
	case MD_BLOCK_TH:
		BLOCK_TH((MD_BLOCK_TD_DETAIL*)d, e);
		break;
	case MD_BLOCK_TD:
		BLOCK_TD((MD_BLOCK_TD_DETAIL*)d, e);
		break;
	default:
		assert(false);
		break;
	}

	return 0;
}

int Renderer::span(MD_SPANTYPE type, void* d, bool e)
{
	// Suppress span rendering while inside a collapsed <details>.
	if (details_hidden(m_details_open_stack))
		return 0;
	// Any span opening before the first text in a quote means this is not
	// an admonition (the marker must be plain text).
	if (e && m_admonition_scan_pending)
		m_admonition_scan_pending = false;
	switch (type)
	{
	case MD_SPAN_EM:
		SPAN_EM(e);
		break;
	case MD_SPAN_STRONG:
		SPAN_STRONG(e);
		break;
	case MD_SPAN_A:
		SPAN_A((MD_SPAN_A_DETAIL*)d, e);
		break;
	case MD_SPAN_IMG:
		SPAN_IMG((MD_SPAN_IMG_DETAIL*)d, e);
		break;
	case MD_SPAN_CODE:
		SPAN_CODE(e);
		break;
	case MD_SPAN_DEL:
		SPAN_DEL(e);
		break;
	case MD_SPAN_LATEXMATH:
		SPAN_LATEXMATH(e);
		break;
	case MD_SPAN_LATEXMATH_DISPLAY:
		SPAN_LATEXMATH_DISPLAY(e);
		break;
	case MD_SPAN_WIKILINK:
		SPAN_WIKILINK((MD_SPAN_WIKILINK_DETAIL*)d, e);
		break;
	case MD_SPAN_U:
		SPAN_U(e);
		break;
	default:
		assert(false);
		break;
	}

	return 0;
}

int Renderer::print(const char* str, const char* str_end)
{
	if (str >= str_end)
        return 0;

    // Inter-block spacing is emitted by block() before each top-level
    // separator-eligible block; set the flag so the very first one is
    // skipped (rendering starts flush at the caller's cursor).
    m_skip_next_block_gap = true;
    m_table_id_counter = 0;
    m_details_id_counter = 0;
    m_in_pre = false;
    m_pre_buffer.clear();

	if (style.fragmentGapTop > 0.0f)
		ImGui::Dummy(ImVec2(0.0f, ImGui::GetFontSize() * style.fragmentGapTop));
	int result = md_parse(str, (MD_SIZE)(str_end - str), &m_md, this);
	if (style.fragmentGapBottom < 0.0f)
		ImGui::NewLine();
	else if (style.fragmentGapBottom > 0.0f)
		ImGui::Dummy(ImVec2(0.0f, ImGui::GetFontSize() * style.fragmentGapBottom));
	return result;
}

////////////////////////////////////////////////////////////////////////////////

Renderer::MdSizedFont Renderer::get_font() const
{
	return MdSizedFont{nullptr, 0.0f}; // no font in this base class!

	//Example:
#if 0
	if (m_is_table_header) {
		return g_font_bold;
	}

	switch (m_hlevel)
	{
	case 0:
		return m_is_strong ? g_font_bold : g_font_regular;
	case 1:
		return g_font_bold_large;
	default:
		return g_font_bold;
	}
#endif

};

ImVec4 Renderer::default_link_color()
{
    auto col_text = ImGui::GetStyle().Colors[ImGuiCol_Text];

    float h, s, v;
    ImGui::ColorConvertRGBtoHSV(col_text.x, col_text.y, col_text.z, h, s, v);
    h = 0.57f;
    if (v >= 0.8f)
        v = 0.8f;
    if (v <= 0.5f)
        v = 0.5f;
    if (s <= 0.5f)
        s = 0.5f;

    ImGui::ColorConvertHSVtoRGB(h, s, v, col_text.x, col_text.y, col_text.z);
    return col_text;
}


ImVec4 Renderer::link_color() const
{
	return resolve_color(style.linkColor, default_link_color());
}

ImVec4 Renderer::get_color() const
{
	if (!m_href.empty())
    {
		return link_color();
	}
	return  ImGui::GetStyle().Colors[ImGuiCol_Text];
}


Renderer::image_status Renderer::get_image(image_info& nfo) const
{
	//Use m_href to identify images

	//Example - Imgui font texture
	nfo.texture = ImGui::GetIO().Fonts->TexRef;
	nfo.size = { 100,50 };
	nfo.uv0 = { 0,0 };
	nfo.uv1 = { 1,1 };

	return image_status::ready;
};

// A rotating spinner, two lines high
void Renderer::draw_loading_spinner()
{
	float size = ImGui::GetFontSize() * 2.0f;
	ImVec2 cursor = ImGui::GetCursorScreenPos();
	ImVec2 center(cursor.x + size * 0.5f, cursor.y + size * 0.5f);
	float radius = size * 0.4f;
	float thickness = 2.0f;
	float t = (float)ImGui::GetTime();

	ImDrawList* dl = ImGui::GetWindowDrawList();
	int segments = 12;
	for (int i = 0; i < segments; i++)
	{
		float a = (float)i / (float)segments * 3.14159265358979f * 2.0f;
		// Fade based on rotation phase
		float fade = std::fmodf((float)i / (float)segments + t * 1.5f, 1.0f);
		ImU32 c = ImGui::GetColorU32(ImGuiCol_Text, fade * 0.8f);
		float inner = radius * 0.5f;
		ImVec2 p1(center.x + std::cosf(a) * inner, center.y + std::sinf(a) * inner);
		ImVec2 p2(center.x + std::cosf(a) * radius, center.y + std::sinf(a) * radius);
		dl->AddLine(p1, p2, c, thickness);
	}
	ImGui::Dummy(ImVec2(size, size));
}

void Renderer::open_url() const
{
	//Example:

#if 0
	if (!m_is_image) {
		SDL_OpenURL(m_href.c_str());
	} else {
		//image clicked
	}
#endif
}

void Renderer::soft_break()
{
    // Convert a soft break (e.g. a new line inside a paragraph into a space)
    ImGui::TextUnformatted(" ");
    ImGui::SameLine(0.0f, 0.0f);
}

} // namespace RichMd
