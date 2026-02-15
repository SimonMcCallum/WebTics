// Copyright Simon McCallum. All Rights Reserved.

#include "WebTicsSubsystem.h"
#include "HttpModule.h"
#include "Interfaces/IHttpResponse.h"
#include "Json.h"
#include "JsonUtilities.h"

void UWebTicsSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);

	// Default configuration
	BaseURL = TEXT("http://localhost:8013");
	APIVersion = TEXT("v1");
	MetricSessionId = -1;
	PlaySessionId = -1;
	bIsSessionActive = false;
	bIsPlaySessionActive = false;

	UE_LOG(LogTemp, Log, TEXT("[WebTics] Subsystem initialized"));
}

void UWebTicsSubsystem::Deinitialize()
{
	// Close sessions on shutdown
	if (bIsPlaySessionActive)
	{
		ClosePlaySession();
	}

	if (bIsSessionActive)
	{
		CloseMetricSession();
	}

	Super::Deinitialize();
}

void UWebTicsSubsystem::Configure(const FString& URL)
{
	BaseURL = URL.TrimChar('/');
	UE_LOG(LogTemp, Log, TEXT("[WebTics] Configured with base URL: %s"), *BaseURL);
}

void UWebTicsSubsystem::OpenMetricSession(const FString& UniqueID, const FString& BuildNumber)
{
	if (bIsSessionActive)
	{
		UE_LOG(LogTemp, Warning, TEXT("[WebTics] Session already active. Close existing session first."));
		return;
	}

	// Create JSON payload
	TSharedPtr<FJsonObject> JsonObject = MakeShared<FJsonObject>();
	JsonObject->SetStringField(TEXT("unique_id"), UniqueID);
	JsonObject->SetStringField(TEXT("build_number"), BuildNumber);

	FString ContentString;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ContentString);
	FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);

	// Create HTTP request
	TSharedRef<IHttpRequest> Request = CreateHttpRequest(TEXT("/api/") + APIVersion + TEXT("/sessions"), TEXT("POST"));
	Request->SetContentAsString(ContentString);
	Request->OnProcessRequestComplete().BindUObject(this, &UWebTicsSubsystem::OnMetricSessionResponse);

	UE_LOG(LogTemp, Log, TEXT("[WebTics] Opening metric session for: %s"), *UniqueID);
	SendHttpRequest(Request);
}

void UWebTicsSubsystem::CloseMetricSession()
{
	if (!bIsSessionActive)
	{
		UE_LOG(LogTemp, Warning, TEXT("[WebTics] No active session to close."));
		return;
	}

	if (bIsPlaySessionActive)
	{
		ClosePlaySession();
	}

	FString Endpoint = FString::Printf(TEXT("/api/%s/sessions/%d/close"), *APIVersion, MetricSessionId);
	TSharedRef<IHttpRequest> Request = CreateHttpRequest(Endpoint, TEXT("POST"));
	Request->OnProcessRequestComplete().BindUObject(this, &UWebTicsSubsystem::OnCloseMetricSessionResponse);

	UE_LOG(LogTemp, Log, TEXT("[WebTics] Closing metric session: %d"), MetricSessionId);
	SendHttpRequest(Request);

	bIsSessionActive = false;
	MetricSessionId = -1;
}

void UWebTicsSubsystem::StartPlaySession()
{
	if (!bIsSessionActive)
	{
		UE_LOG(LogTemp, Error, TEXT("[WebTics] Cannot start play session without active metric session."));
		return;
	}

	if (bIsPlaySessionActive)
	{
		UE_LOG(LogTemp, Warning, TEXT("[WebTics] Play session already active."));
		return;
	}

	// Create JSON payload
	TSharedPtr<FJsonObject> JsonObject = MakeShared<FJsonObject>();
	JsonObject->SetNumberField(TEXT("metric_session_id"), MetricSessionId);

	FString ContentString;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ContentString);
	FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);

	// Create HTTP request
	TSharedRef<IHttpRequest> Request = CreateHttpRequest(TEXT("/api/") + APIVersion + TEXT("/play-sessions"), TEXT("POST"));
	Request->SetContentAsString(ContentString);
	Request->OnProcessRequestComplete().BindUObject(this, &UWebTicsSubsystem::OnPlaySessionResponse);

	UE_LOG(LogTemp, Log, TEXT("[WebTics] Starting play session for metric session: %d"), MetricSessionId);
	SendHttpRequest(Request);
}

void UWebTicsSubsystem::ClosePlaySession()
{
	if (!bIsPlaySessionActive)
	{
		UE_LOG(LogTemp, Warning, TEXT("[WebTics] No active play session to close."));
		return;
	}

	FString Endpoint = FString::Printf(TEXT("/api/%s/play-sessions/%d/close"), *APIVersion, PlaySessionId);
	TSharedRef<IHttpRequest> Request = CreateHttpRequest(Endpoint, TEXT("POST"));
	Request->OnProcessRequestComplete().BindUObject(this, &UWebTicsSubsystem::OnClosePlaySessionResponse);

	UE_LOG(LogTemp, Log, TEXT("[WebTics] Closing play session: %d"), PlaySessionId);
	SendHttpRequest(Request);

	bIsPlaySessionActive = false;
	PlaySessionId = -1;
}

