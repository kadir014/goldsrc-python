#version 330

/*
    Single pass gaussian blur
    Thanks to @mrharicot at https://www.shadertoy.com/view/XdfGDH
*/


#define KERNEL 13
#define SIGMA 7.0


in vec2 v_uv;

out vec4 out_color;

uniform sampler2D s_texture;


float normpdf(float x) {
	return 0.39894 * exp(-0.5 * x * x / (SIGMA * SIGMA)) / SIGMA;
}


void main() {
    // Game framebuffer gets flipped
    vec2 uv = vec2(v_uv.x, 1.0 - v_uv.y);

    const int kernel_size = (KERNEL - 1) / 2;
    float kernel[KERNEL];
    vec3 final_colour = vec3(0.0);
    vec2 texture_size = textureSize(s_texture, 0);
    
    // Create the 1D kernel
    float Z = 0.0;
    for (int j = 0; j <= kernel_size; ++j)
        kernel[kernel_size + j] = kernel[kernel_size - j] = normpdf(float(j));
    
    // get the normalization factor (as the gaussian has been clamped)
    for (int j = 0; j < KERNEL; ++j)
        Z += kernel[j];
    
    // Read out the texels
    for (int i =- kernel_size; i <= kernel_size; ++i) {
        for (int j = -kernel_size; j <= kernel_size; ++j) {
            vec2 offset = vec2(float(i), float(j)) / texture_size;
            vec3 color = texture(s_texture, (uv + offset)).rgb;
            final_colour += kernel[kernel_size+j] * kernel[kernel_size+i] * color;
        }
    }
    
    out_color = vec4(final_colour / (Z * Z), 1.0);
}