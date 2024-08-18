-- Emulate some functions implemented by Noita

io = require 'io'
os = require 'os'

DEV_ROOT = os.getenv("HOME") .. "/Programming/Noita"
DATA_PREFIX = DEV_ROOT .. "/ref/"
MODS_PREFIX = DEV_ROOT .. "/mods/"

mod_setting_cache = {}
globals_cache = {
  ["ORB_MAP_STRING"] = "8,1 1,-3 -9,7 -8,19 -18,28 -20,5 -1,31 20,31 19,5 6,3 19,-3",
  ["NEW_GAME_PLUS_COUNT"] = "0",
}

session_numbers = {
  ["world_seed"] = 0,
  ["NEW_GAME_PLUS_COUNT"] = 0,
}

local function _repr(value)
  if type(value) == "nil" then return tostring(value) end
  if type(value) == "boolean" then return tostring(value) end
  if type(value) == "function" then return tostring(value) end
  if type(value) == "number" then return tostring(value) end
  if type(value) == "string" then return ("%q"):format(value) end
  if type(value) == "userdata" then return tostring(value) end
  if type(value) == "table" then
    local count = 0
    for _ in pairs(value) do count = count + 1 end
    return ("table[%d]{%d}"):format(#value, count)
  end

  return ("unknown[%s] %q"):format(type(value), tostring(value))
end

function print_error(message)
  io.stderr:write(("ERROR: %s\n"):format(message))
  io.stderr:write(debug.traceback() .. "\n")
end

function GamePrint(message)
  io.stderr:write(("GamePrint: %s\n"):format(message))
end

function GamePrintImportant(title, description, ui_custom_decoration_file)
  io.stderr:write(("!! GamePrint: %s\n"):format(title))
  if description then
    io.stderr:write(("!! GamePrint: %s\n"):format(description))
  end
end

function ModSettingGet(conf_var)
  local value = mod_setting_cache[conf_var]
  GamePrint(("ModSettingGet(%q) => %s"):format(conf_var, _repr(value)))
  return value
end

--[[function ModSettingGetAtIndex(index) TODO
  for idx, name in ipairs(mod_setting_cache) do
    if idx = index then
      return {}
    end
  end
end]]

function ModSettingGetCount() return #mod_setting_cache end

ModSettingGetNextValue = ModSettingGet

function ModSettingSet(conf_var, value)
  GamePrint(("ModSettingSet(%q, %s)"):format(conf_var, _repr(value)))
  mod_setting_cache[conf_var] = value
end

function ModSettingSetNextValue(conf_var, value, is_default)
  GamePrint(("ModSettingSetNextValue(%q, %s, default=%s)"):format(
    conf_var, _repr(value), _repr(is_default)))
  mod_setting_cache[conf_var] = value
end

function GlobalsSetValue(key, value)
  globals_cache[key] = tostring(value)
end

function GlobalsGetValue(key, default)
  if globals_cache[key] == nil then GamePrint(("GlobalsGetValue(%q): not defined"):format(key)) end
  return globals_cache[key] or (default or "")
end

function ModTextFileGetContent(filepath)
  local finalpath = filepath
  if filepath:match("^data/") then
    finalpath = DATA_PREFIX .. filepath
  elseif filepath:match("^mods/") then
    finalpath = MODS_PREFIX .. filepath
  end
  if finalpath ~= filepath then
    GamePrint(("Rewrote %q to %q"):format(filepath, finalpath))
  end
  local fobj, err, errno = io.open(finalpath, "r")
  if fobj == nil then
    GamePrintImportant(("Error opening %q: error %d: %s"):format(finalpath, errno, err))
    return nil
  end
  local data = fobj:read("*all")
  fobj:close()
  return data
end

function BiomeMapGetSize()
  local newgame_n = tonumber(GlobalsGetValue("NEW_GAME_PLUS_COUNT"))
  if newgame_n == 0 then
    return 70, 48
  end
  return 64, 48
end

function GameTextGet(text, param0, param1, param2) -- TODO
  -- luacheck: globals I18N
  if not I18N.initialized then
    I18N:init()
  end
  return I18N:get(text)
end

function GameTextGetTranslatedOrNot(text)
  print(("GameTextGetTranslatedOrNot(%q) -- STUB"):format(text))
  return GameTextGet(text)
end

function load_imgui(vinfo)
  if not vinfo then vinfo = {} end
  if type(vinfo) == "string" then vinfo = {mod=vinfo} end
  local version = vinfo.version or "unknown"
  local mod = vinfo.mod or "unknown"
  print(("load_imgui(version=%q, mod=%q)"):format(version, mod))
  return {}
end

--[[ STUBS ]]
function SessionNumbersGetValue(varname)
  local value = session_numbers[varname]
  if value then
    return value
  end
  print(("SessionNumbersGetValue(%q) -- STUB"):format(varname))
  return 0
end

function ModTextFileSetContent(filepath, content)
  print(("ModTextFileSetContent(%q, %d) -- STUB"):format(filepath, content.length))
end

function BiomeMapGetName(biome_x, biome_y)
  print(("BiomeMapGetName(%d, %d) -- STUB"):format(biome_x, biome_y))
  return "_EMPTY_"
end

function GameGetOrbCollectedThisRun(orb_id)
  print(("GameGetOrbCollectedThisRun(%d) -- STUB"):format(orb_id))
  return false
end

function BiomeGetValue(biome_name, key)
  print(("BiomeGetValue(%q, %q) -- STUB"):format(biome_name, key))
  return ""
end

setmetatable(_G, {
  __index = function(self, key)
    if not key:match("^_") then
      io.stderr:write(("_G[%s] not defined\n"):format(_repr(key)))
    end
    return nil
  end
})

--[[
ActionUsed( inventoryitem_id:int )
ActionUsesRemainingChanged( inventoryitem_id:int, uses_remaining:int )
AddFlagPersistent( key:string )
AddMaterialInventoryMaterial( entity_id:int, material_name:string, count:int )
AutosaveDisable()
BaabInstruction( name:string )
BeginProjectile( entity_filename:string )
BeginTriggerDeath()
BeginTriggerHitWorld()
BeginTriggerTimer( timeout_frames:int )
BiomeGetValue( filename:string, field_name:string )
BiomeMapConvertPixelFromUintToInt( color:int )
BiomeMapGetName( x:number = camera_x, y:number = camera_y )
BiomeMapGetPixel( x:int, y:int )
--BiomeMapGetSize()
BiomeMapGetVerticalPositionInsideBiome( x:number, y:number )
BiomeMapLoad( filename:string )
BiomeMapLoadImage( x:int, y:int, image_filename:string )
BiomeMapLoadImageCropped( x:int, y:int, image_filename:string, image_x:int, image_y:int, image_w:int, image_h:int )
BiomeMapLoad_KeepPlayer( filename:string, pixel_scenes:string = "data/biome/_pixel_scenes.xml" )
BiomeMapSetPixel( x:int, y:int, color_int:int )
BiomeMapSetSize( width:int, height:int )
BiomeMaterialGetValue( filename:string, material_name:string, field_name:string )
BiomeMaterialSetValue( filename:string, material_name:string, field_name:string, value:multiple_types )
BiomeObjectSetValue( filename:string, meta_object_name:string, field_name:string, value:multiple_types )
BiomeSetValue( filename:string, field_name:string, value:multiple_types )
BiomeVegetationSetValue( filename:string, material_name:string, field_name:string, value:multiple_types )
CellFactory_GetAllFires( include_statics:bool = true, include_particle_fx_materials:bool = false )
CellFactory_GetAllGases( include_statics:bool = true, include_particle_fx_materials:bool = false )
CellFactory_GetAllLiquids( include_statics:bool = true, include_particle_fx_materials:bool = false )
CellFactory_GetAllSands( include_statics:bool = true, include_particle_fx_materials:bool = false )
CellFactory_GetAllSolids( include_statics:bool = true, include_particle_fx_materials:bool = false )
CellFactory_GetName( material_id:int )
CellFactory_GetTags( material_id:int )
CellFactory_GetType( material_name:string )
CellFactory_GetUIName( material_id:int )
ComponentAddTag( component_id:int, tag:string )
ComponentGetIsEnabled( component_id:int )
ComponentGetMembers( component_id:int )
ComponentGetMetaCustom( component_id:int, variable_name:string )
ComponentGetTypeName( component_id:int )
ComponentGetValue( component_id:int, variable_name:string )
ComponentGetValue2( component_id:int, field_name:string )
ComponentGetValueBool( component_id:int, variable_name:string )
ComponentGetValueFloat( component_id:int, variable_name:string )
ComponentGetValueInt( component_id:int, variable_name:string )
ComponentGetValueVector2( component_id:int, variable_name:string )
ComponentGetVector( component_id:int, array_name:string, type_stored_in_vector:string )
ComponentGetVectorSize( component_id:int, array_member_name:string, type_stored_in_vector:string )
ComponentGetVectorValue( component_id:int, array_name:string, type_stored_in_vector:string, index:int )
ComponentHasTag( component_id:int, tag:string )
ComponentObjectGetMembers( component_id:int, object_name:string )
ComponentObjectGetValue( component_id:int, object_name:string, variable_name:string )
ComponentObjectGetValue2( component_id:int, object_name:string, field_name:string )
ComponentObjectGetValueBool( component_id:int, object_name:string, variable_name:string )
ComponentObjectGetValueFloat( component_id:int, object_name:string, variable_name:string )
ComponentObjectGetValueInt( component_id:int, object_name:string, variable_name:string )
ComponentObjectSetValue( component_id:int, object_name:string, variable_name:string, value:string )
ComponentObjectSetValue2( component_id:int, object_name:string, field_name:string, value_or_values:multiple_types )
ComponentRemoveTag( component_id:int, tag:string )
ComponentSetMetaCustom( component_id:int, variable_name:string, value:string )
ComponentSetValue( component_id:int, variable_name:string, value:string )
ComponentSetValue2( component_id:int, field_name:string, value_or_values:multiple_types )
ComponentSetValueValueRange( component_id:int, variable_name:string, min:number, max:number )
ComponentSetValueValueRangeInt( component_id:int, variable_name:string, min:number, max:number )
ComponentSetValueVector2( component_id:int, variable_name:string, x:number, y:number )
ConvertEverythingToGold( material_dynamic:string = "", material_static:string = "" )
ConvertMaterialEverywhere( material_from_type:int, material_to_type:int )
ConvertMaterialOnAreaInstantly( area_x:int, area_y:int, area_w:int, area_h:int, material_from_type:int, material_to_type:int, trim_box2d:bool, update_edge_graphics_dummy:bool )
CreateItemActionEntity( action_id:string, x:number = 0, y:number = 0 )
DEBUG_GetMouseWorld()
DEBUG_MARK( x:number, y:number, message:string = "", color_r:number = 1, color_g:number = 0, color_b:number = 0 )
DebugBiomeMapGetFilename( x:number = camera_x, y:number = camera_y )
DebugEnableTrailerMode()
DebugGetIsDevBuild()
Debug_SaveTestPlayer()
DoesWorldExistAt( min_x:int, min_y:int, max_x:int, max_y:int )
EndProjectile()
EndTrigger()
EntityAddChild( parent_id:int, child_id:int )
EntityAddComponent( entity_id:int, component_type_name:string, table_of_component_values:{string} = nil )
EntityAddComponent2( entity_id:int, component_type_name, table_of_component_values:{string-multiple_types} = nil )
EntityAddRandomStains( entity:int, material_type:number, amount:number )
EntityAddTag( entity_id:int, tag:string )
EntityApplyTransform( entity_id:int, x:number, y:number = 0, rotation:number = 0, scale_x:number = 1, scale_y:number = 1 )
EntityConvertToMaterial( entity_id:int, material:string )
EntityCreateNew( name:string = "" )
EntityGetAllChildren( entity_id:int )
EntityGetAllComponents( entity_id:int )
EntityGetClosest( pos_x:number, pos_y:number )
EntityGetClosestWithTag(  pos_x:number, pos_y:number, tag:string )
EntityGetClosestWormAttractor( pos_x:number, pos_y:number )
EntityGetClosestWormDetractor( pos_x:number, pos_y:number )
EntityGetComponent( entity_id:int, component_type_name:string, tag:string = "" )
EntityGetComponentIncludingDisabled( entity_id:int, component_type_name:string, tag:string = "" )
EntityGetFilename( entity_id:int )
EntityGetFirstComponent( entity_id:int, component_type_name:string, tag:string = "" )
EntityGetFirstComponentIncludingDisabled( entity_id:int, component_type_name:string, tag:string = "" )
EntityGetFirstHitboxCenter( entity_id:int )
EntityGetHerdRelation( entity_a:int, entity_b:int )
EntityGetHerdRelationSafe( entity_a:int, entity_b:int )
EntityGetInRadius( pos_x:number, pos_y:number, radius:number )
EntityGetInRadiusWithTag( pos_x:number, pos_y:number, radius:number, entity_tag:string )
EntityGetIsAlive( entity_id:int )
EntityGetName( entity_id:int )
EntityGetParent( entity_id:int )
EntityGetRootEntity( entity_id:int )
EntityGetTags( entity_id:int )
EntityGetTransform( entity_id:int )
EntityGetWandCapacity( entity:int )
EntityGetWithName( name:string )
EntityGetWithTag( tag:string )
EntityHasTag( entity_id:int, tag:string )
EntityInflictDamage( entity:int, amount:number, damage_type:string, description:string, ragdoll_fx:string, impulse_x:number, impulse_y:number, entity_who_is_responsible:int = 0, world_pos_x:number = entity_x, world_pos_y:number = entity_y, knockback_force:number = 0 )
EntityIngestMaterial( entity:int, material_type:number, amount:number )
EntityKill( entity_id:int )
EntityLoad( filename:string, pos_x:number = 0, pos_y:number = 0 )
EntityLoadCameraBound( filename:string, pos_x:number = 0, pos_y:number = 0 )
EntityLoadEndGameItem( filename:string, pos_x:number = 0, pos_y:number = 0 )
EntityLoadToEntity( filename:string, entity:int )
EntityRefreshSprite( entity:int, sprite_component:int )
EntityRemoveComponent( entity_id:int, component_id:int )
EntityRemoveFromParent( entity_id:int )
EntityRemoveIngestionStatusEffect( entity:int, status_type_id:string )
EntityRemoveTag( entity_id:int, tag:string )
EntitySave( entity_id:int, filename:string )
EntitySetComponentIsEnabled( entity_id:int, component_id:int, is_enabled:bool )
EntitySetComponentsWithTagEnabled( entity_id:int, tag:string, enabled:bool )
EntitySetDamageFromMaterial( entity:int, material_name:string, damage:number )
EntitySetName( entity_id:int, name:string )
EntitySetTransform( entity_id:int, x:number, y:number = 0, rotation:number = 0, scale_x:number = 1, scale_y:number = 1 )
FindFreePositionForBody( ideal_pos_x:number, idea_pos_y:number, velocity_x:number, velocity_y:number, body_radius:number )
GameAddFlagRun( flag:string )
GameClearOrbsFoundThisRun()
GameCreateParticle( material_name:string, x:number, y:number, how_many:int, xvel:number, yvel:number, just_visual:bool, draw_as_long:bool = false )
GameCreateSpriteForXFrames( filename:string, x:number, y:number, centered:bool = true, sprite_offset_x:number = 0, sprite_offset_y:number = 0, frames:int = 1, emissive:bool = false )
GameCutThroughWorldVertical( x:int, y_min:int, y_max:int, radius:number, edge_darkening_width:number )
GameDestroyInventoryItems( entity_id:int )
GameDoEnding2()
GameDropAllItems( entity_id:int )
GameDropPlayerInventoryItems( entity_id:int )
GameEmitRainParticles( num_particles:int, width_outside_camera:number, material_name:string, velocity_min:number, velocity_max:number, gravity:number, droplets_bounce:bool, draw_as_long:bool )
GameEntityPlaySound( entity_id:int, event_name:string )
GameEntityPlaySoundLoop( entity:int, component_tag:string, intensity:number )
GameGetCameraBounds()
GameGetCameraPos()
GameGetDateAndTimeLocal() ->year:int,month:int,day:int,hour:int,minute:int,second:int
GameGetDateAndTimeUTC()
GameGetFrameNum()
GameGetGameEffect( entity_id:int, game_effect_name:string )
GameGetGameEffectCount( entity_id:int, game_effect_name:string )
GameGetIsGamepadConnected()
GameGetIsTrailerModeEnabled()
GameGetOrbCollectedAllTime( orb_id_zero_based:int )
GameGetOrbCollectedThisRun( orb_id_zero_based:int )
GameGetOrbCountAllTime()
GameGetOrbCountThisRun()
GameGetOrbCountTotal()
GameGetPlayerStatsEntity()
GameGetPotionColorUint( entity_id:int )
GameGetRealWorldTimeSinceStarted()
GameGetVelocityCompVelocity( entity_id:int )
GameGetWorldStateEntity()
GameGiveAchievement( id:string )
GameHasFlagRun( flag:string )
GameIsBetaBuild()
GameIsDailyRun()
GameIsDailyRunOrDailyPracticeRun()
GameIsIntroPlaying()
GameIsInventoryOpen()
GameIsModeFullyDeterministic()
GameKillInventoryItem( inventory_owner_entity_id:int, item_entity_id:int )
GameOnCompleted()
GamePickUpInventoryItem( who_picks_up_entity_id:int, item_entity_id:int, do_pick_up_effects:bool = true )
GamePlayAnimation( entity_id:int, name:string, priority:int, followup_name:string = "", followup_priority:int = 0 )
GamePlaySound( bank_filename:string, event_path:string, x:number, y:number )
GameRegenItemAction( entity_id:int )
GameRegenItemActionsInContainer( entity_id:int )
GameRegenItemActionsInPlayer( entity_id:int )
GameRemoveFlagRun( flag:string )
GameScreenshake( strength:number, x:number = camera_x, y:number = camera_y )
GameSetCameraFree( is_free:bool )
GameSetCameraPos( x:number, y:number )
GameSetPostFxParameter( name:string, x:number, y:number, z:number, w:number )
GameShootProjectile( shooter_entity:int, x:number, y:number, target_x:number, target_y:number, projectile_entity:int, send_message:bool = true, verlet_parent_entity:int = 0 )
GameTextGet( key:string, param0:string = "", param1:string = "", param2:string = "" )
GameTextGetTranslatedOrNot( text_or_key:string )
GameTriggerGameOver()
GameTriggerMusicCue( name:string )
GameTriggerMusicEvent( event_path:string, can_be_faded:bool, x:number, y:number )
GameTriggerMusicFadeOutAndDequeueAll( relative_fade_speed:number = 1 )
GameUnsetPostFxParameter( name:string )
GameVecToPhysicsVec( x:number, y:number = 0 )
GenomeSetHerdId( entity_id:int, new_herd_id:string )
GetDailyPracticeRunSeed()
GetGameEffectLoadTo( entity_id:int, game_effect_name:string, always_load_new:bool )
GetHerdRelation( herd_id_a:int, herd_id_b:int )
GetMaterialInventoryMainMaterial( entity_id:int )
GetParallelWorldPosition( world_pos_x:number, world_pos_y:number )
GetRandomAction( x:number, y:number, max_level:number, i:int = 0)
GetRandomActionWithType( x:number, y:number, max_level:int, type:int, i:int = 0 )
GetSurfaceNormal( pos_x:number, pos_y:number, ray_length:number, ray_count:int )
GetUpdatedComponentID()
GetUpdatedEntityID()
GetValueBool( key:string, default_value:number )
GetValueInteger( key:string, default_value:int )
GetValueNumber( key:string, default_value:number )
--GlobalsGetValue( key:string, default_value:string = "" )
--GlobalsSetValue( key:string, value:string )
GuiAnimateAlphaFadeIn( gui:obj, id:int, speed:number, step:number, reset:bool )
GuiAnimateBegin( gui:obj )
GuiAnimateEnd( gui:obj )
GuiAnimateScaleIn( gui:obj, id:int, acceleration:number, reset:bool )
GuiBeginAutoBox( gui:obj )
GuiBeginScrollContainer( gui:obj, id:int, x:number, y:number, width:number, height:number, scrollbar_gamepad_focusable:bool = true, margin_x:number = 2, margin_y:number = 2 )
GuiButton( gui:obj, id:int, x:number, y:number, text:string )
GuiColorSetForNextWidget( gui:obj, red:number, green:number, blue:number, alpha:number )
GuiCreate()
GuiDestroy( gui:obj )
GuiEndAutoBoxNinePiece( gui:obj, margin:number = 5, size_min_x:number = 0, size_min_y:number = 0, mirrorize_over_x_axis:bool = false, x_axis:number = 0, sprite_filename:string = "data/ui_gfx/decorations/9piece0_gray.png", sprite_highlight_filename:string = "data/ui_gfx/decorations/9piece0_gray.png" )
GuiEndScrollContainer( gui:obj )
GuiGetImageDimensions( gui:obj, image_filename:string, scale:number = 1 )
GuiGetPreviousWidgetInfo( gui:obj )
GuiGetScreenDimensions( gui:obj )
GuiGetTextDimensions( gui:obj, text:string, scale:number = 1, line_spacing:number = 2 )
GuiIdPop( gui:obj )
GuiIdPush( gui:obj, id:int )
GuiIdPushString( gui:obj, str:string )
GuiImage( gui:obj, id:int, x:number, y:number, sprite_filename:string, alpha:number = 1, scale:number = 1, scale_y:number = 0, rotation:number = 0, rect_animation_playback_type:int = GUI_RECT_ANIMATION_PLAYBACK.PlayToEndAndHide, rect_animation_name:string = "" )
GuiImageButton( gui:obj, id:int, x:number, y:number, text:string, sprite_filename:string )
GuiImageNinePiece( gui:obj, id:int, x:number, y:number, width:number, height:number, alpha:number = 1, sprite_filename:string = "data/ui_gfx/decorations/9piece0_gray.png", sprite_highlight_filename:string = "data/ui_gfx/decorations/9piece0_gray.png" )
GuiLayoutAddHorizontalSpacing( gui:obj, amount:number = optional )
GuiLayoutAddVerticalSpacing( gui:obj, amount:number = optional )
GuiLayoutBeginHorizontal( gui:obj, x:number, y:number, position_in_ui_scale:bool = false, margin_x:number = 2, margin_y:number = 2 )
GuiLayoutBeginLayer( gui:obj )
GuiLayoutBeginVertical( gui:obj, x:number, y:number, position_in_ui_scale:bool = false, margin_x:number = 0, margin_y:number = 0 )
GuiLayoutEnd( gui:obj )
GuiLayoutEndLayer( gui:obj )
GuiOptionsAdd( gui:obj, option:int )
GuiOptionsAddForNextWidget( gui:obj, option:int )
GuiOptionsClear( gui:obj )
GuiOptionsRemove( gui:obj, option:int )
GuiSlider( gui:obj, id:int, x:number, y:number, text:string, value:number, value_min:number, value_max:number, value_default:number, value_display_multiplier:number, value_formatting:string, width:number )
GuiStartFrame( gui:obj )
GuiText( gui:obj, x:number, y:number, text:string )
GuiTextCentered( gui:obj, x:number, y:number, text:string )
GuiTextInput( gui:obj, id:int, x:number, y:number, text:string, width:number, max_length:int, allowed_characters:string = "" )
GuiTooltip( gui:obj, text:string, description:string )
GuiZSet( gui:obj, z:float )
GuiZSetForNextWidget( gui:obj, z:float )
HasFlagPersistent( key:string )
HerdIdToString( herd_id:int )
IsInvisible( entity_id:int )
IsPlayer( entity_id:int )
LoadBackgroundSprite( background_file:string, x:number, y:number, background_z_index:number = 40.0, check_biome_corners:bool = false )
LoadEntityToStash( entity_file:string, stash_entity_id:int )
LoadGameEffectEntityTo( entity_id:int, game_effect_entity_file:string )
LoadPixelScene( materials_filename:string, colors_filename:string, x:number, y:number, background_file:string, skip_biome_checks:bool = false, skip_edge_textures:bool = false, color_to_material_table:{string-string} = {}, background_z_index:int = 50 )
LogAction( action_name:string )
LooseChunk( world_pos_x:number, world_pos_y:number, image_filename:string, max_durability:int = 2147483647 )
MagicNumbersGetValue( key:string )
ModDevGenerateSpriteUVsForDirectory( directory_path:string, override_existing:bool = false )
ModGetAPIVersion()
ModGetActiveModIDs()
ModIsEnabled( mod_id:string )
ModLuaFileAppend( to_filename:string, from_filename:string )
ModMagicNumbersFileAdd( filename:string )
ModMaterialsFileAdd( filename:string )
ModRegisterAudioEventMappings( filename:string )
-- ModSettingGet( id:string )
ModSettingGetAtIndex( index:int )
--ModSettingGetCount()
--ModSettingGetNextValue( id:string )
ModSettingRemove( id:string )
--ModSettingSet( id:string, value:bool|number|string )
-- ModSettingSetNextValue( id:string, value:bool|number|string, is_default:bool )
ModTextFileGetContent( filename:string )
ModTextFileSetContent( filename:string, new_content:string )
ModTextFileWhoSetContent( filename:string )
OnActionPlayed( action_id:string )
OnNotEnoughManaForAction()
PhysicsAddBodyCreateBox( entity_id:int, material:string, offset_x:number, offset_y:number, width:int, height:int, centered:bool = false )
PhysicsAddBodyImage( entity_id:int, image_file:string, material:string = "", offset_x:number = 0, offset_y:number = 0, centered:bool = false, is_circle:bool = false, material_image_file:string = "", use_image_as_colors:bool = true )
PhysicsAddJoint( entity_id:int, body_id0:int, body_id1:int, offset_x:number, offset_y:number, joint_type:string )
PhysicsApplyForce( entity_id:int, force_x:number, force_y:number )
PhysicsApplyForceOnArea( calculate_force_for_body_fn:function, ignore_this_entity:int, area_min_x:number, area_min_y:number,area_max_x:number, area_max_y:number )
PhysicsApplyTorque( entity_id:int, torque:number )
PhysicsApplyTorqueToComponent( entity_id:int, component_id:int, torque:number )
PhysicsBody2InitFromComponents( entity_id:int )
PhysicsGetComponentAngularVelocity( entity_id:int, component_id:int )
PhysicsGetComponentVelocity( entity_id:int, component_id:int )
PhysicsRemoveJoints( world_pos_min_x:number, world_pos_min_y:number, world_pos_max_x:number, world_pos_max_y:number  )
PhysicsSetStatic( entity_id:int, is_static:bool )
PhysicsVecToGameVec( x:number, y:number = 0 )
ProceduralRandom( x:number, y:number, a:int|number = optional, b:int|number = optional )
ProceduralRandomf( x:number, y:number, a:number = optional, b:number = optional )
ProceduralRandomi(  x:number, y:number, a:int = optional, b:int = optional )
Random( a:int = optional, b:int = optional )
RandomDistribution( min:int, max:int, mean:int, sharpness:number = 1, baseline:number = 0.005 )
RandomDistributionf( min:number, max:number, mean:number, sharpness:number = 1, baseline:number = 0.005 )
Randomf( min:number = optional, max:number = optional )
Raytrace( x1:number, y1:number, x2:number, y2:number )
RaytracePlatforms( x1:number, y1:number, x2:number, y2:number )
RaytraceSurfaces( x1:number, y1:number, x2:number, y2:number )
RaytraceSurfacesAndLiquiform( x1:number, y1:number, x2:number, y2:number )
RegisterGunAction()
RegisterGunShotEffects()
RegisterProjectile( entity_filename:string )
RegisterSpawnFunction( color:int, function_name:string )
RemoveFlagPersistent( key:string )
SessionNumbersGetValue( key:string )
SessionNumbersSave()
SessionNumbersSetValue( key:string, value:string )
SetPlayerSpawnLocation( x:number, y:number )
SetProjectileConfigs()
SetRandomSeed( x:number, y:number )
SetTimeOut( time_to_execute:number, file_to_execute:string, function_to_call:string = nil )
SetValueBool( key:string, value:number )
SetValueInteger( key:string, value:int )
SetValueNumber( key:string, value:number )
SetWorldSeed( new_seed:int )
SpawnActionItem( x:number, y:number, level:int )
SpawnApparition( x:number, y:number, level:int )
SpawnStash( x:number, y:number, level:int, action_count:int )
StartReload( reload_time:int )
StatsBiomeGetValue( key:string )
StatsBiomeReset()
StatsGetValue( key:string )
StatsGlobalGetValue( key:string )
StatsLogPlayerKill( killed_entity_id:int = 0 )
StreamingForceNewVoting()
StreamingGetConnectedChannelName()
StreamingGetIsConnected()
StreamingGetRandomViewerName()
StreamingGetSettingsGhostsNamedAfterViewers()
StreamingGetVotingCycleDurationFrames()
StreamingSetCustomPhaseDurations( time_between_votes_seconds:number, time_voting_seconds:number )
StreamingSetVotingEnabled( enabled:bool )
StringToHerdId( herd_name:string  )
UnlockItem( action_id:string )
--]]
