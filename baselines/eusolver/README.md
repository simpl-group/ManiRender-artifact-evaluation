EUSolver
========

# Installment

install in Debian/Ubuntu

```shell
sudo apt install cmake
pip install pyparsing z3-solver
pip install -r requirements.txt
# install
rm -fr thirdparty/libeusolver/build
mkdir -p thirdparty/libeusolver/build
bash ./scripts/build.sh
```

test

```bash
./eusolver benchmarks/max/max_2.sl
# (define-fun max2 ((a0 Int) (a1 Int)) Int
#     (ite (>= a0 a1) a0 a1))
```

# Tips for EUSolver.

Q: How to debug in Python? <br>
A: run `src/benchmarks.py`

Q: Cannot debug because it could find correct `eusolver.py`? How to fix this? <br>
A: after run `./script/build.sh`, there will be 2 `eusolver.py` under `eusolver/thirdparty/libeusolver`.
Please delete the one in `thirdparty/libeusolver/src/python`, and make `thirdparty/libeusolver/build` as the source
directory.

Q: How to set source directory in Pycharm? <br>
A: `File | Settings | Project | Project structure`

# Change list

- `src/semantics/semantics_obj.py`
- `src/parsers/sexp.py`
- `src/parsers/parser.py`
- `src/enumerators/enumerators.py`
- `src/exprs/exprtypes.py`

# Refs

- Code: https://bitbucket.org/abhishekudupa/eusolver/src/master/
- README: https://github.com/yuntongzhang/eusolver/blob/main/README.md