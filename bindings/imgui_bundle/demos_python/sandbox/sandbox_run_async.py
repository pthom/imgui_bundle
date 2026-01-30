"""Demonstrates how to use immapp.run_async with asyncio.
"""
import asyncio
from imgui_bundle import imgui, immapp

def gui():
    imgui.text("Hello with run_async!")
    if imgui.button("Exit"):
        from imgui_bundle import hello_imgui
        hello_imgui.get_runner_params().app_shall_exit = True

async def launch_gui():
    await immapp.run_async(gui, window_title="create_task test")
    print("GUI closed")

asyncio.run(launch_gui())
