from setuptools import setup

setup(
    name="fastanalyzer",
    version="0.1.2",
    author="Benjamin Gallois",
    author_email="benjamin.gallois@fasttrack.sh",
    description="Companion application to analyze data extracted with FastTrack software.",
    url="https://github.com/FastTrackOrg/FastAnalyzer",
    packages=['fastanalyzer'],
    install_requires=[
        'fastanalysis',
        'PySide6',
        'matplotlib',
        'seaborn',
        'statannotations',],
    license='MIT',
    python_requires='>=3.6',
    zip_safe=False,
    entry_points = {
        'console_scripts': ['fastanalyzer=fastanalyzer.fastanalyzer:main'],
        }
)
