from imgui_bundle import imgui, hello_imgui

def my_register_tests():
    engine = hello_imgui.get_imgui_test_engine()

    test_inc = imgui.test_engine.register_test(engine, "Demo Tests", "Increment")
    def test_inc_func(ctx: imgui.test_engine.TestContext) -> None:
        ctx.item_click("**/Increment")
    test_inc.test_func = test_inc_func

    test_press = imgui.test_engine.register_test(engine, "Demo Tests", "Press keys")
    def test_press_func(ctx: imgui.test_engine.TestContext) -> None:
        ctx.key_down(imgui.Key.left_alt)
        ctx.key_down(imgui.Key.a)
        ctx.key_up(imgui.Key.a)
        ctx.key_up(imgui.Key.left_alt)
    test_press.test_func = test_press_func


count = 0
nb_alt_a = 0

def gui():
    global count, nb_alt_a

    imgui.text("Hello, world!")
    if imgui.button("Increment"):
        count += 1
    imgui.text("count = %d" % count)

    if imgui.is_key_down(imgui.Key.left_alt) and imgui.is_key_down(imgui.Key.a):
        nb_alt_a += 1

    imgui.text(f"nb_alt_a = {nb_alt_a}")

    imgui.show_id_stack_tool_window()
    imgui.test_engine.show_test_engine_windows(
        hello_imgui.get_imgui_test_engine(), True
    )


def main():
    params = hello_imgui.RunnerParams()
    params.callbacks.show_gui = gui
    params. callbacks.register_tests = my_register_tests
    params.use_imgui_test_engine = True

    hello_imgui.run(params)


if __name__ == "__main__":
    main()

