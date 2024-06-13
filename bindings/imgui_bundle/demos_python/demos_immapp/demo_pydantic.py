from pydantic import BaseModel
from imgui_bundle import immapp, imgui, imgui_md, ImVec2_Pydantic, ImVec4_Pydantic, ImColor_Pydantic
from imgui_bundle.immapp.immapp_code_utils import show_python_code, show_json_dict


class MyParam(BaseModel):
    """A simple pydantic model with imgui_pydantic fields"""
    vec2: ImVec2_Pydantic = ImVec2_Pydantic(1, 2)
    vec4: ImVec4_Pydantic = ImVec4_Pydantic(1, 2, 3, 4)
    color: ImColor_Pydantic = ImColor_Pydantic(0.1, 0.2, 0.3, 0.4)


def demo_pydantic():
    my_param = MyParam()  # Create an instance of MyParam
    imgui_md.render_unindented(f"**my_param:** `{my_param}`")  # Show the instance
    as_json_dict = my_param.model_dump(mode="json")  # Convert the instance to a JSON dict

    # Show the JSON dict
    imgui_md.render_unindented("**as_json_dict**")
    show_json_dict(as_json_dict)

    # Create another instance of MyParam from the JSON dict and show it
    my_param2 = MyParam.model_validate(as_json_dict)
    imgui_md.render_unindented(f"**my_param2:** `{my_param2}`")

    # Test that the two instances are equal
    imgui_md.render_unindented(f"**Are Equal:** `{my_param == my_param2=}`")



def gui():
    imgui_md.render_unindented("""
    # How to use ImVec2 and ImVec4 with Pydantic

    imgui_bundle provide `ImVec2_Pydantic`, `ImVec4_Pydantic`, `ImColor_Pydantic` which are synonyms for
    `ImVec2`, `ImVec4`, `ImColor` (and compatible with Pydantic)

    **Let's define a class like this:**
    """)
    imgui.new_line()
    show_python_code(MyParam)

    imgui_md.render_unindented("**Let's define a function that checks that it can be serialized and validated with Pydantic:**")
    imgui.new_line()
    show_python_code(demo_pydantic)

    imgui.separator_text("And this is the output of the function")
    demo_pydantic()



immapp.run_with_markdown(gui, window_size=(800, 950))
