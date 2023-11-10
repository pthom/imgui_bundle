# -*- coding: utf-8 -*-
from __future__ import absolute_import

from imgui_bundle import imgui
import cocos

from .import compute_fb_scale
from .pyglet_backend import PygletMixin
from .opengl_backend import FixedPipelineRenderer


class ImguiLayer(PygletMixin, cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(ImguiLayer, self).__init__()

        window_size = cocos.director.director.window.get_size()
        viewport_size = cocos.director.director.window.get_viewport_size()

        self.io = imgui.get_io()
        self.io.display_size = window_size
        self.io.display_framebuffer_scale = compute_fb_scale(window_size, viewport_size)

        self.renderer = FixedPipelineRenderer()
