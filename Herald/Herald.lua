-- Herald
--  * keeps combat logging on, so the herald.py watcher on your PC can spot
--    first kills in Logs/WoWCombatLog-*.txt and post them to Discord;
--  * saves a snapshot of the character (level, gold, stats, gear) at login and keeps
--    a fresh one while you play, which the watcher turns into a progress report;
--  * on milestone levels (every 10, and max level) records the level-up and takes
--    a screenshot for the watcher to attach;
--  * saves your guild (name, rank, message of the day, roster) for the watcher's
--    phone page.
-- WoW only writes HeraldDB to disk at logout or /reload, so the progress report
-- and milestone posts go out then. Addons can't reach the internet themselves.

local ADDON = ...
local MILESTONE_EVERY = 10
local SNAPSHOT_EVERY = 10  -- seconds
local ROSTER_EVERY = 60    -- seconds between guild roster requests
local MAX_ROSTER = 1000

local RequestGuildRoster = (C_GuildInfo and C_GuildInfo.GuildRoster) or GuildRoster

local GetItemInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local SLOTS = {
    "HeadSlot", "NeckSlot", "ShoulderSlot", "BackSlot", "ChestSlot", "WristSlot",
    "HandsSlot", "WaistSlot", "LegsSlot", "FeetSlot", "Finger0Slot", "Finger1Slot",
    "Trinket0Slot", "Trinket1Slot", "MainHandSlot", "SecondaryHandSlot", "RangedSlot",
}
local STATS = { "str", "agi", "sta", "int", "spi" }  -- UnitStat index 1..5

local char  -- this character's entry in HeraldDB.chars
local knownLevel = 0  -- highest level seen since the addon loaded
local snapshotting = false
local needStart = false  -- a new session still needs its starting snapshot
local lastRosterAsk = 0

local function say(msg)
    print("|cff66ccffHerald:|r " .. msg)
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
    knownLevel = math.max(knownLevel, plain(UnitLevel("player")) or 0)
    s.level = knownLevel
    s.xp, s.xpMax = plain(call(UnitXP, "player")), plain(call(UnitXPMax, "player"))
    s.rested = plain(call(GetXPExhaustion))
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
    base, pos, neg = plain(base), plain(pos), plain(neg)
    if base then s.stats.ap = base + (pos or 0) + (neg or 0) end
    s.stats.crit = plain(call(GetCritChance))
    s.stats.spellcrit = plain(call(GetSpellCritChance, 2))
    s.stats.dodge = plain(call(GetDodgeChance))

    s.gear = {}
    for _, slot in ipairs(SLOTS) do
        local id = call(GetInventorySlotInfo, slot)
        local link = id and plain(GetInventoryItemLink("player", id))
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

-- The guild as the roster shows it. Returns nil when not in a guild, and false when the
-- game hasn't loaded the guild yet (then the saved one is kept).
local function guildSnapshot()
    if not call(IsInGuild) then return nil end
    local name, rank = call(GetGuildInfo, "player")
    name, rank = plain(name), plain(rank)
    if not name then return false end
    local g = { t = time(), name = name, rank = rank, motd = plain(call(GetGuildRosterMOTD)) }
    local total, online = call(GetNumGuildMembers)
    g.total, g.online = plain(total), plain(online)
    g.members = {}
    for i = 1, math.min(g.total or 0, MAX_ROSTER) do
        local r = { pcall(GetGuildRosterInfo, i) }
        local member = r[1] and plain(r[2])
        if type(member) == "string" then
            local m = {
                name = (member:gsub("%-.*", "")),
                rank = plain(r[3]),
                level = plain(r[5]),
                class = plain(r[12]) or plain(r[6]),
                zone = plain(r[7]),
                online = plain(r[10]) and true or nil,
            }
            local note = plain(r[8])
            if note and note ~= "" then m.note = note end
            if not m.online then
                local y, mo, d, h = call(GetGuildRosterLastOnline, i)
                y, mo, d, h = plain(y), plain(mo), plain(d), plain(h)
                if y then m.away = ((y * 365 + (mo or 0) * 30 + (d or 0)) * 24 + (h or 0)) * 3600 end
            end
            table.insert(g.members, m)
        end
    end
    return g
end

