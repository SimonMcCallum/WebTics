// Copyright Simon McCallum. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Interfaces/IHttpRequest.h"
#include "WebTicsTypes.h"
#include "WebTicsSubsystem.generated.h"

/**
 * WebTics Telemetry Subsystem for Unreal Engine
 *
 * Provides game telemetry and metrics collection with automatic session management.
 *
 * Usage:
 *   UWebTicsSubsystem* WebTics = GetGameInstance()->GetSubsystem<UWebTicsSubsystem>();
 *   WebTics->Configure("http://localhost:8013");
 *   WebTics->OpenMetricSession("player_123", "1.0.0");
 *   WebTics->StartPlaySession();
 *   WebTics->LogEvent(EWebTicsEventType::PLAYER_DEATH, 0);
 *   WebTics->ClosePlaySession();
 *   WebTics->CloseMetricSession();
 */
UCLASS()
class WEBTICS_API UWebTicsSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	// USubsystem interface
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

	/**
	 * Configure the WebTics backend URL
	 * @param URL - Base URL of the WebTics backend (e.g., "http://localhost:8013")
	 */
	UFUNCTION(BlueprintCallable, Category = "WebTics")
	void Configure(const FString& URL);

	/**
	 * Open a new metric session
	 * @param UniqueID - Unique identifier for this player/session
	 * @param BuildNumber - Game build/version number
	 */
	UFUNCTION(BlueprintCallable, Category = "WebTics")
	void OpenMetricSession(const FString& UniqueID, const FString& BuildNumber = TEXT(""));

	/**
	 * Close the current metric session
	 */
	UFUNCTION(BlueprintCallable, Category = "WebTics")
	void CloseMetricSession();

	/**
	 * Start a new play session within the current metric session
	 */
	UFUNCTION(BlueprintCallable, Category = "WebTics")
	void StartPlaySession();

	/**
	 * Close the current play session
	 */
	UFUNCTION(BlueprintCallable, Category = "WebTics")
	void ClosePlaySession();

	/**
	 * Log a single telemetry event
	 * @param EventType - Type of event
	 * @param EventSubtype - Subtype of event (default 0)
	 * @param X - X coordinate (default 0)
	 * @param Y - Y coordinate (default 0)
	 * @param Z - Z coordinate (default 0)
	 * @param Magnitude - Event magnitude/value (default 0.0)
	 * @param AdditionalData - Optional additional data as key-value pairs
	 */
	UFUNCTION(BlueprintCallable, Category = "WebTics")
	void LogEvent(
		EWebTicsEventType EventType,
		int32 EventSubtype = 0,
		int32 X = 0,
		int32 Y = 0,
		int32 Z = 0,
		float Magnitude = 0.0f,
		const TMap<FString, FString>& AdditionalData = TMap<FString, FString>()
	);

	/**
	 * Log event with FVector position
	 * @param EventType - Type of event
	 * @param Position - 3D position vector
	 * @param Magnitude - Event magnitude/value
	 * @param EventSubtype - Subtype of event
	 */
	UFUNCTION(BlueprintCallable, Category = "WebTics", meta = (AdvancedDisplay = "EventSubtype"))
	void LogEventAtPosition(
		EWebTicsEventType EventType,
		FVector Position,
		float Magnitude = 0.0f,
		int32 EventSubtype = 0
	);

	/**
	 * Check if a metric session is currently active
	 */
	UFUNCTION(BlueprintPure, Category = "WebTics")
	bool IsSessionActive() const { return bIsSessionActive; }

	/**
	 * Check if a play session is currently active
	 */
	UFUNCTION(BlueprintPure, Category = "WebTics")
	bool IsPlaySessionActive() const { return bIsPlaySessionActive; }

	// Delegates
	UPROPERTY(BlueprintAssignable, Category = "WebTics")
	FOnSessionCreated OnSessionCreated;

	UPROPERTY(BlueprintAssignable, Category = "WebTics")
	FOnPlaySessionCreated OnPlaySessionCreated;

	UPROPERTY(BlueprintAssignable, Category = "WebTics")
	FOnEventLogged OnEventLogged;

	UPROPERTY(BlueprintAssignable, Category = "WebTics")
	FOnWebTicsError OnWebTicsError;

private:
	// HTTP request handlers
	void OnMetricSessionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);
	void OnCloseMetricSessionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);
	void OnPlaySessionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);
	void OnClosePlaySessionResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);
	void OnEventLoggedResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);

	// Helper functions
	TSharedRef<IHttpRequest> CreateHttpRequest(const FString& Endpoint, const FString& Verb = TEXT("GET"));
	void SendHttpRequest(TSharedRef<IHttpRequest> Request);

	// Configuration
	UPROPERTY()
	FString BaseURL;

	UPROPERTY()
	FString APIVersion;

	// Session state
	UPROPERTY()
	int32 MetricSessionId;

	UPROPERTY()
	int32 PlaySessionId;

	UPROPERTY()
	bool bIsSessionActive;

	UPROPERTY()
	bool bIsPlaySessionActive;
};