void UWebTicsSubsystem::LogEvent(
	EWebTicsEventType EventType,
	int32 EventSubtype,
	int32 X,
	int32 Y,
	int32 Z,
	float Magnitude,
	const TMap<FString, FString>& AdditionalData)
{
	if (!bIsPlaySessionActive)
	{
		UE_LOG(LogTemp, Error, TEXT("[WebTics] Cannot log event without active play session."));
		return;
	}

	// Create JSON payload
	TSharedPtr<FJsonObject> JsonObject = MakeShared<FJsonObject>();
	JsonObject->SetNumberField(TEXT("event_type"), static_cast<int32>(EventType));
	JsonObject->SetNumberField(TEXT("event_subtype"), EventSubtype);
	JsonObject->SetNumberField(TEXT("x"), X);
	JsonObject->SetNumberField(TEXT("y"), Y);
	JsonObject->SetNumberField(TEXT("z"), Z);
	JsonObject->SetNumberField(TEXT("magnitude"), Magnitude);

	// Add additional data if provided
	if (AdditionalData.Num() > 0)
	{
		TSharedPtr<FJsonObject> DataObject = MakeShared<FJsonObject>();
		for (const auto& Pair : AdditionalData)
		{
			DataObject->SetStringField(Pair.Key, Pair.Value);
		}
		JsonObject->SetObjectField(TEXT("data"), DataObject);
	}

	FString ContentString;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&ContentString);
	FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);

	// Create HTTP request
	FString Endpoint = FString::Printf(TEXT("/api/%s/events?play_session_id=%d"), *APIVersion, PlaySessionId);
	TSharedRef<IHttpRequest> Request = CreateHttpRequest(Endpoint, TEXT("POST"));
	Request->SetContentAsString(ContentString);
	Request->OnProcessRequestComplete().BindUObject(this, &UWebTicsSubsystem::OnEventLoggedResponse);

	SendHttpRequest(Request);
}

void UWebTicsSubsystem::LogEventAtPosition(
	EWebTicsEventType EventType,
	FVector Position,
	float Magnitude,
	int32 EventSubtype)
{
	LogEvent(
		EventType,
		EventSubtype,
		static_cast<int32>(Position.X),
		static_cast<int32>(Position.Y),
		static_cast<int32>(Position.Z),
		Magnitude
	);
}

// HTTP Response Handlers

void UWebTicsSubsystem::OnMetricSessionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess)
{
	if (!bSuccess || !Response.IsValid())
	{
		OnWebTicsError.Broadcast(TEXT("Failed to create metric session"));
		return;
	}

	if (Response->GetResponseCode() >= 400)
	{
		FString ErrorMsg = FString::Printf(TEXT("Server error %d: %s"),
			Response->GetResponseCode(), *Response->GetContentAsString());
		OnWebTicsError.Broadcast(ErrorMsg);
		return;
	}

	// Parse JSON response
	TSharedPtr<FJsonObject> JsonObject;
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response->GetContentAsString());

	if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
	{
		MetricSessionId = JsonObject->GetIntegerField(TEXT("id"));
		bIsSessionActive = true;

		UE_LOG(LogTemp, Log, TEXT("[WebTics] Metric session created: %d"), MetricSessionId);
		OnSessionCreated.Broadcast(MetricSessionId);
	}
}

void UWebTicsSubsystem::OnCloseMetricSessionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess)
{
	if (bSuccess && Response.IsValid())
	{
		UE_LOG(LogTemp, Log, TEXT("[WebTics] Metric session closed successfully"));
	}
}

void UWebTicsSubsystem::OnPlaySessionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess)
{
	if (!bSuccess || !Response.IsValid())
	{
		OnWebTicsError.Broadcast(TEXT("Failed to create play session"));
		return;
	}

	if (Response->GetResponseCode() >= 400)
	{
		FString ErrorMsg = FString::Printf(TEXT("Server error %d: %s"),
			Response->GetResponseCode(), *Response->GetContentAsString());
		OnWebTicsError.Broadcast(ErrorMsg);
		return;
	}

	// Parse JSON response
	TSharedPtr<FJsonObject> JsonObject;
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response->GetContentAsString());

	if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
	{
		PlaySessionId = JsonObject->GetIntegerField(TEXT("id"));
		bIsPlaySessionActive = true;

		UE_LOG(LogTemp, Log, TEXT("[WebTics] Play session created: %d"), PlaySessionId);
		OnPlaySessionCreated.Broadcast(PlaySessionId);
	}
}

void UWebTicsSubsystem::OnClosePlaySessionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess)
{
	if (bSuccess && Response.IsValid())
	{
		UE_LOG(LogTemp, Log, TEXT("[WebTics] Play session closed successfully"));
	}
}

void UWebTicsSubsystem::OnEventLoggedResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess)
{
	if (!bSuccess || !Response.IsValid())
	{
		OnEventLogged.Broadcast(false);
		return;
	}

	if (Response->GetResponseCode() >= 400)
	{
		OnEventLogged.Broadcast(false);
		return;
	}

	OnEventLogged.Broadcast(true);
}

// Helper Functions

TSharedRef<IHttpRequest> UWebTicsSubsystem::CreateHttpRequest(const FString& Endpoint, const FString& Verb)
{
	TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
	Request->SetURL(BaseURL + Endpoint);
	Request->SetVerb(Verb);
	Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
	return Request;
}

void UWebTicsSubsystem::SendHttpRequest(TSharedRef<IHttpRequest> Request)
{
	Request->ProcessRequest();
}
