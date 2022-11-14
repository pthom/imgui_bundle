#include "ImFileDialog/ImFileDialog.h"
#include "hello_imgui/hello_imgui_include_opengl.h"

void ImFileDialogSetupTextureLoader()
{
    // ImFileDialog requires you to set the CreateTexture and DeleteTexture
    ifd::FileDialog::Instance().CreateTexture = [](uint8_t* data, int w, int h, char fmt) -> void*
    {
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

        return (void*)(size_t)tex;
    };

    ifd::FileDialog::Instance().DeleteTexture = [](void* tex)
    {
        GLuint texID = (GLuint)((uintptr_t)tex);
        glDeleteTextures(1, &texID);
    };
}
