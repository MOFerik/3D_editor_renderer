#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;
in vec3 fragPos;

struct Light {
  vec3 position;
  vec3 Ia;
  vec3 Id;
  vec3 Is;
};

uniform sampler2D u_texture_1;
uniform Light light;

void main() {
    float gamma = 2.2;
    vec3 color = vec3(1, 0.4, 0);
    color = pow(color, vec3(gamma));

    color = pow(color, 1/vec3(gamma));
    fragColor = vec4(color, 1.0);
}