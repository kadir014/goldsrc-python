#version 330


in vec3 v_normal;
in vec2 v_uv;
in vec3 v_frag_position;

out vec4 out_color;

uniform vec4 u_color;


void main() {
    out_color = u_color;
}