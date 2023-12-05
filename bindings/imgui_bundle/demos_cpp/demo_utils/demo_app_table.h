#pragma once
#include <vector>
#include <string>
#include "immapp/snippets.h"


struct DemoApp
{
    std::string DemoFile;
    std::string Explanation;
    bool IsPythonBackendDemo = false;
};


class DemoAppTable
{
public:
    DemoAppTable(const std::vector<DemoApp> &demoApps, const std::string &demoPythonFolder,
                 const std::string &demo_cpp_folder, const std::string &demoPythonBackendFolder);

    void Gui();

private:
    std::string _DemoPythonFilePath(const DemoApp &demo_app);
    std::string _DemoCppFilePath(const DemoApp &demo_app);
    void _SetDemoApp(const DemoApp &demo_app);

    // members
    Snippets::SnippetData _snippetCpp, _snippetPython;
    std::vector<DemoApp> _demoApps;
    DemoApp _currentApp;
    std::string _demoPythonFolder;
    std::string _demoCppFolder;
    std::string _demoPythonBackendFolder;
};
