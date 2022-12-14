#include "code_str_utils.h"
#include <fplus/fplus.hpp>

using Lines = std::vector<std::string>;
using String = std::string;



bool IsSpaceOrEmpty(const String& s)
{
    return fplus::trim_whitespace(s).size() == 0;
}


Lines StripEmptyLinesInList(const Lines& code_lines)
{
    Lines r;
    r = fplus::drop_while(IsSpaceOrEmpty, code_lines);
    r = fplus::reverse(r);
    r = fplus::drop_while(IsSpaceOrEmpty, r);
    r = fplus::reverse(r);
    return r;
}


String StripEmptyLines(const String& s)
{
    auto lines = fplus::split_lines(true, s);
    auto lines_stripped = StripEmptyLinesInList(lines);
    String r = fplus::join(std::string("\n"), lines_stripped);
    return r;
}


int CountSpacesAtStartOfLine(const String& line)
{
    int nbSpacesthisLine = 0;
    for (auto c : line)
        if (c == ' ')
            ++nbSpacesthisLine;
        else
            return nbSpacesthisLine;
    return nbSpacesthisLine;
}


String RemoveTrailingSpace(const String& line)
{
    return fplus::trim_right(' ', line);
}


int ComputeCodeIndentSize(const String& code)
{
    auto lines = fplus::split_lines(true, code);
    for (const auto& line: lines)
    {
        if (IsSpaceOrEmpty(line))
            continue;
        return CountSpacesAtStartOfLine(line);
    }
    return 0;
}


std::string UnindentCode(const std::string& code, bool flag_strip_empty_lines, bool is_markdown)
{
    int indentSize = ComputeCodeIndentSize(code);

    String whatToReplace;
    for (auto i = 0; i < indentSize; ++i)
        whatToReplace += " ";

    auto lines = fplus::split_lines(true, code);

    Lines processedLines;
    for (const auto& line: lines)
    {
        String processedLine;
        if (fplus::is_prefix_of(whatToReplace, line))
            processedLine = fplus::drop(indentSize, line);
        else
            processedLine = line;

        if (is_markdown)
            processedLines.push_back(processedLine + " ");
        else
            processedLines.push_back(RemoveTrailingSpace(processedLine));
    }

    String r = fplus::join(std::string("\n"), processedLines);
    return r;
}
