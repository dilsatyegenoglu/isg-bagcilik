# -*- coding: utf-8 -*-
"""
İş Sağlığı ve Güvenliği (Bağcılık) - Öğretici Streamlit Uygulaması
==================================================================
© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır.

Bağcılık ön lisans programı İş Sağlığı ve Güvenliği dersi için etkileşimli öğretim
aracı: temel kavramlar ve 6331 sayılı Kanun, bağcılıkta riskler ve KKD, risk
değerlendirmesi, traktör ve makine güvenliği, fiziksel/biyolojik/ergonomik etmenler,
özel gruplar, çevre ve bina güvenliği, yangın, kaza kuramları, risk puanlama ve kaza
oranları, meslek hastalıkları, güvenlik işaretleri. Her konunun sonunda 10 / 20 / 30
seçmeli alıştırma ve adım adım çözüm.

Kurulum   : pip install -r requirements.txt
Çalıştırma: streamlit run isg_streamlit.py
"""

import math
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="İş Sağlığı ve Güvenliği · Bağcılık", page_icon="🦺", layout="wide")

TELIF = "© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır."

# Renkler
MAVI, PEMBE, YESIL, TURUNCU = "#3B6FB6", "#D9577A", "#3C9A5F", "#E8A33B"
MOR, GRI_K, SARI = "#8E5BB5", "#5F6B7A", "#F2C94C"
SIVI, CAM, CAM_K = "#9CC3E6", "#EAF3FB", "#4A5A6A"   # sıvı, cam dolgu, cam çizgi
YAZI = 'font-family="Source Sans Pro, Segoe UI, Arial, sans-serif"'

st.markdown("""
<style>
.kutucuk {border-left:5px solid #3B6FB6; background:rgba(59,111,182,0.08);
          padding:10px 14px; border-radius:6px; margin:6px 0 10px 0;}
.uyari {border-left:5px solid #D9534F; background:rgba(217,83,79,0.08);
        padding:10px 14px; border-radius:6px; margin:6px 0 10px 0;}
.ipucu {border-left:5px solid #3C9A5F; background:rgba(60,154,95,0.08);
        padding:10px 14px; border-radius:6px; margin:6px 0 10px 0;}
.kartlar {display:flex; flex-wrap:wrap; gap:12px; margin:8px 0 14px 0;}
.kart {flex:1 1 220px; border:1px solid rgba(128,128,128,0.35); border-radius:10px;
       padding:12px 14px; background:rgba(128,128,128,0.05);}
.kart h4 {margin:0 0 6px 0; font-size:1.02rem;}
.kart p {margin:0; font-size:0.93rem;}
.dizi {font-family:monospace; font-size:18px; letter-spacing:1px; line-height:2.0;
       overflow-x:auto; white-space:nowrap; padding:6px 10px; border-radius:8px;
       background:rgba(128,128,128,0.07);}
.baz {display:inline-block; min-width:20px; text-align:center; border-radius:4px;
      margin:1px; padding:0 2px; color:#111; font-weight:700;}
.kodon {display:inline-block; border:1.5px solid rgba(128,128,128,0.6); border-radius:6px;
        padding:2px 6px; margin:3px; text-align:center; font-family:monospace;}
.kodon small {display:block; font-family:sans-serif; font-size:11px;}
.zaman {border-left:4px solid #3B6FB6; padding:4px 0 4px 12px; margin:6px 0;}
.zaman b.yil {color:#3B6FB6; font-size:1.05rem;}
.flash {border:2px solid #3B6FB6; border-radius:14px; padding:26px; text-align:center;
        font-size:1.4rem; font-weight:700; margin:10px 0;}
.flash-cevap {font-size:1.05rem; font-weight:400; margin-top:12px;}
.adim-baslik {font-size:1.15rem; font-weight:700; color:#3B6FB6; margin-top:18px;
              border-bottom:2px solid rgba(59,111,182,0.3);}
.etiket {border:2px dashed #5F6B7A; border-radius:10px; padding:12px 16px; max-width:420px;
          background:rgba(242,201,76,0.12); font-family:monospace; line-height:1.6;}
.ekran {font-family:monospace; font-size:1.6rem; background:#1d2b1f; color:#8CF59A;
        padding:8px 14px; border-radius:8px; display:inline-block; letter-spacing:2px;}
.renk-kutu {width:100%; height:110px; border-radius:12px; border:1px solid #999;}
</style>
""", unsafe_allow_html=True)


def ipucu(metin):
    st.markdown(f'<div class="ipucu">{metin}</div>', unsafe_allow_html=True)


def kartlar(liste):
    """liste: [(başlık, metin), ...]"""
    icerik = "".join(f'<div class="kart"><h4>{b}</h4><p>{m}</p></div>' for b, m in liste)
    st.markdown(f'<div class="kartlar">{icerik}</div>', unsafe_allow_html=True)


def kutu(metin):
    st.markdown(f'<div class="kutucuk">{metin}</div>', unsafe_allow_html=True)


def uyari(metin):
    st.markdown(f'<div class="uyari">{metin}</div>', unsafe_allow_html=True)


def ciz(fig, yukseklik=380):
    fig.update_layout(height=yukseklik, margin=dict(l=40, r=20, t=50, b=40),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def tablo(df):
    try:
        st.dataframe(df, hide_index=True, width="stretch")
    except TypeError:
        st.dataframe(df, hide_index=True, use_container_width=True)


def rng():
    if "rng" not in st.session_state:
        st.session_state.rng = np.random.default_rng()
    return st.session_state.rng


SORU_SAYISI = 10


def _md(t):
    return ("md", t)


def _tx(t):
    return ("tex", t)


def _fmt(x, ondalik=4):
    if abs(x - round(x)) < 1e-9 and abs(x) >= 1:
        return f"{int(round(x))}"
    return f"{x:.{ondalik}f}"


def soru_sayi(metin, dogru, cozum, yanlis=(), ondalik=4, tol=None):
    """Sayısal soru; sık yapılan hatalardan türetilen yanlış seçeneklerle seçmeliye çevrilir."""
    return {"tip": "sayi", "metin": metin, "dogru": float(dogru), "yanlis": list(yanlis),
            "ondalik": ondalik, "cozum": cozum}


def soru_secim(r, metin, dogru, yanlislar, cozum):
    return {"tip": "secim", "metin": metin, "dogru": dogru, "yanlis": list(yanlislar),
            "cozum": cozum}


def _secmeliye_cevir(r, s):
    if s["tip"] == "secim":
        secenekler = [s["dogru"]] + s["yanlis"]
    else:
        x, od = s["dogru"], s["ondalik"]
        dogru = _fmt(x, od)
        olasilik = 0 < x < 1
        secenekler = [dogru]
        for v in s["yanlis"]:
            if v is None or not math.isfinite(v) or (v < 0 <= x) or (olasilik and v > 1):
                continue
            t = _fmt(v, od)
            if t not in secenekler:
                secenekler.append(t)
            if len(secenekler) == 4:
                break
        deneme = 0
        while len(secenekler) < 4 and deneme < 200:
            deneme += 1
            if abs(x - round(x)) < 1e-9 and abs(x) >= 1:
                adim_ = max(3, int(round(abs(x) * 0.25)))
                v = x + int(r.choice([-1, 1])) * int(r.integers(1, adim_ + 1))
            elif deneme > 40 or abs(x) < 10 ** (-od + 1):
                v = abs(x) + float(r.integers(5, 400)) * 10 ** (-od)
            else:
                v = x * (1 + float(r.choice([-1, 1])) * float(r.uniform(0.12, 0.6)))
            if (v < 0 <= x) or (olasilik and v >= 1):
                continue
            t = _fmt(v, od)
            if t not in secenekler:
                secenekler.append(t)
        s = dict(s, dogru=dogru)
    sira = r.permutation(len(secenekler))
    s["secenekler"] = [secenekler[i] for i in sira]
    return s


def _sec(r, liste):
    return liste[int(r.integers(0, len(liste)))]


def _kavram_sec(r, havuz, adet):
    idx = r.permutation(len(havuz))[:adet]
    return [havuz[i] for i in idx]


def _al_cevapla(k, i):
    v = st.session_state.get(f"{k}_c{i}")
    if v is not None and f"{k}_cevap{i}" not in st.session_state:
        st.session_state[f"{k}_cevap{i}"] = v


ADET_SECENEK = [10, 20, 30]


def _temizle(k):
    for i in range(1, max(ADET_SECENEK) + 1):
        for ek in ("c", "cevap", "kilit"):
            st.session_state.pop(f"{k}_{ek}{i}", None)


def _al_yenile(k, uretici):
    _temizle(k)
    st.session_state[k] = _uret(uretici, st.session_state.get(f"{k}_adet", SORU_SAYISI))


def _uret(uretici, adet=SORU_SAYISI):
    """Üreticiyi gerektiği kadar çağırıp metni tekrarlanmayan 'adet' soru toplar."""
    r = rng()
    sorular, gorulen = [], set()
    for _ in range(40):
        for s in uretici(r):
            if s["metin"] not in gorulen:
                gorulen.add(s["metin"])
                sorular.append(_secmeliye_cevir(r, s))
            if len(sorular) >= adet:
                return sorular
    return sorular


def alistirma_blogu(anahtar, baslik, uretici):
    st.divider()
    st.subheader(f"✍️ Alıştırmalar: {baslik}")
    st.caption("Her soruda bir seçenek işaretleyin. Yanıtınız kilitlenir; doğru ya da yanlış "
               "olduğu ve **adım adım çözüm** o zaman açılır. Önce kâğıt-kalemle hesaplayın!")
    k = f"al_{anahtar}"
    st.radio("Kaç soru?", ADET_SECENEK, horizontal=True, key=f"{k}_adet",
             on_change=_al_yenile, args=(k, uretici))
    if k not in st.session_state:
        st.session_state[k] = _uret(uretici, st.session_state.get(f"{k}_adet", SORU_SAYISI))
    sorular = st.session_state[k]
    dogru_say = cevap_say = 0
    for i, s in enumerate(sorular, 1):
        with st.container(border=True):
            st.markdown(f"**Soru {i} / {len(sorular)}.** {s['metin']}")
            secili = st.session_state.get(f"{k}_cevap{i}")
            if secili is None:
                st.radio("Seçiniz", s["secenekler"], index=None, key=f"{k}_c{i}",
                         label_visibility="collapsed", on_change=_al_cevapla, args=(k, i))
            else:
                cevap_say += 1
                st.radio("Yanıtınız", s["secenekler"], index=s["secenekler"].index(secili),
                         key=f"{k}_kilit{i}", disabled=True, label_visibility="collapsed")
                if secili == s["dogru"]:
                    dogru_say += 1
                    st.success("✅ Doğru!")
                else:
                    st.error(f"❌ Yanlış. Doğru yanıt: **{s['dogru']}**")
                with st.expander("📖 Nasıl hesaplanır?", expanded=True):
                    for tur, icerik in s["cozum"]:
                        if tur == "tex":
                            for parca in icerik.split(r"\qquad"):
                                st.latex(parca)
                        else:
                            st.markdown(icerik)
    st.progress(cevap_say / len(sorular),
                text=f"Yanıtlanan: {cevap_say} / {len(sorular)}  ·  Doğru: {dogru_say}")
    if cevap_say == len(sorular):
        oran = dogru_say / len(sorular)
        mesaj = (f"🎉 Tebrikler! {dogru_say}/{len(sorular)}" if oran >= 0.8 else
                 f"👍 {dogru_say}/{len(sorular)}: yanlışların çözümlerini tekrar inceleyin"
                 if oran >= 0.5 else
                 f"📚 {dogru_say}/{len(sorular)}: konuyu yukarıdan bir kez daha okuyup yeni "
                 "sorularla deneyin")
        (st.success if oran >= 0.8 else st.info if oran >= 0.5 else st.warning)(mesaj)
    st.button("🎲 Yeni sorular", key=f"{k}_yeni", on_click=_al_yenile, args=(k, uretici))


def svg_goster(svg):
    import base64
    veri = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    st.markdown(f'<div style="width:100%;margin:6px 0 14px 0;text-align:center">'
                f'<img src="data:image/svg+xml;base64,{veri}" style="width:100%;'
                f'max-width:1000px;background:white;border-radius:12px"/></div>',
                unsafe_allow_html=True)


def _krom(x, y, h, w, renk, sent=0.33):
    yc = y + h * sent
    return (f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="{yc - y - 3}" rx="{w / 2}" '
            f'fill="{renk}" stroke="#444" stroke-width="1.4"/>'
            f'<rect x="{x - w / 2}" y="{yc + 3}" width="{w}" height="{y + h - yc - 3}" '
            f'rx="{w / 2}" fill="{renk}" stroke="#444" stroke-width="1.4"/>'
            f'<ellipse cx="{x}" cy="{yc}" rx="{w * 0.3}" ry="5" fill="{renk}" stroke="#444" '
            f'stroke-width="1.2"/>')


def _bant(x, y, w, renk, h=12):
    return (f'<rect x="{x - w / 2 + 1.5}" y="{y - h / 2}" width="{w - 3}" height="{h}" '
            f'fill="{renk}" stroke="#222" stroke-width="0.8"/>')


def _yazi(x, y, t, boy=14, renk="#222", hiza="middle", kalin=False):
    k = ' font-weight="700"' if kalin else ""
    return (f'<text x="{x}" y="{y}" {YAZI} font-size="{boy}" fill="{renk}" '
            f'text-anchor="{hiza}"{k}>{t}</text>')


def _ok(x1, y1, x2, y2, renk="#555"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{renk}" stroke-width="2.2" '
            f'marker-end="url(#okucu)"/>')


_OK_TANIM = ('<defs><marker id="okucu" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
             'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
             'fill="#555"/></marker></defs>')


def _yarim_daire(cx, cy, r, sol, sag):
    return (f'<path d="M{cx},{cy - r} A{r},{r} 0 0 0 {cx},{cy + r} Z" fill="{sol}"/>'
            f'<path d="M{cx},{cy - r} A{r},{r} 0 0 1 {cx},{cy + r} Z" fill="{sag}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#333" stroke-width="1.4"/>')


# ===========================================================================
# ORTAK ŞEMA YARDIMCILARI (Laboratuvar uygulamasından)
# ===========================================================================
def svg_ac(w, h, maks=None):
    m = f"max-width:{maks}px;" if maks else ""
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" style="{m}" '
            f'xmlns="http://www.w3.org/2000/svg">' + _OK_TANIM +
            f'<rect x="0" y="0" width="{w}" height="{h}" rx="12" fill="white"/>')


def _kutu_svg(x, y, w, h, renk, yazi, boy=14, dolgu=None, kalin=True, renk_yazi="#222"):
    d = dolgu or "white"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{d}" stroke="{renk}" '
            f'stroke-width="2"/>' +
            "".join(_yazi(x + w / 2, y + h / 2 + 5 + (i - (len(yazi) - 1) / 2) * (boy + 3), t, boy,
                          renk_yazi, kalin=(kalin and i == 0))
                    for i, t in enumerate(yazi if isinstance(yazi, (list, tuple)) else [yazi])))


_CIZGI = f'stroke="{CAM_K}" stroke-width="2.2" stroke-linejoin="round"'


def _alev(cx, cy, k=1.0):
    return (f'<path d="M{cx},{cy - 30 * k} C{cx + 20 * k},{cy - 10 * k} {cx + 22 * k},{cy + 10 * k} '
            f'{cx + 10 * k},{cy + 22 * k} C{cx + 12 * k},{cy + 8 * k} {cx + 4 * k},{cy + 2 * k} {cx},{cy - 4 * k} '
            f'C{cx - 2 * k},{cy + 8 * k} {cx - 8 * k},{cy + 12 * k} {cx - 8 * k},{cy + 22 * k} '
            f'C{cx - 22 * k},{cy + 10 * k} {cx - 18 * k},{cy - 10 * k} {cx},{cy - 30 * k} Z" fill="#111"/>')


def _ghs_sembol(tur, cx, cy):
    if tur == "alev":
        return _alev(cx, cy - 4) + f'<rect x="{cx - 26}" y="{cy + 22}" width="52" height="5" fill="#111"/>'
    if tur == "oksit":
        return (f'<circle cx="{cx}" cy="{cy + 12}" r="14" fill="none" stroke="#111" stroke-width="6"/>'
                + _alev(cx, cy - 14, 0.7) + f'<rect x="{cx - 26}" y="{cy + 30}" width="52" height="5" fill="#111"/>')
    if tur == "patlayici":
        cizgi = "".join(f'<line x1="{cx}" y1="{cy + 6}" x2="{cx + 30 * math.cos(a)}" '
                        f'y2="{cy + 6 + 30 * math.sin(a)}" stroke="#111" stroke-width="4"/>'
                        for a in np.linspace(0, 2 * math.pi, 13)[:-1])
        return cizgi + f'<circle cx="{cx}" cy="{cy + 6}" r="13" fill="#111"/>'
    if tur == "asindirici":
        return (f'<rect x="{cx - 26}" y="{cy - 28}" width="10" height="22" fill="#111" transform="rotate(-20 {cx - 21} {cy - 17})"/>'
                f'<rect x="{cx + 14}" y="{cy - 28}" width="10" height="22" fill="#111" transform="rotate(20 {cx + 19} {cy - 17})"/>'
                f'<circle cx="{cx - 16}" cy="{cy}" r="3" fill="#111"/><circle cx="{cx + 14}" cy="{cy}" r="3" fill="#111"/>'
                f'<path d="M{cx - 30},{cy + 26} L{cx - 4},{cy + 26} L{cx - 4},{cy + 14} Q{cx - 10},{cy + 8} {cx - 16},{cy + 14} '
                f'Q{cx - 24},{cy + 8} {cx - 30},{cy + 14} Z" fill="#111"/>'
                f'<path d="M{cx + 4},{cy + 26} L{cx + 30},{cy + 26} L{cx + 30},{cy + 14} L{cx + 18},{cy + 8} '
                f'L{cx + 10},{cy + 16} L{cx + 4},{cy + 12} Z" fill="#111"/>')
    if tur == "gaz":
        return (f'<rect x="{cx - 28}" y="{cy}" width="52" height="20" rx="10" fill="#111"/>'
                f'<rect x="{cx + 22}" y="{cy + 5}" width="9" height="10" fill="#111"/>')
    if tur == "zehir":
        return (f'<line x1="{cx - 24}" y1="{cy + 8}" x2="{cx + 24}" y2="{cy + 30}" stroke="#111" stroke-width="6" stroke-linecap="round"/>'
                f'<line x1="{cx + 24}" y1="{cy + 8}" x2="{cx - 24}" y2="{cy + 30}" stroke="#111" stroke-width="6" stroke-linecap="round"/>'
                f'<circle cx="{cx}" cy="{cy - 12}" r="17" fill="#111"/>'
                f'<rect x="{cx - 9}" y="{cy}" width="18" height="10" fill="#111"/>'
                f'<circle cx="{cx - 6}" cy="{cy - 13}" r="4.5" fill="white"/><circle cx="{cx + 6}" cy="{cy - 13}" r="4.5" fill="white"/>')
    if tur == "unlem":
        return (f'<path d="M{cx - 6},{cy - 30} L{cx + 6},{cy - 30} L{cx + 3},{cy + 10} L{cx - 3},{cy + 10} Z" fill="#111"/>'
                f'<circle cx="{cx}" cy="{cy + 21}" r="6" fill="#111"/>')
    if tur == "saglik":
        yildiz = " ".join(f"{cx + (14 if i % 2 == 0 else 6) * math.cos(-math.pi / 2 + i * math.pi / 6):.1f},"
                          f"{cy + 12 + (14 if i % 2 == 0 else 6) * math.sin(-math.pi / 2 + i * math.pi / 6):.1f}"
                          for i in range(12))
        return (f'<circle cx="{cx}" cy="{cy - 22}" r="9" fill="#111"/>'
                f'<path d="M{cx - 22},{cy + 32} L{cx - 20},{cy - 6} Q{cx},{cy - 14} {cx + 20},{cy - 6} '
                f'L{cx + 22},{cy + 32} Z" fill="#111"/><polygon points="{yildiz}" fill="white"/>')
    if tur == "cevre":
        return (f'<line x1="{cx - 16}" y1="{cy + 8}" x2="{cx - 16}" y2="{cy - 26}" stroke="#111" stroke-width="4"/>'
                f'<line x1="{cx - 16}" y1="{cy - 14}" x2="{cx - 28}" y2="{cy - 24}" stroke="#111" stroke-width="3"/>'
                f'<line x1="{cx - 16}" y1="{cy - 6}" x2="{cx - 4}" y2="{cy - 18}" stroke="#111" stroke-width="3"/>'
                f'<line x1="{cx - 32}" y1="{cy + 10}" x2="{cx + 30}" y2="{cy + 10}" stroke="#111" stroke-width="3"/>'
                f'<path d="M{cx + 2},{cy + 22} Q{cx + 14},{cy + 12} {cx + 24},{cy + 22} Q{cx + 14},{cy + 32} {cx + 2},{cy + 22} Z '
                f'M{cx + 24},{cy + 22} L{cx + 32},{cy + 15} L{cx + 32},{cy + 29} Z" fill="#111"/>')
    return ""


GHS = [("alev", "Yanıcı", "Eter, etanol, hekzan"), ("oksit", "Oksitleyici", "Nitratlar, peroksitler"),
       ("patlayici", "Patlayıcı", "Kuru pikrik asit"), ("asindirici", "Aşındırıcı (korozif)", "Derişik H₂SO₄, NaOH"),
       ("gaz", "Basınçlı gaz", "Argon, azot tüpü"), ("zehir", "Akut zehirli", "Siyanürler, HF"),
       ("unlem", "Tahriş edici / zararlı", "Seyreltik asitler"), ("saglik", "Ciddi sağlık tehlikesi",
                                                                  "Kanserojen: Cr(VI), benzen"),
       ("cevre", "Çevreye zararlı", "Cıva, ağır metaller")]


