import moderngl
import pygame
import numpy as np
from pyrr import Matrix44

from view.torus.geometry import generate_torus_mesh
from view.torus.shaders import VERTEX_SHADER, FRAGMENT_SHADER
from view.torus.camera import OrbitalCamera
from view.torus.texture_mapper import GridTextureMapper
from lifeform import Lifeform
from typing import List, Tuple

class TorusRenderer:
    """
    Renders the CA grid mapped onto a 3D torus surface.
    """
    
    def __init__(self, pygame_surface: pygame.Surface, grid_size: tuple, lifeforms: List[Lifeform]):
        self.grid_width, self.grid_height = grid_size
        width, height = pygame_surface.get_size()
        
        try:
            self.ctx = moderngl.create_context()
        except Exception as e:
            raise RuntimeError(f"Error creating moderngl context: {e}") from e

        # Torus geometry parameters
        self.major_radius = 1.0
        self.minor_radius = 0.4
        self.major_segments = 64
        self.minor_segments = 32
        
        # Camera
        self.camera = OrbitalCamera(distance=3.0, aspect_ratio=width / height)
        
        # GL resources
        self.vbo = None
        self.ibo = None
        self.vao = None
        self.shader = None
        self.grid_texture = None
        self.texture_mapper = GridTextureMapper(self.grid_width, self.grid_height, lifeforms)
        self._init_gl_resources()

    def _init_gl_resources(self):
        """Initialize OpenGL buffers, shaders, and torus mesh."""
        self._create_torus_mesh()
        self._compile_shaders()
        self._create_grid_texture()

    def _create_torus_mesh(self):
        vbo_data, ibo_data = generate_torus_mesh(
            self.major_radius, self.minor_radius,
            self.major_segments, self.minor_segments
        )
        self.vbo = self.ctx.buffer(vbo_data.tobytes())
        self.ibo = self.ctx.buffer(ibo_data.tobytes())

    def _compile_shaders(self):
        # A simplified shader that doesn't use textures
        vertex_shader = """
        #version 330 core
        in vec3 in_position;
        in vec3 in_normal;
        in vec2 in_uv;
        out vec3 v_normal;
        out vec2 v_uv;
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        void main() {
            v_normal = mat3(model) * in_normal;
            v_uv = in_uv;
            gl_Position = projection * view * model * vec4(in_position, 1.0);
        }
        """
        fragment_shader = """
        #version 330 core
        in vec3 v_normal;
        in vec2 v_uv;
        out vec4 out_color;
        uniform sampler2D grid_texture;
        void main() {
            vec3 cell_color = texture(grid_texture, v_uv).rgb;
            vec3 n = normalize(v_normal);
            float shade = 0.5 + 0.5 * n.z;
            out_color = vec4(cell_color * shade, 1.0);
        }
        """
        self.shader = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        self.vao = self.ctx.vertex_array(
            self.shader,
            [(self.vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
            self.ibo
        )

    def _create_grid_texture(self):
        self.grid_texture = self.ctx.texture(
            (self.grid_width, self.grid_height),
            3,
            dtype='f1'
        )
        self.grid_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.grid_texture.repeat_x = True
        self.grid_texture.repeat_y = True

    def update_texture(self, grid_state: np.ndarray, lifespans: np.ndarray):
        texture_data = self.texture_mapper.update(grid_state, lifespans)
        self.grid_texture.write(texture_data.tobytes())

    def render(self):
        """
        Render the torus to the active OpenGL context.
        """
        self.camera.update()

        display_info = pygame.display.Info()
        width, height = display_info.current_w, display_info.current_h
        self.ctx.viewport = (0, 0, width, height)
        self.ctx.screen.use()
        self.ctx.clear(0.1, 0.1, 0.15)
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.shader['model'].write(Matrix44.from_eulers((0, self.camera.azimuth, 0), dtype='f4').tobytes())
        self.shader['view'].write(self.camera.view_matrix.astype('f4').tobytes())
        self.shader['projection'].write(self.camera.projection_matrix.astype('f4').tobytes())
        self.grid_texture.use(0)
        self.shader['grid_texture'].value = 0

        self.vao.render(moderngl.TRIANGLES)

    def handle_mouse_down(self, pos: Tuple[int, int]):
        self.camera.handle_mouse_down(pos)

    def handle_mouse_up(self):
        self.camera.handle_mouse_up()

    def handle_mouse_move(self, pos: Tuple[int, int]):
        self.camera.handle_mouse_move(pos)

    def handle_scroll(self, direction: int):
        self.camera.handle_scroll(direction)

    def on_resize(self, width: int, height: int):
        self.camera.on_resize(width, height)
        self.ctx.viewport = (0, 0, width, height)

    def cleanup(self):
        if self.grid_texture:
            self.grid_texture.release()
        if self.vao:
            self.vao.release()
        if self.vbo:
            self.vbo.release()
        if self.ibo:
            self.ibo.release()
        if self.shader:
            self.shader.release()
