# Screen display shaders (used by Window for final blit to screen)
VERTEX_SHADER = """
#version 330
in vec2 in_position;
in vec2 in_texcoord;
out vec2 v_texcoord;
void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    v_texcoord = in_texcoord;
}
"""

FRAGMENT_SHADER = """
#version 330
in vec2 v_texcoord;
out vec4 fragColor;
uniform sampler2D tex;
void main() {
    fragColor = texture(tex, v_texcoord);
}
"""

# Shared vertex shader for SDF draw quads
QUAD_VERT = """
#version 330
in vec2 in_position;
uniform vec2 u_pos;
uniform vec2 u_size;
uniform vec2 u_surface_size;
out vec2 v_texcoord;
void main() {
    v_texcoord = vec2(in_position.x, 1.0 - in_position.y);
    vec2 pixel = u_pos + in_position * u_size;
    vec2 ndc = vec2(pixel.x / u_surface_size.x * 2.0 - 1.0,
                    1.0 - pixel.y / u_surface_size.y * 2.0);
    gl_Position = vec4(ndc, 0.0, 1.0);
}
"""

# SDF rounded rectangle fragment shader
RECT_FRAG = """
#version 330
out vec4 fragColor;
uniform vec4 u_rect;          // x, y, w, h in pixels
uniform vec4 u_color;         // RGBA 0-1
uniform float u_border_radius;
uniform float u_border_width;
uniform float u_surface_height;

float sdRoundedBox(vec2 p, vec2 b, float r) {
    vec2 q = abs(p) - b + vec2(r);
    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

void main() {
    vec2 pixel = vec2(gl_FragCoord.x, u_surface_height - gl_FragCoord.y);
    vec2 center = u_rect.xy + u_rect.zw * 0.5;
    vec2 half_size = u_rect.zw * 0.5;
    float r = min(u_border_radius, min(half_size.x, half_size.y));
    float d = sdRoundedBox(pixel - center, half_size, r);

    float alpha;
    if (u_border_width == 0.0) {
        alpha = smoothstep(0.5, -0.5, d);
    } else {
        float outer = smoothstep(0.5, -0.5, d);
        float inner = smoothstep(0.5, -0.5, d + u_border_width);
        alpha = outer * (1.0 - inner);
    }
    fragColor = vec4(u_color.rgb, u_color.a * alpha);
}
"""

# SDF circle fragment shader
CIRCLE_FRAG = """
#version 330
out vec4 fragColor;
uniform vec2 u_center;
uniform float u_radius;
uniform float u_border_width;
uniform vec4 u_color;
uniform float u_surface_height;

void main() {
    vec2 pixel = vec2(gl_FragCoord.x, u_surface_height - gl_FragCoord.y);
    float d = length(pixel - u_center) - u_radius;

    float alpha;
    if (u_border_width == 0.0) {
        alpha = smoothstep(0.5, -0.5, d);
    } else {
        float outer = smoothstep(0.5, -0.5, d);
        float inner = smoothstep(0.5, -0.5, d + u_border_width);
        alpha = outer * (1.0 - inner);
    }
    fragColor = vec4(u_color.rgb, u_color.a * alpha);
}
"""

# SDF line segment fragment shader
LINE_FRAG = """
#version 330
out vec4 fragColor;
uniform vec2 u_start;
uniform vec2 u_end;
uniform float u_width;
uniform vec4 u_color;
uniform float u_surface_height;

void main() {
    vec2 pixel = vec2(gl_FragCoord.x, u_surface_height - gl_FragCoord.y);
    vec2 pa = pixel - u_start;
    vec2 ba = u_end - u_start;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    float dist = length(pa - ba * h);
    float half_w = u_width * 0.5;
    float coverage = smoothstep(half_w + 0.5, half_w - 0.5, dist);
    fragColor = vec4(u_color.rgb, u_color.a * coverage);
}
"""

# Blit (textured quad) fragment shader
BLIT_FRAG = """
#version 330
in vec2 v_texcoord;
out vec4 fragColor;
uniform sampler2D u_texture;
void main() {
    fragColor = texture(u_texture, v_texcoord);
}
"""
