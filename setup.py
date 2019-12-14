from setuptools import find_packages, setup

setup(
    name="CFR Personalization",
    use_scm_version=False,
    version="0.1.0",
    setup_requires=["setuptools_scm", "pytest-runner"],
    tests_require=["pytest"],
    include_package_data=True,
    packages=find_packages(exclude=["tests", "tests/*"]),
    description="CFR Personalization Server",
    author="Mozilla Corporation",
    author_email="vng@mozilla.com",
    url="https://github.com/mozilla/cfr-personalization",
    license="MPL 2.0",
    install_requires=[],
    data_files=[("scripts", ["cfretl/scripts/compute_weights.py"])],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment :: Mozilla",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
)
