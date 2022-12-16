#pragma once

#include <string>
#include <vector>

std::string UnindentCode(const std::string& code, bool flag_strip_empty_lines = false, bool is_markdown = false);
