'use client';

import React, { useState } from 'react';
import './CircuitBoard.css';

export interface CircuitNode {
  id: string;
  x: number;
  y: number;
  label: string;
  sublabel?: string;
  icon: React.ReactNode;
  description?: string;
  badge?: string;
}

export interface CircuitConnection {
  from: string;
  to: string;
  animated?: boolean;
}

export interface CircuitBoardProps {
  nodes: CircuitNode[];
  connections: CircuitConnection[];
  width?: number;
  height?: number;
  className?: string;
  activeId?: string;
  onNodeSelect?: (node: CircuitNode) => void;
}

export const CircuitBoard: React.FC<CircuitBoardProps> = ({
  nodes,
  connections,
  width = 500,
  height = 300,
  className = '',
  activeId,
  onNodeSelect
}) => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string>(activeId || nodes[0]?.id || '');

  const activeNode = nodes.find(n => n.id === (hoveredId || activeId || selectedId)) || nodes[0];
  const nodeMap = new Map<string, CircuitNode>(nodes.map(n => [n.id, n]));

  const handleSelect = (node: CircuitNode) => {
    setSelectedId(node.id);
    onNodeSelect?.(node);
  };

  return (
    <div className={`circuit-board-wrapper space-y-4 ${className}`.trim()}>
      <div className="circuit-board p-3 sm:p-6" style={{ minHeight: `${height + 40}px` }}>
        <div className="circuit-board__grid" aria-hidden="true" />
        <div className="circuit-board__glow" aria-hidden="true" />

        {/* SVG Circuit Traces */}
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="circuit-board__svg relative z-0"
          aria-hidden="true"
        >
          <defs>
            <linearGradient id="traceGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#2dd4bf" stopOpacity="0.2" />
              <stop offset="50%" stopColor="#2dd4bf" stopOpacity="1" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.2" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {connections.map((conn, idx) => {
            const start = nodeMap.get(conn.from);
            const end = nodeMap.get(conn.to);
            if (!start || !end) return null;

            // Compute clean 90-degree PCB trace
            const midX = (start.x + end.x) / 2;
            const pathD =
              start.y === end.y
                ? `M ${start.x} ${start.y} L ${end.x} ${end.y}`
                : `M ${start.x} ${start.y} H ${midX} V ${end.y} H ${end.x}`;

            return (
              <g key={`${conn.from}-${conn.to}-${idx}`}>
                {/* Base passive trace */}
                <path d={pathD} className="circuit-trace-base" />

                {/* Solder junction dots */}
                {start.y !== end.y && (
                  <>
                    <circle cx={midX} cy={start.y} r="2" fill="rgba(255,255,255,0.25)" />
                    <circle cx={midX} cy={end.y} r="2" fill="rgba(255,255,255,0.25)" />
                  </>
                )}

                {/* Animated glowing energy pulse */}
                {conn.animated !== false && (
                  <path
                    d={pathD}
                    className={`circuit-trace-pulse circuit-trace-pulse--delay-${idx % 4}`}
                  />
                )}
              </g>
            );
          })}
        </svg>

        {/* Nodes positioned over the canvas */}
        <div className="absolute inset-0 pointer-events-none">
          {nodes.map(node => {
            const isSelected = node.id === (activeId || selectedId);

            // Convert viewBox coordinates to percentage positioning
            const leftPercent = (node.x / width) * 100;
            const topPercent = (node.y / height) * 100;

            return (
              <div
                key={node.id}
                role="button"
                tabIndex={0}
                className="circuit-node pointer-events-auto"
                style={{ left: `${leftPercent}%`, top: `${topPercent}%` }}
                data-active={isSelected ? 'true' : undefined}
                onClick={() => handleSelect(node)}
                onKeyDown={e => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleSelect(node);
                  }
                }}
                onMouseEnter={() => setHoveredId(node.id)}
                onMouseLeave={() => setHoveredId(null)}
                aria-label={`${node.label}: ${node.sublabel ?? ''}`}
              >
                <div className="circuit-node__box">
                  {node.icon}
                </div>
                <span className="circuit-node__label">{node.label}</span>
                {node.sublabel && <span className="circuit-node__sublabel">{node.sublabel}</span>}
              </div>
            );
          })}
        </div>
      </div>

      {/* Minimal, Executive Explanation Panel */}
      {activeNode && (
        <div className="p-4 rounded-xl bg-[#091322]/80 border border-teal-500/20 backdrop-blur-md flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse shrink-0" />
            <div>
              <span className="font-semibold text-white tracking-tight mr-2">
                {activeNode.label}
              </span>
              <span className="text-slate-400 font-sans">
                {activeNode.description}
              </span>
            </div>
          </div>
          {activeNode.badge && (
            <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-teal-950/60 text-teal-300 border border-teal-500/30 whitespace-nowrap self-start sm:self-auto">
              {activeNode.badge}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default CircuitBoard;
