-- Addon Updater (the in-game part of updater/updater.py)
--  * at login, says which addons the updater program on the PC updated since last time,
--    with the release notes;
--  * experimental: during play, says when an update was installed that needs a /reload, or
--    one that waits for WoW to restart. Addons can't hear from programs on the PC, so the
--    program writes either a real font or junk to probe/reload.ttf and probe/restart.ttf, and
--    this addon checks every few seconds whether they load as a font.
-- Managed.lua (written by the program) lists the addons it keeps up to date.

local ADDON = ...
local PROBE = "Interface\\AddOns\\" .. ADDON .. "\\probe\\"
local CHECK_SECONDS = 10
local GetMeta = (C_AddOns and C_AddOns.GetAddOnMetadata) or GetAddOnMetadata

local MESSAGES = {
    reload = "An addon update was installed. Type |cffffff00/reload|r to start using it.",
    restart = "An addon update is ready. It installs when you close WoW; it's there next time you play.",
}

local function say(msg)
    print("|cff66ccffAddon Updater:|r " .. msg)
end

local function announce(msg)
    say(msg)
    if RaidNotice_AddMessage and RaidWarningFrame and ChatTypeInfo then
        pcall(RaidNotice_AddMessage, RaidWarningFrame, "Addon Updater: " .. msg, ChatTypeInfo.SYSTEM)
    end
end

local probe  -- a font string that is never shown; only used to try loading the probe fonts

local function lit(name)
    if not probe then return false end
    local ok, loaded = pcall(probe.SetFont, probe, PROBE .. name .. ".ttf", 12, "")
    return (ok and loaded) and true or false
end

local function managed()
    return AddonUpdater_Managed or {}
end

-- Compare each managed addon's version with the one seen at the last login.
local function announceUpdates()
    AddonUpdaterDB.seen = AddonUpdaterDB.seen or {}
    for _, a in ipairs(managed()) do
        local version = GetMeta and GetMeta(a.name, "Version")
        local before = AddonUpdaterDB.seen[a.name]
        if version and before and before ~= version then
            local notes = (a.version == version and a.notes ~= "") and (" - " .. a.notes:gsub("|", "||")) or ""
            say(("%s updated: %s -> |cff00ff00%s|r%s"):format(a.name, before, version, notes))
        end
        if version then AddonUpdaterDB.seen[a.name] = version end
    end
end

local state = {}  -- per probe: lit at login, and whether it was announced this session

local function watchProbes()
    for name in pairs(MESSAGES) do
        local now = lit(name)
        local s = state[name]
        -- Only a probe that lights up during the session counts: one lit at login is left
        -- over from before (a /reload already picked that update up). The exception is
        -- restart, which stays true until WoW closes.
        if now and not s.announced and (not s.atLogin or name == "restart") then
            s.announced = true
            announce(MESSAGES[name])
        end
        if not now then s.atLogin = false end
    end
end

local frame = CreateFrame("Frame")
frame:RegisterEvent("PLAYER_LOGIN")
frame:SetScript("OnEvent", function()
    AddonUpdaterDB = AddonUpdaterDB or {}
    announceUpdates()
    probe = frame:CreateFontString()
    for name in pairs(MESSAGES) do
        state[name] = { atLogin = lit(name), announced = false }
    end
    watchProbes()
    if C_Timer and C_Timer.NewTicker then
        C_Timer.NewTicker(CHECK_SECONDS, watchProbes)
    end
end)

SLASH_ADDONUPDATER1 = "/updates"
SlashCmdList.ADDONUPDATER = function()
    if #managed() == 0 then
        say("no addons are kept up to date yet. Run an addon's installer on your PC.")
        return
    end
    for _, a in ipairs(managed()) do
        local version = GetMeta and GetMeta(a.name, "Version") or "?"
        local latest = (a.version ~= "" and a.version ~= version) and (" (|cff00ff00" .. a.version .. "|r is out)") or ""
        say(("%s %s%s"):format(a.name, version, latest))
    end
    say(("in-game notice check: reload %s, restart %s"):format(
        lit("reload") and "ON" or "off", lit("restart") and "ON" or "off"))
end
