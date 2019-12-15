from typing import Sequence, TypedDict

from bgfx import bgfx, load_shader, ShaderType, as_void_ptr
from pathlib import Path


class ShaderProgram:

    def __init__(self, vertex_src: Path, fragment_src: Path, samplers: Sequence[str], params: Sequence[str]):
        vertex_shader = load_shader(
            str(vertex_src.name), ShaderType.VERTEX, root_path=str(vertex_src.absolute().parent)
        )

        fragment_shader = load_shader(
            str(fragment_src.name), ShaderType.FRAGMENT, root_path=str(fragment_src.absolute().parent)
        )

        self._shader_program = bgfx.createProgram(vertex_shader, fragment_shader, True)
        self._samplers = self._build_samplers(samplers)
        self._params = self._build_params(params)

    def set_params(self, params: Sequence[TypedDict[str, bytes]]):
        for param in params:
            uniform = self._params[param[0]]
            bgfx.setUniform(uniform, as_void_ptr(param[1]))

    def dispose(self):
        for s in self._samplers:
            bgfx.destroy(s)

        for p in self._params:
            bgfx.destroy(p["value"])

        bgfx.destroy(self._shader_program)

    @staticmethod
    def _build_samplers(samplers: Sequence[str]) -> Sequence[bgfx.Uniform]:
        return [
            bgfx.createUniform(sampler, bgfx.UniformType.Sampler)
            for sampler in samplers
        ]

    @staticmethod
    def _build_params(params: Sequence[str]) -> Sequence[TypedDict[str, bgfx.Uniform]]:
        return [
            {
                "name": param,
                "value": bgfx.createUniform(param, bgfx.UniformType.Vec4)
            }
            for param in params
        ]
