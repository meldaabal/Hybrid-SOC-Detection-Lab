# Hibrit Ağ Saldırı Tespit ve SOC İzleme Sistemi

Bu bilgisayar mühendisliği staj projesi, Linux ağ trafiğini ve Windows uç nokta olaylarını bir SOC laboratuvarında izlemek için Suricata ve Wazuh kullanır. Proje kaynakları, ağ imzalarını, sistem ve Sysmon olaylarına yönelik Wazuh kurallarını, Telegram bildirim betiğini ve yerel bir Active Response testini içerir.

## Laboratuvar ve teknolojiler

| Teknoloji | Konum | Görev |
| --- | --- | --- |
| Oracle VirtualBox | Windows ana makine | Kali Linux ve Ubuntu Server sanal makinelerini çalıştırır. |
| Kali Linux | `192.168.50.20` | Ping, TCP SYN ve SSH yoklama senaryoları için trafik kaynağıdır. |
| Ubuntu Server | `192.168.50.10` | Suricata sensörünü, Wazuh Agent’ı ve yerel Active Response test betiğini barındıran laboratuvar uç noktasıdır. |
| Suricata IDS | Ubuntu Server | Görülebilen ağ trafiğini imzalarla karşılaştırır ve eşleşmelerde alarm üretir. |
| Wazuh Agent | Ubuntu Server | Yapılandırılan günlük kaynaklarından olay toplar ve Manager’a iletir. |
| Wazuh Manager, Indexer ve Dashboard | Windows, Docker Desktop | Manager olayları değerlendirir. Indexer alarmları arama için saklar, Dashboard bunları görüntüler. |
| Sysmon | Windows | Süreç oluşturma, dosya oluşturma ve kayıt defteri olayları için telemetri sağlar. Etkin filtreler ve Wazuh’a aktarım ayarları depoda bulunmuyor. |
| Telegram Bot API, Python 3 | Wazuh Manager | Seçilen Wazuh alarmlarını bir Telegram sohbetine iletmek üzere tasarlanmıştır. |
| Bash, Wazuh Active Response | Ubuntu uç noktası | Özel test betiği, çağrıldığında `/tmp/active_response_test.txt` dosyasına zaman damgalı bir test satırı ekler. |

Ubuntu üzerindeki Suricata, Kali’den gelen trafiği izler. Suricata olaylarının Wazuh’a taşınması için Agent’ın EVE JSON çıktısını okuması gerekir. Manager’a ulaşan Linux ve Windows olayları Wazuh kurallarıyla değerlendirilir. Manager’daki Telegram filtresi `100100` ve `100101` alarmlarını seçer. `100100` ayrıca olayı üreten agent üzerindeki Active Response test komutuna bağlanmıştır. Veri akışı ve doğrulama sınırları [mimari belgesinde](docs/architecture.md) açıklanıyor.

## Özel tespit kuralları

[Suricata kuralları](suricata/rules/local.rules) yalnızca `192.168.50.20 → 192.168.50.10` yönünü kapsar.

| SID | Tespit koşulu | Trafik yorumu |
| --- | --- | --- |
| `1000001` | ICMP Echo Request, `itype:8` | Ping isteği. |
| `1000002` | Herhangi bir hedef porta 10 saniyede 20 TCP SYN eşleşmesi, kaynak IP başına `type both` | Olası SYN taraması. Aynı porta giden paketler de sayılır. |
| `1000003` | TCP/22’ye 5 saniyede 2 SYN eşleşmesi, kaynak IP başına `type threshold` | Olası SSH yoklaması. SSH kimlik doğrulama durumu ayrı bir olaydır. |

[Wazuh kural dosyası](wazuh/manager/rules/local_rules.xml) yedi proje kuralı ve dosyada örnek olarak işaretlenmiş bir kural içerir.

| ID | Seviye | Tespit koşulu |
| --- | ---: | --- |
| `100001` | 5 | Örnek SSH kuralı. Üst kural `5716` ve sabit kaynak IP `1.1.1.1`. |
| `100100` | 10 | Üst kural `40700`, `systemd` ve `Stopping suricata.service` mesajı. |
| `100101` | 8 | `sudo` grubunda kullanıcı alanı tam olarak `root`. |
| `100102` | 8 | Sysmon süreç oluşturma olayında `powershell.exe` komut satırında `Get-LocalUser`. |
| `100103` | 9 | Sysmon süreç oluşturma olayında `powershell.exe` komut satırında `Invoke-WebRequest`. |
| `100104` | 8 | Sysmon kayıt defteri değer olayında hedef nesnede `SOCLab`. |
| `100105` | 8 | Sysmon dosya oluşturma olayında hedef dosya yolunda `SOCLab`. |
| `100106` | 10 | Üst kural `61615` ve hedef kayıt defteri nesnesinde `SOCLabPersistence`. Windows Run anahtarı kalıcılık senaryosu için yazıldı. |

## Klasör yapısı

```text
Hybrid-SOC-Detection-Lab/
├── .gitignore
├── README.md
├── docs/
│   ├── architecture.md
│   ├── setup.md
│   └── validation.md
├── integrations/
│   └── telegram/
│       ├── custom-telegram.py
│       └── telegram.conf.example
├── suricata/
│   └── rules/
│       └── local.rules
└── wazuh/
    ├── active-response/
    │   └── test-response.sh
    └── manager/
        └── rules/
            └── local_rules.xml
```

`screenshots/` şu anda boş. Gerçek Telegram yapılandırması, kimlik bilgileri, özel anahtarlar ve ham günlükler yerel tutulur. Paylaşılan [Telegram yapılandırma örneği](integrations/telegram/telegram.conf.example) yalnızca yer tutucular içerir.

## Kurulum ve doğrulama

- [Sistem mimarisi](docs/architecture.md) ağ, uç nokta ve alarm akışını açıklar.
- [Kurulum ve yapılandırma](docs/setup.md) depo dosyalarını canlı bileşen yollarıyla eşleştirir ve gereken ayarları gösterir.
- [Doğrulama planı ve durum](docs/validation.md) saldırı simülasyonlarını, beklenen eşleşmeleri ve mevcut kanıtları listeler.

Kural tanımları ve betik davranışları kaynak dosyalardan incelendi. Telegram’ın canlı çalışması henüz doğrulanmadı ve Manager’da `custom-telegram` adlı uzantısız giriş dosyası eksik. Wazuh `100106` kuralının güvenilir biçimde tetiklendiği de doğrulanmadı. Senaryo başına uçtan uca sonuçlar için [doğrulama belgesine](docs/validation.md) bakın.
