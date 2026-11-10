#!/usr/bin/env python3
"""음악 파일의 BPM을 추정하고 마디·박 타임코드 표를 만든다 (ffmpeg + numpy만 사용).

  python3 scripts/bpm.py music.mp3                  # BPM 추정
  python3 scripts/bpm.py music.mp3 --bars 7         # 7마디 박 타임코드 표 (JSON)
  python3 scripts/bpm.py --bpm 120 --bars 7         # BPM을 알면 음악 없이 표만
  python3 scripts/bpm.py music.mp3 --beats-json > beats.json   # 박·강박(다운비트)·강조 지점
  python3 scripts/bpm.py --selftest
"""
import argparse, json, subprocess, sys
import numpy as np

SR = 11025


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def onset_flux(x, hop=256):
    n = len(x) // hop
    env = np.sqrt(np.add.reduceat(x[: n * hop] ** 2, np.arange(0, n * hop, hop)))
    return np.maximum(np.diff(env), 0), SR / hop


def estimate_bpm(x, lo=70, hi=180):
    # ponytail: 에너지 플럭스 자기상관 — 박자 변화가 심한 곡은 틀릴 수 있다. 그땐 --bpm으로 직접 준다.
    flux, fps = onset_flux(x)
    flux = flux - flux.mean()
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    lags = np.arange(int(fps * 60 / hi), int(fps * 60 / lo) + 1)
    k = lags[np.argmax(ac[lags])]
    a, b, c = ac[k - 1], ac[k], ac[k + 1]
    lag = k + 0.5 * (a - c) / (a - 2 * b + c)  # 포물선 보간: 프레임 단위 양자화 오차 제거
    return round(60 * fps / lag, 1)


def grid(bpm, bars, beats_per_bar=4, offset=0.0):
    beat = 60 / bpm
    return {"bpm": bpm, "beat_sec": round(beat, 4), "bar_sec": round(beat * beats_per_bar, 4),
            "total_sec": round(beat * beats_per_bar * bars, 3),
            "bars": [{"bar": b + 1, "beats": [round(offset + (b * beats_per_bar + i) * beat, 3)
                                               for i in range(beats_per_bar)]} for b in range(bars)]}


def beats_json(x, bpm=None, beats_per_bar=4, n_accents=8):
    """박 위상·강박·강조 지점을 찾아 beats.json 형태로 낸다.
    ponytail: 고정 템포 가정 + 강박은 '마디 안 에너지 최대 박' 추정 — 템포가 변하는 곡은 aubio beat 로 대체."""
    bpm = bpm or estimate_bpm(x)
    flux, fps = onset_flux(x)
    dur = len(x) / SR
    step = 60 / bpm * fps
    at = lambda t: flux[np.clip(np.round(np.asarray(t)).astype(int), 0, len(flux) - 1)].sum()
    phase = max(np.arange(0, step, 0.5), key=lambda p: at(np.arange(p, len(flux), step)))
    beats = np.arange(phase, len(flux), step)
    bar_phase = max(range(beats_per_bar), key=lambda k: at(beats[k::beats_per_bar]))
    # 강조 지점: 반 박 이상 떨어진 플럭스 상위 봉우리
    gap, acc = int(step / 2), []
    for i in np.argsort(flux)[::-1]:
        if all(abs(i - j) >= gap for j in acc):
            acc.append(i)
        if len(acc) == n_accents:
            break
    sec = lambda f: round(float(f) / fps, 3)
    return {"bpm": bpm, "beat_sec": round(60 / bpm, 4), "duration": round(dur, 3), "offset": sec(phase),
            "beats": [sec(b) for b in beats], "downbeats": [sec(b) for b in beats[bar_phase::beats_per_bar]],
            "accents": sorted(sec(i) for i in acc)}


def selftest():
    for bpm in (90, 120, 140):
        t = np.arange(int(SR * 20)) / SR
        x = np.zeros_like(t)
        for k in np.arange(0, 20, 60 / bpm):
            i = int(k * SR)
            x[i:i + 200] = np.hanning(200)
        got = estimate_bpm(x)
        assert abs(got - bpm) <= 2, (bpm, got)
    g = grid(120, 7)
    assert g["total_sec"] == 14.0 and g["bars"][1]["beats"][0] == 2.0
    # 120BPM, 첫 박 0.25초, 매 4박째(강박) 2배 세기, 5.0초에 큰 강조음
    t = np.zeros(SR * 12, dtype=np.float32)
    for i, k in enumerate(np.arange(0.25, 12, 0.5)):
        t[int(k * SR):int(k * SR) + 200] = np.hanning(200) * (1.0 if i % 4 == 0 else 0.5)
    t[int(5.12 * SR):int(5.12 * SR) + 400] = np.hanning(400) * 3
    b = beats_json(t, bpm=120)
    assert abs(b["offset"] - 0.25) < 0.03, b["offset"]
    assert abs(b["downbeats"][0] - 0.25) < 0.03 and abs(b["downbeats"][1] - 2.25) < 0.03, b["downbeats"][:2]
    assert any(abs(a - 5.12) < 0.03 for a in b["accents"]), b["accents"]
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", nargs="?")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--bars", type=int)
    ap.add_argument("--beats-per-bar", type=int, default=4)
    ap.add_argument("--offset", type=float, default=0.0, help="첫 박 시작 초")
    ap.add_argument("--beats-json", action="store_true", help="박·강박·강조 지점 JSON")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); sys.exit()
    if a.beats_json:
        if not a.audio:
            ap.error("--beats-json 은 audio 필요")
        print(json.dumps(beats_json(decode(a.audio), a.bpm, a.beats_per_bar), ensure_ascii=False, indent=1)); sys.exit()
    bpm = a.bpm or (estimate_bpm(decode(a.audio)) if a.audio else ap.error("audio 또는 --bpm 필요"))
    print(json.dumps(grid(bpm, a.bars, a.beats_per_bar, a.offset), ensure_ascii=False, indent=1) if a.bars else bpm)
