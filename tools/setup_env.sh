#!/usr/bin/env bash
# Restore the build environment after a sandbox reset.
pip install -q python-pptx 2>/dev/null
mkdir -p ~/.config/fontconfig
cat > ~/.config/fontconfig/fonts.conf <<'XML'
<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
<alias><family>Courier New</family><prefer><family>Liberation Mono</family></prefer></alias>
<alias><family>Arial</family><prefer><family>Liberation Sans</family></prefer></alias>
</fontconfig>
XML
python3 -c "import pptx; print('python-pptx', pptx.__version__)"
