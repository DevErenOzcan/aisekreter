# Voice Recognition With Django Channels

## Anlık Veri Aktarımı Ve ASGI(Asynchronous Server Gateway Interface)
Frontend kısmında kayıt başlat butonuna tıklandığında, javascript bağlantı bekleyen django websockete bağlanır. Bağlantı sağlandıktan sonra kaydedilen ses akışı belli aralıklarla "recorder.js" kütüphanesi ile wav formatına dönüştürülüp backend tarafındaki ASGI serverın consumerına iletilir. Consumer gelen ses bytelarının header kısmını atıp data kısmını dinamik olarak işleme alır.

![1473343845-django-wsgi](https://github.com/user-attachments/assets/9b6afe2e-0d53-4c18-a6f0-db183a19a7ad)

## Segmentation
Gelen verinin sokulduğu ilk işlem segmentasyondur. "webrtcvad" kütüphanesi aracılığıyla ses verisinin sessiz kısımları tespit edilip bu kısımlara göre veri birleştirilir ya da kesilerek segmentler oluşturulur. Ardından bu segmentlere bir "segment_id" değeri atanarak işleme alınırlar.


## Transcription
Transcription işlemi için açık kaynaklı whisperx modelini projeme entegre ettim. Model üzerinde ince ayar yapabilmek için whisperx kütüphanesi yerine doğrudan modelin kaynak kodunu kullandım. 
Whisperx çalıştırdığım ortam özellikleri şu şekilde:
  - Nvidia rtx 3050ti
  - Driver: 550.120
  - Cuda: 12.4
  - Pytorch 2.5.0

## Konuşmacı Ve Duygu Analizi
Son olarak segmentleri, geliştirdiğimiz derin öğrenme modellerine göndererek kalan analizleri yapıp çıktıları raporluyorum.


