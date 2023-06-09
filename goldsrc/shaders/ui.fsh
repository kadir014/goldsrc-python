#version 330


in vec2 v_uv;

out vec4 out_color;

uniform sampler2D s_texture;


void main() {
    out_color = texture(s_texture, v_uv);
}