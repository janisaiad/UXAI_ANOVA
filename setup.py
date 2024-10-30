from setuptools import setup, Extension, find_packages

# Configuration de l'extension C++
ext_modules = [
    Extension(
        "treeshap",
        sources=["src/tree_shap/main.cpp"],
        extra_compile_args=["-std=c++11"],
    )
]

# Configuration complète avec src
setup(
    name="uxai-anova",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "."},  # Dit à setuptools que les packages sont dans src/
    ext_modules=ext_modules,
    python_requires=">=3.8",
)