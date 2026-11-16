# Kurulum ve yapılandırma

[Proje ana sayfası](../README.md) · [Mimari](architecture.md) · [Doğrulama](validation.md)

Bu adımlar mevcut bir VirtualBox ve Wazuh Docker Desktop laboratuvarına proje kaynaklarını yerleştirmek içindir. Wazuh Compose dosyası, imaj etiketleri, etkin Suricata YAML’ı, Agent yapılandırmaları ve Sysmon XML’i depoda bulunmuyor. Kurulu bileşen sürümlerini ve mevcut yapılandırma kaynaklarını kendi ortamınızda doğrulayın.

## 1. Platformu ve bağlantıları kontrol edin

1. VirtualBox’ta Kali Linux ve Ubuntu Server’ı başlatın. Kali’nin `192.168.50.20`, Ubuntu’nun `192.168.50.10` adresini kullandığını ve Suricata’nın bu trafiği taşıyan arayüzü görebildiğini doğrulayın.
2. Windows’ta mevcut Wazuh Docker Desktop dağıtımını açın. Manager, Indexer ve Dashboard durumunu `docker ps` ile kontrol edin. Bu laboratuvardaki Manager adı `single-node-wazuh.manager-1`.
3. Ubuntu Agent’ın Windows tarafındaki erişilebilir Manager adresine kaydedildiğini ve Dashboard’da bağlı göründüğünü kontrol edin. Manager uç noktası ve port eşlemelerini mevcut Docker dağıtımından doğrulayın.

## 2. Suricata ve Ubuntu Agent

1. [`suricata/rules/local.rules`](../suricata/rules/local.rules) dosyasını Ubuntu’daki `/var/lib/suricata/rules/local.rules` yoluna yerleştirin. Hedefte başka yerel kurallar varsa bunları koruyarak birleştirin.
2. Etkin Suricata yapılandırmasında, örneğin `/etc/suricata/suricata.yaml` kullanılıyorsa bu dosyada, `default-rule-path` ve `rule-files` ayarlarının `local.rules` dosyasını yüklediğini kontrol edin. Mevcut kural girişlerini koruyun. Gerçek arayüzü ve EVE JSON çıktı ayarını doğrulayın.
3. Etkin YAML yolu aşağıdaki örnekle aynıysa Ubuntu’da sözdizimi ve kural yükleme kontrolü için `sudo suricata -T -c /etc/suricata/suricata.yaml` çalıştırın. Kontrol başarılıysa Suricata servisini kendi kurulumunuza göre yeniden yükleyin.
4. Ubuntu’daki `/var/ossec/etc/ossec.conf` dosyasında EVE JSON toplama bloğunu doğrulayın. Suricata’nın etkin çıktısı aşağıdaki yoldaysa bu örnek kullanılabilir. `100100` ve `100101` için ayrıca `systemd` ve `sudo` olaylarını sağlayan günlük kaynaklarını kontrol edin.

```xml
<localfile>
  <log_format>json</log_format>
  <location>/var/log/suricata/eve.json</location>
</localfile>
```

