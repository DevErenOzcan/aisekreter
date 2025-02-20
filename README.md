# Voice Diarization Yeni Yaklaşım

Önceki projemde frontend kısmında ses kaydı bitmeden sesi işlemeye başlayamıyordum. Bu durum ciddi miktarda zaman kaybına sebep oluyordu. Bu duruma çözüm olarak websocket kullanarak uygulamadan tamamen bağımsız dosya gönderim yapısı tasarladım.

## Django Websocket Ve ASGI(Asynchronous Server Gateway Interface)

Frontend kısmında kayıt başlat butonuna tıklandığı anda yapılan şey halihazırda bağlantı bekleyen django websockete bağlanmak."record.js" kütüphanesi ile kaydettiğim veri akışını belli aralıklarla bu bağlantı üzerinden django ASGI server'a gönderiyorum. ASGI server ise gelen ses bytelarından header ve data kısımlarını ayırıp data kısmını bir buffer a kaydediyor. Ardından gerekli işlemleri yapıp sesi istenen formatta meeting_id ve segmnet_id değerlerine göre bir dosyaya yazıyor.

![1473343845-django-wsgi](https://github.com/user-attachments/assets/9b6afe2e-0d53-4c18-a6f0-db183a19a7ad)

