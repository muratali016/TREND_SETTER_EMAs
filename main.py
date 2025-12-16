//@version=5
indicator("MAIN 5/9/20 EMA + VWAP + CFO DASH", overlay=true)

// ==========================================
// 1. INPUTS
// ==========================================
superFastLen = input.int(5,  "Signal EMA (Super Fast)")
fastLen      = input.int(9,  "Trigger EMA (Fast)")
slowLen      = input.int(20, "Trend EMA (Slow)")
src          = input.source(close, "Source")
showLabels   = input.bool(true, "Show Labels")
colorBars    = input.bool(true, "Color Bars by Trend")
showBands    = input.bool(true, "Show VWAP Std Bands", group="Bands")
bandMult     = input.float(2.0, "Band Deviation (Std)", group="Bands")

// Angle controls (Looking at 5 and 9)
angleLookback   = input.int(5,  "Angle Lookback (bars)", minval=1)
minAngleDeg     = input.float(10.0, "Min |Angle| for 'Strong' (deg)")
similarTolDeg   = input.float(6.0,  "Max Angle Difference for 'Similar' (deg)")
volMultStrong   = input.float(1.5,  "Vol × AvgVol for 'Strong'")

// Over-extension control
overExtPct      = input.float(1.0,  "Over-extension above EMA5 (%)", minval=0.1, step=0.1)

// Confirmation controls
confirmBars     = input.int(2, "Confirm bars after cross", minval=1, maxval=5)
confirmVolMult  = input.float(1.0, "Volume × AvgVol for confirmation")

// ==========================================
// 2. CALCULATIONS
// ==========================================
emaSuperFast = ta.ema(src, superFastLen) // 5 EMA
emaFast      = ta.ema(src, fastLen)      // 9 EMA
emaSlow      = ta.ema(src, slowLen)      // 20 EMA
vwap         = ta.vwap(close)

// --- NEW: VWAP STDEV BANDS ---
// Using rolling standard deviation for scalping responsiveness
stdevVal = ta.stdev(close, 20)
bandUpper = vwap + (bandMult * stdevVal)
bandLower = vwap - (bandMult * stdevVal)
currentZScore = (close - vwap) / stdevVal // How many deviations away are we?

// --- NEW: RELATIVE VOLUME (RVOL) ---
vol    = volume
volAvg = ta.sma(vol, 20)
rvol   = vol / volAvg
highVol = vol > volAvg * volMultStrong

// ==========================================
// 3. SIGNAL LOGIC
// ==========================================

// A. STANDARD CROSS SIGNALS (5 crossing 9)
buy  = ta.crossover(emaSuperFast, emaFast)
sell = ta.crossunder(emaSuperFast, emaFast)

// B. TREND ALIGNMENT SIGNALS
// 1. Standard Trend (5 > 9 > 20)
bullishTrendStart = (emaSuperFast > emaFast) and (emaFast > emaSlow) and not ((emaSuperFast[1] > emaFast[1]) and (emaFast[1] > emaSlow[1]))
bearishTrendStart = (emaSuperFast < emaFast) and (emaFast < emaSlow) and not ((emaSuperFast[1] < emaFast[1]) and (emaFast[1] < emaSlow[1]))

// 2. STRONG VWAP TREND (5 > 9 > VWAP > 20)
bullishVwapTrend = (emaSuperFast > emaFast) and (emaFast > vwap) and (vwap > emaSlow)
bearishVwapTrend = (emaSuperFast < emaFast) and (emaFast < vwap) and (vwap < emaSlow)

// Trigger distinct label only when this specific state begins
bullVwapStart = bullishVwapTrend and not bullishVwapTrend[1]
bearVwapStart = bearishVwapTrend and not bearishVwapTrend[1]

// C. ANGLES
pi = 3.1415926535
deltaSuper = emaSuperFast - emaSuperFast[angleLookback]
deltaFast  = emaFast - emaFast[angleLookback]
angleSuper = math.atan(deltaSuper / angleLookback) * 180 / pi
angleFast  = math.atan(deltaFast / angleLookback) * 180 / pi

angleSimilar   = math.abs(angleSuper - angleFast) <= similarTolDeg
bullishAngles  = angleSuper >  minAngleDeg and angleFast >  minAngleDeg
bearishAngles  = angleSuper < -minAngleDeg and angleFast < -minAngleDeg