def svg_ghs():
    sut = 3
    W, H = 690, 3 * 210 + 10
    s = [svg_ac(W, H, 760)]
    for i, (tur, ad, ornek) in enumerate(GHS):
        cx = 115 + (i % sut) * 230
        cy = 85 + (i // sut) * 210
        s.append(f'<rect x="{cx - 50}" y="{cy - 50}" width="100" height="100" fill="white" stroke="#D9241B" '
                 f'stroke-width="9" transform="rotate(45 {cx} {cy})"/>')
        s.append(_ghs_sembol(tur, cx, cy))
        s.append(_yazi(cx, cy + 96, ad, 15, "#222", kalin=True))
        s.append(_yazi(cx, cy + 115, ornek, 13, "#555"))
    s.append("</svg>")
    return "".join(s)


def _sym_simsek(cx, cy, r="#111"):
    return f'<path d="M{cx + 6},{cy - 30} L{cx - 14},{cy + 4} L{cx},{cy + 4} L{cx - 8},{cy + 30} L{cx + 16},{cy - 6} L{cx + 2},{cy - 6} Z" fill="{r}"/>'


def _sym_sicak(cx, cy, r="#111"):
    s = f'<rect x="{cx - 24}" y="{cy + 18}" width="48" height="6" fill="{r}"/>'
    for dx in (-14, 0, 14):
        s += f'<path d="M{cx + dx},{cy + 12} q7,-9 0,-18 q-7,-9 0,-18" fill="none" stroke="{r}" stroke-width="3.5"/>'
    return s


def _sym_bio(cx, cy, r="#111"):
    s = ""
    for a in (90, 210, 330):
        x = cx + 11 * math.cos(math.radians(a))
        y = cy - 11 * math.sin(math.radians(a))
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="none" stroke="{r}" stroke-width="5"/>'
    return s + f'<circle cx="{cx}" cy="{cy}" r="5" fill="{r}"/>'


def _sym_radyo(cx, cy, r="#111"):
    s = f'<circle cx="{cx}" cy="{cy}" r="5" fill="{r}"/>'
    for a in (90, 210, 330):
        a1, a2 = math.radians(a - 30), math.radians(a + 30)
        p = [(cx + R * math.cos(t), cy - R * math.sin(t)) for R, t in ((9, a1), (26, a1), (26, a2), (9, a2))]
        s += (f'<path d="M{p[0][0]:.1f},{p[0][1]:.1f} L{p[1][0]:.1f},{p[1][1]:.1f} A26,26 0 0 0 {p[2][0]:.1f},{p[2][1]:.1f} '
              f'L{p[3][0]:.1f},{p[3][1]:.1f} A9,9 0 0 1 {p[0][0]:.1f},{p[0][1]:.1f} Z" fill="{r}"/>')
    return s


def _sym_lazer(cx, cy, r="#111"):
    s = f'<line x1="{cx - 28}" y1="{cy}" x2="{cx}" y2="{cy}" stroke="{r}" stroke-width="4"/>'
    for a in range(0, 360, 30):
        s += (f'<line x1="{cx + 6 * math.cos(math.radians(a)) + 4}" y1="{cy + 6 * math.sin(math.radians(a))}" '
              f'x2="{cx + 18 * math.cos(math.radians(a)) + 4}" y2="{cy + 18 * math.sin(math.radians(a))}" stroke="{r}" stroke-width="3"/>')
    return s


def _sym_gozluk(cx, cy, r="white"):
    return (f'<circle cx="{cx}" cy="{cy - 6}" r="17" fill="{r}"/>'
            f'<rect x="{cx - 26}" y="{cy - 10}" width="52" height="16" rx="8" fill="#1F5AA6" stroke="{r}" stroke-width="3"/>'
            f'<circle cx="{cx - 11}" cy="{cy - 2}" r="6" fill="{r}"/><circle cx="{cx + 11}" cy="{cy - 2}" r="6" fill="{r}"/>'
            f'<path d="M{cx - 18},{cy + 12} Q{cx},{cy + 32} {cx + 18},{cy + 12}" fill="{r}"/>')


def _sym_eldiven(cx, cy, r="white"):
    return (f'<path d="M{cx - 16},{cy + 28} L{cx - 16},{cy - 6} L{cx - 22},{cy - 16} L{cx - 18},{cy - 20} L{cx - 10},{cy - 10} '
            f'L{cx - 10},{cy - 30} L{cx - 4},{cy - 30} L{cx - 4},{cy - 10} L{cx - 2},{cy - 34} L{cx + 4},{cy - 34} L{cx + 4},{cy - 10} '
            f'L{cx + 8},{cy - 30} L{cx + 14},{cy - 30} L{cx + 12},{cy - 8} L{cx + 18},{cy - 22} L{cx + 23},{cy - 20} L{cx + 16},{cy + 4} '
            f'L{cx + 16},{cy + 28} Z" fill="{r}"/>')


def _sym_onluk(cx, cy, r="white"):
    return (f'<path d="M{cx - 10},{cy - 32} L{cx - 26},{cy - 22} L{cx - 30},{cy + 30} L{cx + 30},{cy + 30} L{cx + 26},{cy - 22} '
            f'L{cx + 10},{cy - 32} L{cx},{cy - 10} Z" fill="{r}"/>'
            f'<line x1="{cx}" y1="{cy - 10}" x2="{cx}" y2="{cy + 30}" stroke="#1F5AA6" stroke-width="2"/>')


def _sym_maske(cx, cy, r="white"):
    return (f'<circle cx="{cx}" cy="{cy - 8}" r="22" fill="{r}"/>'
            f'<path d="M{cx - 16},{cy - 2} Q{cx},{cy + 24} {cx + 16},{cy - 2} Z" fill="#1F5AA6" stroke="#1F5AA6"/>'
            f'<line x1="{cx - 16}" y1="{cy - 2}" x2="{cx - 24}" y2="{cy - 10}" stroke="#1F5AA6" stroke-width="2"/>'
            f'<line x1="{cx + 16}" y1="{cy - 2}" x2="{cx + 24}" y2="{cy - 10}" stroke="#1F5AA6" stroke-width="2"/>')


def _sym_kitap(cx, cy, r="white"):
    return (f'<path d="M{cx},{cy - 18} Q{cx - 16},{cy - 26} {cx - 30},{cy - 20} L{cx - 30},{cy + 20} Q{cx - 16},{cy + 14} {cx},{cy + 22} '
            f'Q{cx + 16},{cy + 14} {cx + 30},{cy + 20} L{cx + 30},{cy - 20} Q{cx + 16},{cy - 26} {cx},{cy - 18} Z" fill="{r}"/>'
            f'<line x1="{cx}" y1="{cy - 18}" x2="{cx}" y2="{cy + 22}" stroke="#1F5AA6" stroke-width="2.5"/>' +
            _yazi(cx, cy - 32, "i", 18, r, kalin=True))


def _sym_sigara(cx, cy):
    return (f'<rect x="{cx - 28}" y="{cy - 4}" width="44" height="10" fill="#111"/><rect x="{cx + 18}" y="{cy - 4}" width="8" height="10" fill="#111"/>'
            f'<path d="M{cx + 20},{cy - 10} q6,-8 0,-16" fill="none" stroke="#111" stroke-width="3"/>')


def _sym_kibrit(cx, cy):
    return (_alev(cx, cy - 6, 0.8) + f'<rect x="{cx - 3}" y="{cy + 12}" width="6" height="20" fill="#111"/>')


def _sym_yemek(cx, cy):
    return (f'<path d="M{cx - 26},{cy - 14} L{cx - 4},{cy - 14} L{cx - 7},{cy + 22} L{cx - 23},{cy + 22} Z" fill="#111"/>'
            f'<line x1="{cx + 12}" y1="{cy - 24}" x2="{cx + 12}" y2="{cy + 26}" stroke="#111" stroke-width="4"/>'
            f'<path d="M{cx + 5},{cy - 24} L{cx + 5},{cy - 8} Q{cx + 12},{cy - 2} {cx + 19},{cy - 8} L{cx + 19},{cy - 24}" '
            f'fill="none" stroke="#111" stroke-width="3"/>')


def _sym_su_yangin(cx, cy):
    return (_alev(cx + 8, cy + 6, 0.7) +
            f'<path d="M{cx - 30},{cy - 24} Q{cx - 8},{cy - 30} {cx + 2},{cy - 10}" fill="none" stroke="#111" stroke-width="4"/>'
            f'<circle cx="{cx - 2}" cy="{cy - 4}" r="2.5" fill="#111"/><circle cx="{cx + 6}" cy="{cy - 6}" r="2.5" fill="#111"/>')


def _sym_arti(cx, cy, r="white"):
    return f'<rect x="{cx - 8}" y="{cy - 24}" width="16" height="48" fill="{r}"/><rect x="{cx - 24}" y="{cy - 8}" width="48" height="16" fill="{r}"/>'


def _sym_gozdusu(cx, cy, r="white"):
    return (f'<path d="M{cx - 28},{cy + 8} Q{cx - 6},{cy - 14} {cx + 16},{cy + 8} Q{cx - 6},{cy + 26} {cx - 28},{cy + 8} Z" fill="{r}"/>'
            f'<circle cx="{cx - 6}" cy="{cy + 8}" r="6" fill="#2E8B57"/>'
            f'<path d="M{cx + 22},{cy - 28} Q{cx + 30},{cy - 10} {cx + 14},{cy - 2}" fill="none" stroke="{r}" stroke-width="3"/>'
            f'<path d="M{cx + 10},{cy - 30} Q{cx + 20},{cy - 14} {cx + 4},{cy - 6}" fill="none" stroke="{r}" stroke-width="3"/>')


def _sym_dus(cx, cy, r="white"):
    s = (f'<path d="M{cx - 24},{cy - 30} L{cx + 10},{cy - 30} L{cx + 10},{cy - 22}" fill="none" stroke="{r}" stroke-width="4"/>'
         f'<path d="M{cx},{cy - 22} L{cx + 20},{cy - 22} L{cx + 16},{cy - 16} L{cx + 4},{cy - 16} Z" fill="{r}"/>'
         f'<circle cx="{cx - 6}" cy="{cy - 4}" r="6" fill="{r}"/>'
         f'<path d="M{cx - 14},{cy + 30} L{cx - 12},{cy + 4} L{cx},{cy + 4} L{cx + 2},{cy + 30} Z" fill="{r}"/>')
    for dx in (6, 10, 14, 18):
        s += f'<line x1="{cx + dx}" y1="{cy - 12}" x2="{cx + dx - 4}" y2="{cy + 6}" stroke="{r}" stroke-width="1.5"/>'
    return s


def _sym_cikis(cx, cy, r="white"):
    return (f'<rect x="{cx + 6}" y="{cy - 28}" width="22" height="56" fill="none" stroke="{r}" stroke-width="3"/>'
            f'<circle cx="{cx - 12}" cy="{cy - 20}" r="6" fill="{r}"/>'
            f'<path d="M{cx - 14},{cy - 12} L{cx - 4},{cy + 4} L{cx - 18},{cy + 26} M{cx - 4},{cy + 4} L{cx + 6},{cy + 22} '
            f'M{cx - 12},{cy - 6} L{cx - 26},{cy + 2} M{cx - 10},{cy - 6} L{cx + 2},{cy - 10}" stroke="{r}" stroke-width="5" '
            f'fill="none" stroke-linecap="round"/>' + _ok(cx - 30, cy + 34, cx + 26, cy + 34).replace("#555", r))


def _sym_sondurucu(cx, cy, r="white"):
    return (f'<rect x="{cx - 10}" y="{cy - 18}" width="20" height="46" rx="6" fill="{r}"/>'
            f'<rect x="{cx - 4}" y="{cy - 28}" width="8" height="10" fill="{r}"/>'
            f'<path d="M{cx + 4},{cy - 26} L{cx + 20},{cy - 30} L{cx + 24},{cy - 20}" fill="none" stroke="{r}" stroke-width="3"/>'
            f'<path d="M{cx - 10},{cy - 26} Q{cx - 26},{cy - 22} {cx - 24},{cy + 4}" fill="none" stroke="{r}" stroke-width="3"/>')


def _sym_alarm(cx, cy, r="white"):
    return (f'<rect x="{cx - 20}" y="{cy - 20}" width="40" height="40" rx="4" fill="none" stroke="{r}" stroke-width="3"/>'
            f'<circle cx="{cx}" cy="{cy}" r="9" fill="{r}"/>'
            f'<path d="M{cx - 26},{cy - 26} q-6,6 0,12 M{cx + 26},{cy - 26} q6,6 0,12" stroke="{r}" stroke-width="3" fill="none"/>')


def _isaret_ciz(grup, cx, cy, fn):
    if grup == "Uyarı (tehlike)":
        return (f'<path d="M{cx},{cy - 52} L{cx + 58},{cy + 46} L{cx - 58},{cy + 46} Z" fill="#F7C600" stroke="#111" '
                f'stroke-width="7" stroke-linejoin="round"/>' + fn(cx, cy + 14))
    if grup == "Zorunluluk (emir)":
        return f'<circle cx="{cx}" cy="{cy}" r="50" fill="#1F5AA6"/>' + fn(cx, cy)
    if grup == "Yasak":
        return (f'<circle cx="{cx}" cy="{cy}" r="46" fill="white"/>' + fn(cx, cy) +
                f'<circle cx="{cx}" cy="{cy}" r="46" fill="none" stroke="#D9241B" stroke-width="9"/>'
                f'<line x1="{cx - 32}" y1="{cy - 32}" x2="{cx + 32}" y2="{cy + 32}" stroke="#D9241B" stroke-width="9"/>')
    renk = "#2E8B57" if grup.startswith("Acil") else "#D9241B"
    return f'<rect x="{cx - 48}" y="{cy - 48}" width="96" height="96" rx="6" fill="{renk}"/>' + fn(cx, cy)


def _ust(k):
    tablo_ = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(k).translate(tablo_)


# ===========================================================================
# İSG ŞEMALARI — tamamı bu uygulama için çizilmiştir
# ===========================================================================
KIRMIZI, SARI_U, YESIL_A = "#D9534F", "#F7C600", "#3C9A5F"


# ---------------------------------------------------------------------------
# Tehlike ve risk
# ---------------------------------------------------------------------------
def _makas(cx, cy, k=1.0, renk="#5F6B7A"):
    return (f'<g transform="translate({cx},{cy}) scale({k})">'
            f'<path d="M-6,-10 L40,-34 L44,-28 L2,-2 Z" fill="#B0B8C1" stroke="#555"/>'
            f'<path d="M-6,10 L40,34 L44,28 L2,2 Z" fill="#B0B8C1" stroke="#555"/>'
            f'<circle cx="0" cy="0" r="5" fill="#333"/>'
            f'<path d="M-4,-4 Q-40,-30 -54,-14 Q-48,0 -6,-2 Z" fill="{renk}"/>'
            f'<path d="M-4,4 Q-40,30 -54,14 Q-48,0 -6,2 Z" fill="{KIRMIZI}"/></g>')


def svg_tehlike_risk():
    W, H = 880, 300
    s = [svg_ac(W, H, 900)]
    s.append(_kutu_svg(20, 20, 260, 260, KIRMIZI, [""], 14))
    s.append(_yazi(150, 52, "TEHLİKE", 22, KIRMIZI, kalin=True))
    s.append(_makas(160, 140, 1.4))
    s.append(_yazi(150, 232, "Zarar verme POTANSİYELİ", 15, "#222", kalin=True))
    s.append(_yazi(150, 254, "keskin bağ makası", 14, "#555"))
    s.append(_ok(290, 150, 340, 150))
    s.append(_kutu_svg(350, 20, 510, 260, TURUNCU, [""], 14))
    s.append(_yazi(605, 52, "RİSK = Olasılık × Şiddet", 22, "#B76E00", kalin=True))
    for i, (ad, ol, renk, aciklama) in enumerate([
            ("Dikkatsiz, eldivensiz, kör makas", 0.85, KIRMIZI, "yüksek risk"),
            ("Bakımlı makas + kesme eldiveni + mola", 0.2, YESIL_A, "düşük risk")]):
        y = 100 + i * 90
        s.append(_yazi(380, y, ad, 15, "#222", "start", True))
        s.append(f'<rect x="380" y="{y + 12}" width="440" height="22" rx="11" fill="#EEF1F5"/>')
        s.append(f'<rect x="380" y="{y + 12}" width="{440 * ol:.0f}" height="22" rx="11" fill="{renk}"/>')
        s.append(_yazi(830, y + 28, aciklama, 13, renk, "end", True))
    s.append(_yazi(605, 262, "Tehlike aynı kaldı (makas yine keskin); değişen, zarar görme İHTİMALİ.", 14, "#333"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Kontrol hiyerarşisi (ters piramit)
# ---------------------------------------------------------------------------
KONTROL = [("Ortadan kaldırma", "Tehlikeyi tamamen yok et", "Yabancı ot için ilaç yerine mekanik mücadele", "#1B7A3E"),
           ("İkame", "Daha az tehlikeliyle değiştir", "Daha düşük toksisiteli ilaç", "#4C9F38"),
           ("Mühendislik önlemi", "Tehlikeyi kaynağında yalıt", "ROPS, kuyruk mili koruyucusu, kabinli traktör", "#E8A33B"),
           ("İdari önlem", "Talimat, eğitim, süre sınırı", "Eğitim, uyarı levhası, dönüşümlü çalışma", "#E07B39"),
           ("KKD", "Son çare: kişiyi korur", "Maske, eldiven, tulum, gözlük", KIRMIZI)]


def svg_kontrol(sec=None):
    W, H = 1000, 420
    s = [svg_ac(W, H, 1000)]
    for i, (ad, kisa, ornek, renk) in enumerate(KONTROL):
        y = 20 + i * 76
        gen = 560 - i * 90
        x = 300 - gen / 2 + 20
        op = 1 if sec in (None, i) else 0.35
        s.append(f'<g opacity="{op}"><path d="M{x},{y} L{x + gen},{y} L{x + gen - 45},{y + 68} L{x + 45},{y + 68} Z" '
                 f'fill="{renk}" stroke="white" stroke-width="2"/>')
        s.append(_yazi(320, y + 32, ad, 18 if i < 4 else 17, "white", kalin=True))
        s.append(_yazi(320, y + 54, kisa, 13, "white"))
        s.append(_yazi(600, y + 40, ornek, 15, "#222", "start"))
        s.append("</g>")
    s.append(_yazi(990, 20, "EN ETKİLİ ▲", 14, "#1B7A3E", "end", True))
    s.append(_yazi(990, 412, "EN AZ ETKİLİ ▼", 14, KIRMIZI, "end", True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Risk değerlendirmesi döngüsü
# ---------------------------------------------------------------------------
RA_ADIM = [("Tehlikeleri belirle", "Bağda hangi işlerde hangi tehlikeler var?"),
           ("Riskleri analiz et", "Olasılık ve şiddeti puanla"),
           ("Önlemlere karar ver", "Kontrol hiyerarşisine göre"),
           ("Uygula ve kaydet", "Tedbirleri hayata geçir, belgele"),
           ("İzle, gözden geçir", "Belirli aralıklarla ve değişiklikte")]


def svg_ra_dongu(sec=None):
    W, H = 760, 520
    cx, cy, R = 380, 270, 185
    s = [svg_ac(W, H, 760)]
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#C9D3DD" stroke-width="6" stroke-dasharray="14 10"/>')
    s.append(_yazi(cx, cy - 6, "Risk", 26, "#1F3F73", kalin=True))
    s.append(_yazi(cx, cy + 24, "değerlendirmesi", 20, "#1F3F73", kalin=True))
    for i, (ad, alt) in enumerate(RA_ADIM):
        a = math.radians(-90 + i * 72)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        renk = TURUNCU if sec == i else MAVI
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="64" fill="white" stroke="{renk}" stroke-width="{5 if sec == i else 3}"/>')
        s.append(_yazi(x, y - 22, str(i + 1), 22, renk, kalin=True))
        parca = ad.split(" ")
        for j, p in enumerate([" ".join(parca[:len(parca) // 2 + len(parca) % 2]), " ".join(parca[len(parca) // 2 + len(parca) % 2:])]):
            s.append(_yazi(x, y + 4 + j * 19, p, 15, "#222", kalin=True))
    if sec is not None:
        s.append(_yazi(cx, H - 10, RA_ADIM[sec][1], 17, TURUNCU, kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Çalışan figürü ve KKD
# ---------------------------------------------------------------------------
KKD_LISTE = {"sapka": "Güneş şapkası", "baret": "Baret", "gozluk": "Koruyucu gözlük", "siperlik": "Yüz siperi",
             "maske": "Solunum maskesi", "kulaklik": "Kulak koruyucu", "eldiven_k": "Kesilmeye dayanıklı eldiven",
             "eldiven_c": "Kimyasala dayanıklı eldiven", "tulum": "Koruyucu tulum", "cizme": "Çizme",
             "testere_p": "Testere pantolonu"}


def svg_calisan(kkd):
    W, H = 520, 560
    cx = 260
    s = [svg_ac(W, H, 460)]
    ten, giysi = "#F1C7A5", ("#E7EEF7" if "tulum" in kkd else "#7FA7D6")
    # bacaklar
    pant = "#E8A33B" if "testere_p" in kkd else giysi
    s.append(f'<rect x="{cx - 46}" y="300" width="40" height="190" rx="14" fill="{pant}" stroke="#555" stroke-width="1.5"/>')
    s.append(f'<rect x="{cx + 6}" y="300" width="40" height="190" rx="14" fill="{pant}" stroke="#555" stroke-width="1.5"/>')
    if "cizme" in kkd:
        for dx in (-48, 4):
            s.append(f'<rect x="{cx + dx}" y="428" width="44" height="86" rx="8" fill="#2E7D32" stroke="#1B4D20" stroke-width="1.5"/>')
            s.append(f'<rect x="{cx + dx - (14 if dx < 0 else 0)}" y="500" width="58" height="24" rx="10" fill="#2E7D32" stroke="#1B4D20" stroke-width="1.5"/>')
    else:
        for dx in (-48, 4):
            s.append(f'<rect x="{cx + dx - (12 if dx < 0 else 0)}" y="486" width="56" height="24" rx="10" fill="#5D4037"/>')
    # gövde
    s.append(f'<path d="M{cx - 70},150 Q{cx},128 {cx + 70},150 L{cx + 62},310 L{cx - 62},310 Z" fill="{giysi}" stroke="#555" stroke-width="1.5"/>')
    if "tulum" in kkd:
        s.append(f'<line x1="{cx}" y1="140" x2="{cx}" y2="310" stroke="#9AA6B2" stroke-width="2" stroke-dasharray="4 3"/>')
    # kollar
    for yon in (-1, 1):
        x0 = cx + yon * 70
        s.append(f'<path d="M{x0},155 L{x0 + yon * 40},290 L{x0 + yon * 16},296 L{x0 - yon * 10},175 Z" fill="{giysi}" stroke="#555" stroke-width="1.5"/>')
        el = "#F2C94C" if "eldiven_k" in kkd else ("#2E8B57" if "eldiven_c" in kkd else ten)
        s.append(f'<circle cx="{x0 + yon * 30}" cy="306" r="17" fill="{el}" stroke="#555" stroke-width="1.5"/>')
    # baş
    s.append(f'<rect x="{cx - 14}" y="112" width="28" height="26" fill="{ten}"/>')
    s.append(f'<circle cx="{cx}" cy="80" r="44" fill="{ten}" stroke="#555" stroke-width="1.5"/>')
    if not ({"gozluk", "siperlik"} & kkd):
        s.append(f'<circle cx="{cx - 15}" cy="74" r="4" fill="#333"/><circle cx="{cx + 15}" cy="74" r="4" fill="#333"/>')
    if "maske" not in kkd:
        s.append(f'<path d="M{cx - 12},100 Q{cx},108 {cx + 12},100" fill="none" stroke="#333" stroke-width="2"/>')
    if "gozluk" in kkd:
        s.append(f'<rect x="{cx - 36}" y="62" width="72" height="24" rx="10" fill="#9FD3F5" fill-opacity="0.7" stroke="#1F3F73" stroke-width="3"/>')
    if "maske" in kkd:
        s.append(f'<path d="M{cx - 30},92 Q{cx},128 {cx + 30},92 L{cx + 22},86 L{cx - 22},86 Z" fill="#5F6B7A" stroke="#333"/>'
                 f'<circle cx="{cx - 24}" cy="106" r="11" fill="#E07B39" stroke="#333"/><circle cx="{cx + 24}" cy="106" r="11" fill="#E07B39" stroke="#333"/>')
    if "kulaklik" in kkd:
        s.append(f'<path d="M{cx - 46},70 Q{cx},6 {cx + 46},70" fill="none" stroke="#D9534F" stroke-width="7"/>'
                 f'<rect x="{cx - 60}" y="62" width="20" height="36" rx="8" fill="#D9534F"/><rect x="{cx + 40}" y="62" width="20" height="36" rx="8" fill="#D9534F"/>')
    if "baret" in kkd:
        s.append(f'<path d="M{cx - 50},58 Q{cx},-6 {cx + 50},58 Z" fill="{SARI_U}" stroke="#8A6D00" stroke-width="2"/>'
                 f'<rect x="{cx - 60}" y="52" width="120" height="10" rx="5" fill="{SARI_U}" stroke="#8A6D00"/>')
    elif "sapka" in kkd:
        s.append(f'<ellipse cx="{cx}" cy="48" rx="80" ry="14" fill="#E9D8A6" stroke="#8D6E63" stroke-width="2"/>'
                 f'<path d="M{cx - 40},48 Q{cx},0 {cx + 40},48 Z" fill="#E9D8A6" stroke="#8D6E63" stroke-width="2"/>')
    if "siperlik" in kkd:
        s.append(f'<path d="M{cx - 48},50 L{cx + 48},50 L{cx + 44},120 L{cx - 44},120 Z" fill="#BFE3FF" fill-opacity="0.45" stroke="#1F3F73" stroke-width="2"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Bağ takvimi
# ---------------------------------------------------------------------------
AYLAR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
BAG_ISLERI = {"Budama": ([1, 2, 3], "#8E5BB5"), "Tel/direk işleri": ([1, 2, 11, 12], "#5F6B7A"),
              "Toprak işleme (traktör)": ([3, 4, 5], "#8C5A3C"), "İlaçlama": ([4, 5, 6, 7, 8], KIRMIZI),
              "Yeşil budama (koltuk alma)": ([5, 6, 7], "#4C9F38"), "Hasat (bağbozumu)": ([8, 9, 10], TURUNCU)}


def svg_bag_takvimi(sec=None):
    W, H = 900, 300
    s = [svg_ac(W, H, 920)]
    x0, w = 210, 56
    for m, a in enumerate(AYLAR):
        s.append(_yazi(x0 + m * w + w / 2, 30, a, 14, "#555", kalin=True))
    for m in (5, 6, 7):
        s.append(f'<rect x="{x0 + m * w}" y="38" width="{w}" height="{H - 50}" fill="#FFF1E0"/>')
    s.append(_yazi(x0 + 6.5 * w, H - 6, "en sıcak aylar", 12, "#B76E00"))
    for i, (ad, (aylar, renk)) in enumerate(BAG_ISLERI.items()):
        y = 50 + i * 38
        op = 1 if sec in (None, ad) else 0.25
        s.append(f'<g opacity="{op}">' + _yazi(200, y + 20, ad, 14, "#222", "end", True))
        for m in aylar:
            s.append(f'<rect x="{x0 + (m - 1) * w + 3}" y="{y + 4}" width="{w - 6}" height="24" rx="6" fill="{renk}"/>')
        s.append("</g>")
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Traktör devrilmesi
# ---------------------------------------------------------------------------
def _don(x, y, ox, oy, aci):
    a = math.radians(aci)
    return (ox + (x - ox) * math.cos(a) - (y - oy) * math.sin(a), oy + (x - ox) * math.sin(a) + (y - oy) * math.cos(a))


def svg_traktor_egim(egim, iz, h, rops, kemer):
    """Arkadan görünüş, yamaç sağa doğru alçalıyor. egim: derece; iz: tekerlek iz genişliği (m);
    h: ağırlık merkezi yüksekliği (m)."""
    kritik = math.degrees(math.atan((iz / 2) / h))
    W, H = 720, 440
    s = [svg_ac(W, H, 720)]
    px = 140
    ox, oy = 470, 300
    a = math.radians(egim)
    devrildi = egim >= kritik
    s.append(f'<path d="M0,{oy - ox * math.tan(a):.1f} L{W},{oy + (W - ox) * math.tan(a):.1f} L{W},{H} L0,{H} Z" fill="#C8E6C9"/>')
    don = egim + (28 if devrildi else 0)
    sol = ox - iz * px
    g = [f'<g transform="rotate({don} {ox} {oy})">']
    g.append(f'<rect x="{sol - 30}" y="{oy - 110}" width="60" height="110" rx="20" fill="#333"/>')
    g.append(f'<rect x="{ox - 30}" y="{oy - 110}" width="60" height="110" rx="20" fill="#333"/>')
    g.append(f'<rect x="{sol + 18}" y="{oy - 140}" width="{iz * px - 36}" height="66" rx="8" fill="#C62828"/>')
    g.append(f'<rect x="{(sol + ox) / 2 - 22}" y="{oy - 178}" width="44" height="40" rx="6" fill="#4E342E"/>')
    if rops:
        g.append(f'<path d="M{sol + 24},{oy - 140} L{sol + 24},{oy - 270} L{ox - 24},{oy - 270} L{ox - 24},{oy - 140}" '
                 f'fill="none" stroke="#FBC02D" stroke-width="12" stroke-linejoin="round"/>')
    if kemer:
        g.append(f'<line x1="{(sol + ox) / 2 - 18}" y1="{oy - 178}" x2="{(sol + ox) / 2 + 18}" y2="{oy - 146}" stroke="#1565C0" stroke-width="6"/>')
    gx0, gy0 = (sol + ox) / 2, oy - h * px
    g.append(f'<circle cx="{gx0}" cy="{gy0}" r="10" fill="white" stroke="#111" stroke-width="3"/>')
    g.append("</g>")
    s += g
    gx, gy = _don(gx0, gy0, ox, oy, don)
    s.append(f'<line x1="{gx:.1f}" y1="{gy:.1f}" x2="{gx:.1f}" y2="{oy + 60}" stroke="{KIRMIZI if devrildi else YESIL_A}" '
             f'stroke-width="3" stroke-dasharray="8 5"/>')
    s.append(f'<circle cx="{ox}" cy="{oy}" r="7" fill="{KIRMIZI}"/>')
    s.append(_yazi(ox + 14, oy + 26, "alttaki tekerlek", 13, KIRMIZI, "start", True))
    s.append(_yazi(20, 34, f"Eğim: {egim}°", 20, "#222", "start", True))
    s.append(_yazi(20, 60, f"Statik devrilme açısı ≈ {kritik:.0f}°", 16, "#555", "start"))
    durum = "DEVRİLİYOR!" if devrildi else ("Sınıra yakın!" if egim > kritik - 8 else "Dengede")
    s.append(_yazi(20, 86, durum, 22, KIRMIZI if durum != "Dengede" else YESIL_A, "start", True))
    s.append(_yazi(W - 10, H - 12, "Ağırlık merkezinden inen çizgi alttaki tekerleği geçerse traktör devrilir.", 13, "#333", "end"))
    s.append("</svg>")
    return "".join(s), kritik


# ---------------------------------------------------------------------------
# Kuyruk mili (PTO)
# ---------------------------------------------------------------------------
def svg_pto(koruyucu):
    W, H = 760, 260
    s = [svg_ac(W, H, 760)]
    s.append(f'<rect x="20" y="40" width="160" height="150" rx="14" fill="#C62828"/>')
    s.append(_yazi(100, 120, "TRAKTÖR", 16, "white", kalin=True))
    s.append(f'<rect x="560" y="60" width="180" height="120" rx="10" fill="#5F6B7A"/>')
    s.append(_yazi(650, 125, "ATOMİZÖR", 16, "white", kalin=True))
    s.append(f'<rect x="180" y="108" width="380" height="18" fill="#9AA6B2"/>')
    for x in range(190, 560, 22):
        s.append(f'<line x1="{x}" y1="108" x2="{x + 12}" y2="126" stroke="#5F6B7A" stroke-width="3"/>')
    if koruyucu:
        s.append(f'<rect x="180" y="96" width="380" height="42" rx="20" fill="{SARI_U}" fill-opacity="0.85" stroke="#8A6D00" stroke-width="2"/>')
        s.append(_yazi(370, 122, "mil koruyucusu (muhafaza)", 15, "#5A4600", kalin=True))
        s.append(_yazi(380, 220, "Dönen mil kapalı: giysi dolanamaz.", 18, YESIL_A, kalin=True))
    else:
        s.append(f'<path d="M330,126 Q350,170 300,200 Q270,215 262,240" fill="none" stroke="#E07B39" stroke-width="10"/>')
        s.append(_yazi(250, 254, "atkı", 13, "#E07B39", kalin=True))
        s.append(_yazi(380, 24, "Koruyucusuz mil dakikada yüzlerce devir döner:", 16, KIRMIZI, kalin=True))
        s.append(_yazi(380, 46, "atkı, bol giysi ya da saç saniyeler içinde dolanır.", 16, KIRMIZI, kalin=True))
        for x in (260, 330, 400, 470):
            s.append(f'<path d="M{x},100 a14,14 0 1,1 20,0" fill="none" stroke="{KIRMIZI}" stroke-width="2.5" marker-end="url(#okucu)"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Doğru ve yanlış yük kaldırma
# ---------------------------------------------------------------------------
def svg_kaldirma():
    W, H = 760, 330
    s = [svg_ac(W, H, 760)]
    for i, (baslik, renk) in enumerate([("YANLIŞ: bel bükük, dizler düz", KIRMIZI), ("DOĞRU: dizler bükük, sırt düz", YESIL_A)]):
        ox = 40 + i * 380
        s.append(_yazi(ox + 150, 30, baslik, 17, renk, kalin=True))
        s.append(f'<line x1="{ox}" y1="290" x2="{ox + 320}" y2="290" stroke="#8C5A3C" stroke-width="4"/>')
        if i == 0:
            s.append(f'<line x1="{ox + 120}" y1="290" x2="{ox + 125}" y2="190" stroke="#333" stroke-width="10" stroke-linecap="round"/>'
                     f'<line x1="{ox + 150}" y1="290" x2="{ox + 135}" y2="190" stroke="#333" stroke-width="10" stroke-linecap="round"/>'
                     f'<line x1="{ox + 130}" y1="190" x2="{ox + 230}" y2="160" stroke="#333" stroke-width="12" stroke-linecap="round"/>'
                     f'<circle cx="{ox + 252}" cy="168" r="20" fill="#333"/>'
                     f'<line x1="{ox + 215}" y1="165" x2="{ox + 240}" y2="250" stroke="#333" stroke-width="8" stroke-linecap="round"/>'
                     f'<rect x="{ox + 220}" y="250" width="60" height="40" fill="{TURUNCU}" stroke="#8D5A00"/>')
            s.append(f'<path d="M{ox + 150},176 Q{ox + 175},150 {ox + 205},164" fill="none" stroke="{KIRMIZI}" stroke-width="4"/>')
            s.append(_yazi(ox + 170, 140, "bel zorlanır", 15, KIRMIZI, kalin=True))
        else:
            s.append(f'<path d="M{ox + 110},290 L{ox + 150},240 L{ox + 120},200" fill="none" stroke="#333" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
                     f'<path d="M{ox + 170},290 L{ox + 200},240 L{ox + 140},200" fill="none" stroke="#333" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
                     f'<line x1="{ox + 130}" y1="200" x2="{ox + 145}" y2="110" stroke="#333" stroke-width="12" stroke-linecap="round"/>'
                     f'<circle cx="{ox + 150}" cy="86" r="20" fill="#333"/>'
                     f'<line x1="{ox + 142}" y1="125" x2="{ox + 175}" y2="200" stroke="#333" stroke-width="8" stroke-linecap="round"/>'
                     f'<rect x="{ox + 160}" y="190" width="60" height="40" fill="{TURUNCU}" stroke="#8D5A00"/>')
            s.append(_yazi(ox + 270, 150, "yük vücuda", 14, YESIL_A, kalin=True))
            s.append(_yazi(ox + 270, 168, "yakın", 14, YESIL_A, kalin=True))
            s.append(_yazi(ox + 60, 150, "sırt düz", 14, YESIL_A, kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Gürültü ölçeği
# ---------------------------------------------------------------------------
GURULTU = [(30, "Fısıltı"), (60, "Normal konuşma"), (78, "Kabinli traktör"), (90, "Kabinsiz traktör"),
           (100, "Motorlu tırpan"), (105, "Motorlu testere"), (120, "Ağrı eşiğine yakın")]


def svg_db(secili=None):
    W, H = 900, 260
    s = [svg_ac(W, H, 920)]
    x0, x1 = 40, 860

    def x(db):
        return x0 + (x1 - x0) * db / 130

    for a, b, renk in [(0, 80, "#C8E6C9"), (80, 85, "#FFF3B0"), (85, 87, "#FFD08A"), (87, 130, "#F8B4B4")]:
        s.append(f'<rect x="{x(a):.0f}" y="110" width="{x(b) - x(a):.0f}" height="40" fill="{renk}"/>')
    for db in range(0, 131, 10):
        s.append(f'<line x1="{x(db):.0f}" y1="150" x2="{x(db):.0f}" y2="160" stroke="#555"/>' + _yazi(x(db), 178, str(db), 13, "#555"))
    for db, ad, renk in [(80, "80: önlem başlar", "#8A6D00"), (85, "85: kulaklık zorunlu", "#B76E00"), (87, "87: sınır değer", KIRMIZI)]:
        s.append(f'<line x1="{x(db):.0f}" y1="100" x2="{x(db):.0f}" y2="160" stroke="{renk}" stroke-width="3"/>')
    s.append(_yazi(x(80) - 4, 214, "80: önlemler başlar", 13, "#8A6D00", "end", True))
    s.append(_yazi(x(85), 234, "85: kulak koruyucu zorunlu", 13, "#B76E00", kalin=True))
    s.append(_yazi(x(87) + 4, 214, "87: maruziyet sınır değeri", 13, KIRMIZI, "start", True))
    for i, (db, ad) in enumerate(GURULTU):
        sec = (secili == ad)
        y = [92, 70, 48, 92, 70, 48, 92][i]
        s.append(f'<line x1="{x(db):.0f}" y1="{y + 4}" x2="{x(db):.0f}" y2="110" stroke="{TURUNCU if sec else "#888"}" stroke-width="{3 if sec else 1.5}"/>')
        s.append(_yazi(x(db), y, f"{ad} ~{db}", 14 if sec else 13, TURUNCU if sec else "#333", kalin=sec))
    s.append(_yazi(450, 26, "Gürültü düzeyi, dB(A) — her +3 dB ses enerjisini İKİYE katlar", 16, "#222", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Domino teorisi ve kaza piramidi
# ---------------------------------------------------------------------------
DOMINO = ["Sosyal çevre ve kişisel geçmiş", "Kişisel kusurlar", "Güvensiz davranış / durum", "Kaza", "Yaralanma / hasar"]


def svg_domino(orta_cekildi):
    W, H = 900, 330
    s = [svg_ac(W, H, 920)]
    for i, ad in enumerate(DOMINO):
        x = 70 + i * 170
        if orta_cekildi and i == 2:
            s.append(f'<rect x="{x - 26}" y="70" width="52" height="170" rx="6" fill="none" stroke="#AAB4BF" stroke-width="2" stroke-dasharray="7 5"/>')
            s.append(_yazi(x, 162, "ÇEKİLDİ", 13, YESIL_A, kalin=True))
            renk, don = "#C8E6C9", 0
        else:
            dustu = (not orta_cekildi) or i < 2
            don = 28 if dustu else 0
            renk = KIRMIZI if (i >= 3 and not orta_cekildi) else (MAVI if i < 3 else "#9AA6B2")
            s.append(f'<rect x="{x - 26}" y="70" width="52" height="170" rx="6" fill="{renk}" stroke="#333" stroke-width="2" '
                     f'transform="rotate({don} {x + 26} 240)"/>')
        for j, p in enumerate(_iki_satir(ad)):
            s.append(_yazi(x, 270 + j * 18, p, 13, "#222", kalin=True))
    s.append(_yazi(450, 34, "Ortadaki taş (güvensiz davranış ve durum) çekilirse zincir kırılır" if orta_cekildi
                   else "Taşlar sırayla devrilir: kaza ve yaralanma kaçınılmaz", 17,
                   YESIL_A if orta_cekildi else KIRMIZI, kalin=True))
    s.append("</svg>")
    return "".join(s)


def _iki_satir(t, sinir=14):
    if len(t) <= sinir:
        return [t]
    k = t.split(" ")
    yarim = len(k) // 2 + len(k) % 2
    return [" ".join(k[:yarim]), " ".join(k[yarim:])]


def svg_bird(k=1):
    W, H = 760, 400
    s = [svg_ac(W, H, 760)]
    katman = [("Ciddi yaralanma / ölüm", 1, KIRMIZI), ("Hafif yaralanma", 10, "#E07B39"),
              ("Yalnızca maddi hasar", 30, SARI_U), ("Ramak kala olay", 600, YESIL_A)]
    cx, tep, alt = 260, 30, 370
    for i, (ad, n, renk) in enumerate(katman):
        y1 = tep + (alt - tep) * i / 4
        y2 = tep + (alt - tep) * (i + 1) / 4
        w1 = (y1 - tep) * 0.9
        w2 = (y2 - tep) * 0.9
        s.append(f'<path d="M{cx - w1},{y1} L{cx + w1},{y1} L{cx + w2},{y2} L{cx - w2},{y2} Z" fill="{renk}" stroke="white" stroke-width="3"/>')
        s.append(_yazi(cx, (y1 + y2) / 2 + 9, f"{n * k:,}".replace(",", "."), 22 if i else 18, "white" if i != 2 else "#333", kalin=True))
        s.append(f'<line x1="{cx + (w1 + w2) / 2 + 6}" y1="{(y1 + y2) / 2}" x2="520" y2="{(y1 + y2) / 2}" stroke="#AAB4BF"/>')
        s.append(_yazi(530, (y1 + y2) / 2 + 6, ad, 17, "#222", "start", True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# 5×5 risk matrisi
# ---------------------------------------------------------------------------
def risk_duzey(p):
    if p == 1:
        return "Önemsiz", "#C8E6C9"
    if p <= 6:
        return "Düşük", "#8BC34A"
    if p <= 12:
        return "Orta", SARI_U
    if p <= 16:
        return "Yüksek", "#FB8C00"
    return "Tolere edilemez", KIRMIZI


def svg_matris(o=None, sd=None):
    W, H = 640, 550
    s = [svg_ac(W, H, 640)]
    x0, y0, c = 140, 40, 88
    for i, ol in enumerate(range(5, 0, -1)):
        s.append(_yazi(x0 - 14, y0 + i * c + c / 2 + 6, str(ol), 18, "#222", "end", True))
        for j, sid in enumerate(range(1, 6)):
            p = ol * sid
            _, renk = risk_duzey(p)
            sec = (ol == o and sid == sd)
            s.append(f'<rect x="{x0 + j * c}" y="{y0 + i * c}" width="{c - 4}" height="{c - 4}" rx="8" fill="{renk}" '
                     f'stroke="{"#111" if sec else "white"}" stroke-width="{6 if sec else 2}"/>')
            s.append(_yazi(x0 + j * c + c / 2 - 2, y0 + i * c + c / 2 + 8, str(p), 24 if sec else 20, "#111", kalin=sec))
    for j in range(5):
        s.append(_yazi(x0 + j * c + c / 2, y0 + 5 * c + 22, str(j + 1), 18, "#222", kalin=True))
    s.append(_yazi(x0 + 2.5 * c, y0 + 5 * c + 52, "ŞİDDET →", 17, "#222", kalin=True))
    s.append(f'<text x="40" y="{y0 + 2.5 * c}" {YAZI} font-size="17" font-weight="700" fill="#222" text-anchor="middle" '
             f'transform="rotate(-90 40 {y0 + 2.5 * c})">OLASILIK →</text>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Yangın üçgeni ve söndürücü kullanımı
# ---------------------------------------------------------------------------
def svg_yangin_ucgeni():
    W, H = 640, 360
    s = [svg_ac(W, H, 640)]
    s.append(f'<path d="M320,40 L560,320 L80,320 Z" fill="#FFF3E0" stroke="{KIRMIZI}" stroke-width="10" stroke-linejoin="round"/>')
    s.append(_alev(320, 230, 1.6).replace("#111", "#E65100"))
    s.append(_yazi(190, 170, "ISI", 22, KIRMIZI, "end", True))
    s.append(_yazi(450, 170, "OKSİJEN", 22, KIRMIZI, "start", True))
    s.append(_yazi(320, 350, "YAKIT (yanıcı madde)", 22, KIRMIZI, kalin=True))
    s.append(_yazi(320, 110, "Biri çekilirse", 15, "#333", kalin=True))
    s.append(_yazi(320, 130, "yangın söner", 15, "#333", kalin=True))
    s.append("</svg>")
    return "".join(s)


PASS = [("1 · Pimi çek", "Mühürlü pimi çekerek çıkar."), ("2 · Ateşin dibine yönelt", "Hortumu alevin kaynağına, dibine tut."),
        ("3 · Tetiğe bas", "Kolu sıkarak söndürücüyü boşalt."), ("4 · Süpür", "Hortumu ateşin dibinde sağa sola süpürür gibi hareket ettir.")]


def svg_pass(adim):
    W, H = 620, 330
    s = [svg_ac(W, H, 620)]
    cx = 170
    s.append(f'<rect x="{cx - 34}" y="110" width="68" height="190" rx="22" fill="{KIRMIZI}" stroke="#8B1E1B" stroke-width="2"/>')
    s.append(f'<rect x="{cx - 12}" y="80" width="24" height="32" fill="#555"/>')
    s.append(f'<path d="M{cx - 12},80 L{cx - 60},60 L{cx - 56},52 L{cx + 4},74 Z" fill="#333"/>')
    s.append(f'<path d="M{cx + 12},86 L{cx + 60},70" stroke="#333" stroke-width="6"/>')
    s.append(f'<rect x="{cx - 26}" y="160" width="52" height="60" rx="4" fill="white"/>')
    s.append(f'<circle cx="{cx}" cy="138" r="14" fill="white" stroke="#333" stroke-width="2"/>'
             f'<path d="M{cx},138 L{cx + 8},130" stroke="{YESIL_A}" stroke-width="3"/>')
    pim = adim == 0
    s.append(f'<g transform="translate({40 if pim else 0},{-20 if pim else 0})"><circle cx="{cx + 22}" cy="92" r="9" fill="none" '
             f'stroke="#FBC02D" stroke-width="4"/></g>')
    if adim >= 1:
        s.append(f'<path d="M{cx - 30},118 Q{cx - 110},150 {cx - 60},230 Q{cx - 20},260 {cx + 150},260" fill="none" stroke="#222" stroke-width="7"/>')
        s.append(f'<path d="M{cx + 150},252 L{cx + 175},248 L{cx + 175},272 L{cx + 150},268 Z" fill="#222"/>')
    if adim >= 2:
        don = {2: 0, 3: -12}[adim] if adim in (2, 3) else 0
        s.append(f'<g transform="rotate({don} {cx + 175} 260)"><path d="M{cx + 175},252 L{cx + 330},215 L{cx + 330},305 Z" '
                 f'fill="#E3F2FD" opacity="0.9"/></g>')
    s.append(_alev(cx + 330, 262, 1.3).replace("#111", "#FB8C00"))
    s.append(f'<rect x="{cx + 280}" y="292" width="110" height="10" fill="#8C5A3C"/>')
    if adim == 3:
        s.append(f'<path d="M{cx + 300},320 Q{cx + 330},300 {cx + 360},320" fill="none" stroke="#1565C0" stroke-width="3" marker-end="url(#okucu)" marker-start="url(#okucu)"/>')
    s.append(_yazi(W / 2, 30, PASS[adim][0], 22, "#222", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Güvenlik ve sağlık işaretleri (ders notundaki 12.2–12.5)
# ---------------------------------------------------------------------------
def _sym_baret(cx, cy, r="white"):
    return (f'<circle cx="{cx}" cy="{cy + 10}" r="18" fill="{r}"/>'
            f'<path d="M{cx - 30},{cy - 2} Q{cx},{cy - 44} {cx + 30},{cy - 2} Z" fill="{r}"/>'
            f'<rect x="{cx - 36}" y="{cy - 6}" width="72" height="7" rx="3" fill="{r}"/>')


def _sym_kulak(cx, cy, r="white"):
    return (f'<circle cx="{cx}" cy="{cy + 2}" r="20" fill="{r}"/>'
            f'<path d="M{cx - 26},{cy} Q{cx},{cy - 46} {cx + 26},{cy}" fill="none" stroke="{r}" stroke-width="6"/>'
            f'<rect x="{cx - 34}" y="{cy - 6}" width="14" height="26" rx="6" fill="{r}" stroke="#1F5AA6" stroke-width="2"/>'
            f'<rect x="{cx + 20}" y="{cy - 6}" width="14" height="26" rx="6" fill="{r}" stroke="#1F5AA6" stroke-width="2"/>')


def _sym_cizme(cx, cy, r="white"):
    return (f'<path d="M{cx - 18},{cy - 30} L{cx + 4},{cy - 30} L{cx + 4},{cy + 8} L{cx + 28},{cy + 14} L{cx + 28},{cy + 28} '
            f'L{cx - 18},{cy + 28} Z" fill="{r}"/>')


def _sym_yaya(cx, cy):
    return (f'<circle cx="{cx + 2}" cy="{cy - 26}" r="7" fill="#111"/>'
            f'<path d="M{cx},{cy - 16} L{cx - 4},{cy + 6} L{cx - 14},{cy + 28} M{cx - 4},{cy + 6} L{cx + 8},{cy + 28} '
            f'M{cx - 2},{cy - 10} L{cx - 16},{cy} M{cx},{cy - 10} L{cx + 14},{cy - 2}" stroke="#111" stroke-width="5" '
            f'fill="none" stroke-linecap="round"/>')


def _sym_kaygan(cx, cy, r="#111"):
    return (f'<circle cx="{cx - 12}" cy="{cy - 16}" r="6" fill="{r}"/>'
            f'<path d="M{cx - 10},{cy - 8} L{cx + 4},{cy + 8} L{cx + 22},{cy + 2} M{cx + 4},{cy + 8} L{cx - 14},{cy + 18} '
            f'M{cx - 8},{cy - 4} L{cx - 24},{cy + 2}" stroke="{r}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
            f'<line x1="{cx - 26}" y1="{cy + 26}" x2="{cx + 26}" y2="{cy + 26}" stroke="{r}" stroke-width="3"/>')


def _sym_is_makinesi(cx, cy, r="#111"):
    return (f'<rect x="{cx - 24}" y="{cy - 6}" width="34" height="18" fill="{r}"/>'
            f'<rect x="{cx - 14}" y="{cy - 24}" width="16" height="18" fill="none" stroke="{r}" stroke-width="3"/>'
            f'<circle cx="{cx - 16}" cy="{cy + 18}" r="8" fill="{r}"/><circle cx="{cx + 6}" cy="{cy + 20}" r="6" fill="{r}"/>'
            f'<line x1="{cx + 16}" y1="{cy - 24}" x2="{cx + 16}" y2="{cy + 20}" stroke="{r}" stroke-width="3"/>'
            f'<line x1="{cx + 16}" y1="{cy + 20}" x2="{cx + 30}" y2="{cy + 20}" stroke="{r}" stroke-width="3"/>')


def _sym_toplanma(cx, cy, r="white"):
    s = ""
    for dx, dy in [(-18, -16), (18, -16), (-18, 16), (18, 16)]:
        s += f'<circle cx="{cx + dx}" cy="{cy + dy - 6}" r="5" fill="{r}"/><rect x="{cx + dx - 4}" y="{cy + dy}" width="8" height="10" fill="{r}"/>'
    for a in range(0, 360, 90):
        x1 = cx + 40 * math.cos(math.radians(a))
        y1 = cy + 40 * math.sin(math.radians(a))
        x2 = cx + 28 * math.cos(math.radians(a))
        y2 = cy + 28 * math.sin(math.radians(a))
        s += f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{r}" stroke-width="3"/>'
    return s


def _sym_telefon(cx, cy, r="white", arti=True):
    s = (f'<path d="M{cx - 22},{cy - 10} Q{cx - 22},{cy - 26} {cx},{cy - 26} Q{cx + 22},{cy - 26} {cx + 22},{cy - 10} '
         f'L{cx + 12},{cy - 10} L{cx + 10},{cy - 16} L{cx - 10},{cy - 16} L{cx - 12},{cy - 10} Z" fill="{r}"/>'
         f'<rect x="{cx - 18}" y="{cy - 6}" width="36" height="30" rx="5" fill="{r}"/>')
    if arti:
        s += f'<rect x="{cx - 3}" y="{cy}" width="6" height="18" fill="#2E8B57"/><rect x="{cx - 9}" y="{cy + 6}" width="18" height="6" fill="#2E8B57"/>'
    return s


def _sym_hidrant(cx, cy, r="white"):
    return (f'<circle cx="{cx}" cy="{cy}" r="22" fill="none" stroke="{r}" stroke-width="7"/>'
            f'<circle cx="{cx}" cy="{cy}" r="8" fill="{r}"/>'
            f'<path d="M{cx + 22},{cy} L{cx + 34},{cy + 26}" stroke="{r}" stroke-width="5"/>')


ISARETLER_ISG = {
    "Yasaklayıcı": ("Yasak", "Yuvarlak; kırmızı kenar ve çapraz çizgi, beyaz zemin: bir davranışı YASAKLAR", [
        ("Sigara içmek yasaktır", _sym_sigara, "İlaç deposu, yakıt deposu, saman ambarı"),
        ("Açık ateşle yaklaşmak yasaktır", _sym_kibrit, "Yakıt deposu, gaz tüpü, kuru ot ve saman yakını"),
        ("Yayaların girmesi yasaktır", _sym_yaya, "Traktör ve iş makinesinin çalıştığı alan"),
        ("Yemek ve içmek yasaktır", _sym_yemek, "İlaç hazırlama yeri, laboratuvar"),
        ("Su ile söndürmek yasaktır", _sym_su_yangin, "Elektrik panosu, yakıt deposu")]),
    "Uyarı": ("Uyarı (tehlike)", "Üçgen; sarı zemin, siyah kenar: bir tehlikeye karşı UYARIR", [
        ("Genel tehlike", lambda cx, cy: _ghs_sembol("unlem", cx, cy + 6), "Başka işaretle anlatılamayan tehlikeler"),
        ("Elektrik tehlikesi", _sym_simsek, "Elektrik panosu, sulama pompası"),
        ("Zehirli madde", lambda cx, cy: _ghs_sembol("zehir", cx, cy + 2), "İlaç deposu, yeni ilaçlanmış alan"),
        ("Yanıcı madde", lambda cx, cy: _ghs_sembol("alev", cx, cy + 2), "Yakıt deposu, LPG tüpü"),
        ("Kaygan zemin, düşme tehlikesi", _sym_kaygan, "Islak depo zemini, merdiven, teras kenarı"),
        ("İş makinesi tehlikesi", _sym_is_makinesi, "Traktör ve forkliftin çalıştığı alan")]),
    "Emredici": ("Zorunluluk (emir)", "Yuvarlak; mavi zemin, beyaz sembol: bir davranışı (çoğunlukla KKD) ZORUNLU kılar", [
        ("Baret takınız", _sym_baret, "Yüksekte çalışma, yüksek istifli depo"),
        ("Kulak koruyucu takınız", _sym_kulak, "Traktör, motorlu testere"),
        ("Koruyucu gözlük takınız", _sym_gozluk, "Budama, ilaç hazırlama"),
        ("Koruyucu eldiven giyiniz", _sym_eldiven, "Budama, ilaçlama"),
        ("Solunum koruyucu takınız", _sym_maske, "İlaçlama, tozlu iş"),
        ("İş ayakkabısı veya çizme giyiniz", _sym_cizme, "Bağ işleri, depo")]),
    "Acil durum": ("Acil durum / ilk yardım", "Kare ya da dikdörtgen; yeşil zemin, beyaz sembol: kaçış yolu, ilk yardım, güvenli durum", [
        ("İlk yardım", _sym_arti, "İlk yardım çantasının yeri"),
        ("Acil çıkış", _sym_cikis, "Kaçış yolu ve çıkış kapısı"),
        ("Acil toplanma alanı", _sym_toplanma, "Binaların dışındaki güvenli alan"),
        ("Göz yıkama", _sym_gozdusu, "İlaç hazırlama yeri, laboratuvar"),
        ("Acil telefon", _sym_telefon, "112 ve Zehir Danışma 114 numaraları")]),
    "Yangınla mücadele": ("Yangın ekipmanı", "Kare ya da dikdörtgen; kırmızı zemin, beyaz sembol: yangın ekipmanının yeri", [
        ("Yangın söndürücü", _sym_sondurucu, "Depo, traktör garajı, bağ evi"),
        ("Yangın alarm butonu", _sym_alarm, "Bina girişi ve koridor"),
        ("Yangın hidrantı ve dolabı", _sym_hidrant, "Büyük depo ve işletmeler"),
        ("Yangın acil telefonu", lambda cx, cy: _sym_telefon(cx, cy, arti=False), "Yangın dolabının yanı")]),
}


def svg_isaret_grubu(grup, secili=None):
    cizim_grup, _, liste = ISARETLER_ISG[grup]
    sut = 3
    satir = (len(liste) + sut - 1) // sut
    W, H = 690, satir * 190 + 10
    s = [svg_ac(W, H, 720)]
    for i, (ad, fn, _) in enumerate(liste):
        cx = 115 + (i % sut) * 230
        cy = 72 + (i // sut) * 190
        op = 1 if secili in (None, ad) else 0.35
        s.append(f'<g opacity="{op}">' + _isaret_ciz(cizim_grup, cx, cy, fn))
        for j, p in enumerate(_iki_satir(ad, 18)):
            s.append(_yazi(cx, cy + 80 + j * 18, p, 15, "#222", kalin=True))
        s.append("</g>")
    s.append("</svg>")
    return "".join(s)


def svg_isaret_turleri_isg():
    W, H = 900, 240
    s = [svg_ac(W, H, 920)]
    for i, (g, (cg, acik, liste)) in enumerate(ISARETLER_ISG.items()):
        cx = 90 + i * 180
        s.append(_isaret_ciz(cg, cx, 85, liste[0][1]))
        s.append(_yazi(cx, 170, g, 16, "#222", kalin=True))
    # GHS
    s.append("</svg>")
    return "".join(s)


# ===========================================================================
# VERİ (ders notundan)
# ===========================================================================
TEMEL_KAVRAM = [
    ("İş sağlığı", "Çalışanların bedensel, ruhsal ve sosyal açıdan tam iyilik hâlinin sürdürülmesini ve işin çalışana, "
                   "çalışanın işe uyumunu amaçlayan çalışmalar bütünü."),
    ("İş güvenliği", "İşin yürütülmesi sırasında sağlığa zarar verebilecek tehlike ve risklerden çalışanları korumaya "
                     "yönelik sistemli çalışmalar."),
    ("Tehlike", "İşyerinde var olan ya da dışarıdan gelebilecek, çalışanı veya işyerini etkileyebilecek zarar veya hasar "
                "verme potansiyeli."),
    ("Risk", "Tehlikeden kaynaklanacak kayıp, yaralanma ya da başka zararlı sonucun meydana gelme ihtimali."),
    ("İş kazası", "İşyerinde veya işin yürütümü sırasında meydana gelen, bedensel veya ruhsal bir zarara yol açan olay."),
    ("Meslek hastalığı", "Sürdürülen işin niteliğine bağlı olarak, işyeri koşulları nedeniyle tekrarlanan bir sebeple "
                         "ortaya çıkan sağlık sorunu."),
]
KKD_TABLO = [
    ("Koruyucu eldiven", "Kesici aletlerde el yaralanmalarını, ilaçlamada cilt temasını önler"),
    ("Koruyucu gözlük / yüz siperi", "Budamada göze dal/tel sıçramasını, ilaçlamada göz temasını önler"),
    ("Solunum maskesi (yarım/tam yüz)", "İlaçlamada kimyasal buhar ve aerosol solunumunu azaltır"),
    ("Koruyucu tulum", "İlaçlamada cilt ve kıyafet temasını önler"),
    ("Çizme", "Islak/kaygan zeminde ve ilaçlamada ayak korumasını sağlar"),
    ("Kulak koruyucu", "Traktör ve motorlu ekipmanla uzun çalışmada işitme kaybını önler"),
    ("Güneşten koruyucu başlık", "Uzun süre açık havada güneş çarpmasını ve cilt hasarını azaltır"),
]
KONTROL_ORNEK = [
    ("Yabancı ot için herbisit yerine mekanik mücadele", "Ortadan kaldırma"),
    ("Daha düşük toksisiteli bir ilaca geçmek", "İkame"),
    ("Traktöre ROPS takmak", "Mühendislik önlemi"), ("Kuyruk miline koruyucu takmak", "Mühendislik önlemi"),
    ("Kabinli traktör kullanmak", "Mühendislik önlemi"), ("İlaçlama öncesi eğitim vermek", "İdari önlem"),
    ("Sıcak saatlerde dönüşümlü çalışma düzeni", "İdari önlem"), ("Depo kapısına uyarı levhası asmak", "İdari önlem"),
    ("Solunum maskesi takmak", "KKD"), ("Kesilmeye dayanıklı eldiven giymek", "KKD"), ("Kulak koruyucu takmak", "KKD"),
]
ORNEK_RA = [
    ("Bağ makasıyla kesik", "El/parmak yaralanması", "Orta", "Kesme eldiveni, bakımlı alet, dikkatli kullanım eğitimi"),
    ("Pestisit maruziyeti", "Zehirlenme, cilt/göz tahrişi", "Yüksek", "Tam KKD, PHI'ye uyum, doğru karışım eğitimi"),
    ("Traktör devrilmesi", "Ağır yaralanma, ölüm", "Yüksek", "ROPS, emniyet kemeri, eğik arazide dikkatli sürüş"),
    ("Uzun süre eğilerek çalışma", "Bel/sırt ağrısı, kas-iskelet hastalığı", "Orta", "Ergonomik duruş eğitimi, dönüşümlü çalışma, mola"),
]
DEVRILME = [
    ("Yana devrilme", "Eğime dik çalışma, hendek ve teras kenarı, yüksek hızla dönüş, ön yükleyicide yükü yukarıda taşıma",
     "Eğimde yavaş gitmek, teras kenarından uzak durmak, yükü alçakta taşımak, iz genişliğini artırmak"),
    ("Arkaya devrilme", "Ağır yükü yüksek noktadan çekmek, saplanan traktörü zorlamak, rampada ani kalkış",
     "Yükü yalnızca çeki demirinden çekmek, saplanınca geri geri çıkmak, ön ağırlık kullanmak"),
]
EKIPMAN = [
    ("Elektrikli/akülü budama makası", "Parmak kesilmesi, kas zorlanması",
     "Boştaki el bıçak hattından uzak, kesilmeye dayanıklı eldiven, düzenli bileme ve bakım"),
    ("Motorlu testere", "Geri tepme (bıçak ucu sert cisme değip testereyi yukarı fırlatır), kesik, gürültü, titreşim",
     "Zincir freni, iki elle tutma, omuz hizasının üstünde kesmeme, testere pantolonu, kask, siperlik, kulaklık"),
    ("İlaçlama atomizörü/pulverizatörü", "Pestisit maruziyeti, hortum patlaması, kuyruk mili",
     "Sızdırmazlık ve hortum kontrolü, tıkanan meme asla ağızla üflenmez, rüzgâr yönüne dikkat, tam KKD"),
]
SICAK = {
    "Sıcak bitkinliği": ("Bol terleme, halsizlik, baş ağrısı, bulantı, baş dönmesi",
                         "Serin ve gölge yere al, giysileri gevşet, bilinci açıksa yudum yudum su içir, dinlendir"),
    "Sıcak çarpması (ACİL)": ("Vücut ısısı çok yüksek (40 °C ve üzeri), bilinç bulanıklığı, saçma konuşma, nöbet; terleme durmuş olabilir",
                              "Hemen 112'yi ara, gölgeye al, su ve ıslak bezle soğut, bilinci kapalıysa ağızdan bir şey verme"),
}
BIYOLOJIK = [
    ("Arı ve eşek arısı sokması", "İğneyi tırnakla kazıyarak çıkar, soğuk uygula; nefes darlığı, yüzde/dilde şişlik, bayılma varsa hemen 112",
     "İğneyi sıkarak çekmek (zehir kesesini boşaltır)"),
    ("Yılan sokması", "Sakin kal, sokulan uzvu hareketsiz tut, yüzük ve saati çıkar, hemen 112", "Yarayı kesmek, ağızla emmek, turnike, buz"),
    ("Akrep sokması", "Soğuk uygula, hareketsiz tut, özellikle çocuklarda hemen 112", "Yarayı kesmek, emmek"),
    ("Kene tutunması", "En kısa sürede sağlık kuruluşunda ya da ince uçlu pensle deriye yakın tutup çıkar; sonraki günlerde ateş, "
                       "halsizlik olursa doktora git", "Elle ezmek, üzerine kolonya, sigara ateşi ya da yağ sürmek"),
    ("Tetanoz", "Toprak bulaşmış her kesik ve batmada yarayı temizle, aşı durumunu kontrol ettir", "Aşıyı ihmal etmek"),
]
KALDIRMA_DY = [
    ("Ali hasat kasasını dizleri düz, belini bükerek yerden kaldırıyor.", False, "Dizler bükülür, sırt düz tutulur."),
    ("Ayşe kasayı göğsüne yakın tutarak bacaklarıyla kalkıyor.", True, "Doğru: yük vücuda yakın, güç bacaklardan."),
    ("Mehmet dolu kasayı elinde tutarken belini çevirerek arkasındaki traktöre koyuyor.", False,
     "Bel değil ayaklar çevrilir."),
    ("Fatma iki kasayı üst üste taşımak yerine iki seferde taşıyor.", True, "Doğru: ağır yük bölünür."),
    ("Hasan yüksek dalı budarken basamaksız bir kasanın üstüne çıkıyor.", False, "Sağlam ve uygun merdiven kullanılır."),
]
MEVSIMLIK = [
    ("Ulaşım", "Kapasitesinin üzerinde doldurulmuş kamyonet, minibüs ve römorkla taşıma; yorgun sürücü",
     "Yalnızca yolcu taşımaya uygun, ruhsatlı araçla ve oturarak taşıma; römorkta insan taşınmaz"),
    ("Barınma", "Çadırda, sel ve yangına açık alanlarda kalma, elektrik kaçağı",
     "Güvenli konaklama alanı, düzgün elektrik tesisatı, yangın söndürücü"),
    ("Hijyen ve su", "Temiz içme suyu ve tuvalet yokluğu, ishal ve salgın hastalık",
     "Temiz su, tuvalet, el yıkama; ilaçlama sonrası yıkanma"),
    ("Sağlık", "Sıcak stresi, pestisit maruziyeti, uzun çalışma saatleri",
     "Mola, gölge, ilaçlanan alana bekleme süresi dolmadan girmeme"),
]
CEVRE = {
    "Deprem": ("Bağ evinin, deponun ya da istinat duvarının yıkılması", "Sağlam yapı, ağır eşyaları sabitleme, deprem çantası, toplanma alanını bilme"),
    "Sel ve taşkın": ("Dere yatağına yakın bağ ve barınma alanlarının su altında kalması", "Dere yatağında barınmamak, meteoroloji uyarılarını izlemek"),
    "Yıldırım": ("Açık arazide, tek ağaç altında ya da traktör üstünde çarpılma",
                 "Fırtınada açık alandan, tek ağaçtan ve metal teller yanından uzaklaşmak; kapalı araç ya da binaya girmek"),
    "Orman ve anız yangını": ("Bağa sıçrayan yangın, rüzgârla yayılan alevler",
                              "Anız yakmamak, yangın şeridi, bağ kenarında kuru ot temizliği, 112'ye hemen haber vermek"),
    "Heyelan": ("Eğimli bağ ve teraslarda toprak kayması", "Teras ve istinat duvarlarını bakımlı tutmak, kaymanın işaretlerini (çatlak, eğilen direk) bildirmek"),
    "Aşırı sıcak ve soğuk": ("Sıcak çarpması, don ve soğuk yaralanması", "Çalışma saatlerini havaya göre düzenlemek, uygun giyinmek"),
    "Trafik": ("Bağ yolu ile karayolu kavşağında traktör kazası", "Görünür olmak, kavşakta durup bakmak, işaretli araç"),
    "Kimyasal kirlilik": ("Komşu parselden pestisit sürüklenmesi, sulama suyunun kirlenmesi", "İlaçlamada rüzgâr yönüne dikkat, komşuyu önceden bilgilendirmek"),
    "Hayvanlar": ("Başıboş köpek, yılan, arı kovanı", "Dikkatli olmak, ilk yardım bilgisini tazelemek"),
}
BINA = [
    ("Yangın", "Prizde aşırı yük, yakıt ve kuru malzeme birikimi, sigara", "Düzenli depolama, uygun yangın söndürücü, sigara yasağı, kaçış yolunu açık tutmak"),
    ("Elektrik", "Hasarlı kablo, ıslak zeminde priz, topraklamasız tesisat", "Yetkili elektrikçi, kaçak akım rölesi, hasarlı kabloyu hemen değiştirmek"),
    ("Gaz ve karbonmonoksit", "LPG tüpü kaçağı, kapalı ortamda soba ya da jeneratör",
     "Tüpü dışarıda ve dik tutmak, sabunlu suyla kaçak kontrolü, havalandırma, karbonmonoksit dedektörü"),
    ("Düşme", "Kaygan zemin, korkuluksuz merdiven ve çatı, yüksekte istif", "Kuru ve temiz zemin, korkuluk, sağlam merdiven, ağır malzemeyi alta istiflemek"),
    ("Deprem", "Devrilen raf ve dolap, düşen eşya", "Raf ve dolapları duvara sabitlemek, ağır eşyayı alt raflara koymak"),
    ("Kimyasal", "Pestisitin gıda ve yemle aynı yerde durması", "Kilitli, havalandırmalı ve etiketli ilaç deposu"),
    ("Aydınlatma ve havalandırma", "Karanlık depo, havasız ilaç deposu", "Yeterli ışık, doğal ya da mekanik havalandırma"),
]
YANGIN_SINIF = {
    "A": ("Katı maddeler", "Odun, saman, karton, kasa"), "B": ("Yanıcı sıvılar", "Benzin, mazot, boya"),
    "C": ("Yanıcı gazlar", "LPG, doğalgaz"), "D": ("Yanıcı metaller", "Magnezyum, alüminyum tozu"),
    "F": ("Yemeklik yağlar", "Mutfakta yanan yağ"),
}
SONDURUCU = ["Su", "Köpük", "Kuru kimyevi toz", "CO₂", "D sınıfı toz", "F sınıfı / ıslak battaniye"]
UYGUNLUK = {  # sınıf -> söndürücü -> (✔ uygun / ✘ uygun değil / – önerilmez)
    "A": ["✔", "✔", "✔", "–", "–", "–"], "B": ["✘", "✔", "✔", "✔", "–", "–"], "C": ["✘", "–", "✔ (önce vana)", "–", "–", "–"],
    "D": ["✘", "✘", "✘", "✘", "✔", "–"], "F": ["✘", "–", "–", "–", "–", "✔"],
    "Elektrik": ["✘", "✘", "✔ (önce elektrik kesilir)", "✔ (önce elektrik kesilir)", "–", "–"],
}
YANAN = {"Kuru saman ve kasa": "A", "Odun deposu": "A", "Mazot bidonu": "B", "Benzin": "B", "Boya": "B",
         "LPG tüpü": "C", "Magnezyum tozu": "D", "Tavada yanan yağ": "F", "Elektrik panosu": "Elektrik", "Sulama pompası motoru": "Elektrik"}
GUVENSIZ = [
    ("Güvensiz davranış (insan kaynaklı)", "KKD takmadan ilaçlamak, emniyet kemeri takmamak, yorgun ya da aceleyle çalışmak, "
                                          "dönen kuyruk milinin üstünden geçmek", "Eğitim, gözetim, yeterli mola, kurallara uyulmasını sağlamak"),
    ("Güvensiz durum (ortam ve ekipman kaynaklı)", "ROPS'suz traktör, koruyucusu sökülmüş kuyruk mili, bakımsız testere, kaygan zemin, "
                                                   "karanlık depo", "Bakım, koruyucuların yerinde olması, düzen ve temizlik, aydınlatma"),
]
FK_OLASILIK = [("Beklenmez", 0.2), ("Beklenmez ama mümkün", 0.5), ("Mümkün ama düşük", 1), ("Olası", 3),
               ("Kuvvetle muhtemel", 6), ("Çok kuvvetle muhtemel", 10)]
FK_FREKANS = [("Çok seyrek (yılda bir ya da daha az)", 0.5), ("Oldukça seyrek (yılda birkaç kez)", 1), ("Seyrek (ayda bir)", 2),
              ("Ara sıra (haftada bir)", 3), ("Sık (günde bir)", 6), ("Sürekli", 10)]
FK_SIDDET = [("Önemsiz (ilk yardım gerekmez)", 1), ("Önemli (ilk yardım)", 3), ("Ciddi (iş günü kaybı)", 7),
             ("Çok ciddi (uzuv kaybı, kalıcı hasar)", 15), ("Çok kötü (ölüm)", 40), ("Felaket (birden çok ölüm)", 100)]


def fk_sinif(p):
    if p >= 400:
        return "Tolerans gösterilemez, iş durdurulur", KIRMIZI
    if p >= 200:
        return "Yüksek, kısa sürede önlem", "#FB8C00"
    if p >= 70:
        return "Önemli, önlem planlanır", SARI_U
    if p >= 20:
        return "Olası, izlenir", "#8BC34A"
    return "Önemsiz", "#C8E6C9"


MH_FARK = [("Ortaya çıkış", "Ani, belirli bir anda", "Yavaş, uzun sürede"), ("Neden", "Tek bir olay", "Tekrarlanan maruziyet"),
           ("Fark edilme", "Hemen", "Çoğu zaman geç, bazen işten ayrıldıktan sonra"),
           ("Örnek", "Traktör devrilmesi, testere kesiği", "İşitme kaybı, kronik pestisit etkisi, bel fıtığı")]
MH_ETMEN = [
    ("Fiziksel", "Gürültü", "Gürültüye bağlı işitme kaybı (traktör, testere)"),
    ("Fiziksel", "Titreşim", "El-kol titreşim sendromu (parmaklarda beyazlama), bel rahatsızlıkları"),
    ("Fiziksel", "Güneşin morötesi ışınları", "Deri kanseri, göz hasarı"),
    ("Kimyasal", "Pestisitler", "Akut ve kronik zehirlenme, sinir sistemi etkileri, deri hastalıkları"),
    ("Kimyasal", "Organik tozlar, küflü saman ve yem", "Çiftçi akciğeri gibi alerjik akciğer hastalıkları, astım"),
    ("Biyolojik", "Bakteri, virüs, parazit", "Bruselloz, tetanoz, Kırım-Kongo Kanamalı Ateşi (kene), leptospiroz"),
    ("Ergonomik", "Ağır yük, eğilerek ve tekrarlı çalışma", "Bel fıtığı, omuz ve dirsek rahatsızlıkları"),
    ("Psikososyal", "Uzun çalışma saatleri, gelir belirsizliği, yalnız çalışma", "Stres, tükenmişlik, uyku bozuklukları"),
]
GHS_PESTISIT = [("zehir", "Akut toksisite (çok zehirli)", "Az miktarı bile öldürücü olabilir"),
                ("asindirici", "Aşındırıcı", "Ciltte ve gözde ağır hasar yapar"),
                ("unlem", "Zararlı, tahriş edici", "Cildi ve gözü tahriş eder, zararlıdır"),
                ("saglik", "Ciddi sağlık tehlikesi", "Kanser, solunum, üreme sağlığı etkileri"),
                ("cevre", "Çevreye zararlı", "Su canlıları için zehirlidir"), ("alev", "Alevlenir", "Kolay tutuşur, ateşten uzak tutulur")]
ISARET_NEREYE = {
    "İlaç deposunun kapısı": {"Sigara içmek yasaktır", "Zehirli madde", "Solunum koruyucu takınız", "Koruyucu eldiven giyiniz",
                              "Açık ateşle yaklaşmak yasaktır"},
    "Elektrik panosu": {"Elektrik tehlikesi", "Su ile söndürmek yasaktır"},
    "Traktör garajı": {"Yangın söndürücü", "Sigara içmek yasaktır", "Kulak koruyucu takınız", "İş makinesi tehlikesi"},
    "İlaç hazırlama yeri": {"Yemek ve içmek yasaktır", "Koruyucu gözlük takınız", "Koruyucu eldiven giyiniz",
                            "Solunum koruyucu takınız", "Göz yıkama"},
    "Bağ evinin çıkış kapısı": {"Acil çıkış", "Acil toplanma alanı"},
    "Alet odası (testere, budama makası)": {"Koruyucu eldiven giyiniz", "Koruyucu gözlük takınız", "Kulak koruyucu takınız"},
}
KKD_ESLE_SOL = ["Kesilmeye dayanıklı eldiven", "Kimyasala dayanıklı eldiven", "Filtreli maske", "Toz maskesi", "Koruyucu gözlük",
                "Siperlik", "Çizme", "Kulaklık", "Baret", "Budama makası", "Testere", "İlaçlama pompası", "Traktör anahtarı",
                "ROPS + emniyet kemeri"]
KKD_ESLE_SAG = {"A": "Bağda budama", "B": "İlaçlama", "C": "Traktörle çalışma", "D": "Testere ile kesim", "E": "Gürültülü ortam",
                "F": "Düşen cisim riski", "G": "Kimyasal sıçrama/maruziyet", "H": "Kesik/yaralanma riski", "I": "Ayak yaralanması",
                "J": "Traktör devrilmesi", "K": "Tozlu ortam", "L": "İlaçlama pompası temizliği"}
KKD_ESLE_CEVAP = {
    "Kesilmeye dayanıklı eldiven": ("ADH", "Budama ve testerede el kesilmesini önler"),
    "Kimyasala dayanıklı eldiven": ("BGL", "İlaçlama ve pompa temizliğinde cilt temasını engeller"),
    "Filtreli maske": ("BG", "Pestisit buharı/tozuna karşı solunum koruması"), "Toz maskesi": ("K", "Tozlu ortamda solunum koruması"),
    "Koruyucu gözlük": ("ABDG", "Göz yaralanması ve kimyasal sıçramaya karşı"),
    "Siperlik": ("BDG", "Yüz ve göz koruması, özellikle ilaçlama/testere"),
    "Çizme": ("ABCDI", "Ayak koruması, kesilme/batma/kimyasal temas"), "Kulaklık": ("CDE", "Traktör ve testere gürültüsüne karşı"),
    "Baret": ("CDF", "Düşen cisim ve kafa travmasına karşı"), "Budama makası": ("AH", "Budama işinin temel ekipmanı"),
    "Testere": ("DH", "Kalın dal/odun kesimi, kesik riski"), "İlaçlama pompası": ("BGL", "İlaçlama uygulaması ve temizliği"),
    "Traktör anahtarı": ("CJ", "Traktörle çalışma, devrilme riski"), "ROPS + emniyet kemeri": ("CJ", "Traktör devrilmesinde operatörü korur"),
}
TEHLIKE_AVI = {
    "A. Alet ve ekipman": ["Budama makası, testere, balta gibi kesici aletler kılıflı ve düzenli mi?",
                           "Kesici aletler çocukların ulaşamayacağı yerde mi?", "Kırık, paslı, gevşek saplı alet yok mu?",
                           "İlaçlama pompası temiz, etiketli ve sızdırmaz mı?", "Pompa hortumu, meme ve contalar sağlam mı?",
                           "Traktörde ROPS var mı?", "Traktörde emniyet kemeri var ve kullanılıyor mu?",
                           "Traktörde far, flaşör, ayna, korna çalışıyor mu?", "Elektrikli aletlerin kablosu/prizi sağlam mı?",
                           "Aletler kullanımdan sonra temizlenip yerine konuyor mu?"],
    "B. İlaç / kimyasal": ["Pestisitler kilitli dolap veya ayrı depoda mı?", "İlaçlar gıda, yem ve içecekten ayrı mı?",
                           "İlaç ambalajları orijinal etiketli mi?", "Boş ilaç ambalajları uygun şekilde bertaraf ediliyor mu?",
                           "İlaçlama sırasında maske, eldiven, gözlük, tulum kullanılıyor mu?", "İlaçlama sonrası kıyafet ayrı yıkanıyor mu?",
                           "İlaçlama sonrası duş alınıyor mu?", "İlaçlama rüzgârlı havada yapılmıyor mu?",
                           "İlaçlama alanına çocuk/hayvan sokulmuyor mu?", "Zehirlenmede aranacak numaralar (112 / 114) biliniyor mu?"],
    "C. KKD": ["Eldiven (kesilmeye + kimyasala dayanıklı) var mı?", "Maske (toz + filtreli) var mı?", "Koruyucu gözlük / siperlik var mı?",
               "Çizme / dayanıklı ayakkabı var mı?", "Baret var mı?", "Kulaklık var mı?", "KKD temiz ve kullanılabilir durumda mı?",
               "KKD kişiye özel mi (ortak kullanım yok mu)?"],
    "D. Ergonomi ve çalışma düzeni": ["Ağır yük kaldırırken doğru teknik kullanılıyor mu?", "Uzun süre eğilerek çalışmada mola veriliyor mu?",
                                      "Budama/hasatta doğru duruş sağlanıyor mu?", "Çalışma alanında gölge/dinlenme yeri var mı?",
                                      "Yeterli su içiliyor mu?", "Öğle saatlerinde ağır iş yapılmıyor mu?"],
    "E. Acil durum ve ilk yardım": ["İlk yardım çantası var mı?", "Çantanın içi eksiksiz mi?", "Çantanın yeri herkesçe biliniyor mu?",
                                    "Yangın söndürücü var mı, kontrol tarihi geçmemiş mi?", "Acil çıkış / toplanma yeri belli mi?",
                                    "112 ve 114 numaraları görünür yerde mi?", "Telefon çekiyor mu, şarjı var mı?"],
    "F. Çevresel ve genel riskler": ["Elektrik kabloları açıkta / ezik / ıslak zeminde değil mi?", "Su birikintisi, kaygan zemin, çukur yok mu?",
                                     "Yangına sebep olabilecek kuru ot, saman, yakıt birikimi yok mu?", "Yakıt/yağ deposu güvenli mi?",
                                     "Hayvanların (köpek, arı, yılan) riskine karşı önlem var mı?", "Güneş çarpmasına karşı önlem alınıyor mu?",
                                     "Çalışma alanı yeterince aydınlık mı?", "İşe başlamadan önce risk değerlendirmesi yapılıyor mu?"],
}
TERIMLER = [
    ("İş sağlığı", TEMEL_KAVRAM[0][1]), ("İş güvenliği", TEMEL_KAVRAM[1][1]), ("Tehlike", TEMEL_KAVRAM[2][1]),
    ("Risk", TEMEL_KAVRAM[3][1]), ("İş kazası", TEMEL_KAVRAM[4][1]), ("Meslek hastalığı", TEMEL_KAVRAM[5][1]),
    ("6331 sayılı Kanun", "2012 tarihli İş Sağlığı ve Güvenliği Kanunu; tarım dahil tüm işyerlerini kapsar."),
    ("KKD", "Kişisel koruyucu donanım: kontrol hiyerarşisinde son çare."),
    ("Risk değerlendirmesi", "Tehlikeleri belirleme, analiz, önlem kararı, uygulama ve izlemeden oluşan döngü."),
    ("Kontrol hiyerarşisi", "Ortadan kaldırma → ikame → mühendislik → idari önlem → KKD."),
    ("PHI", "Hasat öncesi bekleme süresi: son ilaçlama ile hasat arasında bırakılması gereken süre."),
    ("SDS / GBF", "Güvenlik Bilgi Formu: kimyasalın tehlikelerini ve acil durumda yapılacakları anlatır."),
    ("ROPS", "Devrilmeye karşı koruma yapısı; ancak emniyet kemeriyle korur."),
    ("Kuyruk mili (PTO)", "Traktör gücünü bağlı makineye aktaran dönen mil; koruyucusuz mile giysi dolanır."),
    ("Geri tepme", "Testere bıçağının ucu sert cisme değince testerenin yukarı fırlaması."),
    ("Sıcak çarpması", "Vücut ısısı 40 °C ve üstü, bilinç bulanıklığı; acil durumdur, 112 aranır."),
    ("dB(A)", "Gürültü düzeyi birimi; 80'de önlem başlar, 85'te kulak koruyucu zorunlu, 87 sınır değer."),
    ("El-kol titreşimi", "Motorlu testere ve tırpandan; parmaklarda uyuşma ve beyazlama yapar."),
    ("Tüm vücut titreşimi", "Traktör ve engebeli araziden; bel ve sırt rahatsızlıklarına yol açar."),
    ("KKKA", "Kırım-Kongo Kanamalı Ateşi; keneyle bulaşan ciddi hastalık."),
    ("Ramak kala olay", "Zarar verme potansiyeli olduğu hâlde zarara yol açmayan olay."),
    ("Kaza bildirimi", "İşveren iş kazasını en geç 3 iş günü içinde SGK'ya bildirir."),
    ("Kaçak akım rölesi", "Elektrik kaçağında akımı keserek çarpılmayı önleyen cihaz."),
    ("Domino teorisi", "Heinrich: kaza art arda devrilen beş taşa benzer; ortadaki taş çekilirse zincir kırılır."),
    ("Kaza piramidi", "Bird (1969): 1 ciddi : 10 hafif : 30 maddi hasar : 600 ramak kala."),
    ("5×5 risk matrisi", "Risk = olasılık × şiddet; 1–25 arası puan."),
    ("Fine-Kinney", "Risk = olasılık × frekans × şiddet; 400 ve üstü tolerans gösterilemez."),
    ("KSO", "Kaza sıklık oranı = kaza sayısı × 1 000 000 / toplam çalışma saati."),
    ("KAO", "Kaza ağırlık oranı = kayıp iş günü × 1000 / toplam çalışma saati."),
    ("Yangın üçgeni", "Isı, yakıt ve oksijen; biri çekilirse yangın söner."),
    ("A sınıfı yangın", "Katı maddeler: odun, saman, karton."), ("B sınıfı yangın", "Yanıcı sıvılar: benzin, mazot, boya."),
    ("C sınıfı yangın", "Yanıcı gazlar: LPG, doğalgaz."), ("D sınıfı yangın", "Yanıcı metaller: magnezyum."),
    ("F sınıfı yangın", "Yemeklik yağlar; asla su kullanılmaz."),
    ("Emredici işaret", "Mavi yuvarlak, beyaz sembol: bir davranışı zorunlu kılar."),
    ("Yasaklayıcı işaret", "Kırmızı kenarlı, çapraz çizgili yuvarlak: bir davranışı yasaklar."),
    ("Uyarı işareti", "Sarı üçgen, siyah kenar: tehlikeye karşı uyarır."),
    ("Acil durum işareti", "Yeşil kare: kaçış yolu, ilk yardım."), ("Yangınla mücadele işareti", "Kırmızı kare: yangın ekipmanının yeri."),
]


# ===========================================================================
# SAYFALAR
# ===========================================================================
def sayfa_giris():
    st.title("🦺 İş Sağlığı ve Güvenliği · Bağcılık")
    st.markdown("""
Bağcılık Programı **İş Sağlığı ve Güvenliği** dersi için hazırlanmış etkileşimli bir ders
uygulaması. Bağda budamadan hasada, traktörden ilaç deposuna kadar karşılaşılan tehlikeleri
**şemalar, simülasyonlar, hesaplayıcılar ve etkinliklerle** öğrenirsiniz. Her bölümün sonunda
**10, 20 ya da 30 soruluk alıştırma** ve **adım adım çözümler** var.""")
    svg_goster(svg_bag_takvimi())
    kartlar([
        ("1 · İSG'ye giriş", "Temel kavramlar, tehlike–risk, 6331 sayılı Kanun, kazaların nedenleri"),
        ("2 · Bağcılıkta riskler ve KKD", "İşe göre tehlikeler, pestisit güvenliği, PHI hesabı, KKD giydirme"),
        ("3 · Risk değerlendirmesi ve acil durum", "Beş adım, kontrol hiyerarşisi, ilk müdahale"),
        ("4 · Traktör ve bağ makineleri", "Devrilme simülatörü, ROPS ve kemer, kuyruk mili, günlük kontrol listesi"),
        ("5 · Fiziksel, biyolojik, ergonomik", "Sıcak stresi, gürültü ve titreşim, doğru kaldırma, sokmalar ve kene"),
        ("6 · Özel gruplar ve İSG yönetimi", "Mevsimlik işçi, çocuk, genç, gebe; yangın-elektrik; kaza bildirimi, ramak kala"),
        ("7 · Çevre, bina ve yangın", "Doğal tehlikeler, bina tehlikeleri, yangın sınıfları, söndürücü kullanımı"),
        ("8 · Kaza kuramları", "Güvensiz davranış/durum, domino teorisi, kaza piramidi, kontrol hiyerarşisi"),
        ("9 · Risk puanlama ve kaza oranları", "5×5 matris, Fine-Kinney, kaza sıklık ve ağırlık oranı"),
        ("10 · Meslek hastalıkları", "Kaza ile farkı, tarımdaki etmenler, korunma ve tanı"),
        ("11 · Güvenlik işaretleri", "Yasak, uyarı, emir, acil durum, yangın; pestisit etiketi; hangi işaret nereye?"),
        ("12 · Uygulama etkinlikleri", "KKD eşleştirme, tehlike avı kontrol listesi, çıkış kartı"),
        ("13 · Genel tekrar", "Tüm konulardan karışık sorular"),
    ])
    st.markdown("**Hazırlayanlar:** Emine Dilşat Yeğenoğlu & Tevfik Hasan Can")
    uyari("<b>Acil durumda:</b> tek numara <b>112</b>. Zehirlenmelerde ayrıca <b>Ulusal Zehir Danışma Merkezi: 114</b>.")
    ipucu("Telefonda bölümleri sayfanın en üstündeki <b>Bölüm</b> kutusundan ya da sayfa sonundaki "
          "<b>Önceki / Sonraki</b> bağlantılarından seçebilirsiniz.")


# ---------------------------------------------------------------------------
TEHLIKE_RISK = [("Bağ makasının keskin ağzı", "Tehlike"), ("Eldivensiz budamada parmağın kesilme ihtimali", "Risk"),
                ("Depodaki pestisit", "Tehlike"), ("Maskesiz ilaçlamada zehirlenme olasılığı", "Risk"),
                ("Eğimli arazi ve traktör", "Tehlike"), ("ROPS'suz traktörün devrilip sürücüyü ezme ihtimali", "Risk"),
                ("Kabinsiz traktörün gürültüsü", "Tehlike"), ("Yıllarca kulaklıksız çalışan birinin işitme kaybı yaşama olasılığı", "Risk"),
                ("Elektrik panosundaki gerilim", "Tehlike"), ("Islak elle prize dokunan kişinin çarpılma ihtimali", "Risk")]
DAVRANIS_DURUM = [("KKD takmadan ilaçlamak", "Güvensiz davranış"), ("Emniyet kemeri takmamak", "Güvensiz davranış"),
                  ("Yorgun ve aceleyle çalışmak", "Güvensiz davranış"), ("Dönen kuyruk milinin üstünden geçmek", "Güvensiz davranış"),
                  ("Tıkanan memeyi ağızla üflemek", "Güvensiz davranış"), ("ROPS'suz traktör", "Güvensiz durum"),
                  ("Koruyucusu sökülmüş kuyruk mili", "Güvensiz durum"), ("Bakımsız, kör testere", "Güvensiz durum"),
                  ("Kaygan depo zemini", "Güvensiz durum"), ("Karanlık ilaç deposu", "Güvensiz durum"),
                  ("Freni tutmayan traktör", "Güvensiz durum"), ("Kısayol arayıp korkuluğun üstünden atlamak", "Güvensiz davranış")]


def _mini_oyun(anahtar, liste, secenekler, soru):
    if f"{anahtar}_i" not in st.session_state:
        st.session_state[f"{anahtar}_i"] = int(rng().integers(0, len(liste)))
    metin, dogru = liste[st.session_state[f"{anahtar}_i"]]
    st.markdown(f'<div class="flash" style="font-size:1.1rem">{metin}</div>', unsafe_allow_html=True)
    st.caption(soru)
    kol = st.columns(len(secenekler) + 1)
    yanit = None
    for k, sec in zip(kol, secenekler):
        if k.button(sec, key=f"{anahtar}_{sec}"):
            yanit = sec
    if kol[-1].button("➡️ Başka", key=f"{anahtar}_yeni"):
        st.session_state[f"{anahtar}_i"] = int(rng().integers(0, len(liste)))
        st.rerun()
    if yanit is not None:
        if yanit == dogru:
            st.success(f"Doğru: {dogru}.")
        else:
            st.error(f"Tekrar düşünün: bu bir **{dogru.lower()}**.")


def sayfa_temel():
    st.title("1 · İş sağlığı ve güvenliğine giriş")
    st.header("Temel kavramlar")
    tablo(pd.DataFrame(TEMEL_KAVRAM, columns=["Kavram", "Tanım"]))
    st.subheader("Tehlike ile risk aynı şey değildir")
    svg_goster(svg_tehlike_risk())
    st.markdown("**🎯 Mini oyun: tehlike mi, risk mi?**")
    _mini_oyun("tr", TEHLIKE_RISK, ["Tehlike", "Risk"], "Zarar verme potansiyeli mi (tehlike), zarar görme ihtimali mi (risk)?")

    st.header("Yasal çerçeve: 6331 sayılı Kanun")
    st.markdown("""
Türkiye'de iş sağlığı ve güvenliğinin temel dayanağı **6331 sayılı İş Sağlığı ve Güvenliği Kanunu**'dur
(**2012**). Kamu ve özel sektörün bütün işlerini ve işyerlerini kapsar; **tarım ve hayvancılık işleri de
bu kapsamdadır**.""")
    c1, c2 = st.columns(2)
    with c1:
        kutu("<b>👔 İşverenin yükümlülükleri</b><br>• Mesleki riskleri önlemek, eğitim ve bilgi dahil her türlü "
             "tedbiri almak<br>• <b>Risk değerlendirmesi</b> yaptırmak<br>• Uygun <b>KKD</b> sağlamak<br>"
             "• Çalışanları bilgilendirmek ve eğitmek")
    with c2:
        kutu("<b>👷 Çalışanın yükümlülükleri</b><br>• Kendi ve etkilediği diğer çalışanların güvenliğini "
             "gözetmek<br>• Eğitim ve talimatlara uymak<br>• Kendisine verilen <b>KKD'yi doğru kullanmak</b>")
    ipucu("İSG yalnızca işverenin değil, çalışanın da sorumluluğundadır. İki taraf birlikte hareket etmedikçe "
          "önlemler etkili olmaz.")

    st.header("İş kazaları neden olur?")
    st.markdown("Kazalar genellikle tek bir nedenle değil, birden çok etmenin bir araya gelmesiyle olur:")
    tablo(pd.DataFrame({"Neden grubu": ["Güvensiz davranış (insan kaynaklı)", "Güvensiz durum (ortam ve ekipman kaynaklı)"],
                        "Örnekler": ["KKD kullanmamak, dikkatsizlik, acele, eğitimsiz/tecrübesiz personel, yorgunluk, kısayol aramak",
                                     "Bakımsız alet-makine, uygun olmayan koruyucu donanım, düzensiz depolama, kaygan/engebeli zemin, "
                                     "yetersiz aydınlatma"]}))
    st.markdown("**🎯 Mini oyun: güvensiz davranış mı, güvensiz durum mu?**")
    _mini_oyun("dd", DAVRANIS_DURUM, ["Güvensiz davranış", "Güvensiz durum"], "Kişiden mi, ortam/ekipmandan mı kaynaklanıyor?")
    kutu("<b>Tarım neden yüksek riskli?</b> Açık havada değişken koşullarda çalışılır; <b>makine</b> (traktör, "
         "alet-ekipman) ve <b>kimyasal</b> (pestisit, gübre) kullanımı bir aradadır. Bu yüzden tarım, dünyada iş "
         "kazası ve meslek hastalığı riski yüksek sektörler arasındadır.")
    alistirma_blogu("temel", "İSG'ye giriş", gen_temel)


# ---------------------------------------------------------------------------
BAG_TEHLIKE = {
    "Budama": ("Kesici alet yaralanmaları (bağ makası, testere); tekrarlayan hareketten kas-iskelet sorunları",
               "Keskin ve bakımlı alet; kesme eldiveni; düzenli mola", {"eldiven_k", "gozluk", "cizme", "sapka"}),
    "İlaçlama": ("Kimyasala solunum, cilt ve göz yoluyla maruziyet; yanlış karışımla zehirlenme",
                 "Solunum maskesi, tulum, eldiven, gözlük; rüzgârda çalışmama; etiket talimatına uyma",
                 {"maske", "gozluk", "eldiven_c", "tulum", "cizme"}),
    "Toprak işleme (traktör)": ("Traktör devrilmesi, kuyruk miline takılma, gürültü, titreşim",
                                "ROPS ve emniyet kemeri, mil koruyucusu, kulak koruyucu", {"kulaklik", "sapka", "cizme"}),
    "Tel/direk işleri": ("El-parmak sıkışması, telin kırbaçlanması, göz yaralanması",
                         "Koruyucu eldiven ve gözlük; germe aletini doğru kullanma", {"eldiven_k", "gozluk", "cizme"}),
    "Hasat (bağbozumu)": ("Eğilerek tekrarlayan hareket, sıcak çarpması, kesici alet yaralanması",
                          "Ergonomik duruş, mola, sıvı tüketimi, güneşten korunma", {"sapka", "eldiven_k", "cizme"}),
    "Motorlu testere ile kesim": ("Geri tepme, kesik, gürültü, titreşim",
                                  "Zincir freni, iki elle tutma, testere pantolonu, kask, siperlik, kulaklık",
                                  {"baret", "siperlik", "kulaklik", "eldiven_k", "testere_p", "cizme"}),
    "Merdivende çalışma (çardak)": ("Düşme", "Sağlam ve uygun merdiven, denge kontrolü", {"eldiven_k", "cizme", "sapka"}),
}


def sayfa_kkd():
    st.title("2 · Bağcılıkta risk etmenleri ve KKD")
    st.markdown("Bağda yıl boyunca farklı işler yapılır ve her işin kendine özgü tehlikeleri vardır. Bir iş seçin:")
    is_ = st.selectbox("Bağ işi", list(BAG_TEHLIKE))
    takvim = {"Toprak işleme (traktör)": "Toprak işleme (traktör)", "Hasat (bağbozumu)": "Hasat (bağbozumu)",
              "Budama": "Budama", "İlaçlama": "İlaçlama", "Tel/direk işleri": "Tel/direk işleri"}.get(is_)
    svg_goster(svg_bag_takvimi(takvim))
    tehlike, onlem, kkd = BAG_TEHLIKE[is_]
    c1, c2 = st.columns([1.2, 1])
    with c1:
        uyari(f"<b>⚠️ Başlıca tehlike:</b> {tehlike}")
        ipucu(f"<b>Önlem:</b> {onlem}")
        st.markdown("**Bu iş için gereken KKD:**")
        for k in kkd:
            st.markdown(f"- {KKD_LISTE[k]}")
    with c2:
        svg_goster(svg_calisan(kkd))

    st.header("🎯 Çalışanı siz giydirin")
    st.markdown("Bir iş seçin, sonra gereken kişisel koruyucu donanımları işaretleyin.")
    c1, c2 = st.columns([1.1, 1])
    with c1:
        hedef = st.selectbox("Hangi iş için?", list(BAG_TEHLIKE), key="giydir_is")
        secilen = set()
        for k, ad in KKD_LISTE.items():
            if st.checkbox(ad, key=f"giydir_{hedef}_{k}"):
                secilen.add(k)
        kontrol = st.button("✔ Kontrol et", key="giydir_kontrol")
    with c2:
        svg_goster(svg_calisan(secilen))
    if kontrol:
        gerek = BAG_TEHLIKE[hedef][2]
        eksik = gerek - secilen
        fazla = secilen - gerek
        if not eksik:
            st.success("Tebrikler, gereken bütün KKD tamam!" + (f" (Fazladan seçtikleriniz: {', '.join(KKD_LISTE[k] for k in fazla)}; "
                                                                "zararı yok ama bu iş için şart değil.)" if fazla else ""))
        else:
            st.error("Eksik: " + ", ".join(KKD_LISTE[k] for k in eksik))

    st.header("Pestisit güvenliği")
    c1, c2 = st.columns(2)
    with c1:
        kutu("<b>Uygulama öncesi</b><br>• Etiket ve Güvenlik Bilgi Formu (SDS) okunur; doz ve karışıma uyulur<br>"
             "• Sıcak ve <b>rüzgârlı</b> havada ilaçlama yapılmaz (sürüklenme)<br>• Karışım açık alanda, KKD ile hazırlanır")
    with c2:
        kutu("<b>Uygulama sırası ve sonrası</b><br>• Maske, tulum, eldiven, gözlük, çizme<br>• Yemek yenmez, sigara içilmez<br>"
             "• Eller ve yüz bol suyla yıkanır, kıyafetler ayrı yıkanır<br>• <b>Hasat öncesi bekleme süresine (PHI)</b> uyulur")
    st.subheader("🧮 PHI hesaplayıcı: en erken hasat tarihi")
    st.markdown("**Hasat öncesi bekleme süresi (PHI):** son ilaçlama ile hasat arasında bırakılması gereken süredir. "
                "Üründeki kalıntıyı güvenli sınırın altına indirmek için üretici belirler; **etikette yazar**.")
    import datetime as _dt
    c1, c2 = st.columns(2)
    son = c1.date_input("Son ilaçlama tarihi", _dt.date(2026, 8, 10), format="DD.MM.YYYY")
    phi = c2.number_input("Etiketteki PHI (gün)", 1, 120, 21)
    hasat = son + _dt.timedelta(days=int(phi))
    st.success(f"En erken hasat: **{hasat.strftime('%d.%m.%Y')}** ({phi} gün sonra). Bu tarihten önce hasat edilen üründe "
               "izin verilen sınırın üstünde kalıntı kalabilir.")
    st.caption("Sayılar örnektir; gerçek PHI ürüne ve etkin maddeye göre değişir, mutlaka etiketten bakılır.")
    st.header("Bağcılıkta KKD")
    tablo(pd.DataFrame(KKD_TABLO, columns=["KKD", "Kullanım amacı"]))
    alistirma_blogu("kkd", "Bağcılıkta riskler ve KKD", gen_kkd)


# ---------------------------------------------------------------------------
ACIL = {
    "Cilde pestisit bulaştı": ["Bulaşan kıyafeti çıkar.", "Cildi bol suyla **en az 15 dakika** yıka.",
                               "Belirti varsa ürün etiketiyle sağlık kuruluşuna başvur; 112 / Zehir Danışma 114."],
    "Göze pestisit sıçradı": ["Gözü kapakları açık tutarak bol suyla **en az 15 dakika** yıka.", "Ovma.",
                              "Ürün etiketiyle sağlık kuruluşuna başvur."],
    "Pestisit solundu": ["Kişiyi **temiz havaya** çıkar.", "Bilinç durumunu izle.", "Belirti varsa 112'yi ara; etiketi göster."],
    "Pestisit yutuldu": ["**Kusturma.**", "Ağzı suyla çalkalat.", "Hemen 112 ve Zehir Danışma **114**'ü ara; ürün kutusunu yanında götür."],
    "Traktör / makine kazası": ["Makineyi **durdur, motoru kapat**.", "Ek yaralanmaya yol açmayacaksa yaralıyı **hareket ettirme**.",
                                "Ağır kanama varsa **bastır**; 112'yi ara."],
}


def sayfa_ra():
    st.title("3 · Risk değerlendirmesi ve acil durum")
    st.markdown("**Risk değerlendirmesi**, işyerindeki tehlikelerin sistematik biçimde belirlenip değerlendirildiği ve "
                "önlemlerin planlandığı bir **döngüdür**.")
    adim = st.select_slider("Adım", options=list(range(5)), format_func=lambda i: f"{i + 1} · {RA_ADIM[i][0]}")
    svg_goster(svg_ra_dongu(adim))
    st.header("Önlemlerin öncelik sırası: kontrol hiyerarşisi")
    sec = st.radio("Bir basamak seçin", [k[0] for k in KONTROL], horizontal=True, index=4)
    i = [k[0] for k in KONTROL].index(sec)
    svg_goster(svg_kontrol(i))
    kutu(f"<b>{KONTROL[i][0]}:</b> {KONTROL[i][1]}. Bağcılıkta örnek: {KONTROL[i][2]}.")
    uyari("<b>KKD neden son çare?</b> KKD tehlikenin kendisini ortadan kaldırmaz; yalnızca kişiyi kısmen korur ve yanlış "
          "takılırsa işe yaramaz. Önce tehlikeyi kaynağında kaldırmak, değiştirmek ya da yalıtmak gerekir.")
    st.markdown("**🎯 Mini oyun: bu önlem hangi basamakta?**")
    _mini_oyun("kh", KONTROL_ORNEK, [k[0] for k in KONTROL], "Önlemi kontrol hiyerarşisindeki yerine yerleştirin.")

    st.header("Bağ işletmesi için örnek risk değerlendirmesi")
    tablo(pd.DataFrame(ORNEK_RA, columns=["Tehlike", "Olası sonuç", "Risk düzeyi (örnek)", "Önlem"]))
    st.caption("Risk düzeyleri öğretici amaçla basitleştirilmiştir. Sayısal puanlama 9. bölümde (5×5 matris, Fine-Kinney).")

    st.header("🚑 Acil durum ve ilk müdahale")
    kartlar([("🩹 İlk yardım seti", "Her işletmede bulunmalı, yeri herkesçe bilinmeli"),
             ("📞 112 ve 114", "Ciddi kaza ve zehirlenmede vakit kaybetmeden ara"),
             ("🏷️ Pestisit etiketi", "Kullanılan ilaçların adı ve etiketi kolay ulaşılır yerde")])
    olay = st.selectbox("Bir durum seçin", list(ACIL))
    for j, a in enumerate(ACIL[olay], 1):
        st.markdown(f"**{j}.** {a}")
    alistirma_blogu("ra", "Risk değerlendirmesi ve acil durum", gen_ra)


# ---------------------------------------------------------------------------
GUNLUK_KONTROL = ["ROPS takılı ve sağlam", "Emniyet kemeri çalışıyor", "Kuyruk mili koruyucusu takılı",
                  "Lastik havası ve diş derinliği yeterli", "Frenler ve el freni tutuyor", "Far, stop, sinyal, reflektör çalışıyor",
                  "Yağ, yakıt ve hidrolik kaçağı yok", "Basamaklar ve tutamaklar temiz, kaygan değil",
                  "Yangın söndürücü ve ilk yardım çantası var", "Kabinde gereksiz eşya ve yolcu yok"]


def sayfa_traktor():
    st.title("4 · Traktör ve bağ makinelerinde güvenlik")
    st.markdown("""
Tarımdaki ölümlü kazaların önemli bir bölümü **traktörle** ilgilidir; en ölümcül olanı
**devrilmedir**. Bağcılıkta eğimli araziler, teraslar, dar sıra araları ve hendekler bu riski artırır.""")
    st.header("🔬 Devrilme simülatörü")
    c1, c2 = st.columns([1, 1.6])
    with c1:
        egim = st.slider("Arazi eğimi (derece)", 0, 45, 15)
        iz = st.slider("İz genişliği (m)", 0.9, 1.8, 1.2, 0.1, help="Sağ ve sol tekerlek arası; bağ traktörlerinde dardır.")
        h = st.slider("Ağırlık merkezi yüksekliği (m)", 0.6, 1.3, 0.9, 0.05,
                      help="Ön yükleyicide yük yukarı kaldırılınca ağırlık merkezi yükselir.")
        rops = st.checkbox("ROPS (devrilme koruma çerçevesi)", True)
        kemer = st.checkbox("Emniyet kemeri takılı", True)
    with c2:
        svg, kritik = svg_traktor_egim(egim, iz, h, rops, kemer)
        svg_goster(svg)
    st.latex(r"\tan(\theta_{kritik}) = \frac{\text{iz genişliği}/2}{\text{ağırlık merkezi yüksekliği}}")
    st.markdown(f"Bu traktör için duran hâlde devrilme açısı yaklaşık **{kritik:.0f}°**. İz daraldıkça ya da yük yukarı "
                "kaldırıldıkça bu açı **küçülür**.")
    uyari("Bu hesap <b>duran traktör</b> içindir. Hareket, tümsek, çukur, dönüş ve fren bu açıyı çok düşürür; gerçekte traktörler "
          "hesaplanan açının çok altındaki eğimlerde devrilebilir. Eğimde yavaş gidilir, teras kenarından uzak durulur.")
    if egim >= kritik:
        if rops and kemer:
            st.success("ROPS + kemer: sürücü koltukta kalır, ROPS yaşam alanı bırakır. Hayatta kalma şansı yüksek.")
        elif rops and not kemer:
            st.error("ROPS var ama kemer yok: sürücü dışarı fırlar ve traktörün ya da ROPS'un altında kalabilir!")
        else:
            st.error("ROPS yok: devrilmede sürücü için yaşam alanı kalmaz. En ölümcül durum.")
    st.header("Devrilme türleri")
    tablo(pd.DataFrame(DEVRILME, columns=["Devrilme türü", "Başlıca nedenleri", "Önlemler"]))
    ipucu("<b>ROPS ancak emniyet kemeri takılıysa korur.</b> Katlanır ROPS çalışırken açık ve kilitli olmalıdır.")

    st.header("Kuyruk mili (PTO) kazaları")
    koruyucu = st.toggle("Mil koruyucusu takılı", value=False)
    svg_goster(svg_pto(koruyucu))
    kutu("• Mil koruyucusu her zaman takılı ve sağlam olmalı<br>• Bol giysi, atkı ve açık uzun saçla mil yakınında çalışılmaz<br>"
         "• Makineye müdahaleden önce <b>kuyruk mili kapatılır, motor durdurulur, anahtar alınır</b><br>"
         "• Dönen milin üzerinden asla adım atılmaz")
    st.header("Römork ve karayolunda traktör")
    kartlar([("🚫 Römorkta insan", "Taşınmaz; trafik mevzuatı yasaklar, ölümlü kazaların başlıca nedenlerinden"),
             ("💡 Görünür ol", "Far, stop, sinyal, reflektör ve yavaş araç işareti çalışır olmalı"),
             ("⚖️ Yük", "Kapasiteyi aşmamalı, dengeli yüklenmeli"),
             ("🪪 Sürücü", "Ehliyetli olmalı; çocuklar traktör kullanamaz")])
    st.header("Budama makası, motorlu testere ve atomizör")
    tablo(pd.DataFrame(EKIPMAN, columns=["Ekipman", "Başlıca tehlike", "Güvenli kullanım"]))
    st.header("✅ Etkinlik: traktör günlük kontrol listesi")
    st.caption("Okulun ya da kendi işletmenizin traktörünü kontrol edin; uygun olanları işaretleyin.")
    uygun = [st.checkbox(m, key=f"gk_{i}") for i, m in enumerate(GUNLUK_KONTROL)]
    n = sum(uygun)
    st.progress(n / len(GUNLUK_KONTROL), text=f"Uygun: {n} / {len(GUNLUK_KONTROL)}")
    if n == len(GUNLUK_KONTROL):
        st.success("Traktör kullanıma hazır.")
    elif n:
        st.warning("Uygun olmayan maddeler giderilmeden traktör kullanılmamalı: " +
                   ", ".join(m for m, u in zip(GUNLUK_KONTROL, uygun) if not u))
    alistirma_blogu("traktor", "Traktör ve makineler", gen_traktor)


# ---------------------------------------------------------------------------
BELIRTI = ["Bol terleme", "Halsizlik", "Baş ağrısı", "Bulantı", "Baş dönmesi", "Vücut ısısı 40 °C ve üzeri",
           "Bilinç bulanıklığı", "Saçma konuşma", "Nöbet", "Terleme durmuş"]
CIDDI = {"Vücut ısısı 40 °C ve üzeri", "Bilinç bulanıklığı", "Saçma konuşma", "Nöbet", "Terleme durmuş"}


def sayfa_etmen():
    st.title("5 · Fiziksel, biyolojik ve ergonomik etmenler")
    st.header("Sıcak stresi ve güneş çarpması")
    tablo(pd.DataFrame([(k, v[0], v[1]) for k, v in SICAK.items()], columns=["Durum", "Belirtiler", "İlk müdahale"]))
    st.subheader("🩺 Belirtilere göre karar ver")
    sec = st.multiselect("Hasat sırasında arkadaşınızda gördüğünüz belirtiler", BELIRTI, placeholder="Belirti seçin")
    if sec:
        if CIDDI & set(sec):
            st.error("**SICAK ÇARPMASI olabilir: ACİL!** Hemen 112'yi arayın, gölgeye alın, su ve ıslak bezle soğutun; "
                     "bilinci kapalıysa ağızdan bir şey vermeyin.")
        else:
            st.warning("**Sıcak bitkinliği** belirtileri. Serin ve gölge yere alın, giysileri gevşetin, bilinci açıksa yudum "
                       "yudum su içirin, dinlendirin. Belirtiler geçmez ya da ağırlaşırsa 112.")
    kutu("<b>Önlemler:</b> sık ve az az su içmek · en sıcak saatlerde ağır işten kaçınmak · gölgede mola · açık renkli, geniş "
         "kenarlı şapka ve ince uzun kollu giysi. İşe yeni başlayan ve sıcağa alışık olmayan çalışanlar daha fazla risk altındadır.")

    st.header("Gürültü")
    kaynak = st.selectbox("Bir gürültü kaynağı seçin", [g[1] for g in GURULTU], index=5)
    db = dict((g[1], g[0]) for g in GURULTU)[kaynak]
    svg_goster(svg_db(kaynak))
    if db >= 87:
        st.error(f"{kaynak} (~{db} dB(A)): sınır değerin üstü. Kulak koruyucu zorunlu, maruziyet süresi kısaltılmalı.")
    elif db >= 85:
        st.warning(f"{kaynak} (~{db} dB(A)): kulak koruyucu zorunlu.")
    elif db >= 80:
        st.info(f"{kaynak} (~{db} dB(A)): önlemler başlar; kulak koruyucu sağlanır.")
    else:
        st.success(f"{kaynak} (~{db} dB(A)): işitme kaybı riski düşük.")
    st.caption("Gürültü düzeyleri tipik yaklaşık değerlerdir; makineye, bakıma ve uzaklığa göre değişir. Sınırlar: Çalışanların "
               "Gürültü ile İlgili Risklerden Korunmalarına Dair Yönetmelik (80 / 85 / 87 dB(A)).")
    st.subheader("🧮 Eşit enerji ilkesi: ne kadar süre?")
    st.markdown("Ses enerjisi her **3 dB**'de iki katına çıkar. Bu yüzden 85 dB(A)'da 8 saatte alınan doz, 88 dB(A)'da **4 saatte**, "
                "91 dB(A)'da **2 saatte** alınır.")
    d = st.slider("Gürültü düzeyi, dB(A)", 85, 115, 100)
    sure = 8 / 2 ** ((d - 85) / 3)
    st.markdown(f"### {d} dB(A) → yaklaşık **{_sure_yaz(sure)}**")
    st.caption("85 dB(A) ve 8 saat temel alınarak 3 dB kuralıyla hesaplanan öğretici bir değerdir; bu süreden sonra kulak koruyucusuz "
               "her dakika sınırın üstünde doz demektir.")
    uyari("<b>İşitme kaybı yavaş ilerler, ağrısızdır ve geri dönmez.</b>")

    st.header("Titreşim")
    kartlar([("✋ El-kol titreşimi", "Motorlu testere, motorlu tırpan: parmaklarda uyuşma, beyazlama, kavrama gücünde azalma"),
             ("🚜 Tüm vücut titreşimi", "Traktör, engebeli arazi: bel ve sırt rahatsızlıkları"),
             ("🛡️ Önlemler", "Titreşimi azaltılmış ekipman, iyi bakım, düzenli mola, eldiven, süspansiyonlu koltuk")])

    st.header("Kas-iskelet sorunları ve doğru kaldırma")
    svg_goster(svg_kaldirma())
    for i, a in enumerate(["Yükün ağırlığını önceden kontrol et; ağırsa yardım iste ya da bölerek taşı",
                           "Ayaklarını omuz genişliğinde aç, yüke yaklaş", "Belini değil **dizlerini bük**, sırtını düz tut",
                           "Yükü **vücuduna yakın** tut, bacak kaslarınla kalk", "Dönmen gerekiyorsa belini değil **ayaklarını çevir**"], 1):
        st.markdown(f"**{i}.** {a}")
    st.subheader("🎯 Etkinlik: doğru mu, yanlış mı?")
    for i, (durum, dogru, dogrusu) in enumerate(KALDIRMA_DY):
        c1, c2 = st.columns([2.2, 1])
        c1.markdown(durum)
        y = c2.radio("Yanıt", ["Doğru", "Yanlış"], index=None, key=f"kdy_{i}", horizontal=True, label_visibility="collapsed")
        if y is not None:
            if (y == "Doğru") == dogru:
                c1.success("✔ " + dogrusu)
            else:
                c1.error("✘ " + dogrusu)

    st.header("Biyolojik riskler")
    risk = st.selectbox("Bir durum seçin", [b[0] for b in BIYOLOJIK])
    b = [x for x in BIYOLOJIK if x[0] == risk][0]
    c1, c2 = st.columns(2)
    with c1:
        ipucu(f"<b>✅ Ne yapılır:</b> {b[1]}")
    with c2:
        uyari(f"<b>⛔ Ne yapılmaz:</b> {b[2]}")
    kutu("Keneler <b>Kırım-Kongo Kanamalı Ateşi (KKKA)</b> gibi ciddi hastalıkları bulaştırabilir. Bağda açık renkli, uzun kollu giysi "
         "giymek ve paçaları çorabın içine sokmak keneyi fark etmeyi kolaylaştırır. <b>Tetanoz aşısı</b> yetişkinlerde 10 yılda bir tekrarlanır.")
    alistirma_blogu("etmen", "Fiziksel, biyolojik ve ergonomik etmenler", gen_etmen)


def _sure_yaz(saat):
    if saat >= 1:
        return f"{saat:.1f} saat".replace(".", ",")
    dk = saat * 60
    if dk >= 1:
        return f"{dk:.0f} dakika"
    return f"{dk * 60:.0f} saniye"


# ---------------------------------------------------------------------------
def _is_gunu_ekle(tarih, n):
    import datetime as _dt
    t = tarih
    eklenen = 0
    while eklenen < n:
        t += _dt.timedelta(days=1)
        if t.weekday() < 5:
            eklenen += 1
    return t


def sayfa_ozel():
    st.title("6 · Bağ işletmesinde İSG yönetimi ve özel gruplar")
    st.markdown("Bağcılıkta iş gücünün önemli bir kısmı **mevsimlik işçilerdir**; aralarında çocuklar, gençler ve kadınlar da vardır.")
    st.header("Mevsimlik tarım işçileri")
    tablo(pd.DataFrame(MEVSIMLIK, columns=["Konu", "Risk", "Önlem"]))
    st.header("Çocuklar, gençler, gebe ve emziren kadınlar")
    kartlar([("👧 Çocuk işçiliği", "Mevzuat ve ILO sözleşmeleri çocuk çalıştırmayı genel olarak yasaklar; traktör, ilaçlama, ağır yük gibi "
                                  "tehlikeli işlere hiç izin vermez. Tarımda hâlâ ciddi bir sorundur."),
             ("🧑 Genç çalışanlar", "Deneyimsiz oldukları için kazaya daha açıktır: ayrıntılı eğitim, sürekli gözetim, ağır işlerden uzak tutma."),
             ("🤰 Gebe ve emziren kadınlar", "Pestisit ve kimyasallar, ağır yük, uzun süre ayakta durma, aşırı sıcak ve titreşim risklidir; "
                                            "ilaçlama ve kimyasal işlerden uzak tutulur.")])
    st.header("Yangın ve elektrik güvenliği")
    for a in ["Bağ evi, depo ve sulama pompası tesisatı **yetkili elektrikçiye** yaptırılır; açıkta ve ıslak zeminde kablo bırakılmaz",
              "Sulama pompası ve dış prizler için **kaçak akım rölesi** kullanılır",
              "Kuru ot, saman, yakıt ve pestisit **yan yana depolanmaz**; anız ve çöp yakılmaz",
              "Depoda ve traktörde uygun tipte, **kontrol tarihi geçmemiş** yangın söndürücü bulunur"]:
        st.markdown(f"- {a}")
    st.header("İş kazası bildirimi")
    kutu("İşveren iş kazasını kazadan sonraki <b>en geç 3 iş günü</b> içinde <b>SGK</b>'ya bildirir. Meslek hastalığı da öğrenildiği "
         "tarihten itibaren 3 iş günü içinde bildirilir (5510 sayılı Kanun md. 13–14; 6331 sayılı Kanun md. 14).")
    import datetime as _dt
    c1, c2 = st.columns(2)
    kaza = c1.date_input("Kaza tarihi", _dt.date(2026, 10, 16), format="DD.MM.YYYY")
    son = _is_gunu_ekle(kaza, 3)
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    c2.markdown(f"Kaza günü: **{gunler[kaza.weekday()]}**")
    st.success(f"Son bildirim tarihi: **{son.strftime('%d.%m.%Y')} ({gunler[son.weekday()]})**")
    st.caption("Hesaplayıcı yalnızca hafta sonlarını atlar; resmî tatiller hesaba katılmamıştır.")
    st.header("Ramak kala olay")
    st.markdown("""
**Ramak kala olay:** çalışanı, işyerini ya da ekipmanı zarara uğratma potansiyeli olduğu hâlde
**zarara uğratmayan** olaydır (6331 sayılı Kanun). Örnek: traktörün teras kenarında kayıp son anda durması.
Her ciddi kazadan önce çok sayıda ramak kala olay yaşanır; kaydedilip nedenleri giderilirse ciddi kaza önlenir.""")
    st.subheader("📝 Ramak kala kayıt formu")
    c1, c2 = st.columns(2)
    alan = {"Tarih ve saat": c1.text_input("Tarih ve saat", ""), "Yer": c2.text_input("Yer", ""),
            "Ne oldu?": c1.text_area("Ne oldu?", "", height=80), "Olası sonuç": c2.text_area("Olası sonuç", "", height=80),
            "Nedeni": c1.text_input("Nedeni", ""), "Alınan önlem": c2.text_input("Alınan önlem", ""),
            "Kaydı tutan": c1.text_input("Kaydı tutan kişi", "")}
    eksik = [k for k, v in alan.items() if not v.strip()]
    st.markdown('<div class="etiket">' + "<br>".join(f"<b>{k}:</b> {v or '……'}" for k, v in alan.items()) + "</div>",
                unsafe_allow_html=True)
    if eksik:
        st.caption("Eksik alanlar: " + ", ".join(eksik))
    else:
        metin = "\n".join(f"{k}: {v}" for k, v in alan.items())
        st.download_button("⬇️ Kaydı indir (.txt)", metin.encode("utf-8"), "ramak_kala_kaydi.txt")
    alistirma_blogu("ozel", "Özel gruplar ve İSG yönetimi", gen_ozel)


# ---------------------------------------------------------------------------
def sayfa_cevre():
    st.title("7 · Çevre, bina ve yangın güvenliği")
    st.header("Çevremizde güvenliği tehdit eden unsurlar")
    st.markdown("Bağ açık arazide olduğu için doğal tehlikelere doğrudan açıktır.")
    u = st.selectbox("Bir unsur seçin", list(CEVRE))
    c1, c2 = st.columns(2)
    with c1:
        uyari(f"<b>Bağcılıkta örnek:</b> {CEVRE[u][0]}")
    with c2:
        ipucu(f"<b>Önlem:</b> {CEVRE[u][1]}")
    kutu("Türkiye'de bütün acil durumlar için tek numara <b>112</b>'dir. Afet ve acil durum duyuruları için <b>AFAD</b>'ın resmî "
         "kanalları takip edilir.")
    st.header("Binalarda güvenliği tehdit eden unsurlar")
    tablo(pd.DataFrame(BINA, columns=["Tehlike", "Örnek", "Önlem"]))
    st.header("Yangın")
    c1, c2 = st.columns([1, 1.2])
    with c1:
        svg_goster(svg_yangin_ucgeni())
    with c2:
        st.markdown("""
Yangın için üç şey birlikte gerekir: **ısı**, **yakıt** ve **oksijen**. Söndürmenin bütün yolları
bunlardan birini ortadan kaldırmaktır:
- **Soğutma** (su): ısıyı alır
- **Boğma** (köpük, CO₂, battaniye): oksijeni keser
- **Yakıtı uzaklaştırma**: gaz vanasını kapatmak, yanıcıyı çekmek""")
    st.subheader("🔥 Yangın sınıfı ve doğru söndürücü")
    yanan = st.selectbox("Ne yanıyor?", list(YANAN))
    sinif = YANAN[yanan]
    if sinif == "Elektrik":
        st.markdown("**Elektrik yangını:** önce **elektrik kesilir**; suyla müdahale edilmez, CO₂ ya da kuru kimyevi toz kullanılır.")
    else:
        st.markdown(f"**{sinif} sınıfı yangın:** {YANGIN_SINIF[sinif][0].lower()} (ör. {YANGIN_SINIF[sinif][1].lower()})")
    tablo(pd.DataFrame({"Söndürücü": SONDURUCU, "Uygun mu?": UYGUNLUK[sinif]}))
    st.caption("✔ uygun · ✘ kullanılmaz (tehlikeli ya da etkisiz) · – bu sınıf için önerilmez")
    tablo(pd.DataFrame([(k, v[0], v[1]) for k, v in YANGIN_SINIF.items()], columns=["Sınıf", "Yanan madde", "Örnek"]))
    st.subheader("🧯 Yangın söndürücü nasıl kullanılır?")
    a = st.select_slider("Adım", options=list(range(4)), format_func=lambda i: PASS[i][0])
    svg_goster(svg_pass(a))
    kutu(PASS[a][1])
    ipucu("Rüzgâr arkada olacak şekilde, kaçış yolunu arkada bırakarak müdahale edilir. Basınç göstergesi <b>yeşil bölgede</b>, "
          "periyodik kontrol etiketi güncel olmalıdır. Yangın büyükse müdahale etme, alanı boşalt ve 112'yi ara.")
    alistirma_blogu("cevre", "Çevre, bina ve yangın", gen_cevre)


# ---------------------------------------------------------------------------
def sayfa_kuram():
    st.title("8 · İş kazalarının nedenleri ve kuramlar")
    st.markdown("İş kazaları şans eseri olmaz; bir dizi nedenin üst üste gelmesiyle olur.")
    tablo(pd.DataFrame(GUVENSIZ, columns=["Neden grubu", "Bağcılıkta örnek", "Önlem"]))
    kutu("<b>H. W. Heinrich</b> 1930'larda kazaların büyük çoğunluğunun güvensiz davranıştan kaynaklandığını ileri sürdü. Bugün bu görüş "
         "eleştirilir: güvensiz davranışın arkasında çoğu zaman eğitimsizlik, aşırı iş yükü ya da güvensiz bir düzen vardır. "
         "Bu yüzden <b>suçlu aramak yerine sistemi düzeltmek</b> esastır.")
    st.header("Domino teorisi")
    cek = st.toggle("Ortadaki taşı (güvensiz davranış / durum) çek", value=False)
    svg_goster(svg_domino(cek))
    st.markdown("Heinrich'e göre kaza, art arda dizilmiş beş domino taşının devrilmesine benzer. **Ortadaki taş çekilirse zincir kırılır** "
                "ve kaza olmaz. Önlemlerin çoğu bu taşı hedefler.")
    st.header("Kaza piramidi (Bird, 1969)")
    k = st.slider("Ciddi yaralanma / ölüm sayısı", 1, 10, 1)
    svg_goster(svg_bird(k))
    st.markdown(f"Oranlara göre {k} ciddi kazanın altında yaklaşık **{600 * k:,} ramak kala olay** yatar.".replace(",", "."))
    st.caption("Oranlar sektöre göre değişir ama mesaj aynıdır: piramidin tabanındaki ramak kala olaylar kaydedilip önlenirse tepedeki "
               "ciddi kaza da önlenir.")
    st.header("Önlemlerin sırası: kontrol hiyerarşisi")
    svg_goster(svg_kontrol())
    alistirma_blogu("kuram", "Kaza kuramları", gen_kuram)


# ---------------------------------------------------------------------------
OLASILIK_5 = {1: "Çok küçük", 2: "Küçük", 3: "Orta", 4: "Yüksek", 5: "Çok yüksek"}
SIDDET_5 = {1: "Çok hafif (iş günü kaybı yok)", 2: "Hafif", 3: "Orta", 4: "Ciddi (uzuv kaybı, kalıcı hasar)", 5: "Çok ciddi (ölüm)"}
DUZEY_NE = {"Önemsiz": "Önlem gerekmeyebilir", "Düşük": "Mevcut önlemler izlenir", "Orta": "Önlemler planlanır",
            "Yüksek": "Önlem alınmadan işe başlanmaz", "Tolere edilemez": "İş derhal durdurulur"}


def _v(x):
    return f"{x:g}".replace(".", "{,}")


def sayfa_puan():
    st.title("9 · Risk puanlama, kaza sıklık ve ağırlık oranları")
    st.header("5×5 risk matrisi (L tipi)")
    st.latex(r"\text{Risk} = \text{Olasılık} \times \text{Şiddet}")
    c1, c2 = st.columns([1, 1.3])
    with c1:
        o = st.select_slider("Olasılık", options=[1, 2, 3, 4, 5], value=3, format_func=lambda v: f"{v} · {OLASILIK_5[v]}")
        sd = st.select_slider("Şiddet", options=[1, 2, 3, 4, 5], value=4, format_func=lambda v: f"{v} · {SIDDET_5[v]}")
        p = o * sd
        duzey, _ = risk_duzey(p)
        st.metric("Risk puanı", p)
        st.markdown(f"**{duzey}** → {DUZEY_NE[duzey]}")
    with c2:
        svg_goster(svg_matris(o, sd))
    tablo(pd.DataFrame({"Puan": ["1", "2–6", "8–12", "15–16", "20–25"],
                        "Risk düzeyi": ["Önemsiz", "Düşük", "Orta", "Yüksek", "Tolere edilemez"],
                        "Ne yapılır": list(DUZEY_NE.values())}))
    ipucu("<b>Örnek:</b> Testereyle kalın dal kesiminde geri tepme. Olasılık 3, şiddet 4 → risk 12, orta. Zincir freni, eğitim ve KKD "
          "ile olasılık 2'ye düşerse risk 8 olur. Önlem çoğu zaman <b>olasılığı</b> düşürür; şiddeti düşüren önlemler (ROPS, kemer) de vardır.")

    st.header("Fine-Kinney yöntemi")
    st.latex(r"\text{Risk} = \text{Olasılık} \times \text{Frekans} \times \text{Şiddet}")
    c1, c2, c3 = st.columns(3)
    def _etiket(x):
        return f"{x[0]} ({str(x[1]).replace('.', ',')})"
    ol_l, fr_l, si_l = [_etiket(x) for x in FK_OLASILIK], [_etiket(x) for x in FK_FREKANS], [_etiket(x) for x in FK_SIDDET]
    ol = FK_OLASILIK[ol_l.index(c1.selectbox("Olasılık", ol_l, index=3))]
    fr = FK_FREKANS[fr_l.index(c2.selectbox("Frekans", fr_l, index=4))]
    si = FK_SIDDET[si_l.index(c3.selectbox("Şiddet", si_l, index=4))]
    fk = ol[1] * fr[1] * si[1]
    sinif, renk = fk_sinif(fk)
    st.latex(rf"{_v(ol[1])} \times {_v(fr[1])} \times {_v(si[1])} = {_v(fk)}")
    st.markdown(f'<div class="kutucuk" style="border-color:{renk};background:{renk}22"><b>Risk puanı {fk:g}</b> → {sinif}</div>',
                unsafe_allow_html=True)
    tablo(pd.DataFrame({"Risk puanı": ["400 ve üzeri", "200–400", "70–200", "20–70", "20'nin altı"],
                        "Sınıf": ["Tolerans gösterilemez, iş durdurulur", "Yüksek, kısa sürede önlem", "Önemli, önlem planlanır",
                                  "Olası, izlenir", "Önemsiz"]}))
    ipucu("<b>Örnek:</b> Eğimli bağda ROPS'suz traktörle her gün çalışılıyor: 3 × 6 × 40 = <b>720</b>, tolerans gösterilemez. "
          "ROPS takılıp kemer kullanılırsa şiddet 7'ye inebilir: 3 × 6 × 7 = <b>126</b>, önemli düzey.")

    st.header("Kaza sıklık (KSO) ve ağırlık (KAO) oranları")
    st.markdown("Kaza sayısını tek başına karşılaştırmak yanıltıcıdır: 10 kişilik ve 100 kişilik işletmenin kaza sayısı farklı olur. Bu "
                "yüzden kazalar **toplam çalışma saatine** göre oranlanır.")
    c1, c2, c3 = st.columns(3)
    isci = c1.number_input("İşçi sayısı", 1, 5000, 20)
    gun = c2.number_input("Yıllık çalışma günü", 1, 366, 250)
    saat = c3.number_input("Günlük çalışma saati", 1, 16, 8)
    c1, c2 = st.columns(2)
    kaza = c1.number_input("Kaza sayısı", 0, 1000, 2)
    kayip = c2.number_input("Kayıp iş günü", 0, 100000, 15)
    T = isci * gun * saat
    kso = kaza * 1_000_000 / T
    kao = kayip * 1000 / T
    st.latex(rf"\text{{Toplam saat}} = {isci} \times {gun} \times {saat} = {T:,}".replace(",", r"\,"))
    st.latex(rf"\text{{KSO}} = \frac{{{kaza} \times 1\,000\,000}}{{{T:,}}} = {kso:.2f}".replace(",", r"\,").replace(".", "{,}"))
    st.latex(rf"\text{{KAO}} = \frac{{{kayip} \times 1000}}{{{T:,}}} = {kao:.3f}".replace(",", r"\,").replace(".", "{,}"))
    kartlar([("KSO", "1 milyon çalışma saatinde kaç kaza: kazalar NE SIKLIKTA?"),
             ("KAO", "1000 çalışma saatinde kaç iş günü kaybı: kazalar NE KADAR AĞIR?")])
    st.caption("Az ama ağır kazası olan işletmenin KSO'su düşük, KAO'su yüksek çıkar. Bazı ülkeler (ör. ABD) 1 milyon yerine 200 000 saati "
               "temel alır; karşılaştırmada aynı taban kullanılmalıdır.")
    alistirma_blogu("puan", "Risk puanlama ve kaza oranları", gen_puan)


# ---------------------------------------------------------------------------
def sayfa_meslek():
    st.title("10 · Meslek hastalıkları ve nedenleri")
    st.markdown("**Meslek hastalığı**, yapılan işin niteliğine bağlı olarak **tekrarlanan bir nedenle** ya da işin yürütüm koşulları "
                "yüzünden ortaya çıkan hastalıktır. İş kazasından farkı, bir anda değil **aylar ya da yıllar içinde** gelişmesidir.")
    tablo(pd.DataFrame(MH_FARK, columns=["Özellik", "İş kazası", "Meslek hastalığı"]))
    st.header("Tarımda meslek hastalığına yol açan etmenler")
    grup = st.radio("Etmen grubu", sorted({e[0] for e in MH_ETMEN}, key=lambda g: ["Fiziksel", "Kimyasal", "Biyolojik", "Ergonomik",
                                                                                     "Psikososyal"].index(g)), horizontal=True)
    for g, etmen, hastalik in MH_ETMEN:
        if g == grup:
            kutu(f"<b>{etmen}</b> → {hastalik}")
    st.header("Korunma ve tanı")
    for a in ["Maruziyeti **kaynağında** azaltmak (kontrol hiyerarşisi)",
              "Uygun KKD: kulak koruyucu, filtreli maske, kimyasala dayanıklı eldiven, şapka ve uzun kollu giysi",
              "İşe giriş ve **periyodik sağlık muayeneleri** (işitme testi, solunum fonksiyon testi)", "Aşılar (tetanoz)",
              "Şikâyet başladığında doktora **yaptığı işi mutlaka söylemek**"]:
        st.markdown(f"- {a}")
    uyari("Türkiye'de meslek hastalığı tanısını <b>yetkili sağlık kuruluşları</b> (meslek hastalıkları hastaneleri ve yetkilendirilmiş "
          "hastaneler) koyar, <b>SGK</b> onaylar. Meslek hastalıkları, özellikle tarımda, gerçekte olduğundan çok daha az bildirilir; "
          "hastalıklar işle ilişkilendirilmediği için kayıtlara geçmez.")
    alistirma_blogu("meslek", "Meslek hastalıkları", gen_meslek)


# ---------------------------------------------------------------------------
def sayfa_isaret():
    st.title("11 · Güvenlik ve sağlık işaretleri")
    st.markdown("İşaretler bir yasağı, tehlikeyi ya da zorunluluğu **kelimesiz ve hızlıca** anlatır. Sağlık ve Güvenlik İşaretleri "
                "Yönetmeliği'ne göre her türün **şekli ve rengi** bellidir: şekli ve rengi tanıyan, içindeki resmi görmeden anlamı anlar.")
    svg_goster(svg_isaret_turleri_isg())
    tablo(pd.DataFrame([(g, v[1]) for g, v in ISARETLER_ISG.items()] +
                       [("Kimyasal tehlike (etiket)", "Eşkenar dörtgen; kırmızı kenar, beyaz zemin, siyah sembol: ürünün tehlikesi")],
                       columns=["İşaret türü", "Şekil, renk ve anlam"]))
    grup = st.radio("İşaret grubu", list(ISARETLER_ISG), horizontal=True)
    liste = ISARETLER_ISG[grup][2]
    sec = st.selectbox("Bir işaret seçin", ["— Tümü —"] + [x[0] for x in liste])
    svg_goster(svg_isaret_grubu(grup, None if sec.startswith("—") else sec))
    tablo(pd.DataFrame([(x[0], x[2]) for x in liste], columns=["İşaret", "Nerede kullanılır?"]))
    st.header("Pestisit etiketindeki tehlike piktogramları")
    svg_goster(svg_ghs_pestisit())
    kutu("Pestisit ve kimyasal etiketlerinde kırmızı çerçeveli, beyaz zeminli eşkenar dörtgen içinde siyah semboller bulunur (GHS; "
         "Türkiye'de SEA Yönetmeliği). Piktogramın yanında <b>tehlike (H)</b> ve <b>önlem (P)</b> ifadeleri yazar. İlaçlamadan önce "
         "etiket mutlaka okunur.")
    st.header("İşaret asma kuralları")
    for a in ["Tehlikenin bulunduğu yere yakın, kolay görülen yüksekliğe ve iyi aydınlatılmış yere asılır",
              "Çok sayıda işaret yan yana asılmaz; kalabalık işaret dikkati dağıtır", "Tehlike ortadan kalkınca işaret kaldırılır",
              "**İşaret önlemin yerine geçmez**, yalnızca önlemi tamamlar", "Çalışanlara işaretlerin anlamı eğitimle öğretilir"]:
        st.markdown(f"- {a}")
    st.caption("Çizimler yönetmelikteki şekil ve renk kurallarına göre hazırlanmış temsilî örneklerdir; işyerinde TS EN ISO 7010'a uygun "
               "hazır levhalar kullanılır.")
    st.header("🎯 Etkinlik: hangi işaret nereye?")
    tum = [x[0] for g in ISARETLER_ISG.values() for x in g[2]]
    yer = st.selectbox("Yer", list(ISARET_NEREYE))
    secilen = set(st.multiselect("Buraya asılacak işaretler", tum, key=f"nereye_{yer}", placeholder="İşaret seçin"))
    if st.button("✔ Kontrol et", key="nereye_k"):
        cevap = ISARET_NEREYE[yer]
        dogru = secilen & cevap
        st.markdown(f"**Doğru seçtikleriniz ({len(dogru)}):** " + (", ".join(sorted(dogru)) or "—"))
        if cevap - secilen:
            st.warning("Eklenebilecekler: " + ", ".join(sorted(cevap - secilen)))
        if secilen - cevap:
            st.info("Bu yer için şart olmayanlar: " + ", ".join(sorted(secilen - cevap)))
        if secilen == cevap:
            st.success("Mükemmel!")
        st.caption("Cevap anahtarı örnek niteliğindedir; gerekçesini açıklayabildiğiniz başka işaretler de doğru kabul edilebilir.")
    alistirma_blogu("isaret", "Güvenlik işaretleri", gen_isaret)


def svg_ghs_pestisit():
    sut = 3
    W, H = 690, 2 * 210 + 10
    s = [svg_ac(W, H, 720)]
    for i, (tur, ad, ne) in enumerate(GHS_PESTISIT):
        cx = 115 + (i % sut) * 230
        cy = 85 + (i // sut) * 210
        s.append(f'<rect x="{cx - 50}" y="{cy - 50}" width="100" height="100" fill="white" stroke="#D9241B" '
                 f'stroke-width="9" transform="rotate(45 {cx} {cy})"/>')
        s.append(_ghs_sembol(tur, cx, cy))
        s.append(_yazi(cx, cy + 96, ad, 14, "#222", kalin=True))
        for j, p in enumerate(_iki_satir(ne, 26)):
            s.append(_yazi(cx, cy + 114 + j * 15, p, 12, "#555"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
DURUMLAR = ["✅ Var ve güvenli", "⚠️ Var ama riskli", "❌ Yok / eksik", "➖ İlgim yok"]


def sayfa_etkinlik():
    st.title("12 · Uygulama etkinlikleri")
    st.header("Etkinlik 1 · KKD ve ekipman eşleştirme")
    st.markdown("Her KKD/ekipmanı ilgili iş ya da tehlike(ler)le eşleştirin. Birden fazla eşleşme olabilir.")
    with st.expander("📋 İş / tehlike listesi"):
        for h, ad in KKD_ESLE_SAG.items():
            st.markdown(f"**{h}.** {ad}")
    harf = list(KKD_ESLE_SAG)
    puan = 0
    kontrol = st.toggle("Cevapları kontrol et", value=False)
    for i, k in enumerate(KKD_ESLE_SOL, 1):
        c1, c2 = st.columns([1, 1.6])
        c1.markdown(f"**{i}. {k}**")
        sec = [x[0] for x in c2.multiselect(k, [f"{h} · {KKD_ESLE_SAG[h]}" for h in harf], key=f"es_{i}",
                                            label_visibility="collapsed", placeholder="Harf seçin")]
        if kontrol:
            cevap, acik = KKD_ESLE_CEVAP[k]
            dogru = set(sec) == set(cevap)
            puan += dogru
            _ = (c2.success if dogru else c2.info)(f"Anahtar: {', '.join(cevap)} · {acik}")
    if kontrol:
        st.metric("Tam doğru eşleştirme", f"{puan} / {len(KKD_ESLE_SOL)}")

    st.header("Etkinlik 2 · “Bağcının kendi yerinde ne var?” tehlike avı")
    yer = st.radio("Yer", ["Ev", "Bağ evi", "Alet odası", "İlaç deposu", "Sera", "Traktör garajı"], horizontal=True)
    sonuc = {d: [] for d in DURUMLAR}
    for bolum, maddeler in TEHLIKE_AVI.items():
        with st.expander(bolum):
            for j, m in enumerate(maddeler):
                d = st.radio(m, DURUMLAR, index=None, horizontal=True, key=f"av_{bolum}_{j}")
                if d:
                    sonuc[d].append(m)
    toplam = sum(len(v) for v in sonuc.values())
    tum = sum(len(v) for v in TEHLIKE_AVI.values())
    st.progress(toplam / tum, text=f"İşaretlenen: {toplam} / {tum}")
    if toplam:
        c = st.columns(4)
        for k, d in zip(c, DURUMLAR):
            k.metric(d, len(sonuc[d]))
        riskli = sonuc[DURUMLAR[1]] + sonuc[DURUMLAR[2]]
        if riskli:
            uyari("<b>Önce bunları düzeltin:</b><br>" + "<br>".join("• " + m for m in riskli))
        rapor = f"Tehlike avı – {yer}\n\n" + "\n".join(f"{d}:\n" + "\n".join("  - " + m for m in sonuc[d]) for d in DURUMLAR if sonuc[d])
        st.download_button("⬇️ Raporu indir (.txt)", rapor.encode("utf-8"), "tehlike_avi.txt")

    st.header("Etkinlik 3 · Çıkış kartı")
    a = st.text_area("Bugün öğrendiğim 3 tehlike", "")
    b = st.text_area("Kullanmam gereken 2 KKD", "")
    c = st.text_input("Hemen uygulayacağım 1 önlem", "")
    if a and b and c:
        st.success("Teşekkürler! Kartınız hazır.")
        st.download_button("⬇️ Çıkış kartını indir", f"3 tehlike:\n{a}\n\n2 KKD:\n{b}\n\n1 önlem:\n{c}\n".encode("utf-8"), "cikis_karti.txt")
    alistirma_blogu("etkinlik", "Uygulama etkinlikleri", gen_etkinlik)


# ---------------------------------------------------------------------------
def _kart_yeni():
    st.session_state.kart_i = int(rng().integers(0, len(TERIMLER)))
    st.session_state.kart_acik = False


def sayfa_tekrar():
    st.title("13 · Genel tekrar")
    st.header("🃏 Hafıza kartları")
    if "kart_i" not in st.session_state:
        _kart_yeni()
    terim, tanim = TERIMLER[st.session_state.kart_i]
    st.markdown(f'<div class="flash">{terim}' + (f'<div class="flash-cevap">{tanim}</div>' if st.session_state.kart_acik else "")
                + '</div>', unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 2])
    if c1.button("👀 Tanımı göster"):
        st.session_state.kart_acik = True
        st.rerun()
    c2.button("➡️ Sonraki kart", on_click=_kart_yeni)
    with st.expander("📖 Sözlük"):
        ara = st.text_input("Terim ara", "")
        for t, d in TERIMLER:
            if ara.lower() in (t + d).lower():
                st.markdown(f"**{t}:** {d}")
    alistirma_blogu("tekrar", "Karışık sorular", gen_tekrar)


# ===========================================================================
# SORU ÜRETİCİLERİ
# ===========================================================================
def _secim(r, metin, dogru, yanlis, cozum):
    temiz = [y for y in dict.fromkeys(yanlis) if y != dogru][:3]
    return soru_secim(r, metin, dogru, temiz, [_md(c) if isinstance(c, str) else c for c in cozum])


def _tamamla(r, sabit, havuz):
    gerek = SORU_SAYISI - len(sabit)
    secilen = _kavram_sec(r, havuz, min(gerek, len(havuz)))
    hepsi = sabit + secilen
    sira = r.permutation(len(hepsi))
    return [hepsi[i] for i in sira]


def _ek(r, liste):
    return [_secim(r, m, d, y, c) for m, d, y, c in liste]


def _sec_bir(r, liste):
    return liste[int(r.integers(0, len(liste)))]


def _diger(r, tum, dogru, n=3):
    aday = [x for x in dict.fromkeys(tum) if x != dogru]
    return [aday[int(i)] for i in r.permutation(len(aday))[:n]]


def _tr(x, od=2):
    t = f"{x:.{od}f}".rstrip("0").rstrip(".") if od else f"{x:.0f}"
    tam, _, ond = t.partition(".")
    if abs(int(tam)) >= 10000:
        tam = f"{int(tam):,}".replace(",", ".")
    return tam + ("," + ond if ond else "")


# ---------------------------------------------------------------------------
def gen_temel(r):
    sabit = []
    kav, tanim = _sec_bir(r, TEMEL_KAVRAM)
    sabit.append(_secim(r, f"“{tanim}” Bu tanım hangi kavrama aittir?", kav, _diger(r, [k for k, _ in TEMEL_KAVRAM], kav),
                        [f"**{kav}:** {tanim}"]))
    m, d = _sec_bir(r, TEHLIKE_RISK)
    sabit.append(_secim(r, f"“{m}” ifadesi hangisini anlatır?", d, ["Tehlike" if d == "Risk" else "Risk", "Meslek hastalığı", "İş kazası"],
                        ["Tehlike: zarar verme potansiyeli. Risk: bu tehlikenin zarara yol açma ihtimali."]))
    m, d = _sec_bir(r, DAVRANIS_DURUM)
    sabit.append(_secim(r, f"“{m}” hangi kaza nedeni grubuna girer?", d,
                        ["Güvensiz durum" if d == "Güvensiz davranış" else "Güvensiz davranış", "Meslek hastalığı", "Doğal afet"],
                        ["Güvensiz davranış kişiden, güvensiz durum ortam ya da ekipmandan kaynaklanır."]))
    havuz = _ek(r, [
        ("Türkiye'de iş sağlığı ve güvenliğinin temel yasal dayanağı hangisidir?", "6331 sayılı İş Sağlığı ve Güvenliği Kanunu",
         ["5510 sayılı Kanun", "4857 sayılı Kanun", "2872 sayılı Çevre Kanunu"], ["6331 sayılı Kanun, 2012."]),
        ("6331 sayılı Kanun hangi yıl çıkmıştır?", "2012", ["2003", "2008", "2020"], ["2012."]),
        ("6331 sayılı Kanun tarım ve hayvancılık işlerini kapsar mı?", "Evet, kamu ve özel bütün işleri kapsar",
         ["Hayır, yalnızca fabrikaları kapsar", "Yalnızca kamu işlerini kapsar", "Yalnızca 50 kişiden büyük işletmeleri kapsar"],
         ["Tarım ve hayvancılık işleri de kapsamdadır."]),
        ("Hangisi işverenin yükümlülüğüdür?", "Risk değerlendirmesi yaptırmak", ["KKD'yi kendi parasıyla almak",
                                                                             "Talimata uymamak", "Yalnızca kaza olunca önlem almak"],
         ["İşveren: tedbir almak, risk değerlendirmesi, KKD sağlamak, eğitim vermek."]),
        ("Hangisi çalışanın yükümlülüğüdür?", "Kendisine verilen KKD'yi doğru kullanmak", ["Risk değerlendirmesi yaptırmak",
                                                                                        "KKD satın almak", "İSG uzmanı atamak"],
         ["Çalışan: kendi ve çevresinin güvenliğini gözetir, talimata uyar, KKD'yi doğru kullanır."]),
        ("İSG kimin sorumluluğundadır?", "Hem işverenin hem çalışanın", ["Yalnızca işverenin", "Yalnızca çalışanın",
                                                                         "Yalnızca devletin"], ["İki taraf birlikte hareket etmeli."]),
        ("İş kazaları genellikle nasıl oluşur?", "Birden çok etmenin bir araya gelmesiyle", ["Tek bir nedenle", "Tamamen şans eseri",
                                                                                            "Yalnızca makine arızasıyla"],
         ["Güvensiz davranış ve güvensiz durum birlikte."]),
        ("Tarım neden yüksek riskli sektörler arasında sayılır?", "Açık havada makine ve kimyasal kullanımı bir aradadır",
         ["Çalışan sayısı çok azdır", "Hiç makine kullanılmaz", "Yalnızca kapalı alanda çalışılır"], ["Ders notu 1.3."]),
        ("İş sağlığı tanımında hangi iyilik hâlleri yer alır?", "Bedensel, ruhsal ve sosyal", ["Yalnızca bedensel",
                                                                                            "Yalnızca ekonomik", "Yalnızca ruhsal"],
         ["Tam iyilik hâli: bedensel, ruhsal, sosyal."]),
        ("Meslek hastalığını iş kazasından ayıran özellik nedir?", "Tekrarlanan bir nedenle, zamanla ortaya çıkması",
         ["Ani olması", "Yalnızca makinelerden kaynaklanması", "Hiç bildirilmemesi"], ["Meslek hastalığı yavaş gelişir."]),
        ("Keskin bir bağ makası kendi başına neyi temsil eder?", "Tehlike", ["Risk", "Kaza", "Meslek hastalığı"],
         ["Zarar verme potansiyeli = tehlike."]),
        ("Hangisi güvensiz duruma örnektir?", "Bakımsız alet-makine", ["Aceleyle çalışmak", "KKD kullanmamak", "Yorgunluk"],
         ["Ortam/ekipman kaynaklı."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_kkd(r):
    import datetime as _dt
    sabit = []
    is_ = _sec_bir(r, list(BAG_TEHLIKE))
    teh, onlem, kkd = BAG_TEHLIKE[is_]
    sabit.append(_secim(r, f"“{is_}” işinde başlıca tehlike hangisidir?", teh,
                        _diger(r, [v[0] for v in BAG_TEHLIKE.values()], teh), [f"{is_}: {teh}. Önlem: {onlem}."]))
    gerek = _sec_bir(r, sorted(kkd))
    gereksiz = [k for k in KKD_LISTE if k not in kkd]
    sabit.append(_secim(r, f"“{is_}” işinde aşağıdakilerden hangisi gereken KKD'dir?", KKD_LISTE[gerek],
                        [KKD_LISTE[k] for k in _diger(r, gereksiz, None)], [f"Gerekenler: {', '.join(KKD_LISTE[k] for k in kkd)}."]))
    gun, ay = int(r.integers(1, 25)), int(r.integers(6, 9))
    phi = int(r.choice([7, 14, 21, 28, 35]))
    son = _dt.date(2026, ay, gun)
    h = son + _dt.timedelta(days=phi)
    f = lambda t: t.strftime("%d.%m.%Y")
    sabit.append(_secim(r, f"Son ilaçlama {f(son)} tarihinde yapıldı; etikette PHI {phi} gün yazıyor. En erken hasat tarihi hangisidir?",
                        f(h), [f(son + _dt.timedelta(days=phi - 7)), f(son + _dt.timedelta(days=phi // 2)), f(son + _dt.timedelta(days=phi + 7))],
                        ["PHI: son ilaçlama ile hasat arasında bırakılması gereken süre.", f"{f(son)} + {phi} gün = **{f(h)}**"]))
    havuz = _ek(r, [
        ("PHI ne demektir?", "Hasat öncesi bekleme süresi", ["Pestisit hacim indeksi", "Kişisel koruyucu donanım", "İlk yardım protokolü"],
         ["Son ilaçlama ile hasat arasında bırakılması gereken süre."]),
        ("PHI'ye uyulmazsa ne olabilir?", "Üründe izin verilen sınırın üstünde kalıntı kalabilir", ["Ürün daha tatlı olur",
                                                                                                  "İlaç etkisini kaybetmez", "Hiçbir şey olmaz"],
         ["Kalıntı güvenli sınırın üstünde kalır."]),
        ("PHI değeri nereden öğrenilir?", "Ürünün etiketinden", ["Komşudan", "Hava durumundan", "Her ilaç için 7 gündür"],
         ["Ürüne ve etkin maddeye göre değişir."]),
        ("Rüzgârlı havada ilaçlama neden yapılmaz?", "İlaç sürüklenip uygulayıcıya ve çevreye taşınır",
         ["İlaç donar", "Makine bozulur", "Bitki ilacı daha iyi emer"], ["Sürüklenme riski."]),
        ("İlaçlamadan önce hangi belge okunur?", "Etiket ve Güvenlik Bilgi Formu (SDS)", ["Ehliyet", "Fatura", "Garanti belgesi"],
         ["Doz ve karışım talimatı."]),
        ("İlaçlamadan sonra kıyafetler nasıl yıkanır?", "Ayrı yıkanır", ["Ev çamaşırıyla birlikte", "Hiç yıkanmaz", "Ertesi yıl"],
         ["Kalıntının bulaşmasını önlemek için."]),
        ("İlaçlama sırasında hangisi yapılmaz?", "Yemek yemek ve sigara içmek", ["Maske takmak", "Eldiven giymek", "Gözlük takmak"],
         ["Ağız yoluyla maruziyet."]),
        ("Budamada en sık iki tehlike nedir?", "Kesici alet yaralanması ve kas-iskelet sorunları", ["Gürültü ve radyasyon",
                                                                                               "Elektrik ve yangın", "Sel ve heyelan"],
         ["Ders notu 2.1."]),
        ("Tel/direk gerdirmede telin aniden boşalıp çarpmasına ne denir?", "Tel kırbaçlanması", ["Geri tepme", "Devrilme", "Sürüklenme"],
         ["Gözlük ve eldiven kullanılır."]),
        ("Traktörle uzun süre çalışmada işitme kaybını önleyen KKD hangisidir?", "Kulak koruyucu", ["Çizme", "Tulum", "Güneş şapkası"],
         ["Gürültü."]),
        ("İlaçlamada solunum yoluyla maruziyeti azaltan KKD hangisidir?", "Solunum maskesi", ["Baret", "Çizme", "Kulak koruyucu"],
         ["Buhar ve aerosol."]),
        ("Güneş çarpmasını ve cilt hasarını azaltan KKD hangisidir?", "Güneşten koruyucu başlık", ["Baret", "Kulaklık", "Toz maskesi"],
         ["Geniş kenarlı, açık renkli şapka."]),
        ("Çardak sistemlerinde merdivende çalışmanın başlıca tehlikesi nedir?", "Düşme", ["Gürültü", "Zehirlenme", "Elektrik çarpması"],
         ["Sağlam merdiven ve denge kontrolü."]),
        ("Pestisit karışımı nerede hazırlanır?", "Açık alanda, uygun KKD ile", ["Mutfakta", "Kapalı ve havasız depoda", "Çocukların yanında"],
         ["Buharın birikmemesi için."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_ra(r):
    sabit = []
    i = int(r.integers(0, 5))
    sabit.append(_secim(r, f"Risk değerlendirmesinin {i + 1}. adımı hangisidir?", RA_ADIM[i][0],
                        [a[0] for k, a in enumerate(RA_ADIM) if k != i], ["Sıra: " + " → ".join(a[0] for a in RA_ADIM)]))
    m, d = _sec_bir(r, KONTROL_ORNEK)
    sabit.append(_secim(r, f"“{m}” kontrol hiyerarşisinin hangi basamağıdır?", d, _diger(r, [k[0] for k in KONTROL], d),
                        ["Ortadan kaldırma → ikame → mühendislik → idari → KKD"]))
    olay = _sec_bir(r, list(ACIL))
    ilk = ACIL[olay][0].replace("**", "")
    sabit.append(_secim(r, f"“{olay}” durumunda ilk yapılacak hangisidir?", ilk,
                        _diger(r, [v[0].replace("**", "") for v in ACIL.values()], ilk), [" → ".join(a.replace("**", "") for a in ACIL[olay])]))
    havuz = _ek(r, [
        ("Kontrol hiyerarşisinde en etkili önlem hangisidir?", "Tehlikeyi ortadan kaldırmak", ["KKD kullanmak", "Uyarı levhası asmak",
                                                                                             "Eğitim vermek"], ["En üst basamak."]),
        ("Kontrol hiyerarşisinde en son başvurulan önlem hangisidir?", "KKD", ["İkame", "Mühendislik önlemi", "Ortadan kaldırma"],
         ["KKD son çaredir."]),
        ("KKD neden son çaredir?", "Tehlikeyi ortadan kaldırmaz, yalnızca kişiyi kısmen korur", ["Çok pahalıdır",
                                                                                               "Yasaktır", "Her zaman en etkilidir"],
         ["Yanlış takılırsa işe yaramaz."]),
        ("ROPS takmak kontrol hiyerarşisinde hangi basamaktır?", "Mühendislik önlemi", ["İdari önlem", "KKD", "İkame"],
         ["Tehlikeyi kaynağında yalıtır."]),
        ("Risk değerlendirmesi ne zaman yeniden gözden geçirilir?", "Belirli aralıklarla ve bir değişiklik olduğunda",
         ["Hiçbir zaman", "Yalnızca kaza olunca", "10 yılda bir"], ["İzleme ve gözden geçirme adımı."]),
        ("Pestisit maruziyeti örnek risk değerlendirmesinde hangi düzeyde gösterilmiştir?", "Yüksek", ["Düşük", "Önemsiz", "Orta"],
         ["Ders notu 3.2."]),
        ("Cilde pestisit bulaşınca cilt en az kaç dakika yıkanır?", "15 dakika", ["1 dakika", "3 dakika", "Hiç yıkanmaz"],
         ["Bol suyla en az 15 dakika."]),
        ("Pestisit soluyan kişiye ilk ne yapılır?", "Temiz havaya çıkarılır", ["Kusturulur", "Su içirilir", "Yatırılıp bırakılır"],
         ["Bilinç durumu izlenir."]),
        ("Pestisit yutan kişi için hangisi YANLIŞTIR?", "Kusturmak", ["112'yi aramak", "Zehir Danışma 114'ü aramak",
                                                                     "Ürün kutusunu sağlık ekibine göstermek"],
         ["Kusturulmaz: yakıcı madde yemek borusunu ikinci kez yakar."]),
        ("Ulusal Zehir Danışma Merkezi'nin numarası hangisidir?", "114", ["112", "110", "155"], ["24 saat hizmet verir."]),
        ("Traktör kazasında ilk yapılacak iş nedir?", "Makineyi durdurup motoru kapatmak", ["Yaralıyı hemen çekip çıkarmak",
                                                                                          "Fotoğraf çekmek", "Traktörü yeniden çalıştırmak"],
         ["Sonra yaralıyı gereksiz yere hareket ettirmeden yardım beklenir."]),
        ("Ağır kanamada ne yapılır?", "Bölgeye baskı uygulanır, 112 aranır", ["Yara yıkanıp açık bırakılır", "Kişi yürütülür",
                                                                               "Turnike her durumda ilk seçenektir"], ["Doğrudan baskı."]),
        ("Zehirlenmede sağlık personeline iletilmek üzere ne hazır tutulur?", "Pestisitin adı ve etiketi", ["Traktör ruhsatı",
                                                                                                          "Hasat tarihi", "Hava durumu"],
         ["Kolay ulaşılır yerde."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_traktor(r):
    sabit = []
    iz = float(r.choice([1.0, 1.1, 1.2, 1.4, 1.6]))
    h = float(r.choice([0.7, 0.8, 0.9, 1.0, 1.1]))
    sabit.append(_secim(r, f"İz genişliği {_tr(iz, 1)} m olan traktörde ağırlık merkezi {_tr(h, 1)} m'den {_tr(h + 0.3, 1)} m'ye "
                           "yükselirse (ör. ön yükleyicide yük yukarıda) devrilme açısı nasıl değişir?", "Küçülür, devrilme kolaylaşır",
                        ["Büyür, traktör daha dengeli olur", "Değişmez", "Yalnızca arkaya devrilme riski değişir"],
                        [_tx(r"\tan\theta = \frac{\text{iz}/2}{h}"), "h büyüyünce açı küçülür."]))
    dar, gen = sorted(r.choice([0.9, 1.0, 1.1, 1.3, 1.5, 1.7], 2, replace=False))
    sabit.append(_secim(r, f"Aynı yükseklikte ağırlık merkezi olan iki traktörün iz genişlikleri {_tr(dar, 1)} m ve {_tr(gen, 1)} m. "
                           "Yana devrilmeye hangisi daha yatkındır?", f"{_tr(dar, 1)} m izli traktör",
                        [f"{_tr(gen, 1)} m izli traktör", "İkisi aynıdır", "İz genişliğinin etkisi yoktur"],
                        ["Dar iz → küçük devrilme açısı. Bağ traktörlerinin izi dar olduğu için risk yüksektir."]))
    havuz = _ek(r, [
        ("Tarımdaki traktör kazalarında en ölümcül olan hangisidir?", "Devrilme", ["Lastik patlaması", "Far arızası", "Yakıt bitmesi"],
         ["Ders notu 4."]),
        ("ROPS nedir?", "Devrilmeye karşı koruma yapısı", ["Kuyruk mili koruyucusu", "Römork freni", "Yakıt pompası"],
         ["Sürücü için yaşam alanı bırakır."]),
        ("ROPS'lu traktörde emniyet kemeri neden şarttır?", "Kemersiz sürücü dışarı fırlar ve traktörün altında kalabilir",
         ["Kemer yakıt tasarrufu sağlar", "Kemer ROPS'u yerinde tutar", "Gerek yoktur"], ["ROPS ancak kemerle korur."]),
        ("Katlanır ROPS çalışırken nasıl olmalıdır?", "Açık ve kilitli", ["Katlanmış", "Sökülmüş", "Yarı açık"], ["Kural."]),
        ("Yana devrilmenin nedenlerinden biri hangisidir?", "Eğime dik çalışma ve teras kenarı", ["Yükü çeki demirinden çekmek",
                                                                                               "Yavaş gitmek", "Ön ağırlık kullanmak"],
         ["Ders notu 4.1."]),
        ("Arkaya devrilmeyi önleyen önlem hangisidir?", "Yükü yalnızca çeki demirinden çekmek", ["Yükü yüksek noktadan çekmek",
                                                                                               "Saplanan traktörü zorlamak", "Rampada ani kalkış"],
         ["Ön ağırlık da kullanılır."]),
        ("Saplanan traktör nasıl kurtarılır?", "Geri geri çıkılır", ["İleri zorlanır", "Yük yukarı kaldırılır", "Hızla dönülür"],
         ["Zorlamak arkaya devrilmeye yol açar."]),
        ("Atomizöre müdahale etmeden önce hangi üç adım uygulanır?", "Kuyruk milini kapat, motoru durdur, anahtarı al",
         ["Hızı artır, kemeri çöz, ineceğim", "Kornaya bas, ışıkları yak, bekle", "Sadece kuyruk milini yavaşlat"], ["Ders notu 4.2."]),
        ("Kuyruk mili kazalarında başlıca tehlike nedir?", "Bol giysi, atkı ya da saçın dönen mile dolanması",
         ["Yakıt sızıntısı", "Far kamaşması", "Lastik aşınması"], ["Koruyucu takılı olmalı."]),
        ("Dönen kuyruk milinin üzerinden adım atılır mı?", "Asla", ["Dikkatli olunursa evet", "Gece evet", "Koruyucusuzsa evet"],
         ["Kural."]),
        ("Römorkta insan taşınması için hangisi doğrudur?", "Yasaktır", ["Oturarak serbesttir", "10 kişiye kadar serbesttir",
                                                                          "Gündüz serbesttir"], ["Ölümlü kazaların başlıca nedenlerinden."]),
        ("Motorlu testerede “geri tepme” nedir?", "Bıçak ucu sert cisme değince testerenin yukarı fırlaması",
         ["Zincirin kopması", "Motorun durması", "Yakıtın taşması"], ["Zincir freni çalışır olmalı."]),
        ("Motorlu testereyle hangisi YAPILMAZ?", "Omuz hizasının üstünde kesmek", ["İki elle tutmak", "Testere pantolonu giymek",
                                                                                  "Siperlik takmak"], ["Ders notu 4.4."]),
        ("Tıkanan ilaçlama memesi nasıl açılır?", "Asla ağızla üflenmez; uygun araçla temizlenir", ["Ağızla üflenir",
                                                                                                  "Dişle açılır", "Yüzüne doğru basınçla"],
         ["Pestisit ağza kaçar."]),
        ("Traktörü kimler kullanamaz?", "Çocuklar ve ehliyetsizler", ["Ehliyetli yetişkinler", "Eğitim almış işçiler", "İşletme sahibi"],
         ["Sürücü ehliyetli olmalı."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_etmen(r):
    sabit = []
    d = int(r.choice([88, 91, 94, 97, 100]))
    sure = 8 / 2 ** ((d - 85) / 3)
    sabit.append(_secim(r, f"Eşit enerji ilkesine göre 85 dB(A)'da 8 saatte alınan gürültü dozu {d} dB(A)'da kaç saatte alınır?",
                        _sure_yaz(sure), [_sure_yaz(sure * 2), _sure_yaz(sure / 2), _sure_yaz(8 - (d - 85) / 3)],
                        ["Her +3 dB'de süre yarıya iner.", f"{d} − 85 = {d - 85} dB → {(d - 85) // 3} kez yarıya: 8 / 2^{(d - 85) // 3} = **{_sure_yaz(sure)}**"]))
    db = int(r.choice([75, 78, 82, 84, 86, 88, 92, 105]))
    if db < 80:
        c = "Önlem gerekmez (80'in altında)"
    elif db < 85:
        c = "Önlemler başlar, kulak koruyucu sağlanır"
    elif db < 87:
        c = "Kulak koruyucu kullanımı zorunludur"
    else:
        c = "Sınır değer aşılmıştır"
    sabit.append(_secim(r, f"Gürültü düzeyi {db} dB(A) olan bir işte yönetmeliğe göre durum nedir?", c,
                        [x for x in ["Önlem gerekmez (80'in altında)", "Önlemler başlar, kulak koruyucu sağlanır",
                                     "Kulak koruyucu kullanımı zorunludur", "Sınır değer aşılmıştır"] if x != c],
                        ["80 dB(A): önlem başlar · 85: kulak koruyucu zorunlu · 87: sınır değer"]))
    b = _sec_bir(r, BIYOLOJIK)
    sabit.append(_secim(r, f"“{b[0]}” durumunda hangisi YAPILMAZ?", b[2].split(",")[0].strip(),
                        [x[1].split(",")[0].split(";")[0].strip() for x in BIYOLOJIK[:3]], [f"Yapılır: {b[1]}", f"Yapılmaz: {b[2]}"]))
    havuz = _ek(r, [
        ("Sıcak çarpmasını sıcak bitkinliğinden ayıran belirti hangisidir?", "Vücut ısısı 40 °C üstü ve bilinç bulanıklığı",
         ["Bol terleme", "Hafif baş ağrısı", "Susama"], ["Sıcak çarpması acildir, 112."]),
        ("Sıcak çarpmasında bilinci kapalı kişiye ne yapılmaz?", "Ağızdan bir şey verilmez", ["Gölgeye alınmaz",
                                                                                            "Islak bezle soğutulmaz", "112 aranmaz"],
         ["Boğulma riski."]),
        ("Sıcak stresine karşı hangisi doğru önlemdir?", "Sık ve az az su içmek, sıcak saatlerde ağır işten kaçınmak",
         ["Koyu renkli dar giysi", "Mola vermeden çalışmak", "Susamadıkça su içmemek"], ["Ders notu 5.1."]),
        ("İşitme kaybı için hangisi doğrudur?", "Yavaş ilerler, ağrısızdır ve geri dönmez", ["Ani olur ve iyileşir",
                                                                                           "Ağrılıdır", "İlaçla tamamen geçer"],
         ["Önlem şart."]),
        ("Kulak koruyucu hangi düzeyde zorunlu hâle gelir?", "85 dB(A)", ["60 dB(A)", "70 dB(A)", "120 dB(A)"], ["Yönetmelik."]),
        ("Gürültüde maruziyet sınır değeri kaç dB(A)'dır?", "87", ["80", "85", "100"], ["Yönetmelik."]),
        ("Motorlu testere hangi titreşime yol açar?", "El-kol titreşimi", ["Tüm vücut titreşimi", "Hiç titreşim yok", "Ses titreşimi"],
         ["Parmaklarda uyuşma, beyazlama."]),
        ("Traktör ve engebeli arazi hangi titreşime yol açar?", "Tüm vücut titreşimi", ["El-kol titreşimi", "Göz titreşimi", "Yok"],
         ["Bel ve sırt rahatsızlıkları."]),
        ("Doğru yük kaldırmada hangisi yapılır?", "Dizler bükülür, sırt düz tutulur", ["Bel bükülür, dizler düz", "Yük vücuttan uzak tutulur",
                                                                                     "Yük kaldırılırken bel çevrilir"], ["Güç bacaklardan."]),
        ("Yükü taşırken dönmek gerekirse ne yapılır?", "Bel değil ayaklar çevrilir", ["Bel çevrilir", "Yük fırlatılır", "Diz üstü dönülür"],
         ["Bel fıtığı riski."]),
        ("Arı sokmasında iğne nasıl çıkarılır?", "Tırnakla kazıyarak", ["Parmakla sıkarak çekerek", "Ağızla emerek", "Bıçakla keserek"],
         ["Sıkmak zehir kesesini boşaltır."]),
        ("Yılan sokmasında hangisi yapılır?", "Uzuv hareketsiz tutulur, 112 aranır", ["Yara kesilir", "Ağızla emilir", "Buz konur"],
         ["Turnike de yapılmaz."]),
        ("Kene nasıl çıkarılır?", "Sağlık kuruluşunda ya da ince uçlu pensle deriye yakın tutularak", ["Elle ezilerek",
                                                                                                    "Kolonya dökülerek", "Sigara ateşiyle"],
         ["Sonraki günlerde ateş olursa doktora."]),
        ("Kene hangi ciddi hastalığı bulaştırabilir?", "Kırım-Kongo Kanamalı Ateşi", ["Grip", "Tetanoz", "Sıtma"], ["KKKA."]),
        ("Tetanoz aşısı yetişkinlerde kaç yılda bir tekrarlanır?", "10", ["1", "3", "50"], ["Ders notu 5.4."]),
        ("Kenenin fark edilmesini kolaylaştıran giysi hangisidir?", "Açık renkli, uzun kollu; paçalar çorabın içinde",
         ["Koyu renkli şort", "Kolsuz tişört", "Sandalet"], ["Ders notu 5.4."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_ozel(r):
    import datetime as _dt
    sabit = []
    t = _dt.date(2026, 10, int(r.integers(5, 26)))
    son = _is_gunu_ekle(t, 3)
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    f = lambda x: f"{x.strftime('%d.%m.%Y')} {gunler[x.weekday()]}"
    sabit.append(_secim(r, f"Bir iş kazası {f(t)} günü oldu. İşverenin SGK'ya bildirim için son günü hangisidir? (resmî tatil yok)",
                        f(son), [f(t + _dt.timedelta(days=3)), f(_is_gunu_ekle(t, 5)), f(_is_gunu_ekle(t, 1))],
                        ["En geç 3 **iş günü** içinde; hafta sonu sayılmaz.", f"{f(t)} + 3 iş günü = **{f(son)}**"]))
    havuz = _ek(r, [
        ("İş kazası SGK'ya en geç ne zaman bildirilir?", "Kazadan sonraki 3 iş günü içinde", ["1 ay içinde", "1 yıl içinde",
                                                                                            "Hiç bildirilmez"], ["6331 md. 14."]),
        ("Meslek hastalığı ne zaman bildirilir?", "Öğrenildiği tarihten itibaren 3 iş günü içinde", ["10 yıl sonra", "Emeklilikte",
                                                                                                  "Hiç bildirilmez"], ["Ders notu 6.4."]),
        ("Ramak kala olay nedir?", "Zarar verme potansiyeli olduğu hâlde zarara yol açmayan olay", ["Ölümlü kaza",
                                                                                                "Meslek hastalığı", "Maddi hasarlı kaza"],
         ["6331 sayılı Kanun."]),
        ("Ramak kala olaylar neden kaydedilir?", "Nedenleri giderilirse ciddi kaza önlenir", ["Ceza kesmek için",
                                                                                            "Sigorta primi için", "Gerek yoktur"],
         ["Kaza piramidi."]),
        ("Hangisi ramak kala olaya örnektir?", "Traktörün teras kenarında kayıp son anda durması", ["Testereyle parmak kesilmesi",
                                                                                                  "Traktörün devrilmesi", "Bel fıtığı"],
         ["Zarar oluşmadı."]),
        ("Mevsimlik işçilerin ulaşımında hangisi doğrudur?", "Ruhsatlı yolcu aracında oturarak taşınırlar", ["Römorkta taşınırlar",
                                                                                                            "Kamyonet kasasında ayakta",
                                                                                                            "Traktör çamurluğunda"],
         ["Römorkta insan taşınmaz."]),
        ("Çocukların tarımda hangi işte çalışmasına hiç izin verilmez?", "Traktör kullanma ve ilaçlama", ["Ders çalışma",
                                                                                                         "Oyun oynama", "Hiçbiri"],
         ["Tehlikeli işler."]),
        ("Gebe ve emziren kadınlar hangi işlerden uzak tutulur?", "İlaçlama ve kimyasal işler", ["Dinlenme", "Su içme",
                                                                                                "Gölgede oturma"], ["Anne ve bebek için risk."]),
        ("Genç çalışanlar neden kazaya daha açıktır?", "Deneyimsiz oldukları için", ["Daha güçlü oldukları için",
                                                                                    "Daha yavaş çalıştıkları için", "Açık değildir"],
         ["Eğitim ve gözetim gerekir."]),
        ("Sulama pompası ve dış prizlerde hangisi kullanılır?", "Kaçak akım rölesi", ["Uzatma kablosu", "Bant", "Su ile soğutma"],
         ["Çarpılmayı önler."]),
        ("Hangileri yan yana depolanmaz?", "Kuru ot, saman, yakıt ve pestisit", ["Kitap ve defter", "Su ve bardak", "Kürek ve tırmık"],
         ["Yangın riski."]),
        ("Mevsimlik işçiler ilaçlanan alana ne zaman girebilir?", "Bekleme süresi dolduktan sonra", ["Hemen", "İlaçlama sırasında",
                                                                                                   "Hiç girmezler"], ["Maruziyet."]),
        ("Ramak kala formunda hangisi bulunmaz?", "İşçinin maaşı", ["Tarih ve saat", "Ne oldu", "Alınan önlem"], ["Form alanları."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_cevre(r):
    sabit = []
    y = _sec_bir(r, list(YANAN))
    sinif = YANAN[y]
    sabit.append(_secim(r, f"“{y}” yangını hangi sınıftır?", "Elektrik yangını (önce elektrik kesilir)" if sinif == "Elektrik" else f"{sinif} sınıfı",
                        _diger(r, [f"{s} sınıfı" for s in "ABCDF"] + ["Elektrik yangını (önce elektrik kesilir)"],
                               "Elektrik yangını (önce elektrik kesilir)" if sinif == "Elektrik" else f"{sinif} sınıfı"),
                        [f"{k}: {v[0]} ({v[1]})" for k, v in YANGIN_SINIF.items()]))
    s2 = _sec_bir(r, ["B", "D"])
    uygun = [SONDURUCU[i] for i, u in enumerate(UYGUNLUK[s2]) if u.startswith("✔")]
    yasak = [SONDURUCU[i] for i, u in enumerate(UYGUNLUK[s2]) if u.startswith("✘")]
    if s2 == "B":
        sabit.append(_secim(r, "B sınıfı (yanıcı sıvı: mazot, benzin) yangında hangisi KULLANILMAZ?", "Su", uygun,
                            [f"B sınıfı için uygun: {', '.join(uygun)}. Su, yanan sıvıyı sıçratıp yayar."]))
    else:
        sabit.append(_secim(r, "D sınıfı (yanıcı metal: magnezyum tozu) yangında hangisi uygundur?", "D sınıfı toz", yasak,
                            ["Yanıcı metallerde yalnızca özel D sınıfı tozlar kullanılır."]))
    u = _sec_bir(r, list(CEVRE))
    sabit.append(_secim(r, f"Bağcılıkta “{u}” için doğru önlem hangisidir?", CEVRE[u][1],
                        _diger(r, [v[1] for v in CEVRE.values()], CEVRE[u][1]), [f"{u}: {CEVRE[u][1]}"]))
    havuz = _ek(r, [
        ("Yangın üçgenini oluşturan üç öğe hangisidir?", "Isı, yakıt, oksijen", ["Su, toprak, hava", "Isı, su, karbondioksit",
                                                                                  "Yakıt, su, kum"], ["Biri çekilince yangın söner."]),
        ("Yemeklik yağ (F sınıfı) yangınına ne yapılmaz?", "Su dökülmez", ["Islak battaniye örtülür", "F sınıfı söndürücü kullanılır",
                                                                           "Ocak kapatılır"], ["Su yağı sıçratır."]),
        ("Elektrik yangınında ilk yapılacak nedir?", "Elektriği kesmek", ["Su dökmek", "Pencereyi açmak", "Panoya dokunmak"],
         ["Sonra CO₂ ya da kuru kimyevi toz."]),
        ("LPG yangınında söndürmeden önce ne yapılır?", "Gaz vanası kapatılır", ["Su dökülür", "Tüp sallanır", "Kapı kapatılır"],
         ["Yakıtı kesmek."]),
        ("Yangın söndürücü kullanımının doğru sırası hangisidir?", "Pimi çek → ateşin dibine yönelt → tetiğe bas → süpür",
         ["Tetiğe bas → pimi çek → alevin üstüne tut", "Süpür → pimi çek → tetiğe bas", "Alevin tepesine sık → bekle"],
         ["Ders notu 8.3."]),
        ("Söndürücü hortumu nereye yöneltilir?", "Ateşin dibine, alevin kaynağına", ["Alevin tepesine", "Duvara", "Havaya"],
         ["Kaynak söndürülür."]),
        ("Söndürücüyle müdahalede rüzgâr nerede olmalıdır?", "Arkada", ["Önde", "Yanda", "Fark etmez"], ["Kaçış yolu da arkada bırakılır."]),
        ("Söndürücünün basınç göstergesi hangi bölgede olmalıdır?", "Yeşil", ["Kırmızı", "Sarı", "Sıfırda"], ["Periyodik kontrol."]),
        ("Fırtınada yıldırımdan korunmak için hangisi doğrudur?", "Kapalı araç ya da binaya girmek", ["Tek ağacın altına sığınmak",
                                                                                                  "Traktör üstünde beklemek",
                                                                                                  "Metal tellere yaslanmak"],
         ["Açık alandan uzaklaş."]),
        ("Kapalı ortamda jeneratör çalıştırmanın tehlikesi nedir?", "Karbonmonoksit zehirlenmesi", ["Su baskını", "Deprem", "Heyelan"],
         ["Havalandırma ve CO dedektörü."]),
        ("LPG tüpü kaçağı nasıl kontrol edilir?", "Sabunlu suyla", ["Kibrit yakarak", "Koklayarak eğilerek", "Çakmakla"],
         ["Asla alevle kontrol edilmez."]),
        ("Pestisit nasıl bir depoda saklanır?", "Kilitli, havalandırmalı ve etiketli depoda", ["Mutfak dolabında", "Yem çuvallarının yanında",
                                                                                             "Çocuk odasında"], ["Ders notu 8.1."]),
        ("Depremde rafların devrilmesine karşı ne yapılır?", "Raflar duvara sabitlenir, ağır eşya alta konur", ["Ağır eşya üste konur",
                                                                                                             "Raflar boş bırakılır", "Hiçbir şey"],
         ["Ders notu 8.1."]),
        ("Türkiye'de bütün acil durumlar için tek numara hangisidir?", "112", ["110", "155", "177"], ["Tek numara."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_kuram(r):
    sabit = []
    k = int(r.choice([2, 3, 4, 5, 8]))
    katman, oran = _sec_bir(r, [("ramak kala olay", 600), ("yalnızca maddi hasarlı olay", 30), ("hafif yaralanma", 10)])
    sabit.append(_secim(r, f"Bird'ün kaza piramidine göre {k} ciddi yaralanmanın altında yaklaşık kaç {katman} beklenir?",
                        _tr(k * oran, 0), [_tr(oran, 0), _tr(k * oran * 10, 0), _tr(k + oran, 0)],
                        ["1 : 10 : 30 : 600", f"{k} × {oran} = **{_tr(k * oran, 0)}**"]))
    i = int(r.integers(0, 5))
    sabit.append(_secim(r, f"Heinrich'in domino teorisinde {i + 1}. taş hangisidir?", DOMINO[i], [d for j, d in enumerate(DOMINO) if j != i],
                        ["Sıra: " + " → ".join(DOMINO)]))
    havuz = _ek(r, [
        ("Domino teorisinde hangi taş çekilirse kaza önlenir?", "Güvensiz davranış ve güvensiz durum", ["Sosyal çevre", "Kaza",
                                                                                                       "Yaralanma"], ["Ortadaki taş."]),
        ("Domino teorisini kim ortaya koymuştur?", "H. W. Heinrich", ["F. Bird", "Fine ve Kinney", "Mendel"], ["1930'lar."]),
        ("Kaza piramidini kim yayımlamıştır?", "F. Bird (1969)", ["Heinrich (1931)", "Kinney (1976)", "ILO (2012)"], ["Ders notu 9.3."]),
        ("Kaza piramidinin tabanında ne vardır?", "Ramak kala olaylar", ["Ölümlü kazalar", "Hafif yaralanmalar", "Maddi hasar"],
         ["600."]),
        ("Kaza piramidinin ana mesajı nedir?", "Ramak kala olaylar önlenirse ciddi kaza da önlenir", ["Ciddi kazalar önlenemez",
                                                                                                     "Yalnızca ölümler önemlidir",
                                                                                                     "Küçük olaylar önemsizdir"], ["Taban önlenir."]),
        ("Heinrich'in “kazaların çoğu güvensiz davranıştan” görüşü bugün neden eleştirilir?",
         "Davranışın arkasında çoğu zaman eğitimsizlik, iş yükü ve güvensiz düzen vardır", ["Hiç eleştirilmez", "Kazalar şansa bağlıdır",
                                                                                           "Makineler hiç arızalanmaz"],
         ["Suçlu aramak yerine sistemi düzeltmek."]),
        ("Koruyucusu sökülmüş kuyruk mili hangi gruptadır?", "Güvensiz durum", ["Güvensiz davranış", "Meslek hastalığı", "Doğal afet"],
         ["Ekipman kaynaklı."]),
        ("Emniyet kemeri takmamak hangi gruptadır?", "Güvensiz davranış", ["Güvensiz durum", "Ramak kala", "Meslek hastalığı"],
         ["Kişi kaynaklı."]),
        ("Güvensiz davranışı azaltmak için hangisi uygundur?", "Eğitim, gözetim ve yeterli mola", ["Ceza ve suçlama",
                                                                                                  "Mola vermemek", "İşi hızlandırmak"],
         ["Ders notu 9.1."]),
        ("Kontrol hiyerarşisinde ikame ne demektir?", "Daha az tehlikeli olanla değiştirmek", ["Tehlikeyi yok etmek",
                                                                                              "KKD vermek", "Levha asmak"],
         ["Ör. düşük toksisiteli ilaç."]),
        ("Kabinli traktör kontrol hiyerarşisinde hangi basamaktır?", "Mühendislik önlemi", ["İdari önlem", "KKD", "İkame"],
         ["Tehlikeyi yalıtır."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_puan(r):
    sabit = []
    o, sd = int(r.integers(1, 6)), int(r.integers(1, 6))
    p = o * sd
    duz, _ = risk_duzey(p)
    sabit.append(_secim(r, f"5×5 matriste olasılık {o}, şiddet {sd} olan riskin düzeyi nedir?", f"{p} · {duz}",
                        [f"{o + sd} · {risk_duzey(o + sd)[0]}"] + [f"{p} · {x}" for x in ["Önemsiz", "Düşük", "Orta", "Yüksek",
                                                                                             "Tolere edilemez"] if x != duz][:2],
                        [f"Risk = {o} × {sd} = {p} → {duz}: {DUZEY_NE[duz]}"]))
    a = _sec_bir(r, FK_OLASILIK)
    b = _sec_bir(r, FK_FREKANS)
    c = _sec_bir(r, FK_SIDDET)
    fk = a[1] * b[1] * c[1]
    sinif, _ = fk_sinif(fk)
    sabit.append(_secim(r, f"Fine-Kinney: olasılık “{a[0]}” ({_tr(a[1], 1)}), frekans “{b[0].split(' (')[0]}” ({_tr(b[1], 1)}), "
                           f"şiddet “{c[0].split(' (')[0]}” ({c[1]}). Risk sınıfı nedir?", f"{_tr(fk, 1)} · {sinif}",
                        [f"{_tr(fk, 1)} · {x}" for x in ["Önemsiz", "Olası, izlenir", "Önemli, önlem planlanır", "Yüksek, kısa sürede önlem",
                                                          "Tolerans gösterilemez, iş durdurulur"] if x != sinif][:2] +
                        [f"{_tr(a[1] + b[1] + c[1], 1)} · {fk_sinif(a[1] + b[1] + c[1])[0]}"],
                        [f"{_tr(a[1], 1)} × {_tr(b[1], 1)} × {c[1]} = **{_tr(fk, 1)}** → {sinif}"]))
    isci, gun, saat = int(r.choice([10, 20, 25, 40, 50])), int(r.choice([200, 220, 250])), 8
    kaza, kayip = int(r.integers(1, 6)), int(r.integers(5, 60))
    T = isci * gun * saat
    kso, kao = kaza * 1e6 / T, kayip * 1000 / T
    sabit.append(_secim(r, f"{isci} işçi yılda {gun} gün, günde {saat} saat çalışıyor; yılda {kaza} kaza oldu. KSO kaçtır?", _tr(kso, 2),
                        [_tr(kaza * 1000 / T, 4), _tr(kaza * 200000 / T, 2), _tr(kso * 10, 2)],
                        [f"Toplam saat = {isci} × {gun} × {saat} = {_tr(T, 0)}", _tx(rf"KSO = \frac{{{kaza} \times 1\,000\,000}}{{{T}}} = {kso:.2f}")]))
    sabit.append(_secim(r, f"{isci} işçi yılda {gun} gün, günde {saat} saat çalışıyor; kazalarda toplam {kayip} iş günü kaybedildi. KAO kaçtır?",
                        _tr(kao, 3), [_tr(kayip * 1e6 / T, 1), _tr(kao * 10, 3), _tr(kao / 10, 4)],
                        [f"Toplam saat = {_tr(T, 0)}", _tx(rf"KAO = \frac{{{kayip} \times 1000}}{{{T}}} = {kao:.3f}")]))
    havuz = _ek(r, [
        ("5×5 matriste risk nasıl hesaplanır?", "Olasılık × şiddet", ["Olasılık + şiddet", "Olasılık × frekans × şiddet", "Şiddet ÷ olasılık"],
         ["L tipi matris."]),
        ("Fine-Kinney yönteminde risk nasıl hesaplanır?", "Olasılık × frekans × şiddet", ["Olasılık × şiddet", "Frekans + şiddet",
                                                                                          "Şiddet²"], ["Türkiye'de yaygın."]),
        ("5×5 matriste 20–25 puan ne anlama gelir?", "Tolere edilemez, iş derhal durdurulur", ["Önemsiz", "Düşük", "Orta"], ["Ders notu 10.1."]),
        ("5×5 matriste 15–16 puan ne gerektirir?", "Önlem alınmadan işe başlanmaz", ["Önlem gerekmez", "Mevcut önlemler izlenir",
                                                                                   "İş hemen durdurulur"], ["Yüksek risk."]),
        ("Fine-Kinney'de 400 ve üzeri puan ne anlama gelir?", "Tolerans gösterilemez, iş durdurulur", ["Önemsiz", "Olası, izlenir",
                                                                                                     "Önemli"], ["Ders notu 10.2."]),
        ("Fine-Kinney'de ölüm şiddetinin puanı kaçtır?", "40", ["7", "15", "100"], ["Birden çok ölüm 100."]),
        ("Fine-Kinney'de “sık (günde bir)” frekansın puanı kaçtır?", "6", ["0,5", "2", "10"], ["Ders notu 10.2."]),
        ("KSO neyi gösterir?", "1 milyon çalışma saatinde kaç kaza olduğunu", ["1000 saatte kaybedilen iş gününü", "Kaza başına maliyeti",
                                                                               "İşçi sayısını"], ["Sıklık."]),
        ("KAO neyi gösterir?", "1000 çalışma saatinde kaybedilen iş gününü", ["1 milyon saatte kaza sayısını", "Ölüm sayısını",
                                                                              "Ramak kala sayısını"], ["Ağırlık."]),
        ("Az ama ağır kazası olan işletmede ne beklenir?", "KSO düşük, KAO yüksek", ["KSO yüksek, KAO düşük", "İkisi de sıfır",
                                                                                   "İkisi de yüksek"], ["Ders notu 10.3."]),
        ("Kaza sayıları neden doğrudan karşılaştırılmaz?", "İşletmelerin çalışan ve çalışma saati farklıdır",
         ["Kazalar gizlidir", "Sayılar hep aynıdır", "Karşılaştırma yasaktır"], ["Çalışma saatine oranlanır."]),
        ("ROPS ve kemer Fine-Kinney'de hangi bileşeni düşürür?", "Şiddeti", ["Frekansı", "Olasılığı artırır", "Hiçbirini"],
         ["Devrilmede ölüm yerine ciddi yaralanma."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_meslek(r):
    sabit = []
    g, e, h = _sec_bir(r, MH_ETMEN)
    sabit.append(_secim(r, f"Tarımda “{e.lower()}” hangi meslek hastalığına yol açabilir?", h, _diger(r, [x[2] for x in MH_ETMEN], h),
                        [f"{g} etmen: {e} → {h}"]))
    sabit.append(_secim(r, f"“{e}” hangi etmen grubundadır?", g, _diger(r, ["Fiziksel", "Kimyasal", "Biyolojik", "Ergonomik", "Psikososyal"], g),
                        [f"{e}: {g}"]))
    havuz = _ek(r, [
        ("Hangisi meslek hastalığıdır?", "Gürültüye bağlı işitme kaybı", ["Traktör devrilmesi", "Testere kesiği", "Merdivenden düşme"],
         ["Tekrarlanan maruziyet."]),
        ("Hangisi iş kazasıdır?", "Testereyle el kesilmesi", ["Bel fıtığı", "Çiftçi akciğeri", "Kronik pestisit etkisi"], ["Ani olay."]),
        ("Meslek hastalığı nasıl ortaya çıkar?", "Yavaş, uzun sürede", ["Ani, bir anda", "Tek bir olayla", "Hiç belirti vermeden geçer"],
         ["İş kazasından farkı."]),
        ("Çiftçi akciğerine ne yol açar?", "Küflü saman ve organik tozlar", ["Gürültü", "Güneş ışını", "Titreşim"], ["Alerjik akciğer hastalığı."]),
        ("Bruselloz hangi etmen grubundadır?", "Biyolojik", ["Fiziksel", "Kimyasal", "Ergonomik"], ["Bakteri."]),
        ("Güneşin morötesi ışınları hangi hastalığa yol açabilir?", "Deri kanseri ve göz hasarı", ["Bel fıtığı", "İşitme kaybı",
                                                                                                  "Bruselloz"], ["Fiziksel etmen."]),
        ("Meslek hastalığı tanısını kim koyar?", "Yetkili sağlık kuruluşları; SGK onaylar", ["İşveren", "Muhtar", "Çalışanın kendisi"],
         ["Meslek hastalıkları hastaneleri."]),
        ("Meslek hastalıkları tarımda neden az bildirilir?", "Hastalıklar işle ilişkilendirilmediği için", ["Hiç görülmediği için",
                                                                                                          "Yasak olduğu için", "Tedavisi kolay olduğu için"],
         ["Kayıtlara geçmez."]),
        ("Şikâyet başladığında doktora ne mutlaka söylenmelidir?", "Yaptığı iş", ["Tuttuğu takım", "Doğum yeri", "Hiçbir şey"],
         ["İşle ilişki kurulabilsin."]),
        ("Periyodik muayenede hangi test gürültüye karşı yapılır?", "İşitme testi", ["Göz testi", "Kan şekeri", "Boy ölçümü"], ["Odyometri."]),
        ("Uzun çalışma saatleri ve gelir belirsizliği hangi etmen grubundadır?", "Psikososyal", ["Kimyasal", "Fiziksel", "Biyolojik"],
         ["Stres, tükenmişlik."]),
        ("Meslek hastalıkları korunmasında ilk ilke hangisidir?", "Maruziyeti kaynağında azaltmak", ["Yalnızca ilaç kullanmak",
                                                                                                 "Hastalanınca işi bırakmak", "KKD'yi en başta düşünmek"],
         ["Kontrol hiyerarşisi."]),
        ("Solunum fonksiyon testi hangi meslek hastalığı riskine karşı yapılır?", "Organik toz ve kimyasala bağlı akciğer hastalıkları",
         ["İşitme kaybı", "Bel fıtığı", "Deri kanseri"], ["Periyodik muayene."]),
        ("Leptospiroz hangi etmen grubundadır?", "Biyolojik", ["Fiziksel", "Ergonomik", "Psikososyal"], ["Bakteri kaynaklı."]),
        ("El-kol titreşim sendromunun belirtisi hangisidir?", "Parmaklarda beyazlama ve uyuşma", ["İşitme kaybı", "Ateş", "Öksürük"],
         ["Motorlu testere, tırpan."]),
        ("Kronik pestisit maruziyeti hangi sistemi etkileyebilir?", "Sinir sistemini", ["Yalnızca saçları", "Hiçbir sistemi",
                                                                                       "Yalnızca tırnakları"], ["Kimyasal etmen."]),
        ("Bel fıtığı hangi etmen grubuna bağlıdır?", "Ergonomik", ["Biyolojik", "Kimyasal", "Psikososyal"], ["Ağır yük, eğilerek çalışma."]),
        ("Meslek hastalığı bazen ne zaman fark edilir?", "İşten ayrıldıktan sonra bile", ["Her zaman ilk gün", "Asla",
                                                                                         "Yalnızca kaza olunca"], ["Geç fark edilir."]),
        ("İşe giriş muayenesinin amacı nedir?", "Çalışanın sağlık durumunu başlangıçta belirlemek", ["Maaşı belirlemek",
                                                                                                   "İzin günlerini saymak", "Gerek yoktur"],
         ["Sonraki değişiklikler karşılaştırılır."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_isaret(r):
    sabit = []
    grup = _sec_bir(r, list(ISARETLER_ISG))
    ad, _, nerede = _sec_bir(r, ISARETLER_ISG[grup][2])
    sekil = {"Yasaklayıcı": "Kırmızı kenarlı, çapraz çizgili yuvarlak", "Uyarı": "Sarı üçgen, siyah kenar",
             "Emredici": "Mavi yuvarlak, beyaz sembol", "Acil durum": "Yeşil kare", "Yangınla mücadele": "Kırmızı kare"}
    sabit.append(_secim(r, f"“{ad}” işareti hangi şekil ve renktedir?", sekil[grup], [v for k, v in sekil.items() if k != grup],
                        [f"{ad}: {grup.lower()} işareti."]))
    tum = [(x[0], x[2]) for g in ISARETLER_ISG.values() for x in g[2]]
    sabit.append(_secim(r, f"“{ad}” işareti en çok nerede kullanılır?", nerede, _diger(r, [n for _, n in tum], nerede),
                        [f"{ad} → {nerede}"]))
    tur, gad, ne = _sec_bir(r, GHS_PESTISIT)
    sabit.append(_secim(r, f"Pestisit etiketinde “{gad.lower()}” piktogramı ne anlatır?", ne, _diger(r, [x[2] for x in GHS_PESTISIT], ne),
                        [f"{gad}: {ne}"]))
    havuz = _ek(r, [
        ("Mavi yuvarlak işaret ne anlama gelir?", "Bir davranışı zorunlu kılar", ["Yasaklar", "Uyarır", "Kaçış yolunu gösterir"],
         ["Çoğunlukla KKD."]),
        ("Sarı üçgen işaret ne anlama gelir?", "Bir tehlikeye karşı uyarır", ["Zorunlu kılar", "Yasaklar", "Yangın ekipmanını gösterir"],
         ["Uyarı işareti."]),
        ("Kırmızı kenarlı, çapraz çizgili yuvarlak işaret ne anlama gelir?", "Yasaklar", ["Uyarır", "Zorunlu kılar", "İlk yardımı gösterir"],
         ["Yasaklayıcı."]),
        ("Yeşil kare işaret ne gösterir?", "Kaçış yolu, ilk yardım, güvenli durum", ["Yangın ekipmanı", "Tehlike", "Yasak"], ["Acil durum."]),
        ("Kırmızı kare işaret ne gösterir?", "Yangın ekipmanının yerini", ["İlk yardım yerini", "Tehlikeyi", "Zorunluluğu"],
         ["Yangınla mücadele."]),
        ("Pestisit etiketindeki tehlike piktogramı hangi şekildedir?", "Kırmızı çerçeveli, beyaz zeminli eşkenar dörtgen",
         ["Mavi daire", "Yeşil kare", "Sarı üçgen"], ["GHS / SEA Yönetmeliği."]),
        ("Etikette tehlike piktogramının yanında hangi ifadeler yazar?", "Tehlike (H) ve önlem (P) ifadeleri", ["Fiyat ve barkod",
                                                                                                             "Üretici telefonu", "Hasat tarihi"],
         ["Ders notu 12.6."]),
        ("İşaretler için hangisi doğrudur?", "İşaret önlemin yerine geçmez, yalnızca tamamlar", ["İşaret asmak yeterli önlemdir",
                                                                                               "Ne kadar çok işaret o kadar iyi",
                                                                                               "Tehlike bitse de işaret kalır"],
         ["Ders notu 12.7."]),
        ("Tehlike ortadan kalkınca işarete ne yapılır?", "Kaldırılır", ["Bırakılır", "Çoğaltılır", "Boyanır"], ["Kural."]),
        ("İlaç deposu kapısına hangi işaret uygundur?", "Sigara içmek yasaktır", ["Acil toplanma alanı", "Baret takınız",
                                                                                 "Yangın alarm butonu"], ["Ders notu 12.2."]),
        ("Elektrik panosuna hangi işaret asılır?", "Elektrik tehlikesi", ["Yemek ve içmek yasaktır", "Göz yıkama", "Baret takınız"],
         ["Uyarı işareti."]),
        ("Traktör ve iş makinesinin çalıştığı alanda hangi yasak işareti kullanılır?", "Yayaların girmesi yasaktır",
         ["Su ile söndürmek yasaktır", "Sigara içmek yasaktır", "Yemek yasaktır"], ["Ders notu 12.2."]),
        ("İşyerinde hangi standarda uygun levhalar kullanılır?", "TS EN ISO 7010", ["ISO 9001", "ISO 22000", "TS EN 71"], ["Ders notu."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_etkinlik(r):
    sabit = []
    for _ in range(3):
        k = _sec_bir(r, KKD_ESLE_SOL)
        harfler, acik = KKD_ESLE_CEVAP[k]
        h = harfler[int(r.integers(0, len(harfler)))]
        yanlis = [KKD_ESLE_SAG[x] for x in KKD_ESLE_SAG if x not in harfler]
        sabit.append(_secim(r, f"“{k}” aşağıdaki iş/tehlikelerden hangisiyle eşleşir?", KKD_ESLE_SAG[h],
                            [yanlis[int(i)] for i in r.permutation(len(yanlis))[:3]],
                            [f"{k}: {', '.join(KKD_ESLE_SAG[x] for x in harfler)}. {acik}."]))
    yer, isaretler = _sec_bir(r, list(ISARET_NEREYE.items()))
    dogru = _sec_bir(r, sorted(isaretler))
    tum = [x[0] for g in ISARETLER_ISG.values() for x in g[2]]
    disari = [x for x in tum if x not in isaretler]
    sabit.append(_secim(r, f"“{yer}” için en uygun işaret hangisidir?", dogru, [disari[int(i)] for i in r.permutation(len(disari))[:3]],
                        [f"{yer}: {', '.join(sorted(isaretler))}"]))
    bolum = _sec_bir(r, list(TEHLIKE_AVI))
    madde = _sec_bir(r, TEHLIKE_AVI[bolum])
    sabit.append(_secim(r, f"Tehlike avında “{madde}” sorusu hangi bölüme aittir?", bolum, [b for b in TEHLIKE_AVI if b != bolum],
                        [f"{bolum}"]))
    havuz = _ek(r, [
        ("Tehlike avında “Var ama riskli” işaretlenen maddeler için ne yapılır?", "Öncelikle düzeltilir", ["Göz ardı edilir",
                                                                                                          "Bir sonraki yıla bırakılır", "Silinir"],
         ["Risk giderilir."]),
        ("KKD için hangisi doğrudur?", "Kişiye özel olmalı, temiz ve kullanılabilir durumda tutulmalı", ["Herkes ortak kullanır",
                                                                                                       "Kirli de olsa olur", "Yıllarca değiştirilmez"],
         ["Tehlike avı C bölümü."]),
        ("Boş ilaç ambalajları nasıl değerlendirilir?", "Uygun şekilde bertaraf edilir", ["Su kabı yapılır", "Yakılır", "Dereye atılır"],
         ["Tehlike avı B bölümü."]),
        ("İlk yardım çantası için hangisi önemlidir?", "Yerinin herkesçe bilinmesi ve içinin eksiksiz olması", ["Kilitli olması",
                                                                                                             "Gizlenmesi", "Boş tutulması"],
         ["Tehlike avı E bölümü."]),
        ("Çıkış kartında öğrenci neyi yazar?", "3 tehlike, 2 KKD, 1 önlem", ["Notunu", "Devamsızlığını", "Adresini"], ["Ek-3."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_tekrar(r):
    ureticiler = [gen_temel, gen_kkd, gen_ra, gen_traktor, gen_etmen, gen_ozel, gen_cevre, gen_kuram, gen_puan, gen_puan,
                  gen_meslek, gen_isaret, gen_etkinlik]
    secilen = [ureticiler[int(i)] for i in r.permutation(len(ureticiler))[:SORU_SAYISI]]
    return [u(r)[0] for u in secilen]


# ===========================================================================
# Gezinme
# ===========================================================================
SAYFALAR = [
    st.Page(sayfa_giris, title="Giriş", icon="🏠", url_path="giris", default=True),
    st.Page(sayfa_temel, title="1 · İSG'ye giriş", url_path="isg-giris"),
    st.Page(sayfa_kkd, title="2 · Bağcılıkta riskler ve KKD", url_path="riskler-kkd"),
    st.Page(sayfa_ra, title="3 · Risk değerlendirmesi ve acil durum", url_path="risk-acil"),
    st.Page(sayfa_traktor, title="4 · Traktör ve bağ makineleri", url_path="traktor"),
    st.Page(sayfa_etmen, title="5 · Fiziksel, biyolojik, ergonomik", url_path="etmenler"),
    st.Page(sayfa_ozel, title="6 · Özel gruplar ve İSG yönetimi", url_path="ozel-gruplar"),
    st.Page(sayfa_cevre, title="7 · Çevre, bina ve yangın", url_path="cevre-yangin"),
    st.Page(sayfa_kuram, title="8 · Kaza kuramları", url_path="kaza-kuramlari"),
    st.Page(sayfa_puan, title="9 · Risk puanlama ve kaza oranları", url_path="risk-puanlama"),
    st.Page(sayfa_meslek, title="10 · Meslek hastalıkları", url_path="meslek-hastaliklari"),
    st.Page(sayfa_isaret, title="11 · Güvenlik işaretleri", url_path="isaretler"),
    st.Page(sayfa_etkinlik, title="12 · Uygulama etkinlikleri", url_path="etkinlikler"),
    st.Page(sayfa_tekrar, title="13 · Genel tekrar", url_path="genel-tekrar"),
]
gezinme = st.navigation(SAYFALAR)

with st.sidebar:
    tohum = st.number_input("Rastgele tohum (0 = rastgele)", 0, 999999, 0,
                            help="Sınıfta herkes aynı sayıyı girerse aynı soruları görür.")
    if st.session_state.get("tohum") != tohum:
        st.session_state.tohum = tohum
        st.session_state.rng = (np.random.default_rng(tohum) if tohum
                                else np.random.default_rng())
    st.divider()
    st.caption(TELIF)

basliklar = [p.title for p in SAYFALAR]
simdiki = basliklar.index(gezinme.title) if gezinme.title in basliklar else 0
secilen = st.selectbox("📚 Bölüm", basliklar, index=simdiki)
if secilen != gezinme.title:
    st.switch_page(SAYFALAR[basliklar.index(secilen)])

gezinme.run()

st.divider()
c1, _, c3 = st.columns([1, 0.2, 1])
if simdiki > 0:
    c1.page_link(SAYFALAR[simdiki - 1], label=f"◀ {basliklar[simdiki - 1]}")
if simdiki < len(SAYFALAR) - 1:
    c3.page_link(SAYFALAR[simdiki + 1], label=f"{basliklar[simdiki + 1]} ▶")

st.markdown(f'<div style="text-align:center;color:gray;font-size:0.85rem;'
            f'margin-top:24px">{TELIF}</div>', unsafe_allow_html=True)
