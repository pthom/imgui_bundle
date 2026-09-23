/*
 * imgui_md: Markdown for Dear ImGui using MD4C
 * (http://https://github.com/mekhontsev/imgui_md)
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

#ifndef RICHMD_RENDERER_H
#define RICHMD_RENDERER_H

#include "md4c.h"
#include "imgui.h"
#include <string>
#include <vector>

namespace RichMd
{

struct Renderer
{
	// GitHub-style admonitions: > [!NOTE] / [!TIP] / [!IMPORTANT] / [!WARNING] / [!CAUTION]
	enum class AdmonitionKind { None, Note, Tip, Important, Warning, Caution };

	Renderer();
	virtual ~Renderer() {};

	//returns 0 on success
	int print(const char* str, const char* str_end);

	// Enable parsing of LaTeX math spans ($...$ and $$...$$).
	// When enabled, MD_FLAG_LATEXMATHSPANS is set on the md4c parser,
	// and MD_TEXT_LATEXMATH content is accumulated into m_latex_buffer
	// between SPAN_LATEXMATH enter/leave (or SPAN_LATEXMATH_DISPLAY), then drawn on leave
	// with the texture returned by get_latex_texture() (the source is shown when there is none).
	void EnableLatex();

	// Enable or disable a specific MD_FLAG_XXX on the md4c parser.
	// Call before print(); default flags are MD_FLAG_TABLES, MD_FLAG_UNDERLINE,
	// MD_FLAG_STRIKETHROUGH, MD_FLAG_TASKLISTS.
	void set_flag(unsigned flag, bool enable);

	// Colors and spacing. A color with a negative alpha is automatic: derived from the ImGui style
	// at render time, so theme changes are followed. Gaps and scales are relative to the font size.
	struct Style
	{
		ImVec4 linkColor = ImVec4(0, 0, 0, -1);            // automatic: the text color shifted to blue
		ImVec4 linkUnderline = ImVec4(0, 0, 0, -1);        // automatic: ImGuiCol_Button
		ImVec4 linkUnderlineHovered = ImVec4(0, 0, 0, -1); // automatic: ImGuiCol_ButtonHovered
		ImVec4 codeColor = ImVec4(0, 0, 0, -1);            // automatic: the text color, a little more blue
		ImVec4 errorColor = ImVec4(0, 0, 0, -1);           // automatic: the Caution admonition color (invalid formula, failed import: <md-error>)
		ImVec4 quoteBar = ImVec4(0, 0, 0, -1);             // automatic: ImGuiCol_TextDisabled
		ImVec4 kbdBorder = ImVec4(0, 0, 0, -1);            // automatic: ImGuiCol_Border
		ImVec4 markBackground = ImVec4(245.f / 255.f, 205.f / 255.f, 60.f / 255.f, 120.f / 255.f);
		// Note, Tip, Important, Warning, Caution (label and bar)
		ImVec4 admonitionColors[5] = {
			ImVec4(0.35f, 0.65f, 1.00f, 1.0f), ImVec4(0.25f, 0.73f, 0.32f, 1.0f), ImVec4(0.82f, 0.60f, 0.97f, 1.0f),
			ImVec4(0.95f, 0.75f, 0.22f, 1.0f), ImVec4(0.97f, 0.32f, 0.29f, 1.0f) };
		float blockGap = 0.3f;              // vertical gap between blocks
		float headerGapStep = 0.12f;        // extra gap above a header: (7 - level) * headerGapStep
		float subSupScale = 0.7f;           // font size of <sub> and <sup>
		float quoteBarThickness = 2.0f;     // pixels
		float admonitionBarThickness = 3.0f;
		bool linkTooltip = true;            // show the url when hovering a link
		// Space above and below each rendered fragment (a print() call), in em: fragments stack
		// with widgets between them. Bottom: negative = automatic (one ImGui::NewLine()).
		float fragmentGapTop = 0.0f;
		float fragmentGapBottom = -1.0f;
	};
	Style style;

	// The automatic link color: the text color, shifted to blue
	static ImVec4 default_link_color();
	// Resolved colors (automatic ones derived from the ImGui style)
	ImVec4 link_color() const;
	// Decorates the last item as a link (underline, hand cursor, tooltip with the url when
	// style.linkTooltip): returns true when it was clicked. Draw the text with link_color() first.
	static bool link_item(const Style& style, const char* url);
	ImVec4 admonition_color(AdmonitionKind kind) const;

	//for example, these flags can be changed in div callback

	//draw border
	bool m_table_border = true;
	//render header in a different way than other rows
	bool m_table_header_highlight = true;

protected:

	virtual void BLOCK_DOC(bool);
	virtual void BLOCK_QUOTE(bool);
	virtual void BLOCK_UL(const MD_BLOCK_UL_DETAIL*, bool);
	virtual void BLOCK_OL(const MD_BLOCK_OL_DETAIL*, bool);
	virtual void BLOCK_LI(const MD_BLOCK_LI_DETAIL*, bool);
	virtual void BLOCK_HR(bool e);
	virtual void BLOCK_H(const MD_BLOCK_H_DETAIL* d, bool e);
	virtual void BLOCK_CODE(const MD_BLOCK_CODE_DETAIL*, bool);
	virtual void BLOCK_HTML(bool);
	virtual void BLOCK_P(bool);
	virtual void BLOCK_TABLE(const MD_BLOCK_TABLE_DETAIL*, bool);
	virtual void BLOCK_THEAD(bool);
	virtual void BLOCK_TBODY(bool);
	virtual void BLOCK_TR(bool);
	virtual void BLOCK_TH(const MD_BLOCK_TD_DETAIL*, bool);
	virtual void BLOCK_TD(const MD_BLOCK_TD_DETAIL*, bool);

	virtual void SPAN_EM(bool e);
	virtual void SPAN_STRONG(bool e);
	virtual void SPAN_A(const MD_SPAN_A_DETAIL* d, bool e);
	virtual void SPAN_IMG(const MD_SPAN_IMG_DETAIL*, bool);
	virtual void SPAN_CODE(bool);
	virtual void SPAN_DEL(bool);
	virtual void SPAN_LATEXMATH(bool);
	virtual void SPAN_LATEXMATH_DISPLAY(bool);
	virtual void SPAN_WIKILINK(const MD_SPAN_WIKILINK_DETAIL*, bool);
	virtual void SPAN_U(bool);

	////////////////////////////////////////////////////////////////////////////

	struct image_info
	{
		ImTextureRef texture;   // a backend id, or an ImTextureData created by the backend at render time
		ImVec2	size;
		ImVec2	uv0;
		ImVec2	uv1;
	};

	// none: nothing is drawn; ready: nfo is filled; loading: a spinner is drawn in place of the image
	enum class image_status { none, ready, loading };
	// The image at m_img_src. nfo.size is in logical pixels: the renderer applies the font scales.
	virtual image_status get_image(image_info& nfo) const;
	// The spinner drawn while an image is loading
	virtual void draw_loading_spinner();

	// A formula as a texture, in physical pixels (see get_latex_texture)
	struct latex_texture
	{
		ImTextureRef texture;       // invalid (no data, no id): this formula failed, nothing is drawn
		ImVec2 size_px = ImVec2(0.0f, 0.0f);
		float baseline_px = 0.0f;   // from the top of the texture to the text baseline
		std::string error;          // set when the formula is invalid: the source is shown with this message as a tooltip
	};
	// The formula rendered at font_size_px (physical pixels), with the display style for $$...$$.
	// Return false when LaTeX is not available, or when the formula is invalid (then fill out.error):
	// the formula's source is shown instead.
	virtual bool get_latex_texture(const std::string& latex, float font_size_px, ImU32 color, bool display, latex_texture& out) const;

	struct MdSizedFont
	{
		ImFont* font;
		float size;
	};
	virtual MdSizedFont get_font() const;

	virtual ImVec4 get_color() const;

    // By default, code blocks are rendered as text with the code font, but you can override this
    virtual void render_code_block();

    // Code blocks may be rendered inside a child window (see the overrides of render_code_block).
    // Return false where child windows cannot be used (e.g. inside the canvas of a node editor):
    // code blocks are then rendered as inline code.
    virtual bool can_use_child_windows() const { return true; }

    // Draw a non-interactive checkbox glyph for a task-list item bullet.
    // Called from BLOCK_LI when MD_BLOCK_LI_DETAIL::is_task is non-zero.
    virtual void render_task_marker(bool checked);

    // Draw the admonition header row (icon/label) after detecting
    // a GitHub-style "[!NOTE]" / "[!TIP]" / ... marker at the start
    // of a blockquote.
    virtual void render_admonition_header(AdmonitionKind kind);

	//url == m_href
	virtual void open_url() const;
	// A wikilink [[target]] or [[target|label]] was clicked (m_href == target; MD_FLAG_WIKILINKS)
	virtual void open_wikilink() const;
	// A heading was rendered (its text without markup)
	virtual void heading(int level, const std::string& text);

	//returns true if the term has been processed
	virtual bool render_entity(const char* str, const char* str_end);

	//returns true if the term has been processed
	virtual bool check_html(const char* str, const char* str_end);

	//called when '\n' in source text where it is not semantically meaningful
	virtual void soft_break();

	//e==true : enter
	//e==false : leave
	virtual void html_div(const std::string& dclass, bool e);
	////////////////////////////////////////////////////////////////////////////

    virtual void push_code_style();
    virtual void pop_code_style();

	//current state
	std::string m_href;//empty if no link/image
    std::string m_img_src;//empty if no link/image

	bool m_is_underline=false;
	bool m_is_strikethrough = false;
	bool m_is_em = false;
	bool m_is_strong = false;
	// Inline HTML span state (driven by <sub>, <sup>, <kbd>, <mark>)
	bool m_is_sub = false;
	bool m_is_sup = false;
	bool m_is_kbd = false;
	bool m_is_error = false;         // inside <md-error title="reason">: error color, the reason as a tooltip
	std::string m_error_title;
	bool m_is_mark = false;

	// <details>/<summary> state. One bool per currently-open <details>
	// (true = expanded, false = collapsed -> content is skipped).
	// m_details_awaiting_summary is set between <details> and the first
	// <summary>…</summary>, during which the summary's inner text is
	// captured as the header label.
	std::vector<bool> m_details_open_stack;
	bool m_details_awaiting_summary = false;
	// True when the current <details ...> tag had the `open` attribute,
	// so the next <summary>…</summary> should start expanded.
	bool m_details_awaiting_open_default = false;
	// True for exactly one MD_TEXT_HTML event right after </details>
	// is processed — lets us swallow the trailing "\n" that md4c emits
	// as a separate chunk, so content after the collapsible sits tight.
	bool m_details_suppress_next_raw_html = false;
	int m_details_id_counter = 0;  // reset in print(); incremented per <summary> for unique PushID

	// <pre>…</pre> state. Between the tags, raw HTML text is buffered
	// in m_pre_buffer; it's then rendered as monospaced block text
	// (no code-block frame, no syntax coloring). Reset in print().
	bool m_in_pre = false;
	std::string m_pre_buffer;

	bool m_is_table_header = false;
	bool m_is_table_body = false;
	bool m_is_image = false;
	bool m_is_wikilink = false;
	std::string m_heading_text;  // accumulated while inside a heading
	// <center> ... </center>: content centered with the aligned-cell trick
	bool m_in_center = false;
	int m_center_vtx_start = 0;
	float m_center_width = 0.0f;
	bool m_is_code = false; // true for block code and inline code
    bool m_is_code_block = false;
	bool m_is_latex_inline = false; // LaTeX math state (populated when EnableLatex() has been called)
	bool m_is_latex_display = false;
	std::string m_latex_buffer;
	bool m_skip_next_block_gap = true;
	int m_quote_depth = 0;
	std::vector<ImVec2> m_quote_start;  // position (screen coords) of the indented content column at quote entry; used at exit to draw the vertical bar

	// Current quote's kind (None if a plain quote). Cleared on quote enter,
	// set by admonition detection in text().
	AdmonitionKind m_admonition_kind = AdmonitionKind::None;
	// True on entry to a quote while we're waiting for the first text to
	// decide whether it's an admonition. Any span enter or non-match clears it.
	bool m_admonition_scan_pending = false;
	// After detecting a marker like "[!NOTE]", skip the following soft break
	// so the admonition label and the content don't collide on one line.
	bool m_admonition_skip_next_softbr = false;
    std::string m_code_block_language;
    std::string m_code_block;
	unsigned m_hlevel=0; // 0 - no heading

private:

	int text(MD_TEXTTYPE type, const char* str, const char* str_end);
	int block(MD_BLOCKTYPE type, void* d, bool e);
	int span(MD_SPANTYPE type, void* d, bool e);

	void render_text(const char* str, const char* str_end);
	void render_latex_span(bool display);
    void render_inline_code(const char* str, const char* str_end);

	void set_font(bool e);
	void set_color(bool e);
	void set_href(bool e, const MD_ATTRIBUTE& src);
    void set_img_src(bool e, const MD_ATTRIBUTE& src);

	static void line(ImColor c, bool under);

	//table state
	int m_table_id_counter = 0;  // reset in print(); incremented per table for unique PushID
	bool m_table_open = false;   // BeginTable() succeeded for the current table
	// Per-cell alignment state, used while rendering a TH/TD whose
	// align is CENTER or RIGHT. The cell opens a BeginGroup(), notes
	// the drawlist vertex count, and on exit computes the content
	// width from the group, then shifts the vertices horizontally so
	// the content is centered/right-aligned within the cell.
	MD_ALIGN m_cell_align = MD_ALIGN_DEFAULT;
	int m_cell_vtx_start = 0;
	float m_cell_width = 0.0f;

	//list state
	struct list_info
	{
		unsigned	cur_ol;
		char		delim;
		bool		is_ol;
		bool		first_item_pending;
	};
	std::vector<list_info> m_list_stack;

	std::vector<std::string> m_div_stack;

	MD_PARSER m_md;
};

} // namespace RichMd

#endif  /* RICHMD_RENDERER_H */