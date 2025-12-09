import moderngl
import numpy as np
import glm

class Mesh:
    def __init__(self, ctx, vertices, normals, faces):
        self.ctx = ctx
        self.num_indices = faces.size
        
        # Flatten and interleave data: [x, y, z, nx, ny, nz]
        # Vertices and Normals usually come from Marching Cubes as (N, 3) arrays
        # Faces is (M, 3) indices. ModernGL needs vertices unindexed for simple flat shading if we don't use EBO correctly,
        # but Marching Cubes returns indexed geometry.
        
        # However, normal generation often returns per-vertex normals.
        # So we can use indexed rendering.
        
        v_data = np.hstack([vertices, normals]).astype('f4')
        
        self.vbo = self.ctx.buffer(v_data.tobytes())
        self.ibo = self.ctx.buffer(faces.astype('i4').tobytes())
        
        # Shader
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 m_view;
                uniform mat4 m_proj;
                uniform vec3 camera_pos;

                in vec3 in_position;
                in vec3 in_normal;
                
                out vec3 v_pos;
                out vec3 v_normal;
                out vec3 v_camera_pos;

                void main() {
                    v_pos = in_position;
                    v_normal = in_normal;
                    v_camera_pos = camera_pos;
                    gl_Position = m_proj * m_view * vec4(v_pos, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 v_pos;
                in vec3 v_normal;
                in vec3 v_camera_pos;
                out vec4 f_color;

                void main() {
                    vec3 N = normalize(v_normal);
                    vec3 L = normalize(vec3(5.0, 10.0, 5.0) - v_pos); // Light pos
                    vec3 V = normalize(v_camera_pos - v_pos);
                    
                    // Ambient
                    float ambient = 0.1;
                    
                    // Diffuse (Double-sided)
                    float diff = max(dot(N, L), 0.0) + max(dot(-N, L), 0.0) * 0.5;
                    
                    // Specular
                    vec3 R = reflect(-L, N);
                    float spec = pow(max(dot(V, R), 0.0), 32.0);
                    
                    vec3 color = vec3(0.0, 0.8, 1.0); // Cyan
                    vec3 final = color * (ambient + diff) + vec3(1.0) * spec * 0.5;
                    
                    f_color = vec4(final, 1.0);
                }
            '''
        )
        
        self.vao = self.ctx.vertex_array(
            self.prog, 
            [
                (self.vbo, '3f 3f', 'in_position', 'in_normal')
            ],
            index_buffer=self.ibo
        )

    def render(self, camera):
        self.prog['m_view'].write(camera.get_view_matrix())
        self.prog['m_proj'].write(camera.get_projection_matrix())
        self.prog['camera_pos'].write(camera.position)
        self.vao.render(moderngl.TRIANGLES)
