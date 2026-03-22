// ChloeAI — WebSocket client wrapper for Unreal Engine 5.x
// Copy into your game module; add "WebSockets", "Json" to YourModule.Build.cs Dependencies.

#pragma once

#include "CoreMinimal.h"
#include "Interfaces/IWebSocket.h"

DECLARE_DELEGATE_OneParam(FChloeWebSocketSpeech, const FString& /*JsonPayload*/);

/**
 * Thin wrapper around IWebSocket for ws:// connections to the Python backend.
 * On message: raw JSON string is passed to OnSpeechJson for parsing (type, audio_path, visemes, text).
 */
class FChloeWebSocketClient : public TSharedFromThis<FChloeWebSocketClient>
{
public:
	FChloeWebSocketClient();
	~FChloeWebSocketClient();

	void Connect(const FString& Url);
	void Disconnect();

	FChloeWebSocketSpeech OnSpeechJson;

private:
	void HandleConnected();
	void HandleConnectionError(const FString& Error);
	void HandleClosed(int32 StatusCode, const FString& Reason, bool bWasClean);
	void HandleMessage(const FString& Message);

	TSharedPtr<IWebSocket> Socket;
};
