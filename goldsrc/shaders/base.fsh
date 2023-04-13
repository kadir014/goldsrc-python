#version 330


in vec3 v_normal;
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

uniform samplerCube s_skybox;
uniform sampler2D s_texture;


void main() {
    // Ambient lighting
    vec3 ambient = u_ambient_intensity * u_light_color;

    // Diffuse lighting
    vec3 normal = normalize(v_normal);
    vec3 light_dir = normalize(u_light_position - v_frag_position);
    float diffuse_value = max(dot(normal, light_dir), 0.0);
    vec3 diffuse = diffuse_value * u_light_color * u_diffuse_intensity;

    // Specular lighting
    vec3 view_dir = normalize(u_view_position - v_frag_position);
    vec3 reflect_dir = reflect(-light_dir, normal);
    float specular_value = pow(max(dot(view_dir, reflect_dir), 0.0), u_specular_power);
    vec3 specular = specular_value * u_light_color * u_specular_intensity;

    vec3 view_ray = normalize(v_frag_position - u_view_position);
    vec3 reflection_ray = reflect(view_ray, normalize(v_normal));
    vec4 reflection = vec4(texture(s_skybox, reflection_ray).rgb, 1.0);

    vec4 tex = texture(s_texture, v_uv);
    vec3 color = tex.rgb * (ambient + diffuse + specular);
    out_color = vec4(color, tex.a);
}