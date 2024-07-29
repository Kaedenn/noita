read_globals = {
"load_imgui",
--"check_parallel_pos",
--"get_players",
--"orb_map_get",
"print_error",
"async",
"wait",

"EntityLoad",
"EntityLoadEndGameItem",
"EntityLoadCameraBound",
"EntityLoadToEntity",
"EntitySave",
"EntityCreateNew",
"EntityKill",
"EntityGetIsAlive",
"EntityAddComponent",
"EntityRemoveComponent",
"EntityGetAllComponents",
"EntityGetComponent",
"EntityGetFirstComponent",
"EntityGetComponentIncludingDisabled",
"EntityGetFirstComponentIncludingDisabled",
"EntitySetTransform",
"EntityApplyTransform",
"EntityGetTransform",
"EntityAddChild",
"EntityGetAllChildren",
"EntityGetParent",
"EntityGetRootEntity",
"EntityRemoveFromParent",
"EntitySetComponentsWithTagEnabled",
"EntitySetComponentIsEnabled",
"EntityGetName",
"EntitySetName",
"EntityGetTags",
"EntityGetWithTag",
"EntityGetInRadius",
"EntityGetInRadiusWithTag",
"EntityGetClosest",
"EntityGetClosestWithTag",
"EntityGetWithName",
"EntityAddTag",
"EntityRemoveTag",
"EntityHasTag",
"EntityGetFilename",
"ComponentGetValue",
"ComponentGetValueBool",
"ComponentGetValueInt",
"ComponentGetValueFloat",
"ComponentGetValueVector2",
"ComponentSetValue",
"ComponentSetValueVector2",
"ComponentSetValueValueRange",
"ComponentSetValueValueRangeInt",
"ComponentSetMetaCustom",
"ComponentGetMetaCustom",
"ComponentObjectGetValue",
"ComponentObjectGetValueBool",
"ComponentObjectGetValueInt",
"ComponentObjectGetValueFloat",
"ComponentObjectSetValue",
"ComponentAddTag",
"ComponentRemoveTag",
"ComponentHasTag",
"ComponentGetValue2",
"ComponentSetValue2",
"ComponentObjectGetValue2",
"ComponentObjectSetValue2",
"EntityAddComponent2",
"ComponentGetVectorSize",
"ComponentGetVectorValue",
"ComponentGetVector",
"ComponentGetIsEnabled",
"ComponentGetMembers",
"ComponentObjectGetMembers",
"ComponentGetTypeName",
"GetUpdatedEntityID",
"GetUpdatedComponentID",
"SetTimeOut",
"RegisterSpawnFunction",
"SpawnActionItem",
"SpawnStash",
"SpawnApparition",
"LoadEntityToStash",
"AddMaterialInventoryMaterial",
"GetMaterialInventoryMainMaterial",
"GameScreenshake",
"GameOnCompleted",
"GameGiveAchievement",
"GameDoEnding2",
"GetParallelWorldPosition",
"BiomeMapLoad_KeepPlayer",
"BiomeMapLoad",
"BiomeSetValue",
"BiomeGetValue",
"BiomeObjectSetValue",
"BiomeVegetationSetValue",
"BiomeMaterialSetValue",
"BiomeMaterialGetValue",
"GameIsIntroPlaying",
"GameGetIsGamepadConnected",
"GameGetWorldStateEntity",
"GameGetPlayerStatsEntity",
"GameGetOrbCountAllTime",
"GameGetOrbCountThisRun",
"GameGetOrbCollectedThisRun",
"GameGetOrbCollectedAllTime",
"GameClearOrbsFoundThisRun",
"GameGetOrbCountTotal",
"CellFactory_GetName",
"CellFactory_GetType",
"CellFactory_GetUIName",
"CellFactory_GetAllLiquids",
"CellFactory_GetAllSands",
"CellFactory_GetAllGases",
"CellFactory_GetAllFires",
"CellFactory_GetAllSolids",
"CellFactory_GetTags",
"GameGetCameraPos",
"GameSetCameraPos",
"GameSetCameraFree",
"GameGetCameraBounds",
"GameRegenItemAction",
"GameRegenItemActionsInContainer",
"GameRegenItemActionsInPlayer",
"GameKillInventoryItem",
"GamePickUpInventoryItem",
"GameGetAllInventoryItems",
"GameDropAllItems",
"GameDropPlayerInventoryItems",
"GameDestroyInventoryItems",
"GameIsInventoryOpen",
"GameTriggerGameOver",
"LoadPixelScene",
"LoadBackgroundSprite",
"GameCreateCosmeticParticle",
"GameCreateParticle",
"GameCreateSpriteForXFrames",
"GameShootProjectile",
"EntityInflictDamage",
"EntityIngestMaterial",
"EntityRemoveIngestionStatusEffect",
"EntityAddRandomStains",
"EntitySetDamageFromMaterial",
"EntityRefreshSprite",
"EntityGetWandCapacity",
"GamePlayAnimation",
"GameGetVelocityCompVelocity",
"GameGetGameEffect",
"GameGetGameEffectCount",
"LoadGameEffectEntityTo",
"GetGameEffectLoadTo",
"SetPlayerSpawnLocation",
"UnlockItem",
"GameGetPotionColorUint",
"EntityGetFirstHitboxCenter",
"Raytrace",
"RaytraceSurfaces",
"RaytraceSurfacesAndLiquiform",
"RaytracePlatforms",
"FindFreePositionForBody",
"GetSurfaceNormal",
"DoesWorldExistAt",
"StringToHerdId",
"HerdIdToString",
"GetHerdRelation",
"EntityGetHerdRelation",
"EntityGetHerdRelationSafe",
"GenomeSetHerdId",
"EntityGetClosestWormAttractor",
"EntityGetClosestWormDetractor",
"GamePrint",
"GamePrintImportant",
"DEBUG_GetMouseWorld",
"DEBUG_MARK",
"GameGetFrameNum",
"GameGetRealWorldTimeSinceStarted",
"IsPlayer",
"IsInvisible",
"GameIsDailyRun",
"GameIsDailyRunOrDailyPracticeRun",
"GameIsModeFullyDeterministic",
"GlobalsSetValue",
"GlobalsGetValue",
"MagicNumbersGetValue",
"SetWorldSeed",
"SessionNumbersGetValue",
"SessionNumbersSetValue",
"SessionNumbersSave",
"AutosaveDisable",
"StatsGetValue",
"StatsGlobalGetValue",
"StatsBiomeGetValue",
"StatsBiomeReset",
"StatsLogPlayerKill",
"CreateItemActionEntity",
"GetRandomActionWithType",
"GetRandomAction",
"GameGetDateAndTimeUTC",
"GameGetDateAndTimeLocal",
"GameEmitRainParticles",
"GameCutThroughWorldVertical",
"BiomeMapSetSize",
"BiomeMapGetSize",
"BiomeMapSetPixel",
"BiomeMapGetPixel",
"BiomeMapConvertPixelFromUintToInt",
"BiomeMapLoadImage",
"BiomeMapLoadImageCropped",
"BiomeMapGetVerticalPositionInsideBiome",
"BiomeMapGetName",
"SetRandomSeed",
"Random",
"Randomf",
"RandomDistribution",
"RandomDistributionf",
"ProceduralRandom",
"ProceduralRandomf",
"ProceduralRandomi",
"PhysicsAddBodyImage",
"PhysicsAddBodyCreateBox",
"PhysicsAddJoint",
"PhysicsApplyForce",
"PhysicsApplyTorque",
"PhysicsApplyTorqueToComponent",
"PhysicsApplyForceOnArea",
"PhysicsRemoveJoints",
"PhysicsSetStatic",
"PhysicsGetComponentVelocity",
"PhysicsGetComponentAngularVelocity",
"PhysicsBody2InitFromComponents",
"PhysicsVecToGameVec",
"GameVecToPhysicsVec",
"LooseChunk",
"AddFlagPersistent",
"RemoveFlagPersistent",
"HasFlagPersistent",
"GameAddFlagRun",
"GameRemoveFlagRun",
"GameHasFlagRun",
"GameTriggerMusicEvent",
"GameTriggerMusicCue",
"GameTriggerMusicFadeOutAndDequeueAll",
"GamePlaySound",
"GameEntityPlaySound",
"GameEntityPlaySoundLoop",
"GameSetPostFxParameter",
"GameUnsetPostFxParameter",
"GameTextGetTranslatedOrNot",
"GameTextGet",
"GuiCreate",
"GuiDestroy",
"GuiStartFrame",
"GuiOptionsAdd",
"GuiOptionsRemove",
"GuiOptionsClear",
"GuiOptionsAddForNextWidget",
"GuiColorSetForNextWidget",
"GuiZSet",
"GuiZSetForNextWidget",
"GuiIdPush",
"GuiIdPushString",
"GuiIdPop",
"GuiAnimateBegin",
"GuiAnimateEnd",
"GuiAnimateAlphaFadeIn",
"GuiAnimateScaleIn",
"GuiText",
"GuiTextCentered",
"GuiImage",
"GuiImageNinePiece",
"GuiButton",
"GuiImageButton",
"GuiSlider",
"GuiTextInput",
"GuiBeginAutoBox",
"GuiEndAutoBoxNinePiece",
"GuiTooltip",
"GuiBeginScrollContainer",
"GuiEndScrollContainer",
"GuiLayoutBeginHorizontal",
"GuiLayoutBeginVertical",
"GuiLayoutAddHorizontalSpacing",
"GuiLayoutAddVerticalSpacing",
"GuiLayoutEnd",
"GuiLayoutBeginLayer",
"GuiLayoutEndLayer",
"GuiGetScreenDimensions",
"GuiGetTextDimensions",
"GuiGetImageDimensions",
"GuiGetPreviousWidgetInfo",
"GameIsBetaBuild",
"DebugGetIsDevBuild",
"DebugEnableTrailerMode",
"GameGetIsTrailerModeEnabled",
"Debug_SaveTestPlayer",
"DebugBiomeMapGetFilename",
"EntityConvertToMaterial",
"ConvertEverythingToGold",
"ConvertMaterialEverywhere",
"ConvertMaterialOnAreaInstantly",
"GetDailyPracticeRunSeed",
"ModIsEnabled",
"ModGetActiveModIDs",
"ModGetAPIVersion",
"ModSettingGet",
"ModSettingSet",
"ModSettingGetNextValue",
"ModSettingSetNextValue",
"ModSettingRemove",
"ModSettingGetCount",
"ModSettingGetAtIndex",
"StreamingGetIsConnected",
"StreamingGetConnectedChannelName",
"StreamingGetVotingCycleDurationFrames",
"StreamingGetRandomViewerName",
"StreamingGetSettingsGhostsNamedAfterViewers",
"StreamingSetCustomPhaseDurations",
"StreamingForceNewVoting",
"StreamingSetVotingEnabled",
"ModLuaFileAppend",
"ModTextFileGetContent",
"ModTextFileSetContent",
"ModTextFileWhoSetContent",
"ModMagicNumbersFileAdd",
"ModMaterialsFileAdd",
"ModRegisterAudioEventMappings",
"ModDevGenerateSpriteUVsForDirectory",
"RegisterProjectile",
"RegisterGunAction",
"RegisterGunShotEffects",
"BeginProjectile",
"EndProjectile",
"BeginTriggerTimer",
"BeginTriggerHitWorld",
"BeginTriggerDeath",
"EndTrigger",
"SetProjectileConfigs",
"StartReload",
"ActionUsesRemainingChanged",
"ActionUsed",
"LogAction",
"OnActionPlayed",
"OnNotEnoughManaForAction",
"BaabInstruction",
"SetValueNumber",
"GetValueNumber",
"SetValueInteger",
"GetValueInteger",
"SetValueBool",
"GetValueBool",
"dofile",
"dofile_once",
}
