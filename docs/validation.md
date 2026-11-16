# Senaryolar, doğrulama ve açık noktalar

[Proje ana sayfası](../README.md) · [Mimari](architecture.md) · [Kurulum](setup.md)

## Doğrulanan bulgular

| Kapsam | Doğrulanan bilgi |
| --- | --- |
| Suricata kaynak dosyası | [`local.rules`](../suricata/rules/local.rules) içinde üç imza ve `1000001`–`1000003` SID’leri doğrulandı. |
| Wazuh Manager kaynak dosyası | [`local_rules.xml`](../wazuh/manager/rules/local_rules.xml) içinde `100001` ve `100100`–`100106` olmak üzere sekiz kural tanımı doğrulandı. |
| Telegram | Manager yapılandırmasında `100100` ve `100101` filtresi gözlendi. [Python betiğinin](../integrations/telegram/custom-telegram.py) JSON alarmı ve yerel yapılandırmayı okuduğu kaynak üzerinden doğrulandı. `custom-telegram` giriş dosyası Manager dizininde bulunmadı. |
| Active Response | Manager yapılandırmasında `100100 → custom-test-action → test-response.sh` bağlantısı ve `local` konumu gözlendi. [Depodaki betiğin](../wazuh/active-response/test-response.sh) tek eylemi `/tmp/active_response_test.txt` dosyasına zaman damgalı bir test satırı eklemek. |

Bu bulgular dosya ve yapılandırma incelemesine dayanır. Depoda canlı alarm çıktısı, paket yakalaması, Telegram teslimat kaydı veya Active Response çalıştırma kanıtı bulunmuyor.

## Ağ saldırısı simülasyonları

Senaryolar laboratuvar ağı için önerilen kontrollü denemelerdir. Trafik `192.168.50.20` adresinden çıkmalı ve `192.168.50.10` adresine ulaşmalıdır.

| Senaryo | Beklenen eşleşme | Doğrulama noktası |
| --- | --- | --- |
| ICMP erişim yoklaması | Ubuntu’ya ping, SID `1000001`. | Suricata EVE çıktısında SID, kaynak ve hedef IP. |
| TCP SYN port taraması | 10 saniye içinde en az 20 eşleşen SYN, SID `1000002`. | Eşik sağlandığında beklenen alarm. Aynı porta giden SYN’ler de sayılır. |
| SSH servis yoklaması | TCP/22’ye 5 saniye içinde iki eşleşen SYN, SID `1000003`. | SID ve hedef port. Bu koşul TCP yoklaması düzeyinde değerlendirilir. |

TCP/22 trafiği iki TCP kuralının koşullarına da katkıda bulunabilir. Normal bağlantılar ve yeniden iletimler de eşiklere dahil olabilir. Suricata alarmının Wazuh Dashboard’a ulaştığını doğrulamak için aynı zaman aralığında EVE kaydı ile Manager veya Dashboard olayını ilişkilendirin. Bir Suricata SID’si ile Manager’ın Wazuh kural ID’si farklı alanlardır.

## Linux ve Windows tespit senaryoları

| Wazuh ID | Önerilen giriş veya davranış | Eşleşmeyi doğrulamak için |
| --- | --- | --- |
| `100001` | Örnek SSH kimlik doğrulama hatası. | Kontrollü bir günlük örneğiyle üst kural `5716` ve sabit `1.1.1.1` koşulunu inceleyin. |
| `100100` | Yalıtılmış laboratuvarda Suricata servis durdurma olayı. | `systemd` kaynaklı `Stopping suricata.service` mesajını, üst kural `40700` eşleşmesini ve beklenen ID’yi kontrol edin. |
| `100101` | Labda `root` hedefli bir `sudo` olayı. | Çözümlenen kullanıcı alanının `root` olduğunu ve olayın `sudo` grubuna girdiğini kontrol edin. |
| `100102` | Windows PowerShell’de `Get-LocalUser` içeren süreç oluşturma olayı. | Sysmon olay türü, süreç imajı, komut satırı ve `100102` eşleşmesi. |
| `100103` | Windows PowerShell’de izinli bir lab hedefi için `Invoke-WebRequest` içeren süreç oluşturma olayı. | İmaj ve komut satırı alanları. Web isteğinin başarı durumu ayrı kanıt gerektirir. |
| `100104` | Adında `SOCLab` geçen lab kayıt defteri değerinde değişiklik. | Sysmon Event ID 13, `targetObject` alanı ve `100104` eşleşmesi. |
| `100105` | `SOCLab` içeren bir lab yolunda dosya oluşturma. | Sysmon Event ID 11, `targetFilename` alanı ve `100105` eşleşmesi. |
| `100106` | Windows Run anahtarı kalıcılık senaryosundan, `SOCLabPersistence` içeren kontrollü olay örneği. | Gerçek Sysmon kaydındaki `targetObject` değerini ve üst kural `61615` eşleşmesini birlikte kontrol edin. Kuralın güvenilir biçimde tetiklendiği doğrulanmadı. |

Önce örnek olayları `wazuh-logtest` ile inceleyin. Uçtan uca kontrolde kaynaktaki olay ile Manager alarmının zamanını, agent’ını ve kural ID’sini karşılaştırın. [Wazuh kural testi](https://documentation.wazuh.com/current/user-manual/ruleset/testing.html)

## Bildirim ve yanıt doğrulaması

| Bileşen | Kabul ölçütü | Mevcut durum |
| --- | --- | --- |
| Telegram | `100100` veya `100101` alarmı oluşur, Manager yapılandırılan giriş dosyasını çağırır ve beklenen kural ID’siyle test sohbetine mesaj ulaşır. | **Canlı teslimat doğrulanmadı.** Uzantısız `custom-telegram` giriş dosyası eksik. |
| Active Response | Ubuntu Agent kaynaklı `100100` alarmından sonra aynı uç noktada `/tmp/active_response_test.txt` dosyasına yeni zaman damgalı satır eklenir. | Komut bağlantısı ve betik içeriği incelendi. Canlı tetikleme ve dosya kaydı doğrulanmadı. |

Bir senaryo yeniden yürütüldüğünde zaman damgasını, kimlik bilgileri temizlenmiş kaynak olayını, beklenen ve gözlenen SID veya kural ID’sini kaydedin. EVE toplama, Windows olay iletimi, Sysmon filtreleri ve `100106` üst kural bağımlılığı öncelikli açık doğrulama noktalarıdır. FIM ve auditd kapsamına ilişkin doğrulanmış bir senaryo bu depoda belgelenmiyor.
