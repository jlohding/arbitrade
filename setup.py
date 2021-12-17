from setuptools import setup, find_packages

if __name__ == "__main__":
    with open("README.md", encoding="utf-8") as f:
        long_desc = f.read()

    setup(
        name="arbitrade", 
        version="0.0.1",
        author="Jerry Loh",
        description="Python 3.9 Systematic Trading System",
        long_description=long_desc,
        url="https://github.com/jlohding/arbitrade",
        package_dir={"":"src"},
        packages=find_packages(),
        python_requires=">=3.9",
    )

