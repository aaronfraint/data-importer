from setuptools import find_packages, setup

setup(
    name='database_io',
    packages=find_packages(),
    version='0.1.0',
    description='Python package to import data into PostgreSQL',
    author='Aaron Fraint, AICP',
    license='MIT',
    entry_points="""
        [console_scripts]
        db-import=data_importer.cli:main
    """,
)
