@echo off
set PYDOC=C:\Python27\Lib\pydoc.py
set OUTDIR=docs

cd ..

for %%I in (att, att.atg, att.atr, att.template, att.data) do (
%PYDOC% -w %%I
move %%I.html %OUTDIR%
)
