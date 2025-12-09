import glm
import math

class Camera:
    def __init__(self, aspect_ratio=1.6):
        self.position = glm.vec3(5.0, 5.0, 5.0)
        self.target = glm.vec3(0.0, 0.0, 0.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        
        # Orbit params
        self.radius = 10.0
        self.yaw = 45.0
        self.pitch = 30.0
        
        # Projection
        self.fov = 45.0
        self.aspect_ratio = aspect_ratio
        self.near = 0.1
        self.far = 1000.0
        
        self.update_vectors()

    def update_vectors(self):
        # Convert spherical to cartesian
        rad_yaw = glm.radians(self.yaw)
        rad_pitch = glm.radians(self.pitch)
        
        x = self.radius * math.cos(rad_pitch) * math.sin(rad_yaw)
        y = self.radius * math.sin(rad_pitch)
        z = self.radius * math.cos(rad_pitch) * math.cos(rad_yaw)
        
        self.position = glm.vec3(x, y, z) + self.target

    def rotate(self, dx, dy):
        sensitivity = 0.5
        self.yaw -= dx * sensitivity
        self.pitch -= dy * sensitivity
        
        # Clamp pitch to avoid gimbal lock
        self.pitch = max(-89.0, min(89.0, self.pitch))
        self.update_vectors()

    def pan(self, dx, dy):
        # Calculate right and up vectors relative to camera
        forward = glm.normalize(self.target - self.position)
        right = glm.normalize(glm.cross(forward, self.up))
        cam_up = glm.normalize(glm.cross(right, forward))
        
        factor = self.radius * 0.002
        self.target -= (right * dx * factor)
        self.target += (cam_up * dy * factor)
        self.update_vectors()

    def zoom(self, delta):
        if delta > 0:
            self.radius *= 0.9
        else:
            self.radius *= 1.1
        
        self.radius = max(0.1, min(100.0, self.radius))
        self.update_vectors()

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.target, self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(self.fov), self.aspect_ratio, self.near, self.far)
