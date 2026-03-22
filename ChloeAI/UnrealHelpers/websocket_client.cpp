#include "websocket_client.h"

#include "WebSocketsModule.h"
#include "IWebSocket.h"
#include "Modules/ModuleManager.h"

FChloeWebSocketClient::FChloeWebSocketClient() = default;

FChloeWebSocketClient::~FChloeWebSocketClient()
{
	Disconnect();
}

void FChloeWebSocketClient::Connect(const FString& Url)
{
	Disconnect();

	if (!FModuleManager::Get().IsModuleLoaded("WebSockets"))
	{
		FModuleManager::Get().LoadModule("WebSockets");
	}

	FWebSocketsModule& WebSocketsModule = FModuleManager::LoadModuleChecked<FWebSocketsModule>("WebSockets");
	Socket = WebSocketsModule.CreateWebSocket(Url, FString());

	if (!Socket.IsValid())
	{
		HandleConnectionError(TEXT("CreateWebSocket failed"));
		return;
	}

	Socket->OnConnected().AddSP(this, &FChloeWebSocketClient::HandleConnected);
	Socket->OnConnectionError().AddSP(this, &FChloeWebSocketClient::HandleConnectionError);
	Socket->OnClosed().AddSP(this, &FChloeWebSocketClient::HandleClosed);
	Socket->OnMessage().AddSP(this, &FChloeWebSocketClient::HandleMessage);

	Socket->Connect();
}

void FChloeWebSocketClient::Disconnect()
{
	if (Socket.IsValid())
	{
		Socket->OnConnected().RemoveAll(this);
		Socket->OnConnectionError().RemoveAll(this);
		Socket->OnClosed().RemoveAll(this);
		Socket->OnMessage().RemoveAll(this);
		Socket->Close();
		Socket.Reset();
	}
}

void FChloeWebSocketClient::HandleConnected()
{
	UE_LOG(LogTemp, Log, TEXT("ChloeAI WebSocket connected"));
}

void FChloeWebSocketClient::HandleConnectionError(const FString& Error)
{
	UE_LOG(LogTemp, Error, TEXT("ChloeAI WebSocket error: %s"), *Error);
}

void FChloeWebSocketClient::HandleClosed(int32 StatusCode, const FString& Reason, bool bWasClean)
{
	UE_LOG(LogTemp, Log, TEXT("ChloeAI WebSocket closed: %d %s"), StatusCode, *Reason);
}

void FChloeWebSocketClient::HandleMessage(const FString& Message)
{
	OnSpeechJson.ExecuteIfBound(Message);
}
