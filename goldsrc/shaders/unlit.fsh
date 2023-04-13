#version 330


in vec3 v_normal;
in vec2 v_uv;
in vec3 v_frag_position;

out vec4 out_color;

uniform sampler2D s_texture;


void main() {
    out_color = texture(s_texture, v_uv);
}