Yapılandırma değiştiyse Ubuntu Agent’ı yeniden başlatıp bağlantısını ve olay akışını doğrulayın. [Suricata YAML başvurusu](https://docs.suricata.io/en/latest/configuration/suricata-yaml.html) · [Wazuh Suricata entegrasyonu](https://documentation.wazuh.com/current/proof-of-concept-guide/integrate-network-ids-suricata.html)

## 3. Wazuh Manager kuralları ve Windows olayları

1. [`wazuh/manager/rules/local_rules.xml`](../wazuh/manager/rules/local_rules.xml) dosyasını Manager’daki `/var/ossec/etc/rules/local_rules.xml` konumuyla eşleştirin. Kalıcı kural dizinini veya volume eşlemesini Docker dağıtımında doğrulayın. Var olan kuralları ve kural ID’lerini kontrol edip çakışmaları dağıtımdan önce çözün.
2. Manager’ın etkin yapılandırma yolu `/var/ossec/etc/ossec.conf`. Docker dağıtımında ana makineden bağlanan kaynak dosyayı düzenleyin. Wazuh’un tek düğümlü örneğinde bu dosya `config/wazuh_cluster/wazuh_manager.conf` olabilir. Gerçek bind mount yolunu kendi Compose dağıtımınızdan doğrulayın.
3. Manager’da kayıt örnekleriyle kural eşleşmesini incelemek için PowerShell’den `docker exec -it single-node-wazuh.manager-1 /var/ossec/bin/wazuh-logtest` çalıştırabilirsiniz. Kuralların canlı alarm üretmesi için dağıtımın yeniden yükleme adımlarını uygulayıp Manager sağlığını kontrol edin.
4. Windows’ta Sysmon’un `Microsoft-Windows-Sysmon/Operational` kanalını ürettiğini doğrulayın. Windows Wazuh Agent ile doğrudan topluyorsanız `C:\Program Files (x86)\ossec-agent\ossec.conf` altındaki `localfile` bloğunda bu kanalın `eventchannel` biçiminde toplandığını kontrol edin. Depodaki kuralların ihtiyaç duyduğu süreç oluşturma, dosya oluşturma ve kayıt defteri olaylarının Sysmon filtrelerinden geçtiğini ve Manager’a ulaştığını doğrulayın.

[Wazuh Docker yapılandırması](https://documentation.wazuh.com/current/deployment-options/docker/container-usage.html) · [Windows olay toplama](https://documentation.wazuh.com/current/user-manual/capabilities/log-data-collection/configuration.html) · [Kural testi](https://documentation.wazuh.com/current/user-manual/ruleset/testing.html)

## 4. Telegram entegrasyonu

1. [`integrations/telegram/custom-telegram.py`](../integrations/telegram/custom-telegram.py) dosyasının çalışma yolu `/var/ossec/integrations/custom-telegram.py`. Betik Python 3 ve standart kütüphanelerle çalışır.
2. [Örnek yapılandırmayı](../integrations/telegram/telegram.conf.example) esas alarak gerçek `/var/ossec/integrations/telegram.conf` dosyasını yalnızca çalışma ortamında hazırlayın. Betik bu sabit yoldan `BOT_TOKEN` ve `CHAT_ID` anahtarlarını okur. Dosya izinlerini entegrasyonun çalıştığı hesapla sınırlayın.
3. Manager’da gözlenen `<integration>` ayarı `name=custom-telegram` ve `rule_id=100100,100101` kullanıyor. JSON alarm dosyası betiğe ilk argüman olarak iletilmelidir. Uzantısız `/var/ossec/integrations/custom-telegram` giriş dosyası eksik. Canlı doğrulamadan önce bu adı karşılayan, Python betiğine argümanları aktaran çalıştırılabilir girişin ve izinlerinin hedef ortamda tamamlanması gerekir.
4. Manager’ın Telegram Bot API’ye HTTPS erişimini ve test sohbetindeki teslimatı [doğrulama planıyla](validation.md) kontrol edin. Gerçek yapılandırmayı veya kimlik bilgisi içeren hata çıktılarını depoya eklemeyin.

[Wazuh entegrasyon ayarları](https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/integration.html)

## 5. Active Response test eylemi

1. [`wazuh/active-response/test-response.sh`](../wazuh/active-response/test-response.sh) dosyasını olayı üreten Ubuntu Agent üzerinde `/var/ossec/active-response/bin/test-response.sh` konumuna yerleştirin. Linux satır sonlarını, Bash yorumlayıcısını ve çalıştırma izinlerini kontrol edin. Wazuh’un Linux örneğinde sahiplik `root:wazuh`, izin `750` olarak verilir.
2. Manager yapılandırmasında `custom-test-action` adlı `<command>` tanımının `test-response.sh` çalıştırılabilir dosyasına bağlandığını kontrol edin. İlgili `<active-response>` tanımı aynı komut adını, `location=local` ve `rules_id=100100` değerlerini kullanır. Önceki incelemede blokta açık bir `disabled` alanı görülmedi. Etkinleştirme ayarını kurulu Wazuh sürümünün gerektirdiği biçimde doğrulayın.
3. Uçtan uca kontrolde önce Manager’daki `100100` alarmını, sonra Ubuntu’daki `/tmp/active_response_test.txt` dosyasına eklenen yeni zaman damgasını arayın. Betiğin tek eylemi bu test günlüğüne yazmaktır.

[Wazuh Active Response kurulumu](https://documentation.wazuh.com/current/user-manual/capabilities/active-response/how-to-configure.html) · [Active Response alanları](https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/active-response.html)
