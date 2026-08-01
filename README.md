# yzta-bootcamp-19

---

## Team Members

| Name | Role | Social |
|:-------:|:-----:|:--------:|
| Bilal Solmaz | Product Owner | |
| Kübra Güler | Scrum Master | [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20"/>](https://github.com/kkbradd) [<img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" width="20"/>](https://www.linkedin.com/in/kubradguler/) |
| Saadettin Berber | Developer | [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20"/>](https://github.com/saadettinBerber) |
| Özlem Çal | Developer | [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20"/>](https://github.com/zcallz) |
| Pınar Akdoğan | Developer | |

---

<details>
  <summary><h2>Product Description</h2></summary>

Our project focuses on Public Transportation Systems. Images obtained from cameras placed on vehicles and at stops are analyzed using image processing techniques to detect density levels. This enables real-time determination of congestion at the vehicle, route, and stop level — transforming the current static public transportation structure into a more dynamic, data-driven system.

The results of the image analysis are planned to be presented through an admin panel so that managers can easily monitor and use them in decision-making processes. The core goal is to collect the data produced by the analysis and display it with meaningful visuals on the admin panel. In future stages, various analyses, integrations, and additional features are envisioned. However, the primary focus at this stage is to build a robust admin panel infrastructure where data can be presented in a clear, manageable, and effective way.

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

Projemiz, Toplu Taşıma Sistemleri üzerine odaklanmaktadır. Araçlar ve duraklara yerleştirilen kameralardan elde edilen görüntüler, görüntü işleme teknikleri kullanılarak analiz edilerek yoğunluk tespiti yapılması hedeflenmektedir. Bu sayede araç, hat ve durak bazlı yoğunluklar anlık olarak belirlenebilecek; mevcut statik toplu taşıma yapısı daha dinamik ve veriye dayalı bir sisteme dönüştürülebilecektir.

Elde edilen görüntü analiz sonuçlarının, yöneticilerin kolayca takip edebilmesi ve karar süreçlerinde kullanabilmesi için bir admin panel üzerinden sunulması planlanmaktadır. Bu kapsamda, analiz sonucu oluşan verilerin alınması ve anlamlı görsellerle admin panelde gösterilmesi hedeflenmektedir. İlerleyen aşamalarda farklı analizler, çeşitli eklentiler ve geliştirme fikirleri de hayata geçirilmesi düşünülmektedir. Ancak başlangıç aşamasında, verinin anlaşılır, yönetilebilir ve etkili bir şekilde sunulabileceği güçlü bir yönetim paneli altyapısının oluşturulması temel önceliğimizdir.

</details>

</details>

---

<details>
  <summary><h2>Product Features</h2></summary>

- Real-time density detection from camera feeds on vehicles and stops
- Monitoring congestion by vehicle, route, and stop on the admin panel
- Visualization of density data through charts and tables
- Access to historical data and reporting

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Araç ve duraklardaki kameralardan anlık yoğunluk tespiti
- Araç, hat ve durak bazlı yoğunlukların admin panelde izlenmesi
- Yoğunluk verilerinin grafik ve tablolarla görselleştirilmesi
- Geçmiş verilere erişim ve raporlama

</details>

</details>

---

<details>
  <summary><h2>Target Audience</h2></summary>

- **Municipalities and Public Transportation Operators** — managers responsible for route and vehicle management
- **Transportation Planning Departments** — teams that conduct data analysis and optimize transit systems
- **Public Transportation Passengers** — who benefit indirectly from a more efficient and data-driven system

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- **Belediyeler ve Toplu Taşıma İşletmecileri** — hat ve araç yönetiminden sorumlu yöneticiler
- **Ulaşım Planlama Departmanları** — veri analizi yapan ve toplu taşıma sistemlerini optimize eden ekipler
- **Toplu Taşıma Yolcuları** — daha verimli ve veriye dayalı bir sistemden dolaylı olarak faydalananlar

</details>

</details>

---

<details>
  <summary><h2>YOTAY Asistan (Chatbot)</h2></summary>

Yoğunluk verileriyle konuşan, varsayılan olarak tamamen lokal chatbot servisi:
sorular OpenJarvis orkestrasyonuyla lokal LLM'e (Ollama, qwen3.5:0.8b) gider; asistan
gerçek hat/araç verisini backend API'sinden tool çağrılarıyla çekip Türkçe cevaplar.
Varsayılan kurulumda hiçbir veri makineden çıkmaz. Tek komutla çalıştırma:

```bash
docker compose --profile demo up --build
# Panel: http://localhost:3000 — sağ alttaki 💬 düğmesi sohbeti açar.
# Deneme ekranı: http://localhost:3000/#asistan (oturum gerektirmez)

# Ya da doğrudan API'den:
curl -X POST localhost:8100/chat -H "Content-Type: application/json" \
     -d '{"mesaj": "Şu an hatlarda yoğunluk nasıl?"}'
```

**Ekip içi deneme ekranı** (`/#asistan`): panelden bağımsız, oturum istemeyen bir test
alanı. **İki sekmesi** var:

- **💬 Sohbet** — normal chatbot görünümü. Her cevabın altında çağrılan tool'lar, model
  ve süre görünür. Tool çağrılmadan gelen cevaplar *"araç kullanılmadı — doğrulanmadı"*
  diye işaretlenir: küçük model alakasız sorularda tool çağırmadan uydurabiliyor.
- **📡 EventBus** — OpenJarvis'in yayınladığı **tüm** olayların canlı akışı. Zaman
  damgalı, filtresiz: modelin tool çağırma kararı (`inference_end.tool_calls`), hangi
  argümanlarla çağırdığı, tool'un ham çıktısı, token sayıları, her adımın süresi.

Akış SSE ile canlı gelir (`POST /chat/akis`) — model düşünürken adımlar anında görünür,
sonda topluca değil. Tool çağırma davranışı prompt'a duyarlı olduğu için takım
arkadaşları değişikliklerin etkisini burada gözleyebilir.

```bash
# SSE ucunu doğrudan denemek için:
curl -N -X POST localhost:8100/chat/akis -H "Content-Type: application/json" \
     -d '{"mesaj":"Su an en yogun hat hangisi?"}'
```

**Model seçimi:** Ekranın üstünden model değiştirilebilir. Varsayılan `qwen3.5:0.8b`
konteyner açılışında indirilir ve hemen kullanıma hazırdır; daha büyük modeller
listelenir ama **yalnız istendiğinde** indirilir (`indir` düğmesi, birkaç dakika sürer).
İndirilen modeller `ollama_modelleri` volume'unda kalıcıdır — bir kez indirilen model
sonraki açılışlarda hazırdır.

| Model | Boyut | Durum |
|-------|-------|-------|
| `qwen3.5:0.8b` | ~1 GB | Varsayılan, açılışta indirilir |
| `qwen3.5:1.7b` | ~1.4 GB | İstendiğinde indirilir |
| `qwen3.5:4b` | ~2.6 GB | İstendiğinde indirilir |
| `llama3.2:3b` | ~2 GB | İstendiğinde indirilir |

> Model listesi bilinçli olarak küçük tutuldu: 8B üstü modeller CPU'da tool çağırmayı
> dakikalar süren bir işe çeviriyor. Servis yalnız bu listedeki adları kabul eder —
> serbest model adı keyfi indirme tetikleyebilirdi.

**Asistanın araçları:**

| Tool | Ne yapar | Kaynak |
|------|----------|--------|
| `hat_yogunluklari` | Tüm hatların anlık doluluğu | Backend REST |
| `hat_anlik_durum` | Bir hattaki araçların durumu | Backend REST |
| `hat_trend` | Hattın saatlik seyri | Backend REST |
| `yogunluk_tahmini` | Hava + saat ile doluluk tahmini | Yerel joblib modeli |

> `yogunluk_tahmini` bir **demo modelidir**: sentetik veriyle eğitilmiştir (gerçek
> veride hava/saat ↔ doluluk ilişkisi bulunamamış, R²~0). Tool çıktısı bu yüzden her
> zaman "tahmindir, gerçek ölçüm değildir" notu taşır. Model dosyası yoksa asistan
> diğer üç araçla çalışmaya devam eder.

Cevap kalitesi yetmezse opsiyonel olarak Gemini'ye geçilebilir (`ASISTAN_MOTOR=cloud`
+ `GEMINI_API_KEY`); bu modda veriler Google'a gider, bkz.
[asistan/README.md](asistan/README.md#gemini-ile-çalıştırma-opsiyonel).

Ayrıntılar: [asistan/README.md](asistan/README.md)

</details>

---

<details>
  <summary><h2>Veri Metodolojisi</h2></summary>

Sistemdeki sayılar tahminle değil ölçümle belirlendi. İki ayrı kalibrasyon var:

**1. Mock yoğunluk eğrisi — İBB açık verisinden.** Demo verisinin saatlik doluluk
çarpanları uydurulmadı; [İBB Saatlik Toplu Ulaşım Veri Seti](https://data.ibb.gov.tr/dataset/hourly-public-transport-data-set)
(BELBİM akbil işlemleri) indirilip 5 tam iş günü (Ekim 2024) ve bir Pazar (Eylül 2024)
üzerinden **171.438 Üsküdar binişi** toplulaştırıldı.

Veriden çıkan üç bulgu tasarımı doğrudan etkiledi:

- **07:00 günün en yoğun saati** (Üsküdar binişlerinin %9.6'sı) — sabah zirvesi keskin
- **Akşam 15:00–18:00 bir plato**, sivri tepe değil; saat başına daha az yoğun ama
  toplamda sabah zirvesinden **daha fazla yolcu** taşıyor
- **Hafta sonu "ölçeklenmiş iş günü" değil**: Pazar toplamı iş gününün ~%45'i ama
  sabah zirvesi **tamamen kayboluyor** (07:00'de 0.18 ↔ 1.15, ~6 kat fark)

**2. CSRNet sayım ölçeği — elle sayımla.** Demo videosunun 45 saniyesinin her biri elle
sayılıp modelin ham çıktısıyla karşılaştırıldı:

| Ölçüt | Değer |
|---|---|
| Korelasyon (ham ↔ gerçek) | **0.88** |
| MAE, çarpansız → kalibre | 1.64 → **1.06 kişi** |
| `EDGE_SAYIM_CARPANI` | **0.78** |

Model insan sayısındaki *değişimi* doğru takip ediyor; yalnız ölçeği kayıktı.

> Tam yöntem, seçilen günler, uygulanan düzeltmeler ve **bilinen sınırlar** (zirve
> değeri 1.15 ölçülmüş bir doluluk değil, kalibre edilmiş bir seçimdir; hafta sonu
> eğrisi tek bir Pazara dayanır):
> **[docs/veri-metodolojisi.md](docs/veri-metodolojisi.md)**

</details>

---

![Sprint 1](assets/sprint1/Spr%C4%B1nt%201.png)

<details>
  <summary><h1>Sprint 1</h1></summary>

---

  <details>
    <summary><h2>Product Screenshot</h2></summary>

- Camera feeds from vehicles and stops are processed on-device by CSRNet, which converts images into crowd density counts — no images leave the vehicle.
- Count data is transmitted to the central server via MQTT over 4G, enriched with vehicle and route context, then stored in PostgreSQL and cached in Redis for real-time access.
- The admin panel displays live congestion levels by vehicle, route, and stop through a React-based dashboard powered by WebSocket.

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Araç ve duraklardaki kamera görüntüleri, CSRNet modeli tarafından cihaz üzerinde işlenerek kalabalık yoğunluk sayılarına dönüştürülür — hiçbir görüntü araçtan çıkmaz.
- Sayım verisi, MQTT protokolüyle 4G üzerinden merkez sunucuya iletilir; araç ve hat bilgileriyle zenginleştirilerek PostgreSQL'e kaydedilir ve anlık erişim için Redis'e önbelleğe alınır.
- Admin panel, WebSocket destekli React tabanlı gösterge panosu aracılığıyla araç, hat ve durak bazlı anlık yoğunluk seviyelerini görüntüler.

</details>

![Otobüs](assets/sprint1/otobus.png)
![Otobüs 2](assets/sprint1/otobus2.png)
![Akış](assets/sprint1/akis.png)

  </details>

---

  <details>
    <summary><h2>Sprint Board Update</h2></summary>

![Sprint Board 1](assets/sprint1/Ekran%20Resmi%202026-06-28%2023.01.25.png)
![Sprint Board 2](assets/sprint1/Ekran%20Resmi%202026-07-05%2015.07.10.png)

  </details>

---

  <details>
    <summary><h2>Daily Scrum</h2></summary>

![Daily Scrum 1](assets/sprint1/Ekran%20Resmi%202026-06-28%2020.28.12%20(2).png)
![Daily Scrum 2](assets/sprint1/Ekran%20Resmi%202026-07-05%2015.09.52.png)
![Daily Scrum 3](assets/sprint1/Ekran%20Resmi%202026-07-05%2015.10.03.png)

  </details>

---

  <details>
    <summary><h2>Sprint Notes</h2></summary>

- It was decided to use _Trello_ for project management.
- Daily scrum meetings were held via _WhatsApp_ and _Google Meet_ according to team availability.
- It was decided to use _Python_ for the image processing model, and _CSRNet_ was selected as the density estimation model.
- It was decided to use _Firebase_ for the backend.
- It was decided to focus on research and planning in the first sprint.

- **Expected point completion within Sprint:** 200 points

- **Point Completion Logic:** A total target of 1000 points was set. In Sprint 1, 200 points were targeted and completed as the focus was on research and planning. In Sprint 2, 400 points are targeted as the development phase begins. In Sprint 3, 400 points are targeted for the remaining development and integration work.

- **Product Backlog URL:** [Click for Backlog](https://trello.com/b/2BtcZtM4/yzta-bootcamp)

- **Story Selection:**

![Story Selection](assets/sprint1/Ekran%20Resmi%202026-07-06%2013.15.28.png)

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Proje yönetimi için _Trello_ kullanılmasına karar verildi.
- Daily scrum toplantıları, takım müsaitlik durumuna göre _WhatsApp_ ve _Google Meet_ üzerinden gerçekleştirildi.
- Görüntü işleme modeli için _Python_ kullanılmasına karar verildi ve yoğunluk tahmin modeli olarak _CSRNet_ seçildi.
- Backend için _Firebase_ kullanılmasına karar verildi.
- İlk sprintte araştırma ve planlamaya odaklanılmasına karar verildi.

- **Sprint İçinde Tamamlanması Beklenen Puan:** 200 puan

- **Puan Tamamlama Mantığı:** Toplam hedef 1000 puan olarak belirlenmiştir. Sprint 1'de araştırma ve planlama odaklı çalışıldığı için 200 puan hedeflenmiş ve tamamlanmıştır. Sprint 2'de geliştirme aşamasına geçileceğinden 400 puan, Sprint 3'te kalan geliştirme ve entegrasyon çalışmaları için 400 puan hedeflenmiştir.

- **Product Backlog URL:** [Backlog için tıklayın](https://trello.com/b/2BtcZtM4/yzta-bootcamp)

- **Story Seçimi:**

![Story Selection](assets/sprint1/Ekran%20Resmi%202026-07-06%2013.15.28.png)

</details>

  </details>

---

  <details>
    <summary><h2>Sprint Review</h2></summary>

- Research on which data sources and models to use was conducted and discussed as a team.
- CSRNet was selected as the density estimation model after evaluation.
- Technology stack decisions were made collectively (Python, Firebase, Trello).
- The possibility of presenting insights via multi-agent systems was discussed and agreed upon as a future direction.
- Features and enhancements expected to be added in upcoming sprints were identified and planned.

- **Sprint Review Participants:** Bilal Solmaz, Kübra Güler, Saadettin Berber, Özlem Çal, Pınar Akdoğan

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Hangi veri kaynaklarının ve modellerin kullanılacağına dair araştırma yapıldı ve ekip içinde tartışıldı.
- Yoğunluk tahmini modeli olarak CSRNet değerlendirmeler sonucunda seçildi.
- Teknoloji yığını kararları ekip olarak ortaklaşa alındı (Python, Firebase, Trello).
- Multi-agent sistemler aracılığıyla içgörüler sunulabileceği tartışıldı ve gelecek bir hedef olarak benimsendi.
- İlerleyen sprintlerde eklenmesi beklenen özellikler ve geliştirmeler belirlendi ve planlandı.

- **Sprint Review Katılımcıları:** Bilal Solmaz, Kübra Güler, Saadettin Berber, Özlem Çal, Pınar Akdoğan

</details>

  </details>

---

  <details>
    <summary><h2>Sprint Retrospective</h2></summary>

- Task distribution within the team and individual assignments will be clarified at the beginning of the second sprint.
- In the second sprint, the development phase will begin; admin panel UI setup and image processing model implementation will be initiated.
- Firebase integration (backend deploy) will be set up in the second sprint.
- Work on Authentication for the admin panel will begin.
- Data logging API development will be started.
- Live density map UI and Heatmap UI implementation will be planned.
- Frontend and backend deploy preparations will be made.
- Model Training and Model Evaluation (acc, mAP, loss) processes will be initiated.
- Research on KPIs that can be added via AI Agent will continue.

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Takım içindeki görev dağılımı ve her üyenin görev ataması ikinci sprint başlangıcıyla birlikte netleştirilecektir.
- İkinci sprintte geliştirme aşamasına geçilecek; admin panel arayüzü kurulumu ve görüntü işleme modeli implementasyonuna başlanacaktır.
- Firebase entegrasyonu (backend deploy) ikinci sprintte kurulacaktır.
- Admin panel için Authentication çalışmalarına başlanacaktır.
- Data logging API geliştirmesi başlatılacaktır.
- Live density map UI ve Heatmap UI implementasyonu planlanacaktır.
- Frontend ve backend deploy hazırlıkları yapılacaktır.
- Model Training ve Model Evaluation (acc, mAP, loss) süreçleri başlatılacaktır.
- AI Agent ile eklenebilecek KPI'ların araştırılmasına devam edilecektir.

</details>

  </details>

</details>

---

![Sprint 2](assets/sprint1/Spr%C4%B1nt%202.png)

<details>
  <summary><h1>Sprint 2</h1></summary>

---

  <details>
    <summary><h2>Product Screenshot</h2></summary>

- The backend (FastAPI + PostgreSQL + Redis + MQTT) was deployed with a full hexagonal architecture: ingest, real-time state, REST API, and WebSocket broadcast were all implemented and tested end-to-end.
- The admin panel (React) was built with a login page, dashboard, live map, lines, and stops pages, connected to the backend via REST and WebSocket.
- An AI recommendation engine was added: a weekly-pattern detector (30-day window) produces operational suggestions, and a live-alert detector (3-hour window) flags currently congested lines — both interpreted by an LLM (Gemini or a local Ollama model).
- A local chatbot assistant (OpenJarvis + Ollama) was integrated into the panel, answering density questions by calling the backend API directly — no data leaves the machine by default.
- The CSRNet crowd-density model was run locally/on Kaggle against real bus/road footage, producing a density heatmap and a people-count estimate per frame.
- The trained model was evaluated against ground-truth counts on labeled crowd images to measure estimation error.
- A dedicated test dataset was built from bus interior video frames, manually labeled with the person count per frame, to validate the density pipeline end-to-end.

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Backend (FastAPI + PostgreSQL + Redis + MQTT) tam heksagonal mimariyle deploy edildi: veri alımı, anlık durum, REST API ve WebSocket yayını uçtan uca geliştirilip test edildi.
- Admin panel (React) giriş, gösterge paneli, canlı harita, hatlar ve duraklar sayfalarıyla kuruldu; REST ve WebSocket üzerinden backend'e bağlandı.
- Bir AI öneri motoru eklendi: haftalık örüntü tespiti (30 günlük pencere) operasyonel öneriler üretiyor, anlık uyarı tespiti (3 saatlik pencere) o an yoğun olan hatları işaretliyor — ikisi de bir LLM (Gemini veya lokal Ollama modeli) tarafından yorumlanıyor.
- Panele lokal bir chatbot asistanı (OpenJarvis + Ollama) entegre edildi; yoğunluk sorularını doğrudan backend API'sini çağırarak yanıtlıyor — varsayılan kurulumda hiçbir veri makineden çıkmıyor.
- CSRNet kalabalık yoğunluğu modeli lokal/Kaggle üzerinde gerçek otobüs/yol görüntülerine karşı çalıştırılarak yoğunluk ısı haritası ve kare başına kişi sayısı tahmini üretildi.
- Eğitilmiş model, etiketlenmiş kalabalık görüntüleri üzerinde gerçek (ground-truth) sayımlarla karşılaştırılarak tahmin hatası ölçüldü.
- Yoğunluk hattını uçtan uca doğrulamak için otobüs içi video karelerinden, kare başına kişi sayısı manuel olarak etiketlenmiş özel bir test veri seti oluşturuldu.

</details>

![Login](assets/sprint2/01-giris.png)
![Dashboard](assets/sprint2/02-panel.png)
![Asistana Soru Sorma](assets/sprint2/03-asistan-soru.png)
![Asistan Cevabı](assets/sprint2/04-asistan-cevap.png)
![Hatlar](assets/sprint2/lines.png)
![Canlı Harita](assets/sprint2/live-map.png)
![Duraklar](assets/sprint2/stops.png)
![CSRNet Yoğunluk Haritası](assets/sprint2/05-csrnet-yogunluk-haritasi.jpeg)
![CSRNet Model Değerlendirme](assets/sprint2/06-csrnet-model-degerlendirme.jpeg)
![Test Veri Seti](assets/sprint2/07-test-veri-seti.jpeg)

  </details>

---

  <details>
    <summary><h2>AI Motoru Kanıtları (Local, Ollama)</h2></summary>

Backend'in `AI_MOTOR=local` modunda, hiçbir veri makineden çıkmadan Ollama üzerinde çalışan `turkish-gemma-9b-v0.1` modeliyle ürettiği gerçek öneri/uyarı çıktıları:

```text
===================================================================
 YOTAY — YEREL AI MOTORU (OpenJarvis SimpleAgent + Ollama)
 Kanit loglari — 18.07.2026 17:35
===================================================================

### 1) Motor yapilandirmasi (veri makineden cikmiyor)
    local
    http://localhost:11434
    alibayram/turkish-gemma-9b-v0.1:latest

### 2) Servis sagligi
    {
        "durum": "ok",
        "bagimliliklar": {
            "postgres": "ok",
            "redis": "ok",
            "mqtt": "ok"
        }
    }

### 3) Yerel model ile URETILEN ONERILER (Ollama, internet yok)
    [
        {
            "id": 3,
            "hat_id": 1,
            "gun_no": 1,
            "saat_baslangic": 8,
            "saat_bitis": 9,
            "ortalama_doluluk": 0.8829861111111109,
            "karsilastirma_ortalama_doluluk": 0.4018634259259261,
            "oneri_metni": "Pazartesi sabah 8'de sefer sayısını artırmayı düşünün",
            "gerekce": "Ortalama doluluk oranı (0.88) diğer günlere göre belirgin şekilde yüksek.",
            "olusturulma_zamani": "2026-07-18T14:29:03.821817Z"
        },
        {
            "id": 4,
            "hat_id": 1,
            "gun_no": 1,
            "saat_baslangic": 9,
            "saat_bitis": 10,
            "ortalama_doluluk": 0.8673611111111111,
            "karsilastirma_ortalama_doluluk": 0.40239583333333345,
            "oneri_metni": "Pazartesi sabah 9'da sefer sayısını artırmayı düşünün",
            "gerekce": "Ortalama doluluk oranı (0.87) diğer günlere göre belirgin şekilde yüksek.",
            "olusturulma_zamani": "2026-07-18T14:29:03.821817Z"
        },
        {
            "id": 1,
            "hat_id": 1,
            "gun_no": 1,
            "saat_baslangic": 8,
            "saat_bitis": 8,
            "ortalama_doluluk": 0.8829861111111109,
            "karsilastirma_ortalama_doluluk": 0.4018634259259261,
            "oneri_metni": "Pazartesi sabahı 08:00 seferlerinde doluluk oranının yüksek olduğu gözlemlenmiştir. Trafik yoğunluğunu azaltmak için ek araç veya daha sık sefer periyotunu değerlendirin.",
            "gerekce": "Doluluk oranı (0.88) diğer günlere kıyasla belirgin şekilde yüksektir.",
            "olusturulma_zamani": "2026-07-18T13:37:06.532671Z"
        },
        {
            "id": 2,
            "hat_id": 1,
            "gun_no": 1,
            "saat_baslangic": 9,
            "saat_bitis": 9,
            "ortalama_doluluk": 0.8673611111111111,
            "karsilastirma_ortalama_doluluk": 0.40239583333333345,
            "oneri_metni": "Pazartesi sabahı 09:00 seferlerinde doluluk oranının yüksek olduğu gözlemlenmiştir. Trafik yoğunluğunu azaltmak için ek araç veya daha sık sefer periyotunu değerlendirin.",
            "gerekce": "Doluluk oranı (0.87) diğer günlere kıyasla belirgin şekilde yüksektir.",
            "olusturulma_zamani": "2026-07-18T13:37:06.532671Z"
        }
    ]

### 4) Yerel model ile URETILEN UYARILAR
    [
        {
            "id": 1,
            "hat_id": 3,
            "ortalama_doluluk": 1.5271604938271603,
            "ortalama_kisi": 45.81481481481482,
            "uyari_metni": "Yoğunluk eşiği aşılmıştır. Ek sefer değerlendirilebilir.",
            "gerekce": "Ortalama doluluk oranı %152.7 olarak ölçülmüştür.",
            "olusturulma_zamani": "2026-07-18T14:30:36.843826Z"
        }
    ]
```

  </details>

---

  <details>
    <summary><h2>Sprint Board Update</h2></summary>

![Sprint 2 Burndown Chart](assets/sprint2/burndown-chart.png)
![Trello Board](assets/sprint2/08-trello-board.png)
![Trello Board (Güncel)](assets/sprint2/09-trello-board-guncel.png)

  </details>

---

  <details>
    <summary><h2>Daily Scrum</h2></summary>

![Daily Meet](assets/sprint2/10-daily-meet.png)
![WhatsApp — Veri Seti Koordinasyonu](assets/sprint2/11-whatsapp-veri-seti.png)
![WhatsApp — Görev Koordinasyonu](assets/sprint2/12-whatsapp-koordinasyon.png)
![WhatsApp — Model Sonuçları](assets/sprint2/13-whatsapp-model-sonuclari.png)
![WhatsApp — PR Koordinasyonu](assets/sprint2/14-whatsapp-pr-koordinasyon.png)

  </details>

---

  <details>
    <summary><h2>Sprint Notes</h2></summary>

- It was decided to develop the backend with a hexagonal (ports & adapters) architecture on FastAPI, PostgreSQL, Redis, and MQTT, and to deploy it before connecting the frontend.
- It was decided to build the admin panel with React first (login, dashboard, live map, lines, stops) and connect it to the backend incrementally, screen by screen, via REST and WebSocket.
- It was decided to make CORS configurable and add JWT-based authentication so the panel could safely and securely call the backend across origins.
- It was decided to run the CSRNet crowd-density model locally and on Kaggle against real footage, then formally evaluate it (accuracy, mAP, loss / MAE) against labeled data before trusting its output.
- It was decided to build a dedicated test dataset from real bus-interior video frames, with the person count per frame labeled manually, instead of relying only on generic public datasets.
- It was decided to research a fully local LLM option (OpenJarvis on Ollama) so AI features would not require sending data to an external cloud provider by default.
- It was decided to add an AI recommendation/alert engine directly inside the backend (weekly-pattern suggestions + 3-hour anomaly alerts), interpreted by an LLM behind a provider-agnostic port.
- It was decided to build a separate interactive chatbot assistant on top of the same local-first principle, reading live data from the backend via tool calls, with an optional cloud (Gemini) fallback documented clearly for lower-quality-answer cases.
- It was decided to containerize the whole stack (panel + backend + assistant + local LLM + database + broker) behind a single root-level `docker-compose.yml`, so the entire system can be started with one command.
- It was decided to keep the GitHub Pages documentation (architecture, API/MQTT contracts, AI engine, assistant) up to date as each piece of the system was built.

- **Expected point completion within Sprint:** 400 points

- **Point Completion Logic:** A total target of 1000 points was set. In Sprint 1, 200 points were targeted and completed as the focus was on research and planning. In Sprint 2, 400 points were targeted as the development phase began; all 15 backlog stories tracked on the burndown chart were completed within the 14-day window, bringing the remaining points to 0 by Day 14. In Sprint 3, 400 points are targeted for the remaining development and integration work.

- **Product Backlog URL:** [Click for Backlog](https://trello.com/b/2BtcZtM4/yzta-bootcamp)

- **Story Selection:**

![Sprint 2 Burndown Chart](assets/sprint2/burndown-chart.png)

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Backend'in FastAPI, PostgreSQL, Redis ve MQTT üzerinde heksagonal (port & adaptör) mimariyle geliştirilmesine ve frontend bağlanmadan önce deploy edilmesine karar verildi.
- Admin panelin önce React ile kurulmasına (giriş, gösterge paneli, canlı harita, hatlar, duraklar) ve REST/WebSocket üzerinden ekran ekran, aşamalı olarak gerçek backend'e bağlanmasına karar verildi.
- Panel farklı origin'lerden backend'i güvenle çağırabilsin diye CORS'un yapılandırılabilir hale getirilmesine ve JWT tabanlı kimlik doğrulama eklenmesine karar verildi.
- CSRNet kalabalık yoğunluğu modelinin lokal ve Kaggle üzerinde gerçek görüntülere karşı çalıştırılmasına, ardından çıktısına güvenmeden önce etiketlenmiş veriyle biçimsel olarak değerlendirilmesine (doğruluk, mAP, loss / MAE) karar verildi.
- Yalnızca genel amaçlı halka açık veri setlerine güvenmek yerine, otobüs içi gerçek video karelerinden, kare başına kişi sayısı manuel etiketlenmiş özel bir test veri seti oluşturulmasına karar verildi.
- AI özelliklerinin varsayılan olarak veriyi dış bir bulut sağlayıcısına göndermek zorunda kalmaması için tamamen lokal bir LLM seçeneğinin (OpenJarvis + Ollama) araştırılmasına karar verildi.
- Backend içine doğrudan bir AI öneri/uyarı motoru (haftalık örüntü önerileri + 3 saatlik anomali uyarıları) eklenmesine, bunun sağlayıcıdan bağımsız bir port arkasında bir LLM tarafından yorumlanmasına karar verildi.
- Aynı "önce lokal" ilkesinin üzerine, backend'den tool çağrılarıyla canlı veri okuyan ayrı, etkileşimli bir chatbot asistanı geliştirilmesine; cevap kalitesinin düştüğü durumlar için açıkça belgelenmiş opsiyonel bir bulut (Gemini) yedeğinin eklenmesine karar verildi.
- Tüm sistemin (panel + backend + asistan + lokal LLM + veritabanı + broker) tek bir kök `docker-compose.yml` arkasında konteynerlenmesine, böylece tüm sistemin tek komutla başlatılabilmesine karar verildi.
- Sistemin her parçası geliştirildikçe GitHub Pages dokümantasyonunun (mimari, API/MQTT sözleşmeleri, AI motoru, asistan) güncel tutulmasına karar verildi.

- **Sprint İçinde Tamamlanması Beklenen Puan:** 400 puan

- **Puan Tamamlama Mantığı:** Toplam hedef 1000 puan olarak belirlenmiştir. Sprint 1'de araştırma ve planlama odaklı çalışıldığı için 200 puan hedeflenmiş ve tamamlanmıştır. Sprint 2'de geliştirme aşamasına 400 puan hedefiyle geçilmiş; burndown chart'ta takip edilen 15 backlog story'nin tamamı 14 günlük pencerede tamamlanarak kalan puan 14. günde 0'a indirilmiştir. Sprint 3'te kalan geliştirme ve entegrasyon çalışmaları için 400 puan hedeflenmiştir.

- **Product Backlog URL:** [Backlog için tıklayın](https://trello.com/b/2BtcZtM4/yzta-bootcamp)

- **Story Seçimi:**

![Sprint 2 Burndown Chart](assets/sprint2/burndown-chart.png)

</details>

### Sistemi Çalıştırma / Running the System

**1) Tek komutla tüm sistem (önerilen) — Docker Compose**

```bash
# Kök dizinden: panel + backend + asistan + lokal LLM (Ollama) + PostgreSQL + Redis + MQTT
docker compose up --build

# Tohum veriyle birlikte canlı sahte veri akışı (simülatör) da istenirse:
docker compose --profile demo up --build
```

- Panel: `http://localhost:3000` (sağ altta asistan sohbeti)
- Backend API: `http://localhost:8000` (`/docs` altında Swagger arayüzü)
- Asistan servisi: `http://localhost:8100`
- İlk açılışta hem asistan hem backend'in lokal AI motoru, kullandıkları Ollama modellerini (`qwen3.5:0.8b` ~1 GB, öneri/uyarı motoru için ayrıca `YEREL_MODEL`) indirir; modeller kalıcı bir volume'da kalır, sonraki açılışlar beklemesizdir.
- Backend'deki AI Önerileri (30 günlük örüntü) ve Son Uyarılar (3 saatlik anlık) motorları varsayılan olarak `AI_MOTOR=local` ile tamamen lokal çalışır; container her açıldığında zamanlamayı beklemeden bir kez otomatik tetiklenir.
- Opsiyonel bulut motoruna (Gemini) geçmek için kök dizine bir `.env` dosyası eklenip `GEMINI_API_KEY` tanımlanabilir; asistan için `ASISTAN_MOTOR=cloud`, backend AI motoru için `AI_MOTOR=gemini` ayarlanır — bkz. `asistan/README.md` ve `backend/README.md`. `.env` `.gitignore`'da olduğu için anahtar hiçbir zaman repoya girmez.

**2) Sadece backend — Docker**

```bash
cd backend
docker compose up --build -d
python -m app.seed   # tek seferlik: örnek hat/araç/cihaz verisi
```

- Backend: `http://localhost:8000`
- Testler: `uv run pytest tests/unit` (birim), `uv run pytest tests/entegrasyon` (entegrasyon, çalışan bir stack gerektirir)
- Python projelerinde `export UV_LOCKED=1` önerilir: `uv run` kilidi sessizce
  güncellemek yerine uyuşmazlıkta hata verir (bkz. `backend/README.md`)

**3) Sadece frontend — geliştirme (Vite dev server)**

```bash
cd frontend
npm install
npm run dev
```

- Panel: `http://localhost:5173` (backend'in `http://localhost:8000`'de ayakta olması beklenir)
- Üretim build'i: `npm run build` (çıktı `dist/`), ya da `docker compose up --build` ile Nginx üzerinden konteynerli servis

**Gereksinimler:** Docker Desktop (Compose dahil), Node.js 18+ (yalnızca frontend'i Docker dışında çalıştırmak için), Python 3.12 + `uv` (yalnızca backend'i Docker dışında çalıştırmak için). Lokal AI motorları için Ollama'nın indireceği modeller birkaç GB yer kaplayabilir; Docker Desktop'a ayrılan bellek limitinin en az 8 GB olması önerilir.

  </details>

---

  <details>
    <summary><h2>Sprint Review</h2></summary>

- The backend was deployed end-to-end with a fully test-covered hexagonal architecture: MQTT ingest, Redis live state, REST API, and WebSocket broadcast were all implemented, wired together in a composition root, and validated with unit and integration tests.
- JWT-based authentication was added to the backend and wired into the panel's login flow, so only authorized operators can reach the dashboard.
- Configurable CORS middleware was added so the panel (served from a different origin/port) could safely call the backend without hardcoded exceptions.
- The admin panel frontend was built out with React across five core screens — login, dashboard (with an interactive passenger density chart), live map, lines, and stops — and connected to the real backend via REST and WebSocket instead of static mock data.
- An AI recommendation/alert engine was designed and implemented directly inside the backend using the existing hexagonal ports/adapters: a 30-day weekly-pattern SQL query feeds the "AI Suggestions" flow, and a 3-hour anomaly query feeds the "Recent Alerts" flow, both interpreted by an LLM behind the same port.
- The AI engine was made provider-agnostic: it initially supported Gemini, then a fully local Ollama-based generator (OpenJarvis SimpleAgent) was added behind the same port so the system can run with zero data leaving the machine; the active engine is now selected via a single `AI_MOTOR` setting.
- A separate local chatbot assistant (OpenJarvis on Ollama) was researched and built as its own service, answering operator questions by calling the backend's REST endpoints as tools; an optional cloud (Gemini) engine was added afterwards for cases where the local model's answer quality is insufficient, with a clear privacy warning documented for that mode.
- The CSRNet crowd-density model was run locally and on Kaggle against real bus/road footage, producing density heatmaps and per-frame people-count estimates.
- The trained CSRNet model was evaluated against ground-truth counts on labeled crowd images (including the ShanghaiTech dataset) to measure estimation error (MAE, min/max/median error).
- A dedicated test dataset was built from real bus-interior video frames, manually labeled with the person count per frame, to validate the density pipeline end-to-end under realistic conditions.
- The frontend was containerized with a production Nginx service, and a root-level `docker-compose.yml` was added so the entire stack (panel + backend + assistant + local LLM + database + broker) can be started with a single command.
- GitHub Pages documentation was significantly expanded to keep the project log in sync with the fast pace of development: architecture, API/MQTT contracts, the AI engine, and the assistant service were all documented.
- Two independently developed AI workstreams (the backend recommendation/alert engine and the separate chatbot assistant) were reconciled and merged into a single, consistent codebase without losing either team member's work.

- **Sprint Review Participants:** Bilal Solmaz, Kübra Güler, Saadettin Berber, Özlem Çal, Pınar Akdoğan

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Backend, tam test kapsamına sahip heksagonal mimariyle uçtan uca deploy edildi: MQTT veri alımı, Redis anlık durum, REST API ve WebSocket yayını geliştirilip bir kompozisyon kökünde birbirine bağlandı, birim ve entegrasyon testleriyle doğrulandı.
- Backend'e JWT tabanlı kimlik doğrulama eklendi ve panelin giriş akışına kablolandı; böylece gösterge paneline yalnızca yetkili operatörler erişebiliyor.
- Panel (farklı origin/port'tan sunulduğu için) backend'i güvenle çağırabilsin diye yapılandırılabilir CORS middleware eklendi, sabit kodlu istisnalara gerek kalmadı.
- Admin panel frontend'i React ile beş temel ekranda (giriş, etkileşimli yolcu yoğunluğu grafiğine sahip gösterge paneli, canlı harita, hatlar, duraklar) hayata geçirildi ve statik mock veri yerine REST ve WebSocket üzerinden gerçek backend'e bağlandı.
- Backend içinde, mevcut heksagonal port/adaptör yapısı kullanılarak doğrudan bir AI öneri/uyarı motoru tasarlanıp geliştirildi: 30 günlük haftalık örüntü SQL sorgusu "AI Önerileri" akışını, 3 saatlik anomali sorgusu "Son Uyarılar" akışını besliyor; ikisi de aynı port arkasında bir LLM tarafından yorumlanıyor.
- AI motoru sağlayıcıdan bağımsız hale getirildi: önce Gemini desteklendi, ardından aynı port arkasında tamamen lokal bir Ollama tabanlı üretici (OpenJarvis SimpleAgent) eklenerek sistemin hiçbir veri makineden çıkmadan çalışabilmesi sağlandı; aktif motor artık tek bir `AI_MOTOR` ayarıyla seçiliyor.
- Ollama üzerinde OpenJarvis tabanlı ayrı bir lokal chatbot asistanı araştırılıp kendi servisi olarak inşa edildi; operatör sorularını backend'in REST uçlarını tool olarak çağırarak yanıtlıyor. Lokal modelin cevap kalitesi yetmediği durumlar için sonradan opsiyonel bir bulut (Gemini) motoru eklendi, bu moda dair açık bir gizlilik uyarısı belgelendi.
- CSRNet kalabalık yoğunluğu modeli lokal ve Kaggle üzerinde gerçek otobüs/yol görüntülerine karşı çalıştırılarak yoğunluk ısı haritaları ve kare başına kişi sayısı tahminleri üretildi.
- Eğitilmiş CSRNet modeli, etiketlenmiş kalabalık görüntüleri (ShanghaiTech veri seti dahil) üzerinde gerçek (ground-truth) sayımlarla karşılaştırılarak tahmin hatası (MAE, min/maks/medyan hata) ölçüldü.
- Yoğunluk hattını gerçekçi koşullar altında uçtan uca doğrulamak için otobüs içi gerçek video karelerinden, kare başına kişi sayısı manuel olarak etiketlenmiş özel bir test veri seti oluşturuldu.
- Frontend, üretim Nginx servisiyle konteynerlenip kök dizine bir `docker-compose.yml` eklendi; böylece tüm sistem (panel + backend + asistan + lokal LLM + veritabanı + broker) tek komutla ayağa kalkabiliyor.
- Proje günlüğünü geliştirmenin hızına ayak uydurarak güncel tutmak için GitHub Pages dokümantasyonu önemli ölçüde genişletildi: mimari, API/MQTT sözleşmeleri, AI motoru ve asistan servisi belgelendi.
- Birbirinden bağımsız geliştirilen iki AI çalışması (backend'deki öneri/uyarı motoru ve ayrı chatbot asistanı) hiçbir takım üyesinin emeği kaybolmadan tek, tutarlı bir kod tabanında birleştirildi.

- **Sprint Review Katılımcıları:** Bilal Solmaz, Kübra Güler, Saadettin Berber, Özlem Çal, Pınar Akdoğan

</details>

  </details>

---

  <details>
    <summary><h2>Sprint Retrospective</h2></summary>

**What went well**

- The hexagonal architecture on the backend paid off directly: swapping and adding LLM providers (Gemini → local Ollama) for the AI recommendation/alert engine required changes only inside the adapter layer, with zero changes to the domain or application logic.
- The single-command, full-stack Docker Compose setup proved its value — it allowed the whole team to run and demo the panel, backend, database, and both AI paths locally without individual environment setup.
- Building a dedicated, manually labeled test dataset from real bus footage gave the team a much more trustworthy CSRNet evaluation than relying on generic public datasets alone.

**What needs improvement**

- The AI recommendation/alert engine and the chatbot assistant were built in parallel by different team members without early alignment on architecture; a merge was needed afterwards to reconcile both into a single source of truth. Earlier coordination on shared modules (LLM provider abstraction, Docker Compose) is planned for Sprint 3.
- Downloading larger local LLM models over an unstable connection caused repeated interruptions and multiple restarts; a fallback to a smaller model, resumable downloads, or a documented retry strategy will be considered going forward.
- The dashboard's "AI Suggestions" and "Recent Alerts" cards were connected to the real backend endpoints only late in the sprint; earlier end-to-end wiring between frontend and backend features is a goal for Sprint 3.

**Planned for Sprint 3**

- A live mapping system will be built to visualize vehicles and stops geographically on the dashboard, replacing the current placeholder map.
- Lines and stops will be added to the database as first-class, manageable records (instead of only seed data), so the admin panel can reflect the real route network.
- The CSRNet model and its evaluated weights will be integrated into the live pipeline, so density detection on vehicles runs as part of the actual data flow — not just as an offline research script.
- The entire system will be moved from mock/demo data to fully live data end-to-end: real camera/edge input through MQTT, through the backend, into the dashboard, recommendations, and alerts.
- Frontend-backend Docker deployment will be finalized and documented as a single, reproducible production flow.
- Automated tests will be added for the frontend (currently backend-only) to keep the growing UI surface safe to change.

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

**İyi giden yönler**

- Backend'deki heksagonal mimari doğrudan karşılığını verdi: AI öneri/uyarı motorunda LLM sağlayıcısını değiştirmek/eklemek (Gemini → lokal Ollama) yalnızca adaptör katmanında değişiklik gerektirdi, domain veya application mantığına hiç dokunulmadı.
- Tek komutla ayağa kalkan tam-stack Docker Compose kurulumu değerini kanıtladı — tüm ekibin panel, backend, veritabanı ve her iki AI yolunu da bireysel ortam kurulumu yapmadan lokal olarak çalıştırıp demo edebilmesini sağladı.
- Gerçek otobüs görüntülerinden manuel etiketlenmiş özel bir test veri seti oluşturmak, yalnızca genel amaçlı halka açık veri setlerine güvenmek yerine ekibe çok daha güvenilir bir CSRNet değerlendirmesi kazandırdı.

**Geliştirilmesi gereken yönler**

- AI öneri/uyarı motoru ile chatbot asistanı, farklı takım üyeleri tarafından mimari üzerinde erken hizalanmadan paralel geliştirildi; sonrasında ikisini tek bir doğru kaynakta birleştirmek için bir merge gerekti. Paylaşılan modüller (LLM sağlayıcı soyutlaması, Docker Compose) üzerinde daha erken koordinasyon Sprint 3 için planlanıyor.
- Kararsız bir bağlantı üzerinden büyük lokal LLM modelleri indirmek tekrar tekrar kesintiye uğradı ve birçok kez yeniden başlatılması gerekti; ileride daha küçük bir modele düşme, devam ettirilebilir indirme ya da belgelenmiş bir yeniden deneme stratejisi değerlendirilecek.
- Gösterge panelindeki "AI Önerileri" ve "Son Uyarılar" kartları gerçek backend uçlarına ancak sprintin geç bir aşamasında bağlandı; frontend ile backend özellikleri arasında daha erken uçtan uca kablolama Sprint 3 için bir hedef.

**Sprint 3 için planlananlar**

- Gösterge panelindeki mevcut yer tutucu haritanın yerine, araçları ve durakları coğrafi olarak görselleştiren canlı bir haritalandırma sistemi kurulacak.
- Hatlar ve duraklar, sadece tohum verisi olarak değil, admin panelin gerçek güzergah ağını yansıtabilmesi için veritabanına yönetilebilir birinci sınıf kayıtlar olarak eklenecek.
- CSRNet modeli ve değerlendirilmiş ağırlıkları canlı akışa entegre edilerek, araçlardaki yoğunluk tespiti çevrimdışı bir araştırma script'i olarak değil, gerçek veri akışının bir parçası olarak çalışacak.
- Tüm sistem, mock/demo veriden uçtan uca tamamen canlı veriye taşınacak: gerçek kamera/uç cihaz girdisinden MQTT üzerinden backend'e, oradan gösterge paneline, önerilere ve uyarılara kadar.
- Frontend-backend Docker deploy'u, tek ve tekrarlanabilir bir üretim akışı olarak sonlandırılıp belgelenecek.
- Büyüyen arayüz yüzeyini güvenle değiştirebilmek için frontend'e de (şu an yalnızca backend'de olan) otomatik testler eklenecek.

</details>

  </details>

</details>

---

![Sprint 3](assets/sprint1/Spr%C4%B1nt%203.png)

<details>
  <summary><h1>Sprint 3</h1></summary>

---

  <details>
    <summary><h2>Product Screenshot</h2></summary>

![Dashboard — Canlı Harita, AI Önerileri, Yolcu Yoğunluğu Trendi](assets/sprint3/Ekran%20Resmi%202026-08-01%2021.07.25.png)
![Dashboard — AI Önerileri ve YOTAY Asistan (gerçek veriyle tool çağrısı)](assets/sprint3/Ekran%20Resmi%202026-08-01%2021.10.05.png)
![Canlı Harita — tüm hatlar, gerçek güzergahlar ve araç konumları](assets/sprint3/Ekran%20Resmi%202026-08-01%2021.15.23.png)
![Hatlar — gerçek hat kodları ve doluluk seviyeleri](assets/sprint3/Ekran%20Resmi%202026-08-01%2021.15.33.png)
![Hat Detayı — 15U güzergahı ve durak akışı](assets/sprint3/Ekran%20Resmi%202026-08-01%2021.15.48.png)
![Canlı Harita — Hat 15 gerçek CSRNet video görüntüsü](assets/sprint3/Ekran%20Resmi%202026-08-01%2021.16.15.png)
![Duraklar — 31 durak ve geçen hatları](assets/sprint3/Ekran%20Resmi%202026-08-01%2021.16.34.png)

  </details>

---

  <details>
    <summary><h2>Sprint Board Update</h2></summary>

![Sprint 3 Burndown Chart](assets/sprint3/Ekran%20Resmi%202026-08-01%2021.05.14.png)
![Trello Board — Done for 3rd Sprint](assets/sprint3/Ekran%20Resmi%202026-08-01%2021.09.04.png)
![Trello Board — Done for 3rd Sprint (devamı) ve Rejected](assets/sprint3/Ekran%20Resmi%202026-08-01%2021.09.17.png)

  </details>

---

  <details>
    <summary><h2>Daily Scrum</h2></summary>

![WhatsApp — Güzergah/Harita ve Backfill Koordinasyonu](assets/sprint3/Ekran%20Resmi%202026-08-01%2020.52.04.png)
![WhatsApp — Model Entegrasyonu Koordinasyonu](assets/sprint3/Ekran%20Resmi%202026-08-01%2020.51.43.png)
![WhatsApp — Proje Teslimi](assets/sprint3/Ekran%20Resmi%202026-08-01%2020.53.09.png)

  </details>

---

  <details>
    <summary><h2>Sprint Notes</h2></summary>

- It was decided to replace the placeholder map with a real OpenStreetMap/Leaflet live map, seeding the database with a realistic Üsküdar-themed route network (10+ lines, real İETT-style stop names) instead of arbitrary mock data.
- It was decided to move vehicle simulation onto the actual route geometry (OSRM-derived polylines), with a backend scheduler advancing each active vehicle along its line so the map reflects real movement instead of static markers.
- It was decided to generate 30 days of historically realistic ridership data (varying trip frequency per line, per-line rush-hour/weekday patterns derived from İBB's public hourly ridership dataset) so the AI recommendation engine would have statistically meaningful patterns to detect, instead of a handful of live-only data points.
- It was decided to make the historical backfill a "sliding window" job that reruns on every `docker compose up`, automatically topping up from the last recorded measurement to now — so a stopped/restarted container never leaves a data gap.
- It was decided to connect the dashboard's passenger density trend chart to the real backend trend endpoint end-to-end, replacing the last remaining mock chart data, and to keep the chart and its "Total" label expressed in the same unit.
- It was decided to reference lines by their real code (e.g. "15A") instead of their internal numeric ID everywhere a human reads the text — AI suggestion/alert wording, the dashboard alert cards, and the live map's vehicle popups.
- It was decided to add a `CanliYolculukUret` background job so the system keeps producing new, realistic ridership measurements while it is running — not only during the one-time historical backfill — so the map, KPIs, trend chart, and alerts stay live instead of going stale between restarts.
- It was decided to align this live generation to the wall clock (triggering exactly at :00/:15/:30/:45) and to randomize which lines are busy on a given round (within a fixed low/medium/high ratio) so congestion is visibly redistributed every quarter hour instead of being frozen to a fixed time-of-day pattern.
- It was decided to simplify and rebuild the dashboard's KPI cards around what real data could reliably answer: dropping "Active Lines" and "Congested Stops" (out of scope for now), keeping "Congested Lines" and "Average Occupancy" driven by recent real measurements, and always showing the true count of "Active Alerts".
- It was decided to build the CSRNet crowd-counting service into a real edge pipeline (`edge/`) that reads a video source, runs the trained model, and publishes people-count over MQTT using the same message contract as the simulator — so one real device can run alongside simulated ones in the same fleet.
- It was decided to add a real-video playback feature on the live map: clicking the one vehicle actually fed by the CSRNet edge pipeline opens a small player showing its source footage, while simulated vehicles show no such control.
- It was decided to fine-tune the Qwen 3.5 model and evaluate the CSRNet model's accuracy/mAP/loss formally, and to add a weather-model tool to the chatbot's OpenJarvis tool set, extending what operator questions the assistant can answer beyond congestion alone.

- **Expected point completion within Sprint:** 400 points

- **Point Completion Logic:** A total target of 1000 points was set. In Sprint 1, 200 points were targeted and completed as the focus was on research and planning. In Sprint 2, 400 points were targeted and completed as the development phase began. In Sprint 3, 400 points were targeted for moving the system from mock/demo data to fully live, end-to-end data; all 15 backlog stories tracked on the Sprint 3 burndown chart were completed within the 14-day window, bringing the remaining points to 0 by Day 14 and the cumulative total to 1000.

- **Product Backlog URL:** [Click for Backlog](https://trello.com/b/2BtcZtM4/yzta-bootcamp)

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Yer tutucu haritanın yerine gerçek bir OpenStreetMap/Leaflet canlı haritası konulmasına, veritabanının rastgele mock veri yerine gerçekçi bir Üsküdar temalı güzergah ağıyla (10+ hat, gerçek İETT tarzı durak isimleri) tohumlanmasına karar verildi.
- Araç simülasyonunun gerçek güzergah geometrisi (OSRM'den türetilmiş polyline'lar) üzerine taşınmasına, backend'deki bir zamanlayıcının her aktif aracı kendi hattı boyunca ilerletmesine karar verildi; böylece harita sabit işaretçiler yerine gerçek hareketi yansıtıyor.
- AI öneri motorunun istatistiksel olarak anlamlı örüntüler yakalayabilmesi için (yalnızca birkaç canlı veri noktası yerine) 30 günlük, gerçekçi geçmiş yolculuk verisi (hat başına değişen sefer sıklığı, İBB'nin herkese açık saatlik yolculuk veri setinden türetilen hat başına zirve saat/haftaiçi örüntüleri) üretilmesine karar verildi.
- Geçmişe dönük backfill'in her `docker compose up` çalıştığında yeniden çalışan bir "kayan pencere" işi olmasına, son kaydedilen ölçümden şu ana kadar otomatik tamamlama yapmasına karar verildi — böylece durdurulup yeniden başlatılan bir container hiçbir zaman veri boşluğu bırakmıyor.
- Gösterge panelindeki yolcu yoğunluğu trend grafiğinin, geriye kalan son mock grafik verisinin yerine, uçtan uca gerçek backend trend uç noktasına bağlanmasına ve grafik ile "Toplam" etiketinin aynı birimde ifade edilmesine karar verildi.
- Hatlara, bir insanın metni okuduğu her yerde (AI öneri/uyarı metinleri, gösterge paneli uyarı kartları, canlı haritadaki araç popup'ları) iç sayısal ID yerine gerçek hat koduyla (ör. "15A") referans verilmesine karar verildi.
- Sistem çalışırken de gerçekçi, yeni yolculuk ölçümleri üretmeye devam eden bir `CanliYolculukUret` arka plan görevi eklenmesine karar verildi — yalnızca tek seferlik geçmiş backfill sırasında değil; böylece harita, KPI'lar, trend grafiği ve uyarılar, yeniden başlatmalar arasında bayatlamak yerine canlı kalıyor.
- Bu canlı üretimin duvar saatine hizalanmasına (tam olarak :00/:15/:30/:45'te tetiklenmesine) ve her turda hangi hatların yoğun olduğunun (sabit bir düşük/orta/yüksek oranı içinde) rastgele belirlenmesine karar verildi; böylece yoğunluk sabit bir günün-saati örüntüsüne kilitlenmek yerine her çeyrek saatte görünür şekilde yeniden dağılıyor.
- Gösterge panelinin KPI kartlarının, gerçek verinin güvenilir şekilde cevaplayabildiği şeyler etrafında sadeleştirilip yeniden kurulmasına karar verildi: "Aktif Hat" ve "Yoğun Durak" kaldırıldı (şimdilik kapsam dışı), "Yoğun Hat" ve "Ortalama Doluluk" son gerçek ölçümlerden besleniyor, "Aktif Alarm" her zaman gerçek sayıyı gösteriyor.
- CSRNet kalabalık sayım servisinin, bir video kaynağını okuyup eğitilmiş modeli çalıştıran ve kişi sayısını simülatörle aynı mesaj sözleşmesini kullanarak MQTT üzerinden yayınlayan gerçek bir uç (edge) hattına (`edge/`) dönüştürülmesine karar verildi — böylece aynı filoda bir gerçek cihaz simüle edilenlerle birlikte çalışabiliyor.
- Canlı haritaya gerçek video oynatma özelliği eklenmesine karar verildi: CSRNet uç hattı tarafından gerçekten beslenen tek araca tıklanınca kaynak görüntüyü gösteren küçük bir oynatıcı açılıyor, simüle edilen araçlarda böyle bir kontrol hiç görünmüyor.
- Qwen 3.5 modelinin fine-tune edilmesine, CSRNet modelinin doğruluk/mAP/loss değerlerinin biçimsel olarak değerlendirilmesine ve chatbot'un OpenJarvis araç setine bir hava durumu modeli aracı eklenmesine karar verildi; böylece asistanın yanıtlayabildiği operatör soruları yalnızca yoğunlukla sınırlı kalmayıp genişletildi.

- **Sprint İçinde Tamamlanması Beklenen Puan:** 400 puan

- **Puan Tamamlama Mantığı:** Toplam hedef 1000 puan olarak belirlenmiştir. Sprint 1'de araştırma ve planlama odaklı çalışıldığı için 200 puan hedeflenmiş ve tamamlanmıştır. Sprint 2'de geliştirme aşamasına geçilmiş ve 400 puan hedeflenip tamamlanmıştır. Sprint 3'te sistemi mock/demo veriden uçtan uca tamamen canlı veriye taşımak için 400 puan hedeflenmiştir; Sprint 3 burndown chart'ta takip edilen 15 backlog story'nin tamamı 14 günlük pencerede tamamlanarak kalan puan 14. günde 0'a indirilmiş, kümülatif toplam 1000'e ulaşmıştır.

- **Product Backlog URL:** [Backlog için tıklayın](https://trello.com/b/2BtcZtM4/yzta-bootcamp)

</details>

---

  <details>
    <summary><h2>Sprint Review</h2></summary>

- The static placeholder map was replaced end-to-end with a real OpenStreetMap/Leaflet live map: a realistic Üsküdar route network (11 lines with real-style stop names) was seeded, OSRM-derived route geometry was stored per line, and a backend scheduler now advances every active vehicle along its actual route polyline in real time.
- The live map's vehicle markers were made data-driven: color (green/yellow/red) reflects the vehicle's current occupancy level, and clicking a marker shows its real line code and, for the one CSRNet-fed vehicle, a working video-playback popup of its source footage.
- A 30-day historical backfill was built using real hourly ridership multipliers derived from İBB's public transit dataset, combined with a per-line congestion pattern (some lines busy weekday mornings, some evenings, some on specific weekdays) — giving the AI recommendation engine genuine, statistically detectable patterns instead of near-empty tables.
- The backfill was turned into a self-healing "sliding window" job: every `docker compose up` deletes data older than 30 days and tops up from the last known measurement to now, so the system is always fresh regardless of how long it was left stopped.
- A new `CanliYolculukUret` background service was added so ridership keeps being generated while the system is running, not only during the one-off backfill; it triggers exactly on the wall-clock quarter hour (:00/:15/:30/:45), and each round randomly redistributes which lines run low/medium/high — so the live map, KPIs, and trend chart all keep changing realistically hour after hour.
- The dashboard's passenger density trend chart was connected to the real backend trend endpoint for every time range (12h/24h/3d/7d/30d) and for both single-line and all-lines views, with the chart and its "Total" figure now expressed in the same, verified unit.
- The dashboard's KPI row was rebuilt around what live data could answer reliably: "Active Lines" and "Congested Stops" were removed, "Congested Lines" and "Average Occupancy" are now computed from recent real measurements, and "Active Alerts" always reflects the true alert count.
- Every place where a line is referenced in human-readable text — AI suggestion and alert wording, dashboard alert cards, live map popups — was switched from the internal numeric line ID to the real line code (e.g. "15A"), fixing a recurring confusion where alerts referenced a line number that didn't exist in the UI.
- The CSRNet crowd-counting model was wired into a real edge pipeline (`edge/`) that reads an actual video source, runs inference, and publishes people-counts over MQTT using the same contract as the simulator — allowing one real camera-fed vehicle to run side by side with simulated ones in the same fleet.
- The alert-generation engine was made idempotent within its lookback window, so a line that stays congested for an extended period no longer produces a new, nearly-identical alert every cycle.

- **Sprint Review Participants:** Bilal Solmaz, Kübra Güler, Saadettin Berber, Özlem Çal, Pınar Akdoğan

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Statik yer tutucu harita, uçtan uca gerçek bir OpenStreetMap/Leaflet canlı haritasıyla değiştirildi: gerçekçi bir Üsküdar güzergah ağı (gerçekçi durak isimleriyle 11 hat) tohumlandı, hat başına OSRM'den türetilmiş güzergah geometrisi kaydedildi ve backend'deki bir zamanlayıcı artık her aktif aracı gerçek zamanlı olarak kendi güzergah polyline'ı boyunca ilerletiyor.
- Canlı haritadaki araç işaretçileri veri odaklı hale getirildi: renk (yeşil/sarı/kırmızı) aracın o anki doluluk seviyesini yansıtıyor, bir işaretçiye tıklamak gerçek hat kodunu gösteriyor ve CSRNet ile beslenen tek araç için kaynak görüntüsünü oynatan çalışan bir video popup'ı açılıyor.
- İBB'nin herkese açık toplu ulaşım veri setinden türetilen gerçek saatlik yolculuk çarpanları ve hat başına yoğunluk deseni (bazı hatlar haftaiçi sabahları, bazıları akşamları, bazıları belirli haftanın günlerinde yoğun) birleştirilerek 30 günlük bir geçmiş backfill oluşturuldu — AI öneri motoruna neredeyse boş tablolar yerine gerçek, istatistiksel olarak tespit edilebilir örüntüler kazandırıldı.
- Backfill kendi kendini onaran bir "kayan pencere" işine dönüştürüldü: her `docker compose up` çalıştığında 30 günden eski veri silinir ve son bilinen ölçümden şu ana kadar tamamlanır; böylece sistem ne kadar süre kapalı kalırsa kalsın her zaman güncel.
- Yalnızca tek seferlik backfill sırasında değil, sistem çalışırken de yolculuk verisi üretmeye devam eden yeni bir `CanliYolculukUret` arka plan servisi eklendi; tam olarak duvar saatinin çeyreklerinde (:00/:15/:30/:45) tetikleniyor ve her turda hangi hatların düşük/orta/yüksek yoğunlukta olduğunu rastgele yeniden dağıtıyor — böylece canlı harita, KPI'lar ve trend grafiği saatler boyunca gerçekçi şekilde değişmeye devam ediyor.
- Gösterge panelinin yolcu yoğunluğu trend grafiği, her zaman aralığı (12s/24s/3g/7g/30g) ve hem tekil hat hem tüm hatlar görünümü için gerçek backend trend uç noktasına bağlandı; grafik ve "Toplam" rakamı artık aynı, doğrulanmış birimde ifade ediliyor.
- Gösterge panelinin KPI satırı, canlı verinin güvenilir şekilde cevaplayabildiği şeyler etrafında yeniden kuruldu: "Aktif Hat" ve "Yoğun Durak" kaldırıldı, "Yoğun Hat" ve "Ortalama Doluluk" artık son gerçek ölçümlerden hesaplanıyor, "Aktif Alarm" her zaman gerçek uyarı sayısını yansıtıyor.
- Bir hattın insan tarafından okunan metinde referans verildiği her yer — AI öneri/uyarı metinleri, gösterge paneli uyarı kartları, canlı harita popup'ları — iç sayısal hat ID'sinden gerçek hat koduna (ör. "15A") çevrildi; bu, uyarıların arayüzde var olmayan bir hat numarasına referans vermesinden kaynaklanan tekrarlayan bir kafa karışıklığını çözdü.
- CSRNet kalabalık sayım modeli, gerçek bir video kaynağını okuyup çıkarım yapan ve kişi sayılarını simülatörle aynı sözleşmeyi kullanarak MQTT üzerinden yayınlayan gerçek bir uç (edge) hattına (`edge/`) bağlandı — bu sayede gerçek kamerayla beslenen bir araç, aynı filoda simüle edilenlerle yan yana çalışabiliyor.
- Uyarı üretim motoru kendi geriye bakış penceresi içinde idempotent hale getirildi; uzun süre yoğun kalan bir hat artık her döngüde neredeyse aynı yeni bir uyarı üretmiyor.

- **Sprint Review Katılımcıları:** Bilal Solmaz, Kübra Güler, Saadettin Berber, Özlem Çal, Pınar Akdoğan

</details>

  </details>

---

  <details>
    <summary><h2>Sprint Retrospective</h2></summary>

**What went well**

- Moving from mock data to a real, live-generating pipeline (historical backfill + `CanliYolculukUret`) gave the AI recommendation/alert engine genuine patterns to detect for the first time, instead of near-empty or synthetic-looking tables — this was the single biggest improvement to how trustworthy the demo feels.
- Anchoring live data generation to the wall clock (:00/:15/:30/:45) instead of an arbitrary since-startup timer made the system's behavior predictable and easy to reason about when debugging totals and KPI values.
- Wiring the CSRNet model into a real edge pipeline that speaks the same MQTT contract as the simulator meant the "one real device among simulated ones" scenario worked with zero changes to the backend ingest path — the hexagonal architecture's port/adapter boundary paid off again.

**What needs improvement**

- Several rounds of manual tuning were needed to get generated ridership numbers into a believable range (both per-vehicle person counts and the system-wide total per trigger) — an earlier, explicit target range (e.g. "400–950 total across all lines per round") would have saved iteration time.
- A few restarts during active development left short gaps in the live-generated data, which briefly showed up as visual spikes on the trend chart — a clearer separation between "data generation code" and "manual test restarts" would reduce this kind of noise going forward.
- The chatbot assistant's local model calls the right data tool and gives a correct, data-backed answer on many questions (e.g. correctly identifying the currently most-congested line with its real occupancy figure), but this is not yet fully consistent — on some questions it answers from general knowledge instead of calling a tool. This needs dedicated attention, either through model choice or stronger prompting/tool-forcing.

**Planned next steps**

- Finish evaluating whether the chatbot assistant should default to a stronger model (local or cloud) for tool-calling reliability, since small local models were shown to skip the data tools entirely on some questions.
- Move the deployment from local Docker Compose only to a real production environment (single VPS to keep the local-LLM/Ollama service, or a hybrid setup), with domain, HTTPS, and secrets management finalized.
- Add automated tests for the newly added live-generation logic (`CanliYolculukUret`, quarter-hour alignment, category rotation) and for the frontend trend/KPI components, extending test coverage beyond the backend-only suite from Sprint 2.
- Revisit the CSRNet accuracy calibration now that it runs inside the live pipeline rather than as an offline script, using real operating conditions instead of only the manually labeled test set.

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

**İyi giden yönler**

- Mock veriden gerçek, canlı üretim yapan bir hatta (geçmiş backfill + `CanliYolculukUret`) geçmek, AI öneri/uyarı motoruna ilk kez neredeyse boş ya da yapay görünen tablolar yerine gerçek örüntüler kazandırdı — demo'nun ne kadar güvenilir hissettirdiği açısından tek başına en büyük iyileştirme buydu.
- Canlı veri üretimini keyfi bir "açılıştan beri geçen süre" sayacı yerine duvar saatine (:00/:15/:30/:45) sabitlemek, sistemin davranışını öngörülebilir kıldı ve toplamları/KPI değerlerini hata ayıklarken akıl yürütmeyi kolaylaştırdı.
- CSRNet modelini, simülatörle aynı MQTT sözleşmesini konuşan gerçek bir uç hattına bağlamak, "simüle edilenler arasında bir gerçek cihaz" senaryosunun backend veri alım yoluna sıfır değişiklikle çalışmasını sağladı — heksagonal mimarinin port/adaptör sınırı burada da karşılığını verdi.

**Geliştirilmesi gereken yönler**

- Üretilen yolculuk sayılarını inandırıcı bir aralığa (hem araç başına kişi sayısı hem de tetikleme başına sistem geneli toplam) oturtmak için birkaç tur manuel kalibrasyon gerekti — daha önceden net bir hedef aralık (ör. "tur başına tüm hatlarda toplam 400-950") belirlenmiş olsaydı yineleme süresinden tasarruf edilirdi.
- Aktif geliştirme sırasında yapılan birkaç yeniden başlatma, canlı üretilen veride kısa boşluklar bıraktı; bu da trend grafiğinde kısa süreliğine görsel sıçramalar olarak ortaya çıktı — "veri üretim kodu" ile "manuel test yeniden başlatmaları" arasında daha net bir ayrım, ileride bu tür gürültüyü azaltacaktır.
- Chatbot asistanının lokal modeli birçok soruda doğru veri aracını çağırıp gerçek veriye dayalı doğru bir yanıt veriyor (ör. o an en yoğun hattı gerçek doluluk oranıyla birlikte doğru tespit etmesi gibi), ama bu henüz tam tutarlı değil — bazı sorularda araç çağırmak yerine genel bilgiden yanıt üretiyor. Bu, model seçimi ya da daha güçlü prompt/araç zorlama yoluyla özel olarak ele alınmalı.

**Planlanan sonraki adımlar**

- Chatbot asistanının, araç çağırma güvenilirliği için varsayılan olarak daha güçlü bir modele (lokal ya da bulut) geçip geçmeyeceğinin değerlendirilmesi tamamlanacak; küçük lokal modellerin bazı sorularda veri araçlarını tamamen atladığı görüldü.
- Deploy'un yalnızca lokal Docker Compose'dan gerçek bir üretim ortamına (lokal LLM/Ollama servisini korumak için tek bir VPS, ya da hibrit bir kurulum) taşınması; domain, HTTPS ve secrets yönetiminin sonlandırılması.
- Yeni eklenen canlı üretim mantığı (`CanliYolculukUret`, çeyrek saat hizalaması, kategori rotasyonu) ve frontend trend/KPI bileşenleri için otomatik testler eklenerek, Sprint 2'deki yalnızca backend'i kapsayan test setinin ötesine geçilmesi.
- CSRNet doğruluk kalibrasyonunun, artık çevrimdışı bir script değil canlı hattın bir parçası olarak çalıştığı göz önünde bulundurularak, yalnızca manuel etiketlenmiş test seti yerine gerçek çalışma koşullarıyla yeniden gözden geçirilmesi.

</details>

  </details>

</details>
