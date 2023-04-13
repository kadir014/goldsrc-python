#version 330


in mat3 v_tbn;
in vec2 v_uv;
in vec3 v_frag_position;

out vec4 out_color;

uniform vec3 u_view_position;
uniform vec3 u_light_position;

uniform vec3 u_light_color;
uniform float u_ambient_intensity;
uniform float u_diffuse_intensity;
uniform float u_specular_intensity;
uniform float u_specular_power;

uniform sampler2D s_texture;
uniform sampler2D s_normal;


void main() {
    vec3 normal = texture(s_normal, v_uv).rgb;
    normal = normalize(normal * 2.0 - 1.0);

    // Ambient lighting
    vec3 ambient = u_ambient_intensity * u_light_color;

    // Diffuse lighting
    vec3 light_dir = v_tbn * normalize(u_light_position - v_frag_position);
    float diffuse_value = max(dot(normal, light_dir), 0.0);
    vec3 diffuse = diffuse_value * u_light_color * u_diffuse_intensity;

    // Specular lighting
    vec3 view_dir = v_tbn * normalize(u_view_position - v_frag_position);
    vec3 reflect_dir = reflect(-light_dir, normal);
    float specular_value = pow(max(dot(view_dir, reflect_dir), 0.0), u_specular_power);
    vec3 specular = specular_value * u_light_color * u_specular_intensity;

    vec4 tex = texture(s_texture, v_uv);
    vec3 color = tex.rgb * (ambient + diffuse + specular);
    out_color = vec4(color, tex.a);
}