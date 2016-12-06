from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name = 'luis_wrapper',
    packages=find_packages(exclude=['docs', 'tests*']),
    version = '0.1.0',
    description = 'A wrapper around Microsoft LUIS',
    long_description=readme(),
    author = 'Simon Clement',
    author_email = 'simon.clement@gmail.com',
    url = 'https://github.com/SimonTC/luis_wrapper',
    download_url = 'https://github.com/SimonTC/luis_wrapper/tarball/0.1.0',
    keywords = ['LUIS', 'NLP'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['requests'],
    license='MIT'
)
