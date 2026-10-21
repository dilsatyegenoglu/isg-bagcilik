# 🦺 İş Sağlığı ve Güvenliği · Bağcılık

**Bağcılık ön lisans programı İş Sağlığı ve Güvenliği dersi için etkileşimli, Türkçe öğretim uygulaması**

© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır.

---

## Nedir?

Bağda budamadan hasada, traktörden ilaç deposuna kadar karşılaşılan tehlikeleri şemalar,
simülasyonlar, hesaplayıcılar ve etkinliklerle anlatan bir web uygulamasıdır. Bilgisayardan ve
telefondan tarayıcıyla açılır. Bütün şemalar bu uygulama için özgün olarak çizilmiştir.

## İçerik

| Bölüm | Konu ve etkileşimli öğeler |
|---|---|
| 1 · İSG'ye giriş | Temel kavramlar, tehlike–risk şeması, 6331 sayılı Kanun, işveren ve çalışan yükümlülükleri; "tehlike mi risk mi" ve "güvensiz davranış mı durum mu" mini oyunları |
| 2 · Bağcılıkta riskler ve KKD | Bağ takvimi, işe göre tehlike ve önlem, KKD giydirilen çalışan figürü, "çalışanı siz giydirin" oyunu, pestisit güvenliği, PHI (hasat öncesi bekleme süresi) hesaplayıcı |
| 3 · Risk değerlendirmesi ve acil durum | Beş adımlı döngü, kontrol hiyerarşisi (ters piramit) ve sınıflandırma oyunu, örnek risk değerlendirmesi, acil durum senaryoları |
| 4 · Traktör ve bağ makineleri | Devrilme simülatörü (eğim, iz genişliği, ağırlık merkezi, ROPS, kemer), devrilme türleri, kuyruk mili şeması, römork kuralları, ekipman tablosu, günlük kontrol listesi |
| 5 · Fiziksel, biyolojik, ergonomik | Belirtilere göre sıcak bitkinliği / sıcak çarpması kararı, gürültü ölçeği (80/85/87 dB), eşit enerji süre hesabı, titreşim, doğru/yanlış kaldırma şeması ve etkinliği, sokma ve kene ilk müdahalesi |
| 6 · Özel gruplar ve İSG yönetimi | Mevsimlik işçiler, çocuk-genç-gebe çalışanlar, yangın-elektrik, 3 iş günü kaza bildirim hesaplayıcı, indirilebilir ramak kala kayıt formu |
| 7 · Çevre, bina ve yangın | Doğal tehlikeler, bina tehlikeleri, yangın üçgeni, yanan maddeye göre yangın sınıfı ve uygun söndürücü, söndürücü kullanımı adım adım |
| 8 · Kaza kuramları | Güvensiz davranış/durum, Heinrich'in domino teorisi (taşı çekme), Bird'ün kaza piramidi, kontrol hiyerarşisi |
| 9 · Risk puanlama ve kaza oranları | Etkileşimli 5×5 risk matrisi, Fine-Kinney hesaplayıcı, KSO / KAO hesaplayıcı |
| 10 · Meslek hastalıkları | İş kazası ile farkı, tarımdaki etmenler (fiziksel, kimyasal, biyolojik, ergonomik, psikososyal), korunma ve tanı |
| 11 · Güvenlik işaretleri | Şekil-renk-anlam, 26 güvenlik işareti çizimi, pestisit etiketi piktogramları, asma kuralları, "hangi işaret nereye?" etkinliği |
| 12 · Uygulama etkinlikleri | KKD eşleştirme (cevap anahtarıyla), 49 maddelik tehlike avı kontrol listesi ve indirilebilir rapor, çıkış kartı |
| 13 · Genel tekrar | Hafıza kartları, sözlük ve tüm konulardan karışık sorular |

Her bölümün sonunda **10, 20 ya da 30 soruluk seçmeli alıştırma** vardır (öğrenci seçer). Yanıt
seçilince kilitlenir, doğru/yanlış ve adım adım çözüm o zaman açılır. "Yeni sorular" düğmesiyle
sınırsız soru üretilir.

## Kurulum ve çalıştırma

```bash
pip install -r requirements.txt
streamlit run isg_streamlit.py
```

Linux / WSL'de kısaca: `bash baslat.sh`. Ardından tarayıcıda http://localhost:8501

## Yayına alma

GitHub reposuna `isg_streamlit.py` ve `requirements.txt` yüklenir; share.streamlit.io'da
"Create app" ile ana dosya olarak `isg_streamlit.py` seçilir.

## Bilinen sınırlamalar

- Şemalar öğretim amaçlı ve ölçeksizdir; işaretler TS EN ISO 7010 ve GHS işaretlerine benzetilerek sadeleştirilmiştir. İşyerinde standarda uygun hazır levhalar kullanılır.
- Traktör devrilme simülatörü duran traktör için statik bir hesaptır; hareket, tümsek ve dönüş devrilme açısını çok düşürür.
- Gürültü düzeyleri ve eşit enerji süreleri öğretici yaklaşık değerlerdir.
- Kaza bildirim hesaplayıcı yalnızca hafta sonlarını atlar; resmî tatilleri hesaba katmaz.
- İlk yardım bilgileri genel eğitim amaçlıdır; işletmenin acil durum planı ve ürün etiketleri esas alınmalıdır.
- Öğrenci yanıtları kaydedilmez; uygulama öğrenmek için tasarlanmıştır.

## Telif ve kullanım

© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır. Ayrıntılar için
`LICENSE` dosyasına bakın.

İletişim ve izin talepleri: dilsat.yegenoglu@cbu.edu.tr
