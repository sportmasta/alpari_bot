from setuptools import setup
from Cython.Build import cythonize
from setuptools.extension import Extension

extensions = [
    Extension(
        "telegram_bot",
        sources=["bot_main.py"],
        extra_compile_args=["-O3"],  # Оптимизация
    )
]

setup(
    name="telegram_bot",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'embedsignature': True,
        },
    ),
    zip_safe=False,
)