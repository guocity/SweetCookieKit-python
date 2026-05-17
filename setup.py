from setuptools import setup, find_packages

setup(
    name="sweetcookiekit",
    version="0.1.0",
    packages=find_packages(),
    description="Python wrapper for SweetCookieKit macOS browser cookie extraction.",
    author="SweetCookieKit Contributors",
    long_description=open("README-python.md", "r", encoding="utf-8").read() if __import__("os").path.exists("README-python.md") else "",
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)
