# Unreal Engine 5.6 — ChloeAI WebSocket istemcisi

Bu klasördeki `websocket_client.h` / `websocket_client.cpp` dosyalarını kendi **Game Module** veya **plugin** içine kopyalayın ve derleyin.

## Modül bağımlılıkları

`YourProject.Build.cs` içinde `PrivateDependencyModuleNames` (veya Public) listesine ekleyin:

- `WebSockets`
- `Json` (JSON ayrıştırma için)
- `JsonUtilities` (gerekirse)

Örnek:

```csharp
PrivateDependencyModuleNames.AddRange(new string[] {
    "WebSockets",
    "Json",
});
```

Projede **WebSockets** eklentisinin etkin olduğundan emin olun (genelde Engine ile gelir).

## Kullanım (özet)

`FChloeWebSocketClient` içinde `AddSP` kullanıldığı için örneği **paylaşımlı pointer** ile oluşturun:

```cpp
TSharedPtr<FChloeWebSocketClient> Client = MakeShared<FChloeWebSocketClient>();
Client->OnSpeechJson.BindLambda([](const FString& Json) { /* parse */ });
Client->Connect(TEXT("ws://127.0.0.1:8765"));
```

## Bağlantı URL’si

Python backend varsayılan olarak `ws://127.0.0.1:8765` dinler. C++ tarafında:

```cpp
Client->Connect(TEXT("ws://127.0.0.1:8765"));
```

## Gelen mesaj

Sunucu UTF-8 JSON gönderir. `OnSpeechJson` delegate’ine **ham FString** düşer; `FJsonObject` ile parse edin:

- `type` — `"speech"`
- `audio_path` — **mutlak Windows yolu** (ör. `C:\...\ChloeAI\Audio\response.wav`). Bu yolu kullanarak WAV dosyasını okuyun veya `USoundWave` üretin.
- `visemes` — zaman çizelgesi dizisi (`t` saniye, `v` kısa etiket).
- `text` — gösterilecek / alt yazı için metin.

## Blueprint

Sınıfı `UCLASS` ile saran bir Actor Component veya Subsystem yazıp delegate’i `BlueprintAssignable` ile sarmalamak yaygın bir yöntemdir; bu repoda yalnızca C++ iskeleti verilmiştir.

## Dosya yolları

Backend ile Unreal **aynı makinede** olduğu sürece `audio_path` doğrudan `FString` → `FPaths` ile kullanılabilir. Ağ sürücüsü veya farklı PC senaryosu bu proje kapsamı dışındadır.
