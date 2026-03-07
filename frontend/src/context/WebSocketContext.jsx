import React, { createContext, useContext, useEffect, useState, useRef } from 'react';

const WebSocketContext = createContext();

export function useWebSocket() {
  return useContext(WebSocketContext);
}

export const WebSocketProvider = ({ children }) => {
  const [dataStream, setDataStream] = useState([]);
  const [systemState, setSystemState] = useState({
    gridPrice: 0.0,
    gridStatus: 'UNKNOWN',
    batterySoC: 0.0,
    factoryLoad: 0.0,
    actionLog: 'Waiting for connection...'
  });
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);

  const sendIslandingCommand = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ action: "TOGGLE_ISLANDING" }));
    }
  };

  useEffect(() => {
    function connect() {
      ws.current = new WebSocket('ws://localhost:8000/ws');

      ws.current.onopen = () => {
        setIsConnected(true);
        console.log('Connected to Orchestrator API');
      };

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        setSystemState({
          gridPrice: data.gridPrice,
          gridStatus: data.gridStatus,
          batterySoC: data.batterySoC,
          factoryLoad: data.factoryLoad,
          actionLog: data.actionLog,
          batteryHealth: data.batteryHealth,
          transformerHealth: data.transformerHealth,
          firmCapacity: data.firmCapacity,
          activeRoboticLines: data.activeRoboticLines,
          esgReport: data.esgReport,
          predictiveAlerts: data.predictiveAlerts
        });

        setDataStream(prev => {
          const newPoint = {
            time: data.time,
            price: data.gridPrice,
            load: data.factoryLoad
          };
          // Keep the last 20 data points for the chart
          return [...prev.slice(-19), newPoint];
        });
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        console.log('Disconnected. Reconnecting in 3s...');
        setTimeout(connect, 3000);
      };
      
      ws.current.onerror = (err) => {
        console.error('WebSocket Error:', err);
        ws.current.close();
      };
    }

    connect();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const value = {
    dataStream,
    systemState,
    isConnected,
    sendIslandingCommand
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};
