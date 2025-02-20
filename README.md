# Voice Diarization Yeni Yaklaşım

Önceki projemde frontend kısmında ses kaydı bitmeden sesi işlemeye başlayamıyordum. Bu durum ciddi miktarda zaman kaybına sebep oluyordu. Bu duruma çözüm olarak websocket kullanarak uygulamadan tamamen bağımsız dosya gönderim yapısı tasarladım.

## Django Websocket Ve ASGI(Asynchronous Server Gateway Interface)

Frontend kısmında kayıt başlat butonuna tıklandığı anda yapılan şey halihazırda bağlantı bekleyen django websockete bağlanmak."record.js" kütüphanesi ile kaydettiğim veri akışını belli aralıklarla bu bağlantı üzerinden django ASGI server'a gönderiyorum. ASGI server ise gelen ses bytelarından header ve data kısımlarını ayırıp data kısmını bir buffer a kaydediyor. Ardından gerekli işlemleri yapıp sesi istenen formatta meeting_id ve segmnet_id değerlerine göre bir dosyaya yazıyor.

![54DBE4C912DA4BA59B22FD884E8D4E78](https://github.com/user-attachments/assets/23da0290-e866-4b19-bacd-7a098eafc8ae)
