from setuptools import setup, find_packages

setup(
    name='vibe-seeder',
    version='0.1',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'transformers>=4.36.0',
        'torch',
        'accelerate',
        'tqdm'
    ],
    author='iwin2471',
    description='Seed-driven LLM Character Engine',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/iwin2471/vibe-seeder',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
)