// D. 2-BAR CONFIRMATIONS
greenVolOK = true
redVolOK   = true
for i = 0 to confirmBars - 1
    greenBar = close[i] > open[i]
    redBar   = close[i] < open[i]
    volOK    = volume[i] > volAvg[i] * confirmVolMult
    greenVolOK := greenVolOK and greenBar and volOK
    redVolOK   := redVolOK   and redBar   and volOK

confirmedBuy  = buy[confirmBars]  and greenVolOK
confirmedSell = sell[confirmBars] and redVolOK

// E. SERT & OVER-EXTENSION
sertBullish = buy  and bullishAngles and angleSimilar and close > vwap and highVol
sertBearish = sell and bearishAngles and angleSimilar and close < vwap and highVol
overExtended = close > emaSuperFast * (1.0 + overExtPct/100.0) and emaSuperFast > emaFast

// ==========================================
// 4. PLOTS & VISUALS
// ==========================================
plot(emaSuperFast, "EMA 5",  color=color.new(color.black, 0), linewidth=2)
plot(emaFast,      "EMA 9",  color=color.new(color.yellow, 0), linewidth=2)
plot(emaSlow,      "EMA 20", color=color.new(color.purple, 0), linewidth=2)
plot(vwap,         "VWAP",   color=color.new(color.red, 0), linewidth=2)

// Plot Bands (Toggleable)
plot(showBands ? bandUpper : na, "VWAP Upper Band", color=color.new(color.red, 80), linewidth=1)
plot(showBands ? bandLower : na, "VWAP Lower Band", color=color.new(color.green, 80), linewidth=1)
fill(plot(showBands ? bandUpper : na), plot(showBands ? bandLower : na), color=color.new(color.blue, 95), title="VWAP Band Fill")

// Labels
// 1. Scalp Cross (5/9)
plotshape(showLabels and buy,  title="Buy 5/9",  style=shape.triangleup,   location=location.belowbar,
     color=color.new(color.lime, 0), size=size.tiny, text="Buy")
plotshape(showLabels and sell, title="Sell 5/9", style=shape.triangledown, location=location.abovebar,
     color=color.new(color.red, 0),  size=size.tiny, text="Sell")

// 2. Standard Trend Alignment (5 > 9 > 20)
plotshape(showLabels and bullishTrendStart, title="Bull Trend Start", style=shape.labelup, location=location.belowbar,
     color=color.new(color.blue, 0), textcolor=color.white, size=size.small, text="Trend\n5>9>20")
plotshape(showLabels and bearishTrendStart, title="Bear Trend Start", style=shape.labeldown, location=location.abovebar,
     color=color.new(color.blue, 0), textcolor=color.white, size=size.small, text="Trend\n5<9<20")

// 3. STRONG VWAP TREND (5 > 9 > VWAP > 20)
plotshape(showLabels and bullVwapStart, title="Strong VWAP Trend Bull", style=shape.labelup, location=location.belowbar,
     color=color.new(color.orange, 0), textcolor=color.white, size=size.small, text="Strong\n5>9>V>20")
plotshape(showLabels and bearVwapStart, title="Strong VWAP Trend Bear", style=shape.labeldown, location=location.abovebar,
     color=color.new(color.orange, 0), textcolor=color.white, size=size.small, text="Strong\n5<9<V<20")

// 4. Confirmed Signals
plotshape(showLabels and confirmedBuy,  title="Confirmed Buy",  style=shape.triangleup,   location=location.belowbar,
     color=color.new(color.green, 0), size=size.small, text="✅ Buy (2)")
plotshape(showLabels and confirmedSell, title="Confirmed Sell", style=shape.triangledown, location=location.abovebar,
     color=color.new(color.maroon, 0), size=size.small, text="✅ Sell (2)")

// 5. Sert & Over-Ext
plotshape(showLabels and sertBullish, title="Sert Bullish", style=shape.triangleup,
     location=location.belowbar, color=color.new(color.lime, 0), size=size.small, text="Sert Bullish")
plotshape(showLabels and sertBearish, title="Sert Bearish", style=shape.triangledown,
     location=location.abovebar, color=color.new(color.maroon, 0), size=size.small, text="Sert Bearish")
plotshape(showLabels and overExtended, title="Over-Extended",
     style=shape.diamond, location=location.abovebar, color=color.new(color.orange, 0), size=size.tiny, text="Over-Ext")

