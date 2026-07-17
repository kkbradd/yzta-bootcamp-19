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