local lastGuildRead = 0

local function refreshGuild()
    if not char or time() - lastGuildRead < 5 then return end  -- the event comes in bursts
    lastGuildRead = time()
    local g = guildSnapshot()
    if g ~= false then char.guild = g end
end

local function askForRoster()
    if call(IsInGuild) and time() - lastRosterAsk >= ROSTER_EVERY then
        lastRosterAsk = time()
        call(RequestGuildRoster)  -- the answer comes as GUILD_ROSTER_UPDATE
    end
end

-- The game has already emptied the character by PLAYER_LOGOUT: money, XP, stats and
-- gear read as 0 and UnitLevel gives the level from login. So char.last is kept up to
-- date during play instead, and whatever is in it gets written to disk at logout.
local function refreshLast()
    if call(InCombatLockdown) then return end  -- values can be unreadable in combat
    local s = snapshot()
    if s.level > 0 and (s.stats.sta or 0) > 0 then  -- not during a loading screen
        if needStart then
            char.start, needStart = snapshot(), false
        end
        s.sessionStart = char.sessionStart
        char.last = s
        if not call(IsInGuild) then char.guild = nil end  -- left the guild
        askForRoster()
    end
end

local function keepSnapshotting()
    C_Timer.After(SNAPSHOT_EVERY, keepSnapshotting)  -- first, so an error can't end the loop
    local ok, err = pcall(refreshLast)
    if not ok then
        HeraldDB.snapshotError = { t = time(), msg = tostring(err) }
    end
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
frame:RegisterEvent("GUILD_ROSTER_UPDATE")
frame:RegisterEvent("PLAYER_GUILD_UPDATE")
frame:SetScript("OnEvent", function(self, event, ...)
    if event == "ADDON_LOADED" then
        if ... ~= ADDON then return end
        HeraldDB = HeraldDB or {}
        HeraldDB.chars = HeraldDB.chars or {}
        self:UnregisterEvent("ADDON_LOADED")

    elseif event == "PLAYER_ENTERING_WORLD" then
        local isInitialLogin = ...
        local name = UnitName("player")
        local key = name .. "-" .. (GetNormalizedRealmName() or GetRealmName():gsub("%s", ""))
        HeraldDB.chars[key] = HeraldDB.chars[key] or { milestones = {} }
        char = HeraldDB.chars[key]
        local _, class = UnitClass("player")
        local _, race = UnitRace("player")
        char.info = { name = name, realm = GetRealmName(), class = class, race = race,
                      sex = UnitSex("player") }
        -- A /reload keeps the session going; only a real login starts a new one.
        if isInitialLogin or not char.sessionStart then
            char.sessionStart = time()
            needStart = true
        end
        if not snapshotting then
            snapshotting = true
            C_Timer.After(5, keepSnapshotting)  -- let item info load
        end
        C_Timer.After(2, ensureLogging)

    elseif event == "PLAYER_LEVEL_UP" then
        local level = ...
        knownLevel = math.max(knownLevel, level)
        if char and isMilestone(level) then
            table.insert(char.milestones, { level = level, t = time(), zone = GetZoneText() })
            C_Timer.After(1.5, function() call(Screenshot) end)  -- catch the level-up glow
        end

    elseif event == "GUILD_ROSTER_UPDATE" then
        if not call(InCombatLockdown) then pcall(refreshGuild) end

    elseif event == "PLAYER_GUILD_UPDATE" then
        lastRosterAsk = 0
        askForRoster()

    elseif event == "PLAYER_LOGOUT" then
        if char then
            while #char.milestones > 50 do table.remove(char.milestones, 1) end
        end
    end
end)

SLASH_HERALD1 = "/herald"
SlashCmdList.HERALD = function()
    ensureLogging()
    say("combat logging is " .. (LoggingCombat() and "ON" or "OFF"))
    if char and char.sessionStart then
        say(("session: %d min - progress report posts when you log out or /reload")
            :format((time() - char.sessionStart) / 60))
    end
    if char and char.last then
        say(("last snapshot: %d sec ago, level %d"):format(time() - char.last.t, char.last.level))
    end
    if HeraldDB.snapshotError then
        say("last snapshot error: " .. HeraldDB.snapshotError.msg)
    end
end
