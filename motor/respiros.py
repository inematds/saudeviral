#!/usr/bin/env python3
"""Insere os respiros (pausas de 1 s do cartão de virada) num áudio ou num vídeo com áudio.
uso: motor/respiros.py <pasta-da-edicao> <entrada> <saida>
Lê <ed>/respiros.json (gravado pelo gerar_cena.py: [{"t": corte na linha ORIGINAL, "dur": s}]).
Sem respiros, copia a entrada. Vídeo: o buraco é preto (o cartão do palco cobre a tela e o avatar fica desligado nele).
Pedido do Nei em 14/10/2026: virada de página entre assuntos e um tempo antes da pergunta."""
import json, shutil, subprocess, sys
from pathlib import Path

E, ENT, SAI = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
rp = E / "respiros.json"
R = json.loads(rp.read_text()) if rp.exists() else []
if not R:
    shutil.copyfile(ENT, SAI); print("sem respiros"); sys.exit(0)
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", ENT], capture_output=True, text=True).stdout)
tem_v = any(s["codec_type"] == "video" for s in pr["streams"])
cortes = [0.0] + [r["t"] for r in R]
fins = [r["t"] for r in R] + [None]
fc, ins = [], []
for k, (a, b) in enumerate(zip(cortes, fins)):
    lim = f"start={a}" + (f":end={b}" if b is not None else "")
    fc.append(f"[0:a]atrim={lim},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a{k}]")
    if tem_v:
        fc.append(f"[0:v]trim={lim},setpts=PTS-STARTPTS,fps=30,format=yuv420p,setsar=1[v{k}]")
        ins.append(f"[v{k}][a{k}]")
    else:
        ins.append(f"[a{k}]")
    if b is not None:
        d = R[k]["dur"]
        fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{d}[sa{k}]")
        if tem_v:
            w, h = next((s["width"], s["height"]) for s in pr["streams"] if s["codec_type"] == "video")
            fc.append(f"color=c=black:s={w}x{h}:r=30:d={d},format=yuv420p,setsar=1[sv{k}]")
            ins.append(f"[sv{k}][sa{k}]")
        else:
            ins.append(f"[sa{k}]")
n = len(cortes) * 2 - 1
fc.append("".join(ins) + (f"concat=n={n}:v=1:a=1[v][a]" if tem_v else f"concat=n={n}:v=0:a=1[a]"))
cmd = ["ffmpeg", "-v", "error", "-y", "-i", ENT, "-filter_complex", ";".join(fc)]
cmd += (["-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-c:a", "aac", "-b:a", "192k"] if tem_v
        else ["-map", "[a]"]) + [SAI]
subprocess.run(cmd, check=True)
print(f"{len(R)} respiros → {SAI}")
