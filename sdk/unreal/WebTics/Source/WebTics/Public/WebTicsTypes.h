// Copyright Simon McCallum. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "WebTicsTypes.generated.h"

/**
 * Event types for WebTics telemetry
 * Matches the EventTypes defined in Godot and original WebTics
 */
UENUM(BlueprintType)
enum class EWebTicsEventType : uint8
{
	// Player events
	PLAYER_DEATH = 0 UMETA(DisplayName = "Player Death"),
	PLAYER_RESPAWN = 1 UMETA(DisplayName = "Player Respawn"),
	PLAYER_SHOOT = 2 UMETA(DisplayName = "Player Shoot"),
	PLAYER_HIT = 3 UMETA(DisplayName = "Player Hit"),

	// Navigation events
	WAYPOINT_REACHED = 10 UMETA(DisplayName = "Waypoint Reached"),
	LEVEL_COMPLETE = 11 UMETA(DisplayName = "Level Complete"),
	LEVEL_FAILED = 12 UMETA(DisplayName = "Level Failed"),

	// UI events
	BUTTON_CLICK = 20 UMETA(DisplayName = "Button Click"),
	MENU_OPEN = 21 UMETA(DisplayName = "Menu Open"),
	MENU_CLOSE = 22 UMETA(DisplayName = "Menu Close"),

	// Assessment events (for therapeutic/educational games)
	TASK_START = 100 UMETA(DisplayName = "Task Start"),
	TASK_COMPLETE = 101 UMETA(DisplayName = "Task Complete"),
	CORRECT_RESPONSE = 102 UMETA(DisplayName = "Correct Response"),
	INCORRECT_RESPONSE = 103 UMETA(DisplayName = "Incorrect Response"),
	TIMEOUT = 104 UMETA(DisplayName = "Timeout"),

	// ADHD assessment specific
	ATTENTION_TASK = 200 UMETA(DisplayName = "Attention Task"),
	IMPULSIVE_RESPONSE = 201 UMETA(DisplayName = "Impulsive Response"),
	SUSTAINED_ATTENTION = 202 UMETA(DisplayName = "Sustained Attention"),
	SELECTIVE_ATTENTION = 203 UMETA(DisplayName = "Selective Attention"),

	// Custom events
	CUSTOM = 255 UMETA(DisplayName = "Custom")
};

/**
 * Structure for event data to be logged
 */
USTRUCT(BlueprintType)
struct FWebTicsEventData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "WebTics")
	int32 EventType;

	UPROPERTY(BlueprintReadWrite, Category = "WebTics")
	int32 EventSubtype;

	UPROPERTY(BlueprintReadWrite, Category = "WebTics")
	int32 X;

	UPROPERTY(BlueprintReadWrite, Category = "WebTics")
	int32 Y;

	UPROPERTY(BlueprintReadWrite, Category = "WebTics")
	int32 Z;

	UPROPERTY(BlueprintReadWrite, Category = "WebTics")
	float Magnitude;

	UPROPERTY(BlueprintReadWrite, Category = "WebTics")
	TMap<FString, FString> AdditionalData;

	FWebTicsEventData()
		: EventType(0)
		, EventSubtype(0)
		, X(0)
		, Y(0)
		, Z(0)
		, Magnitude(0.0f)
	{}
};

/**
 * Delegates for async callbacks
 */
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSessionCreated, int32, SessionId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPlaySessionCreated, int32, PlaySessionId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnEventLogged, bool, bSuccess);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnWebTicsError, FString, ErrorMessage);
