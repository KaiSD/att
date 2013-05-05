@echo off
set PYDOC=C:\Python27\Lib\pydoc.py
set OUTDIR=docs

cd ..

for %%I in (atg atr data template) do (
%PYDOC% -w %%I
move %%I.html %OUTDIR%
)
