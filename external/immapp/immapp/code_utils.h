#include <fplus/fplus.hpp>

namespace CodeUtils
{
    using Lines = std::vector<std::string>;
    using String = std::string;

    std::string Unindent(const std::string& code, bool is_markdown);
    std::string UnindentCode(const std::string& code);
    std::string UnindentMarkdown(const std::string& code);
} // namespace CodeUtils
