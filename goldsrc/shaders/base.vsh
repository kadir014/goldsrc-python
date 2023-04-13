#version 330


in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;

out vec2 v_uv;
out vec3 v_normal;
out vec3 v_frag_position;

uniform mat4 u_model;
uniform mat4 u_projection;
uniform mat4 u_view;


void main() {
    gl_Position = u_projection * u_view * u_model * vec4(in_position, 1.0);

    v_uv = in_uv;

    v_frag_position = vec3(u_model * vec4(in_position, 1.0));

    v_normal = mat3(transpose(inverse(u_model))) * in_normal;
}