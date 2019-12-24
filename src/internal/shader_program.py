from pathlib import Path
from typing import Tuple, List

from bgfx import bgfx, load_shader, ShaderType, as_void_ptr


class ShaderProgram:
    def __init__(
        self,
        vertex_src: Path,
        fragment_src: Path,
        samplers: List[str],
        params: List[str],
    ):
        vertex_shader = load_shader(
            str(vertex_src.name),
            ShaderType.VERTEX,
            root_path=str(vertex_src.absolute().parent),
        )

        fragment_shader = load_shader(
            str(fragment_src.name),
            ShaderType.FRAGMENT,
            root_path=str(fragment_src.absolute().parent),
        )

        self._shader_program = bgfx.createProgram(vertex_shader, fragment_shader, True)
        self._samplers = self._build_samplers(samplers)
        self._params = self._build_params(params)

    @property
    def program(self):
        return self._shader_program

    @property
    def samplers(self):
        return self._samplers

    def set_param(self, param: Tuple[str, bytes]):
        self._params[param[0]]["value"] = param[1]

    def submit_values(self):
        for param in self._params:
            if not param["value"]:
                continue

            uniform = param["uniform"]
            bgfx.setUniform(uniform, as_void_ptr(param["value"]))

    def dispose(self):
        for s in self._samplers:
            bgfx.destroy(s)

        for p in self._params:
            bgfx.destroy(p["uniform"])

        bgfx.destroy(self._shader_program)

        self._samplers.clear()
        self._params.clear()

    @staticmethod
    def _build_samplers(samplers: List[str]) -> List[bgfx.Uniform]:
        return [
            bgfx.createUniform(sampler, bgfx.UniformType.Sampler)
            for sampler in samplers
        ]

    @staticmethod
    def _build_params(params: List[str]) -> dict:
        return {
            param: {
                "uniform": bgfx.createUniform(param, bgfx.UniformType.Vec4),
                "value": None,
            }
            for param in params
        }
