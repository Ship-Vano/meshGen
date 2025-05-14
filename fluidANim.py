import numpy as np
from vispy import app, gloo

# Генерация данных
num_particles = 1_000_000
positions = np.fromfile("particles.bin", dtype=np.float32).reshape(-1, 2)

# Исправленные шейдеры с явным указанием версии
vertex_shader = """
#version 120
attribute vec2 a_position;
void main() {
    gl_Position = vec4(a_position * 2.0 - 1.0, 0.0, 1.0);
    gl_PointSize = 2.0;
}
"""

fragment_shader = """
#version 120
void main() {
    gl_FragColor = vec4(0.0, 1.0, 0.0, 1.0);
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        # Явно указываем бэкенд
        app.use_app('glfw')
        super().__init__(size=(800, 800), title="Particles", keys='interactive')


        self.program = gloo.Program(vertex_shader, fragment_shader)
        self.program['a_position'] = gloo.VertexBuffer(positions.astype(np.float32))

    def on_draw(self, event):
        gloo.clear(color='black')
        self.program.draw('points')


canvas = Canvas()
app.run()