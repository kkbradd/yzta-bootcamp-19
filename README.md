# yzta-bootcamp-19

---

## Team Members

| Name | Role | Social |
|:-------:|:-----:|:--------:|
| Bilal Solmaz | Product Owner | |
| Kübra Güler | Scrum Master | [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20"/>](https://github.com/kkbradd) [<img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" width="20"/>](https://www.linkedin.com/in/kubradguler/) |
| Saadettın Berber | Developer | [<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20"/>](https://github.com/saadettinBerber) |
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

# Ya da doğrudan API'den:
curl -X POST localhost:8100/chat -H "Content-Type: application/json" \
     -d '{"mesaj": "Şu an hatlarda yoğunluk nasıl?"}'
```

Cevap kalitesi yetmezse opsiyonel olarak Gemini'ye geçilebilir (`ASISTAN_MOTOR=cloud`
+ `GEMINI_API_KEY`); bu modda veriler Google'a gider, bkz.
[asistan/README.md](asistan/README.md#gemini-ile-çalıştırma-opsiyonel).

Ayrıntılar: [asistan/README.md](asistan/README.md)

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

- **Sprint Review Participants:** Bilal Solmaz, Kübra Güler, Saadettın Berber, Özlem Çal, Pınar Akdoğan

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Hangi veri kaynaklarının ve modellerin kullanılacağına dair araştırma yapıldı ve ekip içinde tartışıldı.
- Yoğunluk tahmini modeli olarak CSRNet değerlendirmeler sonucunda seçildi.
- Teknoloji yığını kararları ekip olarak ortaklaşa alındı (Python, Firebase, Trello).
- Multi-agent sistemler aracılığıyla içgörüler sunulabileceği tartışıldı ve gelecek bir hedef olarak benimsendi.
- İlerleyen sprintlerde eklenmesi beklenen özellikler ve geliştirmeler belirlendi ve planlandı.

- **Sprint Review Katılımcıları:** Bilal Solmaz, Kübra Güler, Saadettın Berber, Özlem Çal, Pınar Akdoğan

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

- Backend development began: hexagonal architecture skeleton, data model, idempotent seed, MQTT ingest, Redis live state, REST API, and WebSocket broadcast were built in incremental phases.
- The admin panel frontend was scaffolded in React: login, dashboard (with an interactive passenger density chart), live map, lines, and stops pages were implemented.
- CORS middleware was made configurable so the panel (different origin/port) could call the backend safely.
- The frontend was containerized with a production Nginx service, and the Lines page was connected to the real `/api/hatlar` endpoint.
- JWT-based authentication was added to the backend and wired into the panel's login flow.
- A local chatbot assistant (OpenJarvis on Ollama) was researched and built as a separate service, reading live density data from the backend via tool calls; an optional cloud (Gemini) engine was added later for cases where the local model's answer quality is insufficient.
- An AI recommendation/alert engine was designed and implemented directly in the backend (hexagonal ports/adapters): a weekly-pattern SQL query feeds an LLM for the "AI Suggestions" flow, and a 3-hour anomaly query feeds a "Recent Alerts" flow — both support Gemini and a local Ollama model behind the same port.
- A root-level `docker-compose.yml` was added so the full stack (panel + backend + assistant + local LLM) can be started with a single command.
- GitHub Pages documentation was expanded (architecture, API/MQTT contracts, AI engine, assistant) to keep the project log up to date.

- **Expected point completion within Sprint:** 400 points

- **Point Completion Logic:** As planned in Sprint 1, the development phase began in Sprint 2 with a target of 400 points; all 15 backlog stories tracked on the burndown chart were completed within the 14-day window, bringing the remaining points to 0 by Day 14.

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Backend geliştirmesine başlandı: heksagonal mimari iskeleti, veri modeli, idempotent tohum verisi, MQTT veri alımı, Redis anlık durum, REST API ve WebSocket yayını aşamalı olarak geliştirildi.
- Admin panel frontend'i React ile iskeletlendi: giriş, gösterge paneli (etkileşimli yolcu yoğunluğu grafiğiyle), canlı harita, hatlar ve duraklar sayfaları hayata geçirildi.
- Panel (farklı origin/port) backend'i güvenle çağırabilsin diye CORS middleware yapılandırılabilir hale getirildi.
- Frontend, üretim Nginx servisiyle konteynerlenip Hatlar sayfası gerçek `/api/hatlar` ucuna bağlandı.
- Backend'e JWT tabanlı kimlik doğrulama eklendi ve panelin giriş akışına kablolandı.
- Ollama üzerinde OpenJarvis tabanlı lokal bir chatbot asistanı araştırılıp ayrı bir servis olarak inşa edildi; backend'den canlı yoğunluk verisini tool çağrılarıyla okuyor. Lokal modelin cevap kalitesi yetmediğinde kullanılabilecek opsiyonel bir bulut (Gemini) motoru daha sonra eklendi.
- Backend içinde (heksagonal port/adaptör mimarisiyle) doğrudan bir AI öneri/uyarı motoru tasarlanıp geliştirildi: haftalık örüntü SQL sorgusu "AI Önerileri" akışını, 3 saatlik anomali sorgusu "Son Uyarılar" akışını besliyor — ikisi de aynı port arkasında hem Gemini'yi hem lokal bir Ollama modelini destekliyor.
- Kök dizine bir `docker-compose.yml` eklendi, böylece tüm sistem (panel + backend + asistan + lokal LLM) tek komutla ayağa kalkabiliyor.
- Proje günlüğünü güncel tutmak için GitHub Pages dokümantasyonu genişletildi (mimari, API/MQTT sözleşmeleri, AI motoru, asistan).

- **Sprint İçinde Tamamlanması Beklenen Puan:** 400 puan

- **Puan Tamamlama Mantığı:** Sprint 1'de planlandığı gibi Sprint 2'de geliştirme aşamasına 400 puan hedefiyle geçildi; burndown chart'ta takip edilen 15 backlog story'nin tamamı 14 günlük pencerede tamamlanarak kalan puan 14. günde 0'a indirildi.

</details>

  </details>

---

  <details>
    <summary><h2>Sprint Review</h2></summary>

- The backend was deployed end-to-end with a fully test-covered hexagonal architecture (MQTT ingest, Redis live state, REST API, WebSocket broadcast, JWT authentication).
- The admin panel frontend was connected to the real backend across its core screens (login, dashboard, lines, live map, stops).
- Two AI-driven capabilities were shipped: an automatic recommendation/alert engine running inside the backend, and an interactive chatbot assistant running as a separate, privacy-conscious service.
- A single-command, full-stack Docker Compose setup was delivered, lowering the barrier for anyone on the team (or evaluators) to run the whole system locally.
- Documentation (root README, backend README, GitHub Pages site) was kept in sync with the fast pace of development.

- **Sprint Review Participants:** Bilal Solmaz, Kübra Güler, Saadettın Berber, Özlem Çal, Pınar Akdoğan

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- Backend, tam test kapsamına sahip heksagonal mimariyle uçtan uca deploy edildi (MQTT veri alımı, Redis anlık durum, REST API, WebSocket yayını, JWT kimlik doğrulama).
- Admin panel frontend'i temel ekranlarında (giriş, gösterge paneli, hatlar, canlı harita, duraklar) gerçek backend'e bağlandı.
- İki AI destekli yetenek hayata geçirildi: backend içinde çalışan otomatik öneri/uyarı motoru ve ayrı, gizliliğe duyarlı bir servis olarak çalışan etkileşimli chatbot asistanı.
- Tek komutla ayağa kalkan tam-stack Docker Compose kurulumu teslim edildi; bu, ekipteki (veya değerlendiricilerdeki) herkesin sistemi lokal olarak çalıştırmasını kolaylaştırdı.
- Dokümantasyon (kök README, backend README, GitHub Pages sitesi) geliştirmenin hızına ayak uydurarak güncel tutuldu.

- **Sprint Review Katılımcıları:** Bilal Solmaz, Kübra Güler, Saadettın Berber, Özlem Çal, Pınar Akdoğan

</details>

  </details>

---

  <details>
    <summary><h2>Sprint Retrospective</h2></summary>

- The AI recommendation/alert engine and the chatbot assistant were built in parallel by different team members without early alignment on architecture; a merge was needed afterwards to reconcile both into a single source of truth. Earlier coordination on shared modules (LLM provider abstraction, Docker Compose) is planned for Sprint 3.
- Downloading larger local LLM models over an unstable connection caused repeated interruptions; a fallback to a smaller model or a documented retry strategy will be considered going forward.
- The image-processing model (CSRNet) integration and the live density map UI are carried over to Sprint 3, alongside connecting the "AI Suggestions" and "Recent Alerts" cards on the dashboard to the real backend endpoints.
- Frontend-backend Docker deployment will be finalized and documented as a single, reproducible flow in Sprint 3.

<details>
  <summary><h4>Türkçe Açıklama</h4></summary>

- AI öneri/uyarı motoru ile chatbot asistanı, farklı takım üyeleri tarafından mimari üzerinde erken hizalanmadan paralel geliştirildi; sonrasında ikisini tek bir doğru kaynakta birleştirmek için bir merge gerekti. Paylaşılan modüller (LLM sağlayıcı soyutlaması, Docker Compose) üzerinde daha erken koordinasyon Sprint 3 için planlanıyor.
- Kararsız bir bağlantı üzerinden büyük lokal LLM modelleri indirmek tekrar tekrar kesintiye uğradı; ileride daha küçük bir modele düşme ya da belgelenmiş bir yeniden deneme stratejisi değerlendirilecek.
- Görüntü işleme modeli (CSRNet) entegrasyonu ve canlı yoğunluk haritası arayüzü, gösterge panelindeki "AI Önerileri" ve "Son Uyarılar" kartlarının gerçek backend uçlarına bağlanmasıyla birlikte Sprint 3'e devrediliyor.
- Frontend-backend Docker deploy'u Sprint 3'te tek, tekrarlanabilir bir akış olarak sonlandırılıp belgelenecek.

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

  </details>

---

  <details>
    <summary><h2>Sprint Board Update</h2></summary>

  </details>

---

  <details>
    <summary><h2>Daily Scrum</h2></summary>

  </details>

---

  <details>
    <summary><h2>Sprint Notes</h2></summary>

  </details>

---

  <details>
    <summary><h2>Sprint Review</h2></summary>

  </details>

---

  <details>
    <summary><h2>Sprint Retrospective</h2></summary>

  </details>

</details>
