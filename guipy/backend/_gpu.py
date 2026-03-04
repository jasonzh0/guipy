import moderngl
from guipy.backend._shaders import (
    QUAD_VERT, RECT_FRAG, CIRCLE_FRAG, LINE_FRAG, BLIT_FRAG,
)

_ctx = None
_dpi_scale = 1.0
_rect_prog = None
_circle_prog = None
_line_prog = None
_blit_prog = None
_quad_vbo = None
_rect_vao = None
_circle_vao = None
_line_vao = None
_blit_vao = None


def init_gpu(ctx, dpi_scale=1.0):
    global _ctx, _dpi_scale, _rect_prog, _circle_prog, _line_prog, _blit_prog
    global _quad_vbo, _rect_vao, _circle_vao, _line_vao, _blit_vao

    _ctx = ctx
    _dpi_scale = dpi_scale

    import numpy as np
    vertices = np.array([
        0.0, 0.0,
        1.0, 0.0,
        0.0, 1.0,
        1.0, 1.0,
    ], dtype='f4')
    _quad_vbo = _ctx.buffer(vertices)

    _rect_prog = _ctx.program(vertex_shader=QUAD_VERT, fragment_shader=RECT_FRAG)
    _circle_prog = _ctx.program(vertex_shader=QUAD_VERT, fragment_shader=CIRCLE_FRAG)
    _line_prog = _ctx.program(vertex_shader=QUAD_VERT, fragment_shader=LINE_FRAG)
    _blit_prog = _ctx.program(vertex_shader=QUAD_VERT, fragment_shader=BLIT_FRAG)

    _rect_vao = _ctx.vertex_array(_rect_prog, [(_quad_vbo, '2f', 'in_position')])
    _circle_vao = _ctx.vertex_array(_circle_prog, [(_quad_vbo, '2f', 'in_position')])
    _line_vao = _ctx.vertex_array(_line_prog, [(_quad_vbo, '2f', 'in_position')])
    _blit_vao = _ctx.vertex_array(_blit_prog, [(_quad_vbo, '2f', 'in_position')])


def get_context():
    global _ctx
    if _ctx is None:
        _ctx = moderngl.create_standalone_opengl_context()
        init_gpu(_ctx)
    return _ctx


def get_dpi_scale():
    return _dpi_scale


def _setup_blend(fbo, phys_size):
    """Set up FBO with blending. phys_size is in physical pixels."""
    fbo.use()
    _ctx.viewport = (0, 0, phys_size[0], phys_size[1])
    _ctx.enable(moderngl.BLEND)
    _ctx.blend_func = (
        moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA,
    )
    _ctx.blend_equation = moderngl.FUNC_ADD


def draw_rect(fbo, surface_size, color, x, y, w, h, border_width=0, border_radius=0):
    """All coordinates are in physical pixels."""
    _setup_blend(fbo, surface_size)

    pad = 1
    qx = x - pad
    qy = y - pad
    qw = w + pad * 2
    qh = h + pad * 2

    _rect_prog['u_pos'].value = (float(qx), float(qy))
    _rect_prog['u_size'].value = (float(qw), float(qh))
    _rect_prog['u_surface_size'].value = (float(surface_size[0]), float(surface_size[1]))
    _rect_prog['u_rect'].value = (float(x), float(y), float(w), float(h))
    _rect_prog['u_color'].value = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0, color[3] / 255.0)
    _rect_prog['u_border_radius'].value = float(border_radius)
    _rect_prog['u_border_width'].value = float(border_width)
    _rect_prog['u_surface_height'].value = float(surface_size[1])

    _rect_vao.render(moderngl.TRIANGLE_STRIP)
    _ctx.disable(moderngl.BLEND)


def draw_circle(fbo, surface_size, color, cx, cy, radius, border_width=0):
    """All coordinates are in physical pixels."""
    _setup_blend(fbo, surface_size)

    pad = 2
    qx = cx - radius - pad
    qy = cy - radius - pad
    qw = radius * 2 + pad * 2
    qh = radius * 2 + pad * 2

    _circle_prog['u_pos'].value = (float(qx), float(qy))
    _circle_prog['u_size'].value = (float(qw), float(qh))
    _circle_prog['u_surface_size'].value = (float(surface_size[0]), float(surface_size[1]))
    _circle_prog['u_center'].value = (float(cx), float(cy))
    _circle_prog['u_radius'].value = float(radius)
    _circle_prog['u_border_width'].value = float(border_width)
    _circle_prog['u_color'].value = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0, color[3] / 255.0)
    _circle_prog['u_surface_height'].value = float(surface_size[1])

    _circle_vao.render(moderngl.TRIANGLE_STRIP)
    _ctx.disable(moderngl.BLEND)


def draw_line(fbo, surface_size, color, x0, y0, x1, y1, width=1):
    """All coordinates are in physical pixels."""
    _setup_blend(fbo, surface_size)

    pad = int(width / 2) + 2
    qx = min(x0, x1) - pad
    qy = min(y0, y1) - pad
    qw = abs(x1 - x0) + pad * 2
    qh = abs(y1 - y0) + pad * 2

    _line_prog['u_pos'].value = (float(qx), float(qy))
    _line_prog['u_size'].value = (float(qw), float(qh))
    _line_prog['u_surface_size'].value = (float(surface_size[0]), float(surface_size[1]))
    _line_prog['u_start'].value = (float(x0), float(y0))
    _line_prog['u_end'].value = (float(x1), float(y1))
    _line_prog['u_width'].value = float(width)
    _line_prog['u_color'].value = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0, color[3] / 255.0)
    _line_prog['u_surface_height'].value = float(surface_size[1])

    _line_vao.render(moderngl.TRIANGLE_STRIP)
    _ctx.disable(moderngl.BLEND)


def blit_texture(dst_fbo, dst_phys_size, src_texture, src_phys_size, dest_pos_phys):
    """All coordinates/sizes are in physical pixels."""
    _setup_blend(dst_fbo, dst_phys_size)

    dx, dy = float(dest_pos_phys[0]), float(dest_pos_phys[1])
    sw, sh = float(src_phys_size[0]), float(src_phys_size[1])

    _blit_prog['u_pos'].value = (dx, dy)
    _blit_prog['u_size'].value = (sw, sh)
    _blit_prog['u_surface_size'].value = (float(dst_phys_size[0]), float(dst_phys_size[1]))

    src_texture.use(0)
    if 'u_texture' in _blit_prog:
        _blit_prog['u_texture'].value = 0

    _blit_vao.render(moderngl.TRIANGLE_STRIP)
    _ctx.disable(moderngl.BLEND)
