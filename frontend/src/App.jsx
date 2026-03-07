import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, Battery, Factory, Zap, WifiOff, ShieldAlert } from 'lucide-react';
import { useWebSocket } from './context/WebSocketContext';

export default function Dashboard() {
  const { dataStream, systemState, isConnected, sendIslandingCommand } = useWebSocket();

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header */}
        <header className="flex items-center justify-between pb-6 border-b border-neutral-800">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              Resilient Micro-Hub Orchestrator
            </h1>
            <p className="text-neutral-400 mt-1">Real-Time BTM (Behind-the-Meter) Operations</p>
          </div>
          <div className="flex items-center gap-4">
            
            <button 
              onClick={sendIslandingCommand}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border font-medium transition-all ${
                systemState.gridStatus !== "NORMAL" 
                  ? "bg-red-500/20 text-red-400 border-red-500/50 hover:bg-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.3)]" 
                  : "bg-neutral-900 text-neutral-400 border-neutral-700 hover:bg-neutral-800 hover:text-white"
              }`}
            >
              <ShieldAlert className="w-4 h-4" />
              {systemState.gridStatus !== "NORMAL" ? "Restore Grid" : "Force Islanding"}
            </button>

            <div className="flex items-center gap-2 bg-neutral-900 px-4 py-2 rounded-full border border-neutral-800">
               {isConnected ? (
                 <>
                   <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                   <span className="text-sm font-medium text-neutral-300">Live Telemetry</span>
                 </>
               ) : (
                 <>
                   <WifiOff className="w-4 h-4 text-red-500" />
                   <span className="text-sm font-medium text-red-500">Disconnected</span>
                 </>
               )}
            </div>
          </div>
        </header>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          
          <MetricCard 
            icon={<Activity className="text-cyan-400" />}
            title="ERCOT LMP (Real-Time)"
            value={`$${systemState.gridPrice.toFixed(2)}`}
            subtitle="per MWh"
            alert={systemState.gridStatus !== "NORMAL"}
          />
          
          <MetricCard 
            icon={<Battery className="text-emerald-400" />}
            title="Battery & Cell Health"
            value={`${systemState.batterySoC.toFixed(1)}% SoC`}
            subtitle={systemState.batteryHealth ? `Cell Health: ${systemState.batteryHealth.toFixed(1)}%` : "10.0 MWh Capacity"}
            alert={systemState.batteryHealth && systemState.batteryHealth < 90.0}
          />

          <MetricCard 
            icon={<Factory className="text-orange-400" />}
            title="Robotic Factory Lines"
            value={`${systemState.activeRoboticLines !== undefined ? systemState.activeRoboticLines : 4} / 4 Active`}
            subtitle={`${systemState.factoryLoad.toFixed(2)} MW (Firm: ${systemState.firmCapacity ? systemState.firmCapacity.toFixed(2) : '0.50'} MW)`}
          />

          <MetricCard 
            icon={<Zap className="text-purple-400" />}
            title="AI Trading Agent"
            value={systemState.gridStatus !== "NORMAL" ? "ISLANDED" : "LangGraph Active"}
            subtitle={systemState.actionLog}
            highlight={systemState.gridStatus !== "NORMAL" || systemState.actionLog.includes("High grid price") || systemState.actionLog.includes("Low grid price")}
          />
        </div>

        {/* Charts Dashboard */}
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-2xl">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Activity className="w-5 h-5 text-neutral-400" />
            Grid Price vs. Factory Load
          </h2>
          <div className="h-80 w-full relative">
            {!isConnected && (
              <div className="absolute inset-0 z-10 flex items-center justify-center bg-neutral-950/50 backdrop-blur-sm rounded-lg">
                <span className="text-neutral-400 font-medium">Connecting to Backend Data Stream...</span>
              </div>
            )}
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dataStream}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                <XAxis dataKey="time" stroke="#737373" fontSize={12} tickMargin={10} />
                <YAxis yAxisId="left" stroke="#22d3ee" fontSize={12} domain={['auto', 'auto']} />
                <YAxis yAxisId="right" orientation="right" stroke="#fb923c" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#171717', border: '1px solid #262626', borderRadius: '8px' }}
                  itemStyle={{ color: '#e5e5e5' }}
                />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="price" stroke="#22d3ee" strokeWidth={2} dot={false} name="Grid Price ($)" isAnimationActive={false} />
                <Line yAxisId="right" type="stepAfter" dataKey="load" stroke="#fb923c" strokeWidth={2} dot={false} name="Factory Load (MW)" isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* ESG Compliance Ledger */}
        {systemState.esgReport && (
          <div className="mt-8 bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <Zap className="w-5 h-5 text-emerald-400" />
                ESG & Automated Compliance Ledger (ISSB / CBAM)
              </h2>
              <span className="text-xs font-mono text-neutral-500 bg-neutral-950 px-3 py-1 rounded-full border border-neutral-800">
                MRV Verified • LOCAL NODE
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-4 bg-neutral-950 rounded-lg border border-neutral-800">
                <h4 className="text-sm text-neutral-400 mb-1">Total Clean Energy Used (BTM)</h4>
                <div className="text-2xl font-mono text-white flex items-baseline gap-2">
                  {systemState.esgReport.cleanEnergyUsedMWh.toFixed(2)} <span className="text-sm text-neutral-500">MWh</span>
                </div>
              </div>
              
              <div className="p-4 bg-neutral-950 rounded-lg border border-emerald-900/50 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl -mr-16 -mt-16"></div>
                <h4 className="text-sm text-neutral-400 mb-1 relative z-10">Scope 3 Emissions Avoided</h4>
                <div className="text-2xl font-mono text-emerald-400 flex items-baseline gap-2 relative z-10">
                  {systemState.esgReport.emissionsAvoidedLbs.toFixed(2)} <span className="text-sm text-emerald-600/50">lbs CO₂</span>
                </div>
              </div>
              
              <div className="p-4 bg-neutral-950 rounded-lg border border-neutral-800">
                <h4 className="text-sm text-neutral-400 mb-1">Total Resilience Uptime</h4>
                <div className="text-2xl font-mono text-white flex items-baseline gap-2">
                  {systemState.esgReport.islandedHours.toFixed(2)} <span className="text-sm text-neutral-500">Hours Islanded</span>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

// Reusable UI Component
function MetricCard({ icon, title, value, subtitle, highlight, alert }) {
  let bgStyle = 'bg-neutral-900 border-neutral-800 shadow-lg';
  let titleStyle = 'text-white';
  
  if (alert) {
      bgStyle = 'bg-red-950/20 border-red-500 shadow-red-500/20 shadow-lg';
      titleStyle = 'text-red-400';
  } else if (highlight) {
      bgStyle = 'bg-neutral-800 border-purple-500 shadow-purple-500/20 shadow-lg';
      titleStyle = 'text-purple-400';
  }

  return (
    <div className={`p-6 rounded-xl border flex flex-col justify-between transition-colors duration-500 ${bgStyle}`}>
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-neutral-950 rounded-lg border border-neutral-800">
           {icon}
        </div>
        <h3 className="text-sm font-medium text-neutral-400">{title}</h3>
      </div>
      <div>
        <div className={`text-2xl font-bold ${titleStyle}`}>{value}</div>
        <div className="text-xs text-neutral-500 mt-1">{subtitle}</div>
      </div>
    </div>
  );
}
