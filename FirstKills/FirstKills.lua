-- FirstKills
--  * keeps combat logging on, so the wow-firstkills.py watcher on your PC can spot
--    first kills in Logs/WoWCombatLog-*.txt and post them to Discord;
--  * saves a snapshot of the character (level, gold, stats, gear) at login and at
--    logout / reload, which the watcher turns into a progress report;
--  * on milestone levels (every 10, and max level) records the level-up and takes
--    a screenshot for the watcher to attach.
-- WoW only writes FirstKillsDB to disk at logout or /reload, so the progress report
-- and milestone posts go out then. Addons can't reach the internet themselves.

local ADDON = ...
local MILESTONE_EVERY = 10

local GetItemInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local SLOTS = {
    "HeadSlot", "NeckSlot", "ShoulderSlot", "BackSlot", "ChestSlot", "WristSlot",
    "HandsSlot", "WaistSlot", "LegsSlot", "FeetSlot", "Finger0Slot", "Finger1Slot",
    "Trinket0Slot", "Trinket1Slot", "MainHandSlot", "SecondaryHandSlot", "RangedSlot",
}
local STATS = { "str", "agi", "sta", "int", "spi" }  -- UnitStat index 1..5

local char  -- this character's entry in FirstKillsDB.chars

local function say(msg)
    print("|cff66ccffFirstKills:|r " .. msg)
end

-- Values can be "secret" (unreadable) for addons in some situations; store nothing then.
local function plain(v)
    if issecretvalue and issecretvalue(v) then return nil end
    return v
end

local function call(fn, ...)
    if type(fn) ~= "function" then return nil end
    local ok, a, b, c, d = pcall(fn, ...)
    if ok then return a, b, c, d end
end

local function snapshot()
    local s = { t = time(), zone = GetZoneText() }
    s.level = plain(UnitLevel("player"))
    s.xp, s.xpMax = plain(call(UnitXP, "player")), plain(call(UnitXPMax, "player"))
    s.money = plain(call(GetMoney))
    s.health = plain(call(UnitHealthMax, "player"))
    s.power = plain(call(UnitPowerMax, "player"))
    s.powerType = select(2, call(UnitPowerType, "player"))

    s.stats = {}
    for i, key in ipairs(STATS) do
        local _, effective = call(UnitStat, "player", i)
        s.stats[key] = plain(effective)
    end
    local _, armor = call(UnitArmor, "player")
    s.stats.armor = plain(armor)
    local base, pos, neg = call(UnitAttackPower, "player")
    if base then s.stats.ap = plain(base + (pos or 0) + (neg or 0)) end
    s.stats.crit = plain(call(GetCritChance))
    s.stats.spellcrit = plain(call(GetSpellCritChance, 2))
    s.stats.dodge = plain(call(GetDodgeChance))

    s.gear = {}
    for _, slot in ipairs(SLOTS) do
        local id = call(GetInventorySlotInfo, slot)
        local link = id and GetInventoryItemLink("player", id)
        if link then
            local name, _, quality, ilvl = call(GetItemInfo, link)
            s.gear[slot] = {
                id = tonumber(link:match("item:(%d+)")),
                name = name or link:match("%[(.-)%]"),
                q = quality,
                ilvl = ilvl,
            }
        end
    end
    return s
end

local function ensureLogging()
    if LoggingCombat and not LoggingCombat() then
        local ok = pcall(LoggingCombat, true)
        if ok and LoggingCombat() then
            say("combat logging on - first kills go to Discord")
        else
            say("couldn't turn on combat logging, type /combatlog")
        end
    end
end

local function isMilestone(level)
    local max = call(GetMaxPlayerLevel)
    return level % MILESTONE_EVERY == 0 or (max and level == max)
end

local frame = CreateFrame("Frame")
frame:RegisterEvent("ADDON_LOADED")
frame:RegisterEvent("PLAYER_ENTERING_WORLD")
frame:RegisterEvent("PLAYER_LEVEL_UP")
frame:RegisterEvent("PLAYER_LOGOUT")
frame:SetScript("OnEvent", function(self, event, ...)
    if event == "ADDON_LOADED" then
        if ... ~= ADDON then return end
        FirstKillsDB = FirstKillsDB or {}
        FirstKillsDB.chars = FirstKillsDB.chars or {}
        self:UnregisterEvent("ADDON_LOADED")

    elseif event == "PLAYER_ENTERING_WORLD" then
        local isInitialLogin = ...
        local name = UnitName("player")
        local key = name .. "-" .. (GetNormalizedRealmName() or GetRealmName():gsub("%s", ""))
        FirstKillsDB.chars[key] = FirstKillsDB.chars[key] or { milestones = {} }
        char = FirstKillsDB.chars[key]
        local _, class = UnitClass("player")
        local _, race = UnitRace("player")
        char.info = { name = name, realm = GetRealmName(), class = class, race = race,
                      sex = UnitSex("player") }
        -- A /reload keeps the session going; only a real login starts a new one.
        if isInitialLogin or not char.sessionStart then
            char.sessionStart = time()
            C_Timer.After(5, function() char.start = snapshot() end)  -- let item info load
        end
        C_Timer.After(2, ensureLogging)

    elseif event == "PLAYER_LEVEL_UP" then
        local level = ...
        if char and isMilestone(level) then
            table.insert(char.milestones, { level = level, t = time(), zone = GetZoneText() })
            C_Timer.After(1.5, function() call(Screenshot) end)  -- catch the level-up glow
        end

    elseif event == "PLAYER_LOGOUT" then
        if char then
            char.last = snapshot()
            char.last.sessionStart = char.sessionStart
            while #char.milestones > 50 do table.remove(char.milestones, 1) end
        end
    end
end)

SLASH_FIRSTKILLS1 = "/firstkills"
SLASH_FIRSTKILLS2 = "/fk"
SlashCmdList.FIRSTKILLS = function()
    ensureLogging()
    say("combat logging is " .. (LoggingCombat() and "ON" or "OFF"))
    if char and char.sessionStart then
        say(("session: %d min - progress report posts when you log out or /reload")
            :format((time() - char.sessionStart) / 60))
    end
end
