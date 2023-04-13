#version 330


in vec3 in_position;

uniform mat4 u_projection;
uniform mat4 u_view;

out vec3 v_uv;


void main() {
    gl_Position = u_projection * u_view * vec4(in_position, 1.0);

    v_uv = in_position;
}