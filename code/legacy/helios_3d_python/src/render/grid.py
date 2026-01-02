import moderngl
import numpy as np
import glm

class InfiniteGrid:
    def __init__(self, ctx):
        self.ctx = ctx
        
        # Shader
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 m_view;
                uniform mat4 m_proj;
                uniform vec3 camera_pos;

                in vec3 in_position;
                
                out vec3 v_pos;
                out vec3 v_camera_pos;

                void main() {
                    v_pos = in_position * 100.0; // Scale grid
                    v_camera_pos = camera_pos;
                    gl_Position = m_proj * m_view * vec4(v_pos, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 v_pos;
                in vec3 v_camera_pos;
                out vec4 f_color;

                void main() {
                    // Grid Logic
                    vec2 coord = v_pos.xz;
                    vec2 derivative = fwidth(coord);
                    vec2 grid = abs(fract(coord - 0.5) - 0.5) / derivative;
                    float line = min(grid.x, grid.y);
                    
                    // Fade out
                    float d = distance(v_pos, vec3(v_camera_pos.x, 0.0, v_camera_pos.z));
                    float alpha = 1.0 - smoothstep(10.0, 50.0, d);
                    
                    if(line < 1.0 && alpha > 0.0) {
                        vec3 color = vec3(0.5);
                        // Axis highlights
                        if(abs(v_pos.x) < 0.1) color = vec3(1.0, 0.0, 0.0); // Z axis (local logic, wait x=0 is Z axis visual)
                        if(abs(v_pos.z) < 0.1) color = vec3(0.0, 0.0, 1.0); // X axis
                        
                        f_color = vec4(color, alpha * 0.5);
                    } else {
                        discard;
                    }
                }
            '''
        )
        
        # Quad geometry (XZ plane) - simplified for "infinite" illusion
        # Actually for infinite grid we usually draw a full screen quad and raytrace, 
        # or a large quad. Let's use a large quad for simplicity.
        vertices = np.array([
            -1.0, 0.0, -1.0,
             1.0, 0.0, -1.0,
            -1.0, 0.0,  1.0,
             1.0, 0.0,  1.0,
        ], dtype='f4')
        
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.vertex_array(self.prog, [(self.vbo, '3f', 'in_position')])

    def render(self, camera):
        self.ctx.enable(moderngl.BLEND)
        
        self.prog['m_view'].write(camera.get_view_matrix())
        self.prog['m_proj'].write(camera.get_projection_matrix())
        self.prog['camera_pos'].write(camera.position)
        
        self.vao.render(moderngl.TRIANGLE_STRIP)
        
        self.ctx.disable(moderngl.BLEND)
