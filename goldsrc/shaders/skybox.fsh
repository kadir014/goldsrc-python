#version 330


in vec3 v_uv;

out vec4 out_color;

uniform samplerCube s_cubemap;


void main() {
    out_color = texture(s_cubemap, v_uv);
}