#version 330


in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;
in vec3 in_tangent;
in vec3 in_bitangent;

out mat3 v_tbn;
out vec2 v_uv;
out vec3 v_frag_position;

uniform mat4 u_model;
uniform mat4 u_projection;
uniform mat4 u_view;


void main() {
    gl_Position = u_projection * u_view * u_model * vec4(in_position, 1.0);

    v_uv = in_uv;

    v_frag_position = vec3(u_model * vec4(in_position, 1.0));

    vec3 tangent =   normalize(vec3(u_model * vec4(in_tangent, 0.0)));
    vec3 bitangent = normalize(vec3(u_model * vec4(in_bitangent, 0.0)));
    vec3 normal =    normalize(vec3(u_model * vec4(in_normal, 0.0)));

    v_tbn = transpose(mat3(tangent, bitangent, normal));
}