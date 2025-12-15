from setuptools import setup, find_packages

setup(
    name='ankigen',
    version='0.1.0',
    description='Anki flashcard generator CLI with LLM and Anki-Connect',
    packages=find_packages(),
    install_requires=[
        'langchain>=0.0.350',
        'loguru>=0.7.0',
        'pyyaml>=6.0',
        'requests>=2.31.0',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            # CLI only via python -m ankigen
        ],
    },
)