// Bar coloring
barcolor(colorBars ? (emaSuperFast > emaFast ? color.new(color.lime, 70) : color.new(color.red, 70)) : na)

// ==========================================
// 5. ALERTS
// ==========================================
alertcondition(buy,               title="5/9 EMA Bull Cross",   message="5 EMA crossed ABOVE 9 EMA")
alertcondition(sell,              title="5/9 EMA Bear Cross",   message="5 EMA crossed BELOW 9 EMA")
alertcondition(bullishTrendStart, title="Bull Trend Start",     message="Perfect Bull Alignment: 5 > 9 > 20")
alertcondition(bearishTrendStart, title="Bear Trend Start",     message="Perfect Bear Alignment: 5 < 9 < 20")
alertcondition(bullVwapStart,     title="Strong VWAP Bull",     message="Strong Bull Alignment: 5 > 9 > VWAP > 20")
alertcondition(bearVwapStart,     title="Strong VWAP Bear",     message="Strong Bear Alignment: 5 < 9 < VWAP < 20")

// ==========================================
// 6. CFO DASHBOARD (VIX / ADR / Exp Move / ADX / RVOL / STD)
// ==========================================

// Get Data
vixVal = request.security("CBOE:VIX", "", close)
dHigh  = request.security(syminfo.tickerid, "D", high)
dLow   = request.security(syminfo.tickerid, "D", low)
adrVal = request.security(syminfo.tickerid, "D", ta.sma(high - low, 10))
dayRangeCurrent = dHigh - dLow
expectedMovePct = vixVal / 16.0
[diplus, diminus, adxVal] = ta.dmi(14, 14)

// Draw Table (Increased size to 7 rows)
var table dashTable = table.new(position.bottom_right, 2, 7, border_width=1, frame_color=color.gray, border_color=color.gray)

if barstate.islast
    // Headers
    table.cell(dashTable, 0, 0, "Metric",   bgcolor=color.gray, text_color=color.white, text_size=size.small)
    table.cell(dashTable, 1, 0, "Value",    bgcolor=color.gray, text_color=color.white, text_size=size.small)

    // Row 1: VIX
    table.cell(dashTable, 0, 1, "VIX",      bgcolor=color.black, text_color=color.white, text_size=size.small)
    table.cell(dashTable, 1, 1, str.tostring(vixVal, "#.##"), bgcolor=vixVal > 20 ? color.maroon : color.black, text_color=color.white, text_size=size.small)

    // Row 2: ADR
    table.cell(dashTable, 0, 2, "ADR (10)", bgcolor=color.black, text_color=color.white, text_size=size.small)
    table.cell(dashTable, 1, 2, str.tostring(adrVal, "#.##"), bgcolor=dayRangeCurrent > adrVal ? color.orange : color.black, text_color=color.white, text_size=size.small)

    // Row 3: Exp Move
    table.cell(dashTable, 0, 3, "Exp Move", bgcolor=color.black, text_color=color.white, text_size=size.small)
    table.cell(dashTable, 1, 3, str.tostring(expectedMovePct, "#.##") + "%", bgcolor=color.black, text_color=color.white, text_size=size.small)

    // Row 4: ADX
    table.cell(dashTable, 0, 4, "ADX (14)", bgcolor=color.black, text_color=color.white, text_size=size.small)
    table.cell(dashTable, 1, 4, str.tostring(adxVal, "#.##"), bgcolor=adxVal > 25 ? color.green : color.gray, text_color=color.white, text_size=size.small)

    // Row 5: RVOL (Volume / Avg)
    table.cell(dashTable, 0, 5, "RVOL",     bgcolor=color.black, text_color=color.white, text_size=size.small)
    table.cell(dashTable, 1, 5, str.tostring(rvol, "#.##") + "x", bgcolor=rvol > 1.0 ? color.green : color.gray, text_color=color.white, text_size=size.small)

    // Row 6: STD Dist (Distance from VWAP)
    zScoreColor = math.abs(currentZScore) > 2.0 ? color.orange : color.black
    table.cell(dashTable, 0, 6, "VWAP Dev", bgcolor=color.black, text_color=color.white, text_size=size.small)
    table.cell(dashTable, 1, 6, (currentZScore > 0 ? "+" : "") + str.tostring(currentZScore, "#.##") + "σ", bgcolor=zScoreColor, text_color=color.white, text_size=size.small)
