// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2023 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include "hello_imgui/hello_imgui.h"
#include "hello_imgui/hello_imgui_include_opengl.h"
# include "imgui.h"
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
#include "ImFileDialog/ImFileDialog.h"

#include <string>

void setup_texture_loader()
{
    // ImFileDialog requires you to set the CreateTexture and DeleteTexture
    ifd::FileDialog::Instance().CreateTexture = [](uint8_t* data, int w, int h, char fmt) -> ImTextureID {
        GLuint tex;

        glGenTextures(1, &tex);
        glBindTexture(GL_TEXTURE_2D, tex);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, (fmt == 0) ? GL_BGRA : GL_RGBA, GL_UNSIGNED_BYTE, data);
        glGenerateMipmap(GL_TEXTURE_2D);
        glBindTexture(GL_TEXTURE_2D, 0);

        return (ImTextureID)(size_t)tex;
    };

    ifd::FileDialog::Instance().DeleteTexture = [](ImTextureID tex) {
        GLuint texID = (GLuint)((uintptr_t)tex);
        glDeleteTextures(1, &texID);
    };
}


void gui()
{
    ImGui::Begin("Control Panel");
    if (ImGui::Button("Open file"))
        ifd::FileDialog::Instance().Open("ShaderOpenDialog", "Open a shader", "Image file (*.png;*.jpg;*.jpeg;*.bmp;*.tga){.png,.jpg,.jpeg,.bmp,.tga},.*", true);
    if (ImGui::Button("Open directory"))
        ifd::FileDialog::Instance().Open("DirectoryOpenDialog", "Open a directory", "");
    if (ImGui::Button("Save file"))
        ifd::FileDialog::Instance().Save("ShaderSaveDialog", "Save a shader", "*.sprj {.sprj}");
    ImGui::End();

    // file dialogs
    if (ifd::FileDialog::Instance().IsDone("ShaderOpenDialog")) {
        if (ifd::FileDialog::Instance().HasResult()) {
            const std::vector<std::filesystem::path>& res = ifd::FileDialog::Instance().GetResults();
            for (const auto& r : res) // ShaderOpenDialog supports multiselection
                printf("OPEN[%s]\n", r.u8string().c_str());
        }
        ifd::FileDialog::Instance().Close();
    }
    if (ifd::FileDialog::Instance().IsDone("DirectoryOpenDialog")) {
        if (ifd::FileDialog::Instance().HasResult()) {
            std::string res = ifd::FileDialog::Instance().GetResult().string();
            printf("DIRECTORY[%s]\n", res.c_str());
        }
        ifd::FileDialog::Instance().Close();
    }
    if (ifd::FileDialog::Instance().IsDone("ShaderSaveDialog")) {
        if (ifd::FileDialog::Instance().HasResult()) {
            std::string res = ifd::FileDialog::Instance().GetResult().string();
            printf("SAVE[%s]\n", res.c_str());
        }
        ifd::FileDialog::Instance().Close();
    }

}


int main(int , char *[])
{
    setup_texture_loader();

    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = gui;
    HelloImGui::Run(runnerParams);
    return 0;
}
