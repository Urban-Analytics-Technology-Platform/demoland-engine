#!/bin/bash
rm -rf ../build ../demoland_engine.egg-info ./wheel_build
python -m pip wheel . -w wheel_build
cp wheel_build/demoland* ../web/public/
