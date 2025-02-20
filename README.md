# Voice Diarization Yeni Yaklaşım

Önceki projemde frontend kısmında ses kaydı bitmeden sesi işlemeye başlayamıyordum. Bu durum ciddi miktarda zaman kaybına sebep oluyordu. Bu duruma çözüm olarak websocket kullanarak uygulamadan tamamen bağımsız dosya gönderim yapısı tasarladım.

## Django Websocket Ve ASGI(Asynchronous Server Gateway Interface)

Frontend kısmında kayıt başlat butonuna tıklandığı anda yapılan şey halihazırda bağlantı bekleyen django websockete bağlanmak."record.js" kütüphanesi ile kaydettiğim veri akışını belli aralıklarla bu bağlantı üzerinden django ASGI server'a gönderiyorum. ASGI server ise gelen ses bytelarından header ve data kısımlarını ayırıp data kısmını bir buffer a kaydediyor. Ardından gerekli işlemleri yapıp sesi istenen formatta meeting_id ve segmnet_id değerlerine göre bir dosyaya yazıyor.

![Pasted image (3)](https://github.com/user-attachments/assets/2c65deb3-cbe4-4105-9d84-951e07ffca1c)